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
    def traverse(self, depth: int):
        print(' ' * (depth * 2), self, sep='')

class ProgramNode(AstNode):
    def __init__(self):
        self.functions = [] # type: List[AstNode]

    def __repr__(self):
        return "ProgramNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        for node in self.functions:
            node.traverse(depth + 1)


class FunctionNode(AstNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.statements = [] # type: List[AstNode]

    def __repr__(self):
        return f"FunctionNode(name={self.name})"

    def traverse(self, depth: int):
        super().traverse(depth)
        for node in self.statements:
            node.traverse(depth + 1)


class BlockNode(AstNode):
    def __init__(self, creates_scope: bool):
        self.creates_scope = creates_scope
        self.statements = [] # type: List[AstNode]

    def __repr__(self):
        return f"BlockNode(creates_scope={self.creates_scope})"

    def traverse(self, depth: int):
        super().traverse(depth)
        for node in self.statements:
            node.traverse(depth + 1)


class ReturnStmtNode(AstNode):
    def __init__(self):
        self.expression = None # type: AstNode

    def __repr__(self):
        return "ReturnStmtNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.expression.traverse(depth + 1)

class ConstantNode(AstNode):
    def __init__(self, value_type: str, value: any):
        self.type = value_type
        self.value = value

    def __repr__(self):
        return f"ConstantNode(type={self.type}, value={self.value})"

class UnaryOperatorNode(AstNode):
    class Type(Enum):
        Negation = '-'
        BitwiseComplement = '~'
        LogicalNegation = '!'

    def __init__(self, operator_type: Type):
        super().__init__()
        self.type = UnaryOperatorNode.Type(operator_type)
        self.expression = None # type: AstNode

    def __repr__(self):
        return f"UnaryOperatorNode(type={self.type})"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.expression.traverse(depth + 1)

class BinaryOperatorNode(AstNode):
    class Type(Enum):
        Addition = '+'
        Subtraction = '-'
        Multiplication = '*'
        Division = '/'
        Assignment = '='

    def __init__(self, operator_type: Type):
        super().__init__()
        self.type = BinaryOperatorNode.Type(operator_type)
        self.lhs_expression = None # type: AstNode
        self.rhs_expression = None # type: AstNode

    def __repr__(self):
        return f"BinaryOperatorNode(type={self.type})"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.lhs_expression.traverse(depth + 1)
        self.rhs_expression.traverse(depth + 1)

class LogicOperatorNode(AstNode):
    class Type(Enum):
        LessThan = '<'
        LessThanOrEqual = '<='
        Equals = '=='
        NotEquals = '!='
        GreaterThanOrEqual = '>='
        GreaterThan = '>'
        And = 'and'
        Or = 'or'

    def __init__(self, operator_type: Type):
        super().__init__()
        self.type = LogicOperatorNode.Type(operator_type)
        self.lhs_expression = None # type: AstNode
        self.rhs_expression = None # type: AstNode

    def __repr__(self):
        return f"LogicOperatorNode(type={self.type})"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.lhs_expression.traverse(depth + 1)
        self.rhs_expression.traverse(depth + 1)

class DeclarationNode(AstNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name
        self.init_expression = None # type: AstNode

    def __repr__(self):
        return f"DeclarationNode(name={self.name})"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.init_expression.traverse(depth + 1)

class VariableNode(AstNode):
    def __init__(self, name: str):
        super().__init__()
        self.name = name

    def __repr__(self):
        return f"VariableNode(name={self.name})"


class ConditionNode(AstNode):
    def __init__(self):
        super().__init__()
        self.if_condition = None # type: AstNode
        self.elif_conditions = [] # type: List[AstNode]
        self.else_condition = None # type: AstNode

    def __repr__(self):
        return f"ConditionNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.if_condition.traverse(depth + 1)
        for cond in self.elif_conditions:
            cond.traverse(depth + 1)
        if self.else_condition:
            self.else_condition.traverse(depth + 1)

class IfStatementNode(AstNode):
    def __init__(self):
        super().__init__()
        self.condition_expression = None # type: AstNode
        self.true_block = None # type: BlockNode

    def __repr__(self):
        return "IfStatementNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.condition_expression.traverse(depth + 1)
        self.true_block.traverse(depth + 1)

class ElifStatementNode(AstNode):
    def __init__(self):
        super().__init__()
        self.condition_expression = None # type: AstNode
        self.true_block = None # type: BlockNode

    def __repr__(self):
        return "ElifStatementNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.condition_expression.traverse(depth + 1)
        self.true_block.traverse(depth + 1)

class ElseStatementNode(AstNode):
    def __init__(self):
        super().__init__()
        self.false_block = None # type: BlockNode

    def __repr__(self):
        return "ElseStatementNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.false_block.traverse(depth + 1)

class TernaryOperatorNode(AstNode):
    def __init__(self):
        super().__init__()
        self.condition_expression = None # type: AstNode
        self.true_statement = None # type: AstNode
        self.false_statement = None # type: AstNode

    def __repr__(self):
        return "TernaryOperatorNode()"

    def traverse(self, depth: int):
        super().traverse(depth)
        self.condition_expression.traverse(depth + 1)
        self.true_statement.traverse(depth + 1)
        self.false_statement.traverse(depth + 1)

class AstDumper:
    @staticmethod
    def dump(node: AstNode, depth: int = 0):
        node.traverse(depth)
