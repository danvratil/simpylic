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

from typing import List

from .node import StmtNode
from .blocknode import BlockNode


class FunDefNode(StmtNode):
    def __init__(self, name: str, arguments: List[str]):
        super().__init__()
        self.__name = name
        self.__arguments = arguments

    def __repr__(self):
        return f"FunDefNode(name={self.__name}, args={self.__arguments})"

    @property
    def name(self) -> str:
        return self.__name

    @property
    def arguments(self) -> List[str]:
        return self.__arguments

    @property
    def body(self) -> BlockNode:
        return self._child_by_type(BlockNode)

    @body.setter
    def body(self, node: BlockNode):
        self._replace_child(FunDefNode.body.fget, node)
