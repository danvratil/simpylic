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

from typing import Union, Callable, Any
from enum import Enum

from .node import Node, ExprNode


class BinaryOperatorNode(ExprNode):
    class Type(Enum):
        Addition = '+'
        Subtraction = '-'
        Multiplication = '*'
        Division = '/'
        Assignment = '='

    def __init__(self, operator_type: Union[str, Type]):
        super().__init__()
        self.__type = BinaryOperatorNode.Type(operator_type)

    def __repr__(self):
        return f"BinaryOperatorNode(type={self.__type})"

    @property
    def type(self) -> 'Type':
        return self.__type

    @property
    def lhs_expr(self) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, '_lhs')

    @lhs_expr.setter
    def lhs_expr(self, expr: ExprNode):
        self.__replace_expr('_lhs', BinaryOperatorNode.lhs_expr.fget, expr)

    @property
    def rhs_expr(self) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, '_rhs')

    @rhs_expr.setter
    def rhs_expr(self, expr: ExprNode):
        self.__replace_expr('_rhs', BinaryOperatorNode.rhs_expr.fget, expr)

    def __replace_expr(self, name: str, old_fun: Callable[[Any], Node], new: ExprNode):
        if hasattr(new, '_lhs'):
            delattr(new, '_lhs')
        if hasattr(new, '_rhs'):
            delattr(new, '_rhs')
        setattr(new, name, True)
        self._replace_child(old_fun, new)
