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

from .node import Node, StmtNode


class BlockNode(Node):
    def __init__(self, creates_scope: bool):
        super().__init__()
        self.__creates_scope = creates_scope

    def __repr__(self):
        return f"BlockNode(creates_scope={self.__creates_scope})"

    @property
    def creates_scope(self) -> bool:
        return self.__creates_scope

    def add_statement(self, stmt: StmtNode):
        self._add_child(stmt)

    @property
    def statements(self) -> List[StmtNode]:
        # FIXME
        # assert all([isinstance(x, StmtNode) for x in self.children])
        return cast(List[StmtNode], self.children)
