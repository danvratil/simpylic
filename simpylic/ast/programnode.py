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

from typing import Iterable, cast

from .scopenode import ScopeNode
from .fundefnode import FunDefNode


class ProgramNode(ScopeNode):
    def __repr__(self):
        return "ProgramNode()"

    def add_function(self, func: FunDefNode):
        self._add_child(func)

    @property
    def functions(self) -> Iterable[FunDefNode]:
        assert all(isinstance(x, FunDefNode) for x in self.children)
        return cast(Iterable[FunDefNode], self.children)
