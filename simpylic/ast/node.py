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

from typing import TypeVar, Callable, Optional, Iterable, Type, Any, cast

SubNode = TypeVar('SubNode', bound='Node')

class Node:
    def __init__(self):
        self.__parent = None
        self.__children = [] # type: List[Node]

    def traverse(self, depth: int):
        print(' ' * (depth * 2), self, sep='')
        for child in self.__children:
            child.traverse(depth + 1)

    def visit(self, callback: Callable):
        callback(self)
        for child in self.__children:
            child.visit(callback)

    @property
    def parent(self) -> 'Node':
        return self.__parent

    @property
    def children(self) -> Iterable['Node']:
        return self.__children

    def _add_child(self, node: 'Node'):
        self.__children.append(node)
        node._set_parent(self)

    def _remove_child(self, node: 'Node'):
        if node in self.__children:
            self.__children.remove(node)
        node._set_parent(None)

    def _replace_child(self, old_fun: Callable[[Any], 'Node'], new: Optional['Node']):
        try:
            old: Optional[Node] = old_fun(self)
        except KeyError:
            old = None
        if old:
            self._remove_child(old)
        if new:
            self._add_child(new)

    def _child_by_type(self, typ: Type['Node']) -> SubNode:
        for child in self.__children:
            if isinstance(child, typ):
                return cast(SubNode, child)
        raise KeyError(f"No child with type {type}")

    def _child_by_type_and_attr(self, typ: Type['Node'], attr: str) -> SubNode:
        for child in self.__children:
            if isinstance(child, typ) and hasattr(child, attr):
                return cast(SubNode, child)
        raise KeyError(f"No such child with type {type} and attribute {attr}")

    def _set_parent(self, parent: Optional['Node']):
        self.__parent = parent


class ExprNode(Node):
    pass


class StmtNode(Node):
    pass
