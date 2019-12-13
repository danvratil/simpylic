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

from .scopenode import ScopeNode
from .node import Node

def find_enclosing_scope(node: Node) -> ScopeNode:
    if node.parent:
        node = node.parent # skip self
        while node:
            if isinstance(node, ScopeNode):
                return node
            node = node.parent
        # top-level ProgramNode is always a ScopeNode
        assert False

    return node
