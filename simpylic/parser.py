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

from typing import List, Optional, cast

from . import ast
from .tokenizer import TokenType, Token


class ParserError(Exception):
    pass


class Parser:
    def __init__(self):
        self.__variables = []
        self.__functions = []
        self.__indentation_level = 0
        self.__line_indentation = 0

    def parse(self, tokens: List[Token]) -> ast.ProgramNode:
        root = ast.ProgramNode()
        main = ast.FunDefNode("main", arguments=[])
        main.body = ast.BlockNode(creates_scope=True)
        root.add_function(main)

        while tokens:
            stmt_node = self.__parse_statement(tokens)
            if stmt_node:
                main.body.add_statement(cast(ast.StmtNode, stmt_node))

        return root

    def __pop_newlines(self, tokens: List[Token]):
        while tokens and tokens[0].type == TokenType.NewLine:
            tokens.pop(0)
        if tokens and tokens[0].type == TokenType.Whitespace:
            self.__line_indentation = len(tokens[0].text)
        else:
            self.__line_indentation = 0

    def __parse_statement(self, tokens: List[Token]) -> Optional[ast.StmtNode]:
        peek_token = tokens[0]
        if peek_token.type == TokenType.Whitespace:
            self.__line_indentation = len(peek_token.text)
            tokens.pop(0)
            peek_token = tokens[0]

        if peek_token.type == TokenType.KeywordReturn:
            return self.__parse_return_stmt(tokens)
        if peek_token.type == TokenType.KeywordIf:
            return self.__parse_if_statement(tokens)
        if peek_token.type == TokenType.KeywordWhile:
            return self.__parse_while_statement(tokens)
        if peek_token.type == TokenType.KeywordDef:
            return self.__parse_function_definition(tokens)
        if peek_token.type == TokenType.Identifier:
            # FIXME
            expression_stack: List[ast.ExprNode] = []
            self.__parse_expression(tokens, expression_stack)
            return expression_stack.pop()
        if peek_token.type == TokenType.NewLine:
            tokens.pop(0)
            return None

        raise ParserError(f'Unexpected statement identifier {tokens[0]}')

    def __parse_return_stmt(self, tokens: List[Token]) -> ast.ReturnStmtNode:
        token = tokens.pop(0)
        assert token.type == TokenType.KeywordReturn

        stmt_node = ast.ReturnStmtNode()

        expression_stack: List[ast.ExprNode] = []
        self.__parse_expression(tokens, expression_stack)
        assert len(expression_stack) == 1
        stmt_node.expr = expression_stack.pop()

        return stmt_node

    def __parse_function_definition(self, tokens: List[Token]) -> ast.FunDefNode:
        assert tokens[0].type == TokenType.KeywordDef
        tokens.pop(0)  # pop the 'def' keyword

        assert tokens[0].type == TokenType.Identifier
        name_token = tokens.pop(0)
        self.__functions.append(name_token.text)

        assert tokens[0].type == TokenType.LeftParenthesis
        tokens.pop(0)

        arguments = []
        while tokens and tokens[0].type != TokenType.RightParenthesis:
            arguments.append(tokens.pop(0).text)
            assert tokens[0].type == TokenType.Comma
            tokens.pop(0)  # pop the comma

        assert tokens and tokens[0].type == TokenType.RightParenthesis
        tokens.pop(0)  # pop the parenthesis

        node = ast.FunDefNode(name_token.text, arguments)

        assert tokens and tokens[0].type == TokenType.Colon
        tokens.pop(0)  # pop the colon
        self.__pop_newlines(tokens)

        node.body = self.__parse_block(tokens, creates_scope=True)

        return node

    def __parse_while_statement(self, tokens: List[Token]) -> ast.WhileStmtNode:
        assert tokens[0].type == TokenType.KeywordWhile
        tokens.pop(0)  # pop the 'while' keyword

        while_node = ast.WhileStmtNode()
        expression_stack: List[ast.ExprNode] = []
        self.__parse_expression(tokens, expression_stack)
        assert len(expression_stack) == 1
        while_node.condition_expr = cast(ast.ExprNode, expression_stack.pop())
        assert tokens[0].type == TokenType.Colon
        tokens.pop(0)  # pop the colon
        self.__pop_newlines(tokens)

        while_node.body = self.__parse_block(tokens, creates_scope=False)

        return while_node

    def __parse_if_statement(self, tokens: List[Token]) -> ast.ConditionNode:
        condition_node = ast.ConditionNode()

        def parse_if(self, tokens: List[Token]) -> ast.IfStmtNode:
            assert tokens[0].type == TokenType.KeywordIf
            tokens.pop(0)  # pop the 'if' keyword

            if_node = ast.IfStmtNode()
            expression_stack: List[ast.ExprNode] = []
            self.__parse_expression(tokens, expression_stack)
            assert len(expression_stack) == 1
            if_node.condition_expr = expression_stack.pop()
            assert tokens[0].type == TokenType.Colon
            tokens.pop(0)  # pop the colon
            self.__pop_newlines(tokens)
            if_node.true_block = self.__parse_block(tokens, creates_scope=False)
            return if_node

        def parse_else(self, tokens: List[Token]) -> ast.ElseStmtNode:
            assert tokens[0].type == TokenType.KeywordElse
            tokens.pop(0)  # pop the 'else' keyword
            assert tokens[0].type == TokenType.Colon
            tokens.pop(0)  # pop the colon
            self.__pop_newlines(tokens)

            else_node = ast.ElseStmtNode()
            else_node.false_block = self.__parse_block(tokens, creates_scope=False)
            return else_node

        def parse_elif(self, tokens: List[Token]) -> ast.ElifStmtNode:
            assert tokens[0].type == TokenType.KeywordElif
            tokens.pop(0)  # pop the 'elif' keyword

            elif_node = ast.ElifStmtNode()
            expression_stack: List[ast.ExprNode] = []
            self.__parse_expression(tokens, expression_stack)
            assert len(expression_stack) == 1
            elif_node.condition_expr = expression_stack.pop()
            assert tokens[0].type == TokenType.Colon
            tokens.pop(0)  # pop the colon
            self.__pop_newlines(tokens)
            elif_node.true_block = self.__parse_block(tokens, creates_scope=False)
            return elif_node

        indentation = self.__line_indentation
        condition_node.if_statement = parse_if(self, tokens)
        while True:
            self.__pop_newlines(tokens)
            if tokens[0].type == TokenType.KeywordElif and self.__line_indentation == indentation:
                condition_node.add_elif_statement(parse_elif(self, tokens))
            elif tokens[0].type == TokenType.KeywordElse and self.__line_indentation == indentation:
                condition_node.else_statement = parse_else(self, tokens)
                break  # nothing may follow else
            else:
                break

        return condition_node

    def __parse_parenthesized_subexpression(self, tokens: List[Token],
                                            expression_stack: List[ast.ExprNode]):
        assert tokens[0].type == TokenType.LeftParenthesis
        tokens.pop(0)  # pop the left parenthesis
        depth = 1
        subtokens = []
        while tokens:
            if tokens[0].type == TokenType.LeftParenthesis:
                depth += 1
            elif tokens[0].type == TokenType.RightParenthesis:
                depth -= 1
                if depth == 0:
                    tokens.pop(0)  # pop the final closing parenthesis
                    break

            subtokens.append(tokens.pop(0))

        if depth != 0:
            raise ParserError(f'Missing closing parenthesis for opening parenthesis on '
                              'line {start.line}, char {start.pos}.')

        self.__parse_expression(subtokens, expression_stack)

    @staticmethod
    def __parse_literal(tokens: List[Token], expression_stack: List[ast.ExprNode]) -> Token:
        token = tokens.pop(0)
        expression_stack.append(ast.ConstantNode(value_type='int', value=int(token.text)))

        return token

    def __parse_block(self, tokens: List[Token], creates_scope: bool) -> ast.BlockNode:
        block = ast.BlockNode(creates_scope)
        assert tokens[0].type == TokenType.Whitespace
        indentation = len(tokens[0].text)
        if indentation <= self.__indentation_level:
            raise ParserError(f'Invalid indentation on line {tokens[0].line}.')
        prev_level = self.__indentation_level
        self.__indentation_level = indentation
        while len(tokens[0].text) == indentation:
            assert tokens[0].type == TokenType.Whitespace
            tokens.pop(0)  # pop the indentation token
            stmt = self.__parse_statement(tokens)
            if stmt:
                block.add_statement(stmt)
            self.__pop_newlines(tokens)
            if not tokens or tokens[0].type != TokenType.Whitespace:
                break

        self.__indentation_level = prev_level

        return block

    def __parse_identifier(self, tokens: List[Token],
                           expression_stack: List[ast.ExprNode]) -> Token:

        def parse_assignment(self, var_token: Token, tokens: List[Token],
                             expression_stack: List[ast.ExprNode]) -> ast.ExprNode:
            if var_token.text not in self.__variables:
                node = ast.VarDeclNode(name=var_token.text)
                tokens.pop(0)  # eat the '=' operator
                self.__parse_expression(tokens, expression_stack)
                node.init_expr = expression_stack.pop()
                self.__variables.append(var_token.text)
            else:
                node = ast.VarNode(name=var_token.text)

            return node

        def parse_function_call(self, name_token: Token, tokens: List[Token],
                                expression_stack: List[ast.ExprNode]) -> ast.FunCallNode:
            if name_token.text not in self.__functions:
                raise ParserError(f"Call to an unknown function {name_token.text} on "
                                  "line {name_token.line}, char {name_token.pos}")

            node = ast.FunCallNode(name_token.text)

            assert tokens[0].type == TokenType.LeftParenthesis
            tokens.pop(0)  # pop the parentheses

            while tokens and tokens[0].type != TokenType.RightParenthesis:
                self.__parse_expression(tokens, expression_stack)
                node.add_argument(expression_stack.pop())

                assert tokens[0].type == TokenType.Comma
                tokens.pop(0)  # pop the comma

            assert tokens and tokens[0].type == TokenType.RightParenthesis
            tokens.pop(0)  # pop the right parenthesis

            return node

        token = tokens.pop(0)
        if tokens and tokens[0].type == TokenType.Assignment:
            node = parse_assignment(self, token, tokens, expression_stack)
        elif tokens and tokens[0].type == TokenType.LeftParenthesis:
            node = parse_function_call(self, token, tokens, expression_stack)
        else:
            if token.text not in self.__variables:
                raise ParserError(f"Undefined variable {token.text}")

            node = ast.VarNode(name=token.text)

        expression_stack.append(node)

        return token

    def __parse_bound_unary_operator(self, tokens: List[Token],
                                     expression_stack: List[ast.ExprNode]) -> Token:
        operator_token = tokens.pop(0)
        node = ast.UnaryOperatorNode(operator_token.text)
        self.__parse_expression(tokens, expression_stack)
        node.expr = expression_stack.pop()

        expression_stack.append(node)

        return operator_token

    def __parse_binary_operator(self, tokens: List[Token],
                                expression_stack: List[ast.ExprNode]) -> Token:
        operator_token = tokens.pop(0)
        node = ast.BinaryOperatorNode(operator_token.text)
        node.lhs_expr = expression_stack.pop()

        self.__parse_expression(tokens, expression_stack, operator_token)
        node.rhs_expr = expression_stack.pop()

        expression_stack.append(node)

        return operator_token

    def __parse_logic_operator(self, tokens: List[Token],
                               expression_stack: List[ast.ExprNode]) -> Token:
        operator_token = tokens.pop(0)
        node = ast.LogicOperatorNode(operator_token.text)
        node.lhs_expr = expression_stack.pop()

        self.__parse_expression(tokens, expression_stack, operator_token)
        node.rhs_expr = expression_stack.pop()

        expression_stack.append(node)

        return operator_token

    def __parse_ternary_operator(self, tokens: List[Token],
                                 expression_stack: List[ast.ExprNode]) -> Token:
        operator_token = tokens.pop(0)
        node = ast.TernaryOperatorNode()
        node.condition_expr = expression_stack.pop()

        self.__parse_expression(tokens, expression_stack)
        node.true_expr = expression_stack.pop()
        assert tokens[0].type == TokenType.Colon
        tokens.pop(0)  # pop colon

        self.__parse_expression(tokens, expression_stack)
        node.false_expr = expression_stack.pop()

        expression_stack.append(node)

        return operator_token

    def __parse_expression(self, tokens: List[Token], expression_stack: List[ast.ExprNode],
                           operator: Token = None) -> None:
        # Must be a literal or an unary operator
        if tokens[0].type == TokenType.LeftParenthesis:
            self.__parse_parenthesized_subexpression(tokens, expression_stack)

        token = None
        terminals = (TokenType.NewLine, TokenType.Colon, TokenType.Comma,
                     TokenType.RightParenthesis)
        while tokens and tokens[0].type not in terminals:
            if (not token or token.type != TokenType.Literal) \
                    and tokens[0].type.is_unary_operator():
                token = self.__parse_bound_unary_operator(tokens, expression_stack)
            elif tokens[0].type == TokenType.Literal:
                token = self.__parse_literal(tokens, expression_stack)
            elif tokens[0].type == TokenType.Identifier:
                token = self.__parse_identifier(tokens, expression_stack)
            elif tokens[0].type.is_binary_operator() \
                    or tokens[0].type.is_logic_operator() \
                    or tokens[0].type.is_ternary_operator():
                if operator and operator.type.priority() < tokens[0].type.priority():
                    return

                if tokens[0].type.is_binary_operator():
                    token = self.__parse_binary_operator(tokens, expression_stack)
                elif tokens[0].type.is_logic_operator():
                    token = self.__parse_logic_operator(tokens, expression_stack)
                elif tokens[0].type.is_ternary_operator():
                    token = self.__parse_ternary_operator(tokens, expression_stack)
