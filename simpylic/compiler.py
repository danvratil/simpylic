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

from . import ast
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
        for func in program_node.functions:
            self.emit_function_asm(func)

    def emit_function_asm(self, function_node: ast.FunctionNode):
        with self.emitter.function(function_node.name):
            for stmt in function_node.statements:
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
        self.__emit_expression_stmt(ret_node.expression);

    def __emit_declaration_asm(self, decl_node: ast.DeclarationNode):
        self.__emit_expression_stmt(decl_node.init_expression)
        self.emitter.instruction("pushq %rax")
        self.__stack_index -= 8
        self.__variable_map[decl_node.name] = self.__stack_index

    def __emit_condition_asm(self, cond_node: ast.ConditionNode):
        post_conditional_lbl = self.__generate_label("post_cond")

        def parse_if_or_elif(self, node: ast.AstNode, cond_label: str, post_conditional_lbl: str, is_last: bool) -> str:
            if isinstance(node, ast.ElifStatementNode):
                self.emitter.label(cond_label)

            self.__emit_expression_stmt(node.condition_expression)
            self.emitter.instruction("cmpl", "$0", "%eax")
            if is_last:
                self.emitter.instruction("je", post_conditional_lbl)
            else:
                cond_label = self.__generate_label("cond")
                self.emitter.instruction("je", cond_label)
            self.emit_statement_asm(node.true_statement)
            self.emitter.instruction("jmp", post_conditional_lbl)
            return cond_label

        cond_label = self.__generate_label("cond")
        is_last = not cond_node.elif_conditions and not cond_node.else_condition
        cond_label = parse_if_or_elif(self, cond_node.if_condition, cond_label, post_conditional_lbl, is_last)

        for index, node in enumerate(cond_node.elif_conditions):
            is_last = index == (len(cond_node.elif_conditions) - 1) and not cond_node.else_condition
            cond_label = parse_if_or_elif(self, node, cond_label, post_conditional_lbl, is_last)

        if cond_node.else_condition:
            self.emitter.label(cond_label)
            self.emit_statement_asm(cond_node.else_condition.false_statement)

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
            self.__emit_expression_stmt(stmt_node.expression)
            if stmt_node.type == ast.UnaryOperatorNode.Type.Negation:
                self.emitter.instruction("neg", "%eax")
            elif stmt_node.type == ast.UnaryOperatorNode.Type.LogicalNegation:
                self.emitter.instruction("cmp", "$0", "%eax");
                self.emitter.instruction("sete", "%al");
                self.emitter.instruction("movzb", "%al", "%eax");
            elif stmt_node.type == ast.UnaryOperatorNode.Type.BitwiseComplement:
                self.emitter.instruction("not", "%eax")
        elif isinstance(stmt_node, ast.BinaryOperatorNode):
            if stmt_node.type == ast.BinaryOperatorNode.Type.Assignment:
                # First prepare the content
                self.__emit_expression_stmt(stmt_node.rhs_expression)
                offset = self.__variable_map[stmt_node.lhs_expression.name]
                self.emitter.instruction("mov", "%eax", f"{offset}(%rbp)")
            elif stmt_node.type == ast.BinaryOperatorNode.Type.Addition or stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                self.__emit_expression_stmt(stmt_node.lhs_expression)
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.rhs_expression)
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Addition:
                    self.emitter.instruction("add", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                    self.emitter.instruction("imul", "%ecx", "%eax")
            else:
                self.__emit_expression_stmt(stmt_node.rhs_expression)
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.lhs_expression)
                self.emitter.pop_stack("%rcx")
                if stmt_node.type == ast.BinaryOperatorNode.Type.Subtraction:
                    self.emitter.instruction("sub", "%ecx", "%eax")
                elif stmt_node.type == ast.BinaryOperatorNode.Type.Division:
                    self.emitter.instruction("cdq") # Sign-extend eax to edx:eax (idiv requires signed value)
                    self.emitter.instruction("idiv", "%ecx")
        elif isinstance(stmt_node, ast.LogicOperatorNode):
            if stmt_node.type == ast.LogicOperatorNode.Type.Or:
                self.__emit_expression_stmt(stmt_node.lhs_expression)
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("je", label)
                self.emitter.instruction("mov", "$1", "%eax")
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.__emit_expression_stmt(stmt_node.rhs_expression)
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("mov", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            elif stmt_node.type == ast.LogicOperatorNode.Type.And:
                self.__emit_expression_stmt(stmt_node.lhs_expression)
                label = self.__generate_label("_clause")
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("jne", label)
                self.emitter.instruction("jmp", f"{label}_end")
                self.emitter.label(label)
                self.__emit_expression_stmt(stmt_node.rhs_expression)
                self.emitter.instruction("cmp", "$0", "%eax")
                self.emitter.instruction("mov", "$0", "%eax")
                self.emitter.instruction("setne", "%al")
                self.emitter.label(f"{label}_end")
            else:
                self.__emit_expression_stmt(stmt_node.lhs_expression)
                self.emitter.push_stack("%rax")
                self.__emit_expression_stmt(stmt_node.rhs_expression)
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
        elif isinstance(stmt_node, ast.TernaryOperatorNode):
            else_label = self.__generate_label("conditional")
            post_conditional_lbl = self.__generate_label("post_conditional")

            self.__emit_expression_stmt(stmt_node.condition_expression)
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("je", else_label)
            self.__emit_expression_stmt(stmt_node.true_expression)
            self.emitter.instruction("jmp", post_conditional_lbl)
            self.emitter.label(else_label)
            self.__emit_expression_stmt(stmt_node.false_expression)
            self.emitter.label(post_conditional_lbl)
        else:
            raise AsmGeneratorError(f"Invalid expression {stmt_node} in statement")