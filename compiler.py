"""
 Copyright (C) 2019  Daniel Vrátil <me@dvratil.cz>

 This program is free software: you can redistribute it and/or modify
 it under the terms of the GNU General Public License as published by
 the Free Software Foundation, either version 3 of the License, or
 (at your option) any later version.

 This program is distributed in the hope that it will be useful,
 but WITHOUT ANY WARRANTY; without even the implied warranty of
 MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 GNU General Public License for more details.

 You should have received a copy of the GNU General Public License
 along with this program.  If not, see <https://www.gnu.org/licenses/>.
"""

import ast

class AsmGeneratorError(Exception):
    pass

class AsmEmitter:
    class FunctionEmitter:
        def __init__(self, emitter, name):
            self._emitter = emitter
            self._name = name

        def __enter__(self):
            self._emitter.begin_function(self._name)

        def __exit__(self, type, value, traceback):
            self._emitter.end_function()

    def __init__(self, output):
        self._output = output
        self._depth = 0
        self._step = 4

    def function(self, name):
        return AsmEmitter.FunctionEmitter(self, name)

    def begin_function(self, name):
        self._write(f"    .global {name}")
        self._write(f"{name}:")
        self._depth += 1
        self.instruction("pushq", "%rbp")
        self.instruction("movq", "%rsp", "%rbp")

    def end_function(self):
        self.instruction("popq", "%rbp")
        self.instruction("ret")
        self._depth -= 1

    def instruction(self, instruction, *args):
        self._write(f"{instruction} {', '.join([str(s) for s in args])}")

    def label(self, label):
        self._write(f"{label}:", ident=False)

    def push_stack(self, reg):
        self.instruction("push", reg)

    def pop_stack(self, reg):
        self.instruction("pop", reg)

    def _write(self, data, ident=True):
        if ident:
            self._output.write(" " * self._depth * self._step)
        self._output.write(data)
        self._output.write("\n")


class AsmGenerator:
    def __init__(self, output):
        self.emitter = AsmEmitter(output)
        self.__lastLabelId = 0

    def generate(self, ast):
        self.emit_program_asm(ast)


    def emit_program_asm(self, program_node):
        for func in program_node.nodes():
            self.emit_function_asm(func)

    def emit_function_asm(self, function_node):
        with self.emitter.function(function_node.name):
            for stmt in function_node.nodes():
                self.emit_statement_asm(stmt)

    def emit_statement_asm(self, stmt_node):
        if isinstance(stmt_node, ast.ReturnStmtNode):
            self.emit_return_stmt_asm(stmt_node)
        else:
            raise AsmGeneratorError("Node {stmt_node} is not a statement node")

    def emit_return_stmt_asm(self, ret_node):
        # For return we first need to emit the expression, then the return itself
        assert(len(ret_node.nodes()) == 1)

        expr_node = ret_node.nodes()[0]
        self.emit_expression_stmt(expr_node);

    def __generate_label(self, label):
        label = f'{label}_{self.__lastLabelId}'
        self.__lastLabelId += 1
        return label

    def emit_expression_stmt(self, stmt_node):
        if isinstance(stmt_node, ast.ConstantNode):
            self.emitter.instruction("movl", f"${stmt_node.value}", "%eax");
        elif isinstance(stmt_node, ast.UnaryOperatorNode):
            # First prepare the content
            assert(len(stmt_node.nodes()) == 1)
            self.emit_expression_stmt(stmt_node.nodes()[0])
            if stmt_node.type == ast.UnaryOperatorNode.Type.Negation:
                self.emitter.instruction("neg", "%eax")
            elif stmt_node.type == ast.UnaryOperatorNode.Type.LogicalNegation:
                self.emitter.instruction("cmpl", "$0", "%eax");
                self.emitter.instruction("sete", "%al");
                self.emitter.instruction("movzbl", "%al", "%eax");
            elif stmt_node.type == ast.UnaryOperatorNode.Type.BitwiseComplement:
                self.emitter.instruction("not", "%eax")
        elif isinstance(stmt_node, ast.BinaryOperatorNode):
            # First prepare the content
            assert(len(stmt_node.nodes()) == 2);
            if stmt_node.type == ast.BinaryOperatorNode.Type.Addition or stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                self.emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.push_stack("%rax")
                self.emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Addition:
                    self.emitter.instruction("addl", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                    self.emitter.instruction("imul", "%ecx", "%eax")
            else:
                self.emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.push_stack("%rax")
                self.emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Subtraction:
                    self.emitter.instruction("subl", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Division:
                    self.emitter.instruction("cdq") # Sign-extend eax to edx:eax (idiv requires signed value)
                    self.emitter.instruction("idivl", "%ecx")
        elif isinstance(stmt_node, ast.LogicOperatorNode):
            assert(len(stmt_node.nodes()) == 2)
            if stmt_node.type == ast.LogicOperatorNode.Type.Or:
                self.emit_expression_stmt(stmt_node.nodes()[0])
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmpl", "$0", "%eax")
                self.emitter.instruction("je", label)
                self.emitter.instruction("movl", "$1", "%eax")
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.instruction("cmpl", "$0", "%eax")
                self.emitter.instruction("movl", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            elif stmt_node.type == ast.LogicOperatorNode.Type.And:
                self.emit_expression_stmt(stmt_node.nodes()[0])
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmpl", "$0", "%eax")
                self.emitter.instruction("jne", label)
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.instruction("cmpl", "$0", "%eax")
                self.emitter.instruction("movl", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            else:
                self.emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.push_stack("%rax")
                self.emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.pop_stack("%rcx")
                self.emitter.instruction("cmpl", "%eax", "%ecx")
                self.emitter.instruction("movl", "$0", "%eax")   # zero-out eax, keep flags
                if stmt_node.type == ast.LogicOperatorNode.Type.Equals:
                    self.emitter.instruction("sete", "%al")
                elif stmt_node.type == ast.LogicOperatorNode.Type.NotEquals:
                    self.emitter.instruction("setne", "%al")
                elif stmt_node.type == ast.LogicOperatorNode.Type.LessThanOrEqual:
                    self.emitter.instruction("setle", "%al")
                elif stmt_node.type == ast.LogicOperatorNode.Type.GreaterThanOrEqual:
                    self.emitter.instruction("setge", "%al")
                elif stmt_node.type == ast.LogicOperatorNode.Type.LessThan:
                    self.emitter.instruction("setl", "%al")
                elif stmt_node.type == ast.LogicOperatorNode.Type.GreaterThan:
                    self.emitter.instruction("setg", "%al")
                else:
                    raise AsmGeneratorError(f"Invalid logic operator type {stmt_node.type}")
        else:
            raise AsmGeneratorError(f"Invalid expression {stmt_node} in statement")
