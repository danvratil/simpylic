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

from typing import Optional, List, cast


from .node import StmtNode
from .ifstmtnode import IfStmtNode
from .elifstmtnode import ElifStmtNode
from .elsestmtnode import ElseStmtNode

class ConditionNode(StmtNode):
    def __repr__(self):
        return f"ConditionNode()"

    @property
    def if_statement(self) -> IfStmtNode:
        return self._child_by_type(IfStmtNode)

    @if_statement.setter
    def if_statement(self, stmt: IfStmtNode):
        self._replace_child(ConditionNode.if_statement.fget, stmt)

    @property
    def elif_statements(self) -> List[ElifStmtNode]:
        return [cast(ElifStmtNode, x) for x in self.children if isinstance(x, ElifStmtNode)]

    def add_elif_statement(self, stmt: ElifStmtNode):
        self._add_child(stmt)

    @property
    def else_statement(self) -> Optional[ElseStmtNode]:
        try:
            return self._child_by_type(ElseStmtNode)
        except KeyError:
            return None

    @else_statement.setter
    def else_statement(self, stmt: ElseStmtNode):
        self._replace_child(ConditionNode.__unsafe_else_stmt, stmt)

    def __unsafe_else_stmt(self) -> ElseStmtNode:
        return self._child_by_type(ElseStmtNode)
