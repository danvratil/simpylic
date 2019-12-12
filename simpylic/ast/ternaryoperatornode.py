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

from typing import Callable, Any

from .node import Node, ExprNode

class TernaryOperatorNode(ExprNode):
    def __repr__(self):
        return "TernaryOperatorNode()"

    @property
    def condition_expr(self) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, '_cond_expr')

    @condition_expr.setter
    def condition_expr(self, expr: ExprNode):
        self.__replace_expr('_cond_expr', TernaryOperatorNode.condition_expr.fget, expr)

    @property
    def true_expr(self) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, '_true_expr')

    @true_expr.setter
    def true_expr(self, expr: ExprNode):
        self.__replace_expr('_true_expr', TernaryOperatorNode.true_expr.fget, expr)

    @property
    def false_expr(self) -> ExprNode:
        return self._child_by_type_and_attr(ExprNode, '_false_expr')

    @false_expr.setter
    def false_expr(self, node: ExprNode):
        self.__replace_expr('_false_expr', TernaryOperatorNode.false_expr.fget, node)

    def __replace_expr(self, name: str, old_fun: Callable[[Any], Node], new: ExprNode):
        if hasattr(new, '_true_expr'):
            delattr(new, '_true_expr')
        if hasattr(new, '_false_expr'):
            delattr(new, '_false_expr')
        if hasattr(new, '_cond_expr'):
            delattr(new, '_cond_expr')

        setattr(new, name, True)
        self._replace_child(old_fun, new)
