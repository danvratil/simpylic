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

from . import ast
from .tokenizer import TokenType, Token

from typing import List

class ParserError(Exception):
    pass

class Parser:
    def __init__(self):
        pass

    def parse(self, tokens: List[Token]):
        self.__variables = []

        root = ast.ProgramNode()
        main = ast.FunctionNode("main")
        root.functions.append(main)

        while tokens:
            stmt_node = self.__parse_statement(tokens)
            if stmt_node:
                main.statements.append(stmt_node)

        return root

    def __parse_statement(self, tokens: List[Token]):
        peek_token = tokens[0]
        if peek_token.type == TokenType.KeywordReturn:
            return self.__parse_return_stmt(tokens)
        elif peek_token.type == TokenType.KeywordIf:
            return self.__parse_if_statement(tokens)
        elif peek_token.type == TokenType.Identifier:
            expression_stack = []
            self.__parse_expression(tokens, expression_stack)
            assert(len(expression_stack) == 1)
            return expression_stack[0]
        elif peek_token.type == TokenType.NewLine:
            tokens.pop(0)
            return None
        else:
            raise ParserError(f'Unexpected statement identifier {tokens[0]}')

    def __parse_return_stmt(self, tokens: List[Token]):
        token = tokens.pop(0)
        assert(token.type == TokenType.KeywordReturn)

        stmt_node = ast.ReturnStmtNode()

        expression_stack = []
        self.__parse_expression(tokens, expression_stack)
        assert(len(expression_stack) == 1)
        stmt_node.expression = expression_stack.pop(0)

        return stmt_node

    def __parse_if_statement(self, tokens: List[Token]):
        condition_node = ast.ConditionNode()

        def parse_if(self, tokens: List[Token]):
            assert(tokens[0].type == TokenType.KeywordIf)
            tokens.pop(0) # pop the 'if' keyword

            if_node = ast.IfStatementNode()
            expression_stack = []
            self.__parse_expression(tokens, expression_stack)
            assert(len(expression_stack) == 1)
            if_node.condition_expression = expression_stack.pop(0)
            assert(tokens[0].type == TokenType.Colon)
            tokens.pop(0) # pop the colon
            while tokens[0].type == TokenType.NewLine: tokens.pop(0)
            if_node.true_statement = self.__parse_statement(tokens)
            return if_node

        def parse_else(self, tokens: List[Token]):
            assert(tokens[0].type == TokenType.KeywordElse)
            tokens.pop(0) # pop the 'else' keyword
            assert(tokens[0].type == TokenType.Colon)
            tokens.pop(0) # pop the colon
            while tokens[0].type == TokenType.NewLine: tokens.pop(0)

            else_node = ast.ElseStatementNode()
            else_node.false_statement = self.__parse_statement(tokens)
            return else_node

        def parse_elif(self, tokens: List[Token]):
            assert(tokens[0].type == TokenType.KeywordElif)
            tokens.pop(0) # pop the 'elif' keyword

            elif_node = ast.ElifStatementNode()
            expression_stack = []
            self.__parse_expression(tokens, expression_stack)
            assert(len(expression_stack) == 1)
            elif_node.condition_expression = expression_stack.pop(0)
            assert(tokens[0].type == TokenType.Colon)
            tokens.pop(0) # pop the colon
            while tokens[0].type == TokenType.NewLine: tokens.pop(0)
            elif_node.true_statement = self.__parse_statement(tokens)
            return elif_node

        condition_node.if_condition = parse_if(self, tokens)

        while True:
            while tokens[0].type == TokenType.NewLine: tokens.pop(0)

            if tokens[0].type == TokenType.KeywordElif:
                condition_node.elif_conditions.append(parse_elif(self, tokens))
            elif tokens[0].type == TokenType.KeywordElse:
                condition_node.else_condition = parse_else(self, tokens)
                break # nothing may follow else
            else:
                break

        return condition_node

    def __parse_parenthesized_subexpression(self, tokens: List[Token], expression_stack: List[ast.AstNode]):
        assert(tokens[0].type == TokenType.LeftParenthesis)
        start = tokens.pop(0) # pop the left parenthesis
        depth = 1
        subtokens = []
        while tokens:
            if tokens[0].type == TokenType.LeftParenthesis:
                depth += 1
            elif tokens[0].type == TokenType.RightParenthesis:
                depth -= 1
                if depth == 0:
                    tokens.pop(0) # pop the final closing parenthesis
                    break

            subtokens.append(tokens.pop(0))

        if depth != 0:
            raise ParserError(f'Missing closing parenthesis for opening parenthesis on line {start.line}, char {start.pos}.')

        self.__parse_expression(subtokens, expression_stack)


    def __parse_expression(self, tokens: List[Token], expression_stack: List[ast.AstNode], operator: ast.AstNode = None):
        # Must be a literal or an unary operator
        if tokens[0].type == TokenType.LeftParenthesis:
            self.__parse_parenthesized_subexpression(tokens, expression_stack)

        token = None
        while tokens and tokens[0].type != TokenType.NewLine and tokens[0].type != TokenType.Colon:
            if (not token or token.type != TokenType.Literal) and tokens[0].type.is_unary_operator():
                token = tokens.pop(0)
                node = ast.UnaryOperatorNode(token.text)
                self.__parse_expression(tokens, expression_stack)
                node.expression = expression_stack.pop(0)
                expression_stack.append(node)
            elif tokens[0].type == TokenType.Literal:
                token = tokens.pop(0)
                expression_stack.append(ast.ConstantNode(type='int', value=int(token.text)))
            elif tokens[0].type == TokenType.Identifier:
                token = tokens.pop(0)
                if tokens and tokens[0].type == TokenType.Assignment:
                    if token.text not in self.__variables:
                        node = ast.DeclarationNode(name=token.text)
                        tokens.pop(0) # eat the '=' operator
                        self.__parse_expression(tokens, expression_stack)
                        node.init_expression = expression_stack.pop(0)
                        self.__variables.append(token.text)
                    else:
                        node = ast.VariableNode(name=token.text)
                else:
                    if not token.text in self.__variables:
                        raise ParserError(f"Undefined variable {token.text}")
                    else:
                        node = ast.VariableNode(name=token.text)
                expression_stack.append(node)

            elif tokens[0].type.is_binary_operator() or tokens[0].type.is_logic_operator() or tokens[0].type.is_ternary_operator():
                if operator and operator.type.priority() < tokens[0].type.priority():
                    return

                if tokens[0].type.is_binary_operator():
                    operator_token = tokens.pop(0)
                    node = ast.BinaryOperatorNode(operator_token.text)
                    node.lhs_expression = expression_stack.pop(0)

                    self.__parse_expression(tokens, expression_stack, operator_token)
                    node.rhs_expression = expression_stack.pop(0)

                    expression_stack.append(node)
                elif tokens[0].type.is_logic_operator():
                    operator_token = tokens.pop(0)
                    node = ast.LogicOperatorNode(operator_token.text)
                    node.lhs_expression = expression_stack.pop(0)

                    self.__parse_expression(tokens, expression_stack, operator_token)
                    node.rhs_expression = expression_stack.pop(0)

                    expression_stack.append(node)
                elif tokens[0].type.is_ternary_operator():
                    operator_token = tokens.pop(0)
                    node = ast.TernaryOperatorNode()
                    node.condition_expression = expression_stack.pop(0)

                    self.__parse_expression(tokens, expression_stack)
                    node.true_expression = expression_stack.pop(0)
                    assert(tokens[0].type == TokenType.Colon)
                    tokens.pop(0) # pop colon

                    self.__parse_expression(tokens, expression_stack)
                    node.false_expression = expression_stack.pop(0)

                    expression_stack.append(node)