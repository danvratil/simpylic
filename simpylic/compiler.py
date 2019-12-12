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

from typing import TextIO, Dict, Union, cast

from . import ast

class AsmGeneratorError(Exception):
    pass

class AsmEmitter:
    class FunctionEmitter:
        def __init__(self, emitter, name: str):
            self._emitter = emitter
            self._name = name

        def __enter__(self):
            self._emitter.begin_function(self._name)

        def __exit__(self, _type, value, traceback):
            self._emitter.end_function()

    def __init__(self, output: TextIO):
        self._output = output
        self._depth = 0
        self._step = 4

    def function(self, name: str):
        return AsmEmitter.FunctionEmitter(self, name)

    def begin_function(self, name: str):
        self.label(name)
        self._depth += 1
        self.push_stack("%rbp")
        self.instruction("mov", "%rsp", "%rbp")

    def end_function(self):
        self.instruction("mov", "%rbp", "%rsp")
        self.pop_stack("%rbp")
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
        self.__last_label_id = 0
        self.__stack_index = 0
        self.__variable_map: Dict[str, int] = {}

    def generate(self, program_node: ast.ProgramNode):
        self.emit_program_asm(program_node)


    def emit_program_asm(self, program_node: ast.ProgramNode):
        self.emitter._depth += 1
        self.emitter.instruction(".global", "main")
        self.emitter._depth -= 1
        for func in program_node.functions:
            self.emit_function_asm(func)

    def emit_function_asm(self, function_node: ast.FunDefNode):
        with self.emitter.function(function_node.name):
            self.__process_block(function_node.body)

    def emit_statement_asm(self, stmt_node: ast.StmtNode):
        if isinstance(stmt_node, ast.ReturnStmtNode):
            self.__emit_return_stmt_asm(stmt_node)
        elif isinstance(stmt_node, ast.VarDeclNode):
            self.__emit_variable_declaration_asm(stmt_node)
        elif isinstance(stmt_node, ast.ConditionNode):
            self.__emit_condition_asm(stmt_node)
        elif isinstance(stmt_node, ast.WhileStmtNode):
            self.__emit_while_loop_asm(stmt_node)
        else:
            self.__emit_expression_stmt(cast(ast.ExprNode, stmt_node))

    def __generate_label(self, label: str):
        label = f'{label}_{self.__last_label_id}'
        self.__last_label_id += 1
        return label

    def __process_block(self, block_node: ast.BlockNode):
        for stmt in block_node.statements:
            self.emit_statement_asm(stmt)

    def __emit_return_stmt_asm(self, ret_node: ast.ReturnStmtNode):
        self.__emit_expression_stmt(ret_node.expr)

    def __emit_variable_declaration_asm(self, decl_node: ast.VarDeclNode):
        self.__emit_expression_stmt(decl_node.init_expr)
        self.emitter.instruction("pushq %rax")
        self.__stack_index -= 8
        self.__variable_map[decl_node.name] = self.__stack_index

    def __emit_condition_asm(self, cond_node: ast.ConditionNode):
        post_conditional_lbl = self.__generate_label("post_cond")

        def parse_if_or_elif(self, node: Union[ast.IfStmtNode, ast.ElifStmtNode], cond_label: str,
                             post_conditional_lbl: str, is_last: bool) -> str:
            if isinstance(node, ast.ElifStmtNode):
                self.emitter.label(cond_label)

            self.__emit_expression_stmt(node.condition_expr)
            self.emitter.instruction("cmpl", "$0", "%eax")
            if is_last:
                self.emitter.instruction("je", post_conditional_lbl)
            else:
                cond_label = self.__generate_label("cond")
                self.emitter.instruction("je", cond_label)
            self.__process_block(node.true_block)
            self.emitter.instruction("jmp", post_conditional_lbl)
            return cond_label

        cond_label = self.__generate_label("cond")
        is_last = not cond_node.elif_statements and not cond_node.else_statement
        cond_label = parse_if_or_elif(self, cond_node.if_statement, cond_label,
                                      post_conditional_lbl, is_last)

        for index, node in enumerate(cond_node.elif_statements):
            is_last = index == (len(cond_node.elif_statements) - 1) and not cond_node.else_statement
            cond_label = parse_if_or_elif(self, node, cond_label, post_conditional_lbl, is_last)

        if cond_node.else_statement:
            self.emitter.label(cond_label)
            self.__process_block(cond_node.else_statement.false_block)

        # End of the entire if statement
        self.emitter.label(post_conditional_lbl)


    def __emit_while_loop_asm(self, stmt_node: ast.WhileStmtNode):
        start_label = self.__generate_label("loop_start")
        end_label = self.__generate_label("loop_end")

        self.emitter.label(start_label)
        self.__emit_expression_stmt(stmt_node.condition_expr)
        self.emitter.instruction("cmpl", "$0", "%eax")
        self.emitter.instruction("je", end_label)

        self.__process_block(stmt_node.body)
        self.emitter.instruction("jmp", start_label)

        self.emitter.label(end_label)


    def __emit_constant_value(self, stmt_node: ast.ConstantNode):
        self.emitter.instruction("mov", f"${stmt_node.value}", "%eax")


    def __emit_variable_access(self, stmt_node: ast.VarNode):
        offset = self.__variable_map[stmt_node.name]
        self.emitter.instruction("mov", f"{offset}(%rbp)", "%eax")


    def __emit_unary_operation(self, stmt_node: ast.UnaryOperatorNode):
        # First prepare the content
        self.__emit_expression_stmt(stmt_node.expr)
        if stmt_node.type == ast.UnaryOperatorNode.Type.Negation:
            self.emitter.instruction("neg", "%eax")
        elif stmt_node.type == ast.UnaryOperatorNode.Type.LogicalNegation:
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("sete", "%al")
            self.emitter.instruction("movzb", "%al", "%eax")
        elif stmt_node.type == ast.UnaryOperatorNode.Type.BitwiseComplement:
            self.emitter.instruction("not", "%eax")


    def __emit_binary_operation(self, stmt_node: ast.BinaryOperatorNode):
        if stmt_node.type == ast.BinaryOperatorNode.Type.Assignment:
            # First prepare the content
            self.__emit_expression_stmt(stmt_node.rhs_expr)
            assert isinstance(stmt_node.lhs_expr, (ast.VarDeclNode, ast.VarNode))
            offset = self.__variable_map[stmt_node.lhs_expr.name]
            self.emitter.instruction("mov", "%eax", f"{offset}(%rbp)")
        elif stmt_node.type in (ast.BinaryOperatorNode.Type.Addition,
                                ast.BinaryOperatorNode.Type.Multiplication):
            self.__emit_expression_stmt(stmt_node.lhs_expr)
            self.emitter.push_stack("%rax")
            self.__emit_expression_stmt(stmt_node.rhs_expr)
            self.emitter.pop_stack("%rcx")
            if stmt_node.type == ast.BinaryOperatorNode.Type.Addition:
                self.emitter.instruction("add", "%ecx", "%eax")
            elif stmt_node.type == ast.BinaryOperatorNode.Type.Multiplication:
                self.emitter.instruction("imul", "%ecx", "%eax")
        else:
            self.__emit_expression_stmt(stmt_node.rhs_expr)
            self.emitter.push_stack("%rax")
            self.__emit_expression_stmt(stmt_node.lhs_expr)
            self.emitter.pop_stack("%rcx")
            if stmt_node.type == ast.BinaryOperatorNode.Type.Subtraction:
                self.emitter.instruction("sub", "%ecx", "%eax")
            elif stmt_node.type == ast.BinaryOperatorNode.Type.Division:
                self.emitter.instruction("cdq") # Sign-extend eax to edx:eax
                                                # (idiv requires signed value)
                self.emitter.instruction("idiv", "%ecx")


    def __emit_logic_operation(self, stmt_node: ast.LogicOperatorNode):
        if stmt_node.type == ast.LogicOperatorNode.Type.Or:
            self.__emit_expression_stmt(stmt_node.lhs_expr)
            label = self.__generate_label("_clause")
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("je", label)
            self.emitter.instruction("mov", "$1", "%eax")
            self.emitter.instruction("jmp", f"{label}_end")
            self.emitter.label(label)
            self.__emit_expression_stmt(stmt_node.rhs_expr)
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("mov", "$0", "%eax")
            self.emitter.instruction("setne", "%al")
            self.emitter.label(f"{label}_end")
        elif stmt_node.type == ast.LogicOperatorNode.Type.And:
            self.__emit_expression_stmt(stmt_node.lhs_expr)
            label = self.__generate_label("_clause")
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("jne", label)
            self.emitter.instruction("jmp", f"{label}_end")
            self.emitter.label(label)
            self.__emit_expression_stmt(stmt_node.rhs_expr)
            self.emitter.instruction("cmp", "$0", "%eax")
            self.emitter.instruction("mov", "$0", "%eax")
            self.emitter.instruction("setne", "%al")
            self.emitter.label(f"{label}_end")
        else:
            self.__emit_expression_stmt(stmt_node.lhs_expr)
            self.emitter.push_stack("%rax")
            self.__emit_expression_stmt(stmt_node.rhs_expr)
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


    def __emit_ternary_operation(self, stmt_node: ast.TernaryOperatorNode):
        else_label = self.__generate_label("conditional")
        post_conditional_lbl = self.__generate_label("post_conditional")

        self.__emit_expression_stmt(stmt_node.condition_expr)
        self.emitter.instruction("cmp", "$0", "%eax")
        self.emitter.instruction("je", else_label)
        self.__emit_expression_stmt(stmt_node.true_expr)
        self.emitter.instruction("jmp", post_conditional_lbl)
        self.emitter.label(else_label)
        self.__emit_expression_stmt(stmt_node.false_expr)
        self.emitter.label(post_conditional_lbl)


    def __emit_expression_stmt(self, stmt_node: ast.ExprNode):
        if isinstance(stmt_node, ast.ConstantNode):
            self.__emit_constant_value(stmt_node)
        elif isinstance(stmt_node, ast.VarNode):
            self.__emit_variable_access(stmt_node)
        elif isinstance(stmt_node, ast.UnaryOperatorNode):
            self.__emit_unary_operation(stmt_node)
        elif isinstance(stmt_node, ast.BinaryOperatorNode):
            self.__emit_binary_operation(stmt_node)
        elif isinstance(stmt_node, ast.LogicOperatorNode):
            self.__emit_logic_operation(stmt_node)
        elif isinstance(stmt_node, ast.TernaryOperatorNode):
            self.__emit_ternary_operation(stmt_node)
        else:
            raise AsmGeneratorError(f"Invalid expression {stmt_node} in statement")
