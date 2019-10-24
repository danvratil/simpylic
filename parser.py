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
        expr_node = self.__parse_expression(tokens)
        stmt_node.add_node(expr_node)

        return stmt_node

    def __parse_expression(self, tokens):
        # Must be a literal or an unary operator
        token = tokens.pop(0)
        if token.type == TokenType.Operator:
            operator_node = ast.UnaryOperatorNode(token.text)
            node = self.__parse_expression(tokens)
            operator_node.add_node(node)
            return operator_node
        elif token.type == TokenType.Literal:
            if len(tokens) > 2 and tokens[0].type == TokenType.Operator:
                operator_token = tokens.pop(0)
                operator_node = ast.BinaryOperatorNode(operator_token.text)
                operator_node.add_node(ast.ConstantNode(type='int', value=int(token.text)))
                operator_node.add_node(self.__parse_expression(tokens))
                return operator_node
            else:
                return ast.ConstantNode(type='int', value=int(token.text))
        else:
            raise ParseError(f'Invalid token {token}')

