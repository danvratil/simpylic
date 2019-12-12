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

from typing import cast

from .ast import Node, ProgramNode, AstVisitor


class AstPreprocessor:
    def __init__(self):
        pass

    def process(self, tree: Node):
        self.__extract_nested_functions(tree)

    def __extract_nested_functions(self, tree: Node):
        program = cast(ProgramNode, tree)

        def visit(node: Node):
            pass

        visitor = AstVisitor(program, visit)
        visitor.visit()
        # TODO: Find nested function definitions and move them to the top-level
        # TODO: Rename the nested functions (and all references to them) to have a globally
        #       unique name, possibly containing the name of all parent functions (and maybe
        #       a nubmer)
