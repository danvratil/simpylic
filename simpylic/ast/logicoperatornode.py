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

class LogicOperatorNode(ExprNode):
    class Type(Enum):
        LessThan = '<'
        LessThanOrEqual = '<='
        Equals = '=='
        NotEquals = '!='
        GreaterThanOrEqual = '>='
        GreaterThan = '>'
        And = 'and'
        Or = 'or'

    def __init__(self, operator_type: Union[str, Type]):
        super().__init__()
        self.__type = LogicOperatorNode.Type(operator_type)

    def __repr__(self):
        return f"LogicOperatorNode(type={self.__type})"

    @property
    def type(self) -> 'Type':
        return self.__type

    @property
    def lhs_expr(self) -> ExprNode:
        return self.__get_expr('_lhs_expr')

    @lhs_expr.setter
    def lhs_expr(self, expr: ExprNode):
        self.__replace_expr('_lhs_expr', LogicOperatorNode.lhs_expr.fget, expr)

    @property
    def rhs_expr(self) -> ExprNode:
        return self.__get_expr('_rhs_expr')

    @rhs_expr.setter
    def rhs_expr(self, expr: ExprNode):
        self.__replace_expr('_rhs_expr', LogicOperatorNode.rhs_expr.fget, expr)

    def __get_expr(self, name: str) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, name)

    def __replace_expr(self, name: str, old_fun: Callable[[Any], Node], new: ExprNode):
        if hasattr(new, '_rhs_expr'):
            delattr(new, '_rhs_expr')
        if hasattr(new, '_lhs_expr'):
            delattr(new, '_lhs_expr')

        setattr(new, name, True)
        self._replace_child(old_fun, new)
