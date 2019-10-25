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

import ast
from tokenizer import TokenType, Token

class ParserError(Exception):
    pass

class Parser:
    def __init__(self):
        pass

    def parse(self, tokens):
        root = ast.ProgramNode()
        main = ast.FunctionNode("main")
        root.add_node(main)

        while tokens:
            node = self.__parse_statement(tokens)
            if node:
                main.add_node(node)

        return root

    def __parse_statement(self, tokens):
        peek_token = tokens[0]
        if peek_token.type == TokenType.Identifier and peek_token.text == 'return':
            return self.__parse_return_stmt(tokens)
        elif peek_token.type == TokenType.NewLine:
            tokens.pop(0)
            return None
        else:
            raise ParserError(f'Unexpected statement identifier {tokens[0]}')

    def __parse_return_stmt(self, tokens):
        token = tokens.pop(0)
        assert(token.type == TokenType.Identifier and token.text == 'return')

        stmt_node = ast.ReturnStmtNode()

        expression_stack = []
        self.__parse_expression(tokens, expression_stack)
        assert(len(expression_stack) == 1)
        stmt_node.add_node(expression_stack[0])

        return stmt_node

    def __parse_expression(self, tokens, expression_stack):
        # Must be a literal or an unary operator
        token = tokens.pop(0)
        if token.type == TokenType.Parenthesis:
            assert(token.text =='(')
            self.__parse_expression(tokens, expression_stack)
            token = tokens.pop(0)
            assert(token.type == TokenType.Parenthesis and token.text ==')')

        if not expression_stack and token.type == TokenType.Operator:
            node = ast.UnaryOperatorNode(token.text)
            self.__parse_expression(tokens, expression_stack)
            node.add_node(expression_stack.pop())
            expression_stack.append(node)
        else:
            if not expression_stack:
                expression_stack.append(ast.ConstantNode(type='int', value=int(token.text)))
            if len(tokens) > 2 and tokens[0].type == TokenType.Operator:
                rhs = expression_stack.pop()
                operator_token = tokens.pop(0)
                self.__parse_expression(tokens, expression_stack)
                lhs = expression_stack.pop()

                node = ast.BinaryOperatorNode(operator_token.text)
                node.add_node(rhs)
                node.add_node(lhs)
                expression_stack.append(node)

