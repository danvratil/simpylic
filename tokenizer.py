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
    def __init__(self, text, type, line, pos):
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

    def __get_symbol_type(self, c):
        if c == ' ' or c == '\t' or c == '\r':
            return Symbol.Whitespace
        elif c == '\n':
            return Symbol.NewLine
        elif (c >= 'a' and c <= 'z') or (c >= 'A' and c <= 'Z'):
            return Symbol.Letter
        elif c >= '0' and c <= '9':
            return Symbol.Digit
        elif c in '+-*/~!':
            return Symbol.Operator

        raise TokenizerError(f'Unknown symbol {c}', self.__line, self.__pos)

    def __token_for_symbol(self, symbol, last_token):
        if symbol == Symbol.Operator:
            return TokenType.Operator
        elif symbol == Symbol.NewLine:
            return TokenType.NewLine
        elif symbol == Symbol.Whitespace:
            return TokenType.Whitespace
        elif symbol == Symbol.Letter:
            return TokenType.Identifier
        elif symbol == Symbol.Digit:
            if last_token == TokenType.Identifier:
                return TokenType.Identifier
            else:
                return TokenType.Literal

        assert(False)

    def __token_pos(self):
        return {'line': self.__line,
                'pos': self.__pos - len(self.__token_text)}

    def __terminate_token(self, token):
        if token == TokenType.Unknown:
            pass
        elif token == TokenType.NewLine:
            self.__newline_token()
        elif token == TokenType.Operator:
            self.__operator_token()
        elif token == TokenType.Identifier:
            self.__identifier_token()
        elif token == TokenType.Literal:
            self.__literal_token()
        elif token == TokenType.Whitespace:
            self.__whitespace_token()
        else:
            raise TokenizerError(f'Invalid expression: expected whitespace, identifier or literal, got \'{token}\'', self.__line, self.__pos)

    def __newline_token(self):
        self.__tokens.append(Token(None, type=TokenType.NewLine, line=self.__line, pos=self.__pos - 1))
        self.__line += 1
        self.__pos = -1
        self.__token_text = ''

    def __text_token(self, token):
        self.__tokens.append(Token(self.__token_text, type=token, **self.__token_pos()))
        self.__token_text = ''

    def __operator_token(self):
        self.__text_token(TokenType.Operator);

    def __identifier_token(self):
        self.__text_token(TokenType.Identifier)

    def __literal_token(self):
        self.__text_token(TokenType.Literal)

    def __whitespace_token(self):
        # FIXME: Re-enable whitespace tokens once we start supporting indentation
        #self.__text_token(TokenType.Whitespace)
        self.__token_text = ''

    def tokenize(self):
        self.__line = 1
        self.__pos = 1
        self.__token_text = ''
        self.__tokens = []

        last_token = TokenType.Unknown
        while True:
            c = self.source.read(1)
            if not c:
                break

            symbol = self.__get_symbol_type(c)
            token_type = self.__token_for_symbol(symbol, last_token)

            if token_type == TokenType.NewLine:
                self.__terminate_token(last_token)
                last_token = TokenType.Unknown
            elif token_type == TokenType.Operator:
                # Operators are (so far) always single character
                self.__terminate_token(last_token)
                last_token = TokenType.Unknown
            elif token_type != last_token:
                if last_token != TokenType.Unknown:
                    self.__terminate_token(last_token)

            self.__token_text += c
            self.__pos += 1
            last_token = token_type

        if last_token != TokenType.Unknown:
            self.__terminate_token(last_token)

        return self.__tokens

