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

from typing import Callable

from .node import Node


class AstError(RuntimeError):
    pass


class AstDumper:
    @staticmethod
    def dump(node: Node, depth: int = 0):
        node.traverse(depth)


class AstVisitor:
    def __init__(self, ast: Node, callback: Callable):
        self.__ast = ast
        self.__callback = callback

    def visit(self):
        self.__ast.visit(self.__callback)
