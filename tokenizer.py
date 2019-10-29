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

import itertools

from enum import Enum, unique

class TokenType(Enum):
    Unknown = 0
    Whitespace = 1
    NewLine = 2
    Literal = 3
    Identifier = 4

    __FirstOperator = 10
    Plus = 10
    Minus = 11
    Star = 12
    Slash = 13
    LessThan = 14
    Equals = 15
    GreaterThan = 16
    Negation = 17
    Tilde = 18
    __LastOperator = 90

    LeftParenthesis = 91
    RightParenthesis = 92

    KeywordReturn = 100
    KeywordAnd = 101
    KeywordOr = 102

    def is_operator(self):
        return self.value >= TokenType.__FirstOperator.value and self.value <= TokenType.__LastOperator.value

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

    __operators = { '+': TokenType.Plus,
                    '-': TokenType.Minus,
                    '*': TokenType.Star,
                    '/': TokenType.Slash,
                    '~': TokenType.Tilde,
                    '!': TokenType.Negation,
                    '<': TokenType.LessThan,
                    '=': TokenType.Equals,
                    '>': TokenType.GreaterThan,
                    '(': TokenType.LeftParenthesis,
                    ')': TokenType.RightParenthesis
                  }

    __keywords = { 'return': TokenType.KeywordReturn,
                   'and': TokenType.KeywordAnd,
                   'or': TokenType.KeywordOr
                 }

    def __init__(self, source):
        self.source = source

    def __token_pos(self):
        return {'line': self.__line,
                'pos': self.__pos - len(self.__token_text)}

    def tokenize(self):
        self.__line = 1
        self.__pos = 1
        self.__token_text = ''
        self.__tokens = []

        char_iter = itertools.chain.from_iterable(self.source)
        c = next(char_iter, None)
        while c is not None:
            # We ignore whitespaces for now
            if c == ' ' or c == '\t':
                self.__pos += 1
            elif c == '\n':
                self.__tokens.append(Token(text=c, type=TokenType.NewLine, **self.__token_pos()))
                self.__pos = 0
                self.__line += 1
            elif c in Tokenizer.__operators:
                self.__tokens.append(Token(text=c, type=Tokenizer.__operators[c], **self.__token_pos()))
                self.__pos += 1
            elif c.isalpha():
                token_text = c
                while True:
                    c = next(char_iter, None)
                    if not c or not c.isalpha() and not c.isdigit():
                        break
                    token_text += c
                if token_text in Tokenizer.__keywords:
                    token_type = Tokenizer.__keywords[token_text]
                else:
                    token_type = TokenType.Identifier
                self.__tokens.append(Token(text=token_text, type=token_type, **self.__token_pos()))
                self.__pos += len(token_text)
                continue
            elif c.isdigit():
                token_text = c
                while True:
                    c = next(char_iter, None)
                    if not c or not c.isdigit():
                        break
                    token_text +=c
                self.__tokens.append(Token(text=token_text, type=TokenType.Literal, **self.__token_pos()))
                self.__pos += len(token_text)
                continue
            else:
                raise TokenizerError(f"Invalid token '{c}' on line {self.__line}, pos {self.__pos}")

            c = next(char_iter, None)

        return self.__tokens

