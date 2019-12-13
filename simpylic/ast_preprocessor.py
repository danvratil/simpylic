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

from typing import List, cast

from .ast import Node, ProgramNode, FunDefNode
from .ast import asthelper as AstHelper


class AstPreprocessor:
    def __init__(self):
        pass

    def process(self, tree: Node):
        self.__extract_nested_functions(tree)

    def __extract_nested_functions(self, tree: Node):
        program = cast(ProgramNode, tree)

        def build_function_name(node: FunDefNode):
            name = node.name
            node = node.parent
            while node:
                if isinstance(node, FunDefNode):
                    name = f"_{node.name}_{name}"
                node = node.parent
            return name

        def find_functions(node: Node, function_stack: List[FunDefNode]):
            if isinstance(node, FunDefNode):
                new_name = build_function_name(node)
                scope = AstHelper.find_enclosing_scope(node)
                scope.rename_function_calls(node.name, new_name)
                node.name = new_name  # rename the function
                function_stack.append(node)

            for child in node.children:
                find_functions(child, function_stack)

        def move_functions_to_program_scope(program: ProgramNode, function_stack: List[FunDefNode]):
            for fun in function_stack:
                parent = fun.parent
                parent.remove_child(fun)
                program.add_function(fun)

        function_stack: List[FunDefNode] = []
        find_functions(program, function_stack)
        move_functions_to_program_scope(program, function_stack)
