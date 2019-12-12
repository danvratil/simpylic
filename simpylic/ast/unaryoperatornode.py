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

from typing import Union
from enum import Enum

from .node import ExprNode

class UnaryOperatorNode(ExprNode):
    class Type(Enum):
        Negation = '-'
        BitwiseComplement = '~'
        LogicalNegation = '!'

    def __init__(self, operator_type: Union[str, Type]):
        super().__init__()
        self.__type = UnaryOperatorNode.Type(operator_type)

    def __repr__(self):
        return f"UnaryOperatorNode(type={self.__type})"

    @property
    def type(self) -> 'Type':
        return self.__type

    @property
    def expr(self) -> ExprNode:
        return self._child_by_type(ExprNode)

    @expr.setter
    def expr(self, node: ExprNode):
        self._add_child(node)
