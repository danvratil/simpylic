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

    def _write(self, data):
        self._output.write(" " * self._depth * self._step)
        self._output.write(data)
        self._output.write("\n")



class AsmGenerator:
    def __init__(self, output):
        self.emitter = AsmEmitter(output)

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
        if len(ret_node.nodes()) != 1:
            raise AsmGeneratorError("Invalid return node {ret_node}: expected one expression subnode")

        expr_node = ret_node.nodes()[0]
        self.emit_expression_stmt(expr_node);

    def emit_expression_stmt(self, stmt_node):
        if isinstance(stmt_node, ast.ConstantNode):
            self.emitter.instruction("movl", f"${stmt_node.value}", "%eax");
        elif isinstance(stmt_node, ast.UnaryOperatorNode):
            # First prepare the content
            if len(stmt_node.nodes()) != 1:
                return AsmGeneratorError("Missing argument to an unary operator.")
            self.emit_expression_stmt(stmt_node.nodes()[0])
            if stmt_node.type == ast.UnaryOperatorNode.Type.Negation:
                self.emitter.instruction("neg", "%eax")
            elif stmt_node.type == ast.UnaryOperatorNode.Type.LogicalNegation:
                self.emitter.instruction("cmpl", "$0", "%eax");
                self.emitter.instruction("sete", "%al");
                self.emitter.instruction("movzbl", "%al", "%eax");
            elif stmt_node.type == ast.UnaryOperatorNode.Type.BitwiseComplement:
                self.emitter.instruction("not", "%eax")

        else:
            raise AsmGeneratorError("Invalid expression in return statement")
