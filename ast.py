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

class AstError(RuntimeError):
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
        Negation = '-'
        BitwiseComplement = '~'
        LogicalNegation = '!'

    def __init__(self, type):
        super().__init__()
        self.type = UnaryOperatorNode.Type(type)

    def __repr__(self):
        return f"UnaryOperatorNode(type={self.type})"

class BinaryOperatorNode(NonleafNode):
    class Type(Enum):
        Addition = '+'
        Subtraction = '-'
        Multiplication = '*'
        Division = '/'
        Assignment = '='

    def __init__(self, type):
        super().__init__()
        self.type = BinaryOperatorNode.Type(type)

    def __repr__(self):
        return f"BinaryOperatorNode(type={self.type})"

class LogicOperatorNode(NonleafNode):
    class Type(Enum):
        LessThan = '<'
        LessThanOrEqual = '<='
        Equals = '=='
        NotEquals = '!='
        GreaterThanOrEqual = '>='
        GreaterThan = '>'
        And = 'and'
        Or = 'or'

    def __init__(self, type):
        super().__init__()
        self.type = LogicOperatorNode.Type(type)

    def __repr__(self):
        return f"LogicOperatorNode(type={self.type})"

class DeclarationNode(NonleafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"DeclarationNode(name={self.name})"

class VariableNode(LeafNode):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"VariableNode(name={self.name})"


class ConditionNode(NonleafNode):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return f"ConditionNode()"

class IfStatementNode(NonleafNode):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "IfStatementNode()"

class ElifStatementNode(NonleafNode):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "ElifStatementNode()"

class ElseStatementNode(NonleafNode):
    def __init__(self):
        super().__init__()

    def __repr__(self):
        return "ElseStatementNode()"

class AstDumper:
    @staticmethod
    def dump(node: AstNode, depth: int = 0, step: int = 2):
        print(" " * depth * step + str(node))
        if isinstance(node, NonleafNode):
            for subnode in node.nodes():
                AstDumper.dump(subnode, depth + 1)
