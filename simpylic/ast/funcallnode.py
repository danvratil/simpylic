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

from .node import ExprNode


class FunCallNode(ExprNode):
    def __init__(self, name: str):
        super().__init__()
        self.__name = name

    def __repr__(self):
        return f"FunCallNode(name={self.__name})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def arguments(self) -> List[ExprNode]:
        assert all([isinstance(x, ExprNode) for x in self.children])
        return cast(List[ExprNode], self.children)

    def add_argument(self, expr: ExprNode):
        self._add_child(expr)
