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

from enum import Enum

def AstError(RuntimeError):
    pass

class AstNode:
    pass

class LeafNode(AstNode):
    pass

class NonleafNode(AstNode):
    def __init__(self):
        self._subnodes = []

    def add_node(self, node):
        self._subnodes.append(node)

    def nodes(self):
        return self._subnodes

class ProgramNode(NonleafNode):
    def __repr__(self):
        return "ProgramNode()"

class FunctionNode(NonleafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"FunctionNode(name={self.name})"

class ReturnStmtNode(NonleafNode):
    def __repr__(self):
        return "ReturnStmtNode()"

class ConstantNode(LeafNode):
    def __init__(self, type, value):
        self.type = type
        self.value = value

    def __repr__(self):
        return f"ConstantNode(type={self.type}, value={self.value})"

class UnaryOperatorNode(NonleafNode):
    class Type(Enum):
        Negation = 1,
        BitwiseComplement = 2
        LogicalNegation = 3

        @staticmethod
        def fromText(text):
            if text == "-":
                return UnaryOperatorNode.Type.Negation
            elif text == '~':
                return UnaryOperatorNode.Type.BitwiseComplement
            elif text == "!":
                return UnaryOperatorNode.Type.LogicalNegation
            else:
                raise AstError(f"Unkown unary operator '{text}'")

    def __init__(self, type):
        super().__init__()
        self.type = type

    def __repr__(self):
        return f"UnaryOperatorNode(type={self.type})"

class AstDumper:
    @staticmethod
    def dump(node, depth = 0, step = 2):
        print(" " * depth * step + str(node))
        if isinstance(node, NonleafNode):
            for subnode in node.nodes():
                AstDumper.dump(subnode, depth + 1)
