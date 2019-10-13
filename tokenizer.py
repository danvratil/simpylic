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

class TokenType(Enum):
    Unknown = 0
    Whitespace = 1
    NewLine = 2
    Literal = 3
    Identifier = 4
    Operator = 5

class Symbol(Enum):
    Unknown = 0
    Letter = 1
    Digit = 2
    Whitespace = 3
    NewLine = 4
    Operator = 5

class Token:
    def __init__(self, type, line, pos, text):
        self.type = type
        self.line = line
        self.pos = pos
        self.text = text

    def __repr__(self):
        return f"Token(type={self.type}, text=\"{self.text}\", line={self.line}, pos={self.pos})"

    def __eq__(self, other):
        return self.type == other.type \
            and self.line == other.line \
            and self.pos == other.pos \
            and self.text == other.text

class TokenizerError(Exception):
    def __init__(self, what, line, char):
        self.what = what
        self.line = line
        self.char = char

    def __str__(self):
        return f"{self.what} on line {self.line}:{self.char}"

class Tokenizer:
    def __init__(self, source):
        self.source = source

    def tokenize(self):
        self.line = 1
        self.pos = 1
        last_token = TokenType.Unknown
        token_text = ""
        tokens = []
        while True:
            c = self.source.read(1)
            if not c:
                break

            symbol = self.get_symbol(c)
            token = self.token_for_symbol(symbol, last_token)
            if token != last_token:
                if last_token in [TokenType.Literal, TokenType.Identifier, TokenType.Operator]:
                    tokens.append(Token(type=last_token, line=self.line, pos=self.pos - len(token_text), text=token_text))
                elif token == TokenType.NewLine:
                    tokens.append(Token(type=token, line=self.line, pos=self.pos, text='\n'))
                    self.line += 1
                    self.pos = 1

                token_text = ""
                last_token = token

            if token == last_token:
                if token in [TokenType.Literal, TokenType.Identifier, TokenType.Operator]:
                    token_text += c

            self.pos += 1

        if last_token in [TokenType.Literal, TokenType.Identifier, TokenType.Operator]:
            tokens.append(Token(type=last_token, line=self.line, pos=self.pos - len(token_text), text=token_text))

        return tokens


    def get_symbol(self, c):
        if c == ' ' or c == '\t' or c == '\r':
            return Symbol.Whitespace
        elif c == '\n':
            return Symbol.NewLine
        elif (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z'):
            return Symbol.Letter
        elif c >= '0' and c <= '9':
            return Symbol.Digit
        elif c == '-' or c == '!' or c == '~':
            return Symbol.Operator

        raise TokenizerError(f"Unknown symbol {c}", self.line, self.pos)

    def token_for_symbol(self, symbol, token):
        if symbol == Symbol.Whitespace:
            return TokenType.Whitespace
        elif symbol == Symbol.NewLine:
            return TokenType.NewLine
        elif symbol == Symbol.Operator:
            return TokenType.Operator
        elif symbol == Symbol.Letter or symbol == Symbol.Digit:
            if token == TokenType.Identifier or token == TokenType.Literal:
                return token
            elif symbol == Symbol.Digit:
                return TokenType.Literal
            elif symbol == Symbol.Letter:
                return TokenType.Identifier

        raise TokenizeError(f"Unknown symbol {symbol}", self.line, self.pos)
