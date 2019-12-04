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
from typing import TextIO

class AsmGeneratorError(Exception):
    pass

class AsmEmitter:
    class FunctionEmitter:
        def __init__(self, emitter, name: str):
            self._emitter = emitter
            self._name = name

        def __enter__(self):
            self._emitter.begin_function(self._name)

        def __exit__(self, type, value, traceback):
            self._emitter.end_function()

    def __init__(self, output: TextIO):
        self._output = output
        self._depth = 0
        self._step = 4

    def function(self, name: str):
        return AsmEmitter.FunctionEmitter(self, name)

    def begin_function(self, name: str):
        self._write(f"    .global {name}")
        self._write(f"{name}:")
        self._depth += 1
        self.instruction("pushq", "%rbp")
        self.instruction("movq", "%rsp", "%rbp")

    def end_function(self):
        self.instruction("movq" ,"%rbp", "%rsp")
        self.instruction("popq", "%rbp")
        self.instruction("ret")
        self._depth -= 1

    def instruction(self, instruction: str, *args):
        self._write(f"{instruction} {', '.join([str(s) for s in args])}")

    def label(self, label: str):
        self._write(f"{label}:", ident=False)

    def push_stack(self, reg: str):
        self.instruction("push", reg)

    def pop_stack(self, reg: str):
        self.instruction("pop", reg)

    def _write(self, data: str, ident=True):
        if ident:
            self._output.write(" " * self._depth * self._step)
        self._output.write(data)
        self._output.write("\n")


class AsmGenerator:
    def __init__(self, output: TextIO):
        self.emitter = AsmEmitter(output)
        self.__lastLabelId = 0

    def generate(self, ast: ast.AstNode):
        self.__stack_index = 0
        self.__variable_map = {}
        self.emit_program_asm(ast)


    def emit_program_asm(self, program_node: ast.ProgramNode):
        for func in program_node.nodes():
            self.emit_function_asm(func)

    def emit_function_asm(self, function_node: ast.FunctionNode):
        with self.emitter.function(function_node.name):
            for stmt in function_node.nodes():
                self.emit_statement_asm(stmt)

    def emit_statement_asm(self, stmt_node: ast.AstNode):
        if isinstance(stmt_node, ast.ReturnStmtNode):
            self.__emit_return_stmt_asm(stmt_node)
        elif isinstance(stmt_node, ast.DeclarationNode):
            self.__emit_declaration_asm(stmt_node)
        elif isinstance(stmt_node, ast.ConditionNode):
            self.__emit_condition_asm(stmt_node)
        else:
            self.__emit_expression_stmt(stmt_node)

    def __generate_label(self, label: str):
        label = f'{label}_{self.__lastLabelId}'
        self.__lastLabelId += 1
        return label

    def __emit_return_stmt_asm(self, ret_node: ast.AstNode):
        # For return we first need to emit the expression, then the return itself
        assert(len(ret_node.nodes()) == 1)

        expr_node = ret_node.nodes()[0]
        self.__emit_expression_stmt(expr_node);

    def __emit_declaration_asm(self, decl_node: ast.DeclarationNode):
        assert(len(decl_node.nodes()) == 1)

        init_expr_node = decl_node.nodes()[0]
        self.__emit_expression_stmt(init_expr_node)
        self.emitter.instruction("pushq %rax")
        self.__stack_index -= 8
        self.__variable_map[decl_node.name] = self.__stack_index

    def __emit_condition_asm(self, cond_node: ast.ConditionNode):
        nodes = cond_node.nodes()
        assert(len(nodes) > 0)

        post_conditional_lbl = self.__generate_label("post_cond")

        while nodes:
            node = nodes.pop(0)
            if isinstance(node, ast.IfStatementNode) or isinstance(node, ast.ElifStatementNode):
                if isinstance(node, ast.ElifStatementNode):
                    self.emitter.label(cond_label)

                self.__emit_expression_stmt(node.nodes()[0])
                self.emitter.instruction("cmpl", "$0", "%eax")
                if not nodes:
                    self.emitter.instruction("je", post_conditional_lbl)
                else:
                    cond_label = self.__generate_label("cond")
                    self.emitter.instruction("je", cond_label)
                self.emit_statement_asm(node.nodes()[1])
                self.emitter.instruction("jmp", post_conditional_lbl)
            else:
                self.emitter.label(cond_label)
                self.emit_statement_asm(node.nodes()[0])

        # End of the entire if statement
        self.emitter.label(post_conditional_lbl)

    def __emit_expression_stmt(self, stmt_node: ast.AstNode):
        if isinstance(stmt_node, ast.ConstantNode):
            self.emitter.instruction("mov", f"${stmt_node.value}", "%eax");
        elif isinstance(stmt_node, ast.VariableNode):
            offset = self.__variable_map[stmt_node.name]
            self.emitter.instruction("mov", f"{offset}(%rbp)", "%eax")
        elif isinstance(stmt_node, ast.UnaryOperatorNode):
            # First prepare the content
            assert(len(stmt_node.nodes()) == 1)
            self.__emit_expression_stmt(stmt_node.nodes()[0])
            if stmt_node.type == ast.UnaryOperatorNode.Type.Negation:
                self.emitter.instruction("neg", "%eax")
            elif stmt_node.type == ast.UnaryOperatorNode.Type.LogicalNegation:
                self.emitter.instruction("cmp", "$0", "%eax");
                self.emitter.instruction("sete", "%al");
                self.emitter.instruction("movzb", "%al", "%eax");
            elif stmt_node.type == ast.UnaryOperatorNode.Type.BitwiseComplement:
                self.emitter.instruction("not", "%eax")
        elif isinstance(stmt_node, ast.BinaryOperatorNode):
            # First prepare the content
            assert(len(stmt_node.nodes()) == 2);
            if stmt_node.type == ast.BinaryOperatorNode.Type.Assignment:
                expr_node = stmt_node.nodes()[1]
                self.__emit_expression_stmt(expr_node)
                var_node = stmt_node.nodes()[0]
                offset = self.__variable_map[var_node.name]
                self.emitter.instruction("mov", "%eax", f"{offset}(%rbp)")
            elif stmt_node.type == ast.BinaryOperatorNode.Type.Addition or stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                self.__emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Addition:
                    self.emitter.instruction("add", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                    self.emitter.instruction("imul", "%ecx", "%eax")
            else:
                self.__emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Subtraction:
                    self.emitter.instruction("sub", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Division:
                    self.emitter.instruction("cdq") # Sign-extend eax to edx:eax (idiv requires signed value)
                    self.emitter.instruction("idiv", "%ecx")
        elif isinstance(stmt_node, ast.LogicOperatorNode):
            assert(len(stmt_node.nodes()) == 2)
            if stmt_node.type == ast.LogicOperatorNode.Type.Or:
                self.__emit_expression_stmt(stmt_node.nodes()[0])
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("je", label)
                self.emitter.instruction("mov", "$1", "%eax")
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.__emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("mov", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            elif stmt_node.type == ast.LogicOperatorNode.Type.And:
                self.__emit_expression_stmt(stmt_node.nodes()[0])
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("jne", label)
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.__emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("mov", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            else:
                self.__emit_expression_stmt(stmt_node.nodes()[0])
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.nodes()[1])
                self.emitter.pop_stack("%rcx")
                self.emitter.instruction("cmp", "%eax", "%ecx")
                self.emitter.instruction("mov", "$0", "%eax")   # zero-out eax, keep flags
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
