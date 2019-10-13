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

        self.process_tokens_for_node(main, iter(tokens))

        return root

    def process_tokens_for_node(self, parent_node, tokens):
        while True:
            token = next(tokens, None)
            if not token:
                break

            if token.type in [TokenType.Identifier, TokenType.Literal, TokenType.Operator]:
                node = self.node_for_token(token)
                parent_node.add_node(node)
                self.process_tokens_for_node(node, tokens)

    def node_for_token(self, token):
        if token.type == TokenType.Literal:
            return ast.ConstantNode(type="int", value=int(token.text))
        elif token.type == TokenType.Operator:
            return ast.UnaryOperatorNode(type=ast.UnaryOperatorNode.Type.fromText(token.text))
        else:
            if token.text == "return":
                return ast.ReturnStmtNode()

        raise ParserError(f"Unknown token {token}")
