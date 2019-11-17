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

from enum import Enum, auto

class TokenType(Enum):
    Unknown = auto()
    Whitespace = auto()
    NewLine = auto()
    Literal = auto()
    Identifier = auto()

    Plus = auto()
    Minus = auto()
    Star = auto()
    Slash = auto()
    LessThan = auto()
    LessThanOrEqual = auto()
    Equals = auto()
    NotEquals = auto()
    GreaterThan = auto()
    GreaterThanOrEqual = auto()
    Negation = auto()
    Tilde = auto()
    Assignment = auto()

    LeftParenthesis = auto()
    RightParenthesis = auto()

    KeywordReturn = auto()
    KeywordAnd = auto()
    KeywordOr = auto()

    __unary_operators = [Minus, Tilde, Negation]
    __binary_operators = [Plus, Minus, Star, Slash, Assignment]
    __logic_operators = [LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual, Equals, NotEquals, KeywordAnd, KeywordOr]

    def is_unary_operator(self):
        return self.value in TokenType.__unary_operators.value

    def is_binary_operator(self):
        return self.value in TokenType.__binary_operators.value

    def is_logic_operator(self):
        return self.value in TokenType.__logic_operators.value

    def priority(self):
        if self.is_unary_operator():
            return 100
        elif self.is_logic_operator():
            if self == TokenType.KeywordAnd or self == TokenType.KeywordOr:
                return 90
            else:
                return 80
        elif self.is_binary_operator():
            return 80
        else:
            return 1

class Token:
    def __init__(self, text, type, line, pos):
        self.type = type
        self.line = line
        self.pos = pos
        self.text = text

    def __repr__(self):
        return f"Token(type={self.type}, priority={self.type.priority()}, text=\"{self.text}\", line={self.line}, pos={self.pos})"

    def __eq__(self, other):
        return self.type == other.type \
            and self.line == other.line \
            and self.pos == other.pos \
            and self.text == other.text

class TokenizerError(Exception):
    def __init__(self, what, line, pos):
        self.what = what
        self.line = line
        self.pos = pos

    def __str__(self):
        return f"{self.what} on line {self.line}:{self.pos}"

class Tokenizer:

    __operators = [ '+', '-', '*', '/', '~', '!', '<', '>', '(', ')', '=' ]

    __single_operators = { '+': TokenType.Plus,
                           '-': TokenType.Minus,
                           '*': TokenType.Star,
                           '/': TokenType.Slash,
                           '~': TokenType.Tilde,
                           '!': TokenType.Negation,
                           '(': TokenType.LeftParenthesis,
                           ')': TokenType.RightParenthesis
                         }
    __long_operators = { '==': TokenType.Equals,
                         '!=': TokenType.NotEquals,
                         '<' : TokenType.LessThan,
                         '>=': TokenType.GreaterThanOrEqual,
                         '<=': TokenType.LessThanOrEqual,
                         '>' : TokenType.GreaterThan,
                         '=' : TokenType.Assignment
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
                if c in Tokenizer.__single_operators:
                    self.__tokens.append(Token(text=c, type=Tokenizer.__single_operators[c], **self.__token_pos()))
                    self.__pos += 1
                else:
                    token_text = c
                    while True:
                        c = next(char_iter, None)
                        if not c or c not in Tokenizer.__operators:
                            break
                        token_text += c
                    if token_text in Tokenizer.__long_operators:
                        self.__tokens.append(Token(text=token_text, type=Tokenizer.__long_operators[token_text], **self.__token_pos()))
                        self.__pos += len(token_text)
                    else:
                        raise TokenizerError(f"Unknown operator '{token_text}'", **self.__token_pos())
                    continue
            elif c.isalpha():
                token_text = c
                while True:
                    c = next(char_iter, None)
                    if not c or not c.isalpha() and not c.isdigit() and not c == '_':
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
                raise TokenizerError(f"Invalid token '{c}'", **self.__token_pos())

            c = next(char_iter, None)

        return self.__tokens

