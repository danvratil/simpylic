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

from .node import StmtNode, ExprNode

class VarDeclNode(StmtNode):
    def __init__(self, name: str):
        super().__init__()
        self.__name = name

    def __repr__(self):
        return f"VarDeclNode(name={self.__name})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def init_expr(self) -> ExprNode:
        return self._child_by_type(ExprNode)

    @init_expr.setter
    def init_expr(self, expr: ExprNode):
        self._replace_child(VarDeclNode.init_expr.fget, expr)
