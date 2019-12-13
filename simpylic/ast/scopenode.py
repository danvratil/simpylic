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

from .blocknode import BlockNode
from .funcallnode import FunCallNode

class ScopeNode(BlockNode):
    def __repr__(self):
        return f"ScopeNode()"

    def rename_function_calls(self, old_name: str, new_name: str):
        self.__recursively_rename(self, old_name, new_name)

    def __recursively_rename(self, node: 'Node', old_name: str, new_name: str):
        if isinstance(node, FunCallNode) and node.name == old_name:
            node.name = new_name

        for child in node.children:
            self.__recursively_rename(child, old_name, new_name)


