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
from typing import TextIO, List, Iterator
from enum import Enum, auto


class TokenType(Enum):
    Unknown = auto()
    Whitespace = auto()  # Only considered for indentation
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
    QuestionMark = auto()
    Comma = auto()

    LeftParenthesis = auto()
    RightParenthesis = auto()

    KeywordReturn = auto()
    KeywordAnd = auto()
    KeywordOr = auto()
    KeywordIf = auto()
    KeywordElif = auto()
    KeywordElse = auto()
    KeywordWhile = auto()
    KeywordDef = auto()

    Colon = auto()

    __unary_operators = [Minus, Tilde, Negation]
    __binary_operators = [Plus, Minus, Star, Slash, Assignment]
    __ternary_operators = [QuestionMark, Colon]
    __logic_operators = [LessThan, LessThanOrEqual, GreaterThan, GreaterThanOrEqual, Equals,
                         NotEquals, KeywordAnd, KeywordOr]

    def is_unary_operator(self):
        return self.value in TokenType.__unary_operators.value

    def is_binary_operator(self):
        return self.value in TokenType.__binary_operators.value

    def is_logic_operator(self):
        return self.value in TokenType.__logic_operators.value

    def is_ternary_operator(self):
        return self.value in TokenType.__ternary_operators.value

    def priority(self):
        if self.is_unary_operator():
            return 100
        if self.is_logic_operator():
            return 90 if self in (TokenType.KeywordAnd, TokenType.KeywordOr) else 80
        if self.is_binary_operator():
            return 95 if self == TokenType.Assignment else 80
        if self.is_ternary_operator():
            return 92

        return 1


class Token:
    def __init__(self, text: str, token_type: TokenType, line: int, pos: int):
        self.type = token_type
        self.line = line
        self.pos = pos
        self.text = text

    def __repr__(self):
        return f"Token(type={self.type}, priority={self.type.priority()}, text=\"{self.text}\", " \
               f"line={self.line}, pos={self.pos})"

    def __eq__(self, other):
        return self.type == other.type \
            and self.line == other.line \
            and self.pos == other.pos \
            and self.text == other.text


class TokenizerError(Exception):
    def __init__(self, what, line, pos):
        super().__init__(self, what)
        self.what = what
        self.line = line
        self.pos = pos

    def __str__(self):
        return f"{self.what} on line {self.line}:{self.pos}"


class Tokenizer:

    __operators = ['+', '-', '*', '/', '~', '!', '<', '>', '(', ')', '=', '?']

    __single_operators = {'+': TokenType.Plus,
                          '-': TokenType.Minus,
                          '*': TokenType.Star,
                          '/': TokenType.Slash,
                          '~': TokenType.Tilde,
                          '!': TokenType.Negation,
                          '(': TokenType.LeftParenthesis,
                          ')': TokenType.RightParenthesis,
                          '?': TokenType.QuestionMark}
    __long_operators = {'==': TokenType.Equals,
                        '!=': TokenType.NotEquals,
                        '<':  TokenType.LessThan,
                        '>=': TokenType.GreaterThanOrEqual,
                        '<=': TokenType.LessThanOrEqual,
                        '>':  TokenType.GreaterThan,
                        '=':  TokenType.Assignment}

    __keywords = {'return': TokenType.KeywordReturn,
                  'and': TokenType.KeywordAnd,
                  'or': TokenType.KeywordOr,
                  'if': TokenType.KeywordIf,
                  'elif': TokenType.KeywordElif,
                  'else': TokenType.KeywordElse,
                  'while': TokenType.KeywordWhile,
                  'def': TokenType.KeywordDef}

    def __init__(self, source: TextIO):
        self.source = source
        self.__line = 1
        self.__pos = 1
        self.__token_text = ''
        self.__tokens: List[str] = []

    def __token_pos(self):
        return {'line': self.__line,
                'pos': self.__pos}

    def __tokenize_newline(self, char: str, char_iter: Iterator[str]) -> str:
        self.__tokens.append(Token(char, TokenType.NewLine, **self.__token_pos()))
        self.__pos = 1
        self.__line += 1
        return next(char_iter, None)

    def __tokenize_colon(self, char: str, char_iter: Iterator[str]) -> str:
        self.__tokens.append(Token(char, TokenType.Colon, **self.__token_pos()))
        self.__pos += 1
        return next(char_iter, None)

    def __tokenize_comma(self, char: str, char_iter: Iterator[str]) -> str:
        self.__tokens.append(Token(',', TokenType.Comma, **self.__token_pos()))
        self.__pos += 1
        return next(char_iter, None)

    def __tokenize_whitespace(self, char: str,
                              char_iter: Iterator[str]) -> str:
        if self.__pos == 1:
            self.__token_text = ""
            while char and char in (' ', '\t'):
                self.__token_text += char
                char = next(char_iter, None)

            self.__tokens.append(Token(self.__token_text, TokenType.Whitespace,
                                       **self.__token_pos()))
            self.__pos += len(self.__token_text)
            return char

        self.__pos += 1
        return next(char_iter, None)

    def __tokenize_operator(self, char: str,
                            char_iter: Iterator[str]) -> str:
        if char in Tokenizer.__single_operators:
            self.__tokens.append(Token(char, Tokenizer.__single_operators[char],
                                       **self.__token_pos()))
            self.__pos += 1
            return next(char_iter, None)

        self.__token_text = ""
        while char and char in Tokenizer.__operators:
            self.__token_text += char
            char = next(char_iter, None)

        if self.__token_text in Tokenizer.__long_operators:
            self.__tokens.append(Token(self.__token_text,
                                       Tokenizer.__long_operators[self.__token_text],
                                       **self.__token_pos()))
            self.__pos += len(self.__token_text)
            return char

        raise TokenizerError(f"Unknown operator '{self.__token_text}'",
                             **self.__token_pos())

    def __tokenize_alpha(self, char: str,
                         char_iter: Iterator[str]) -> str:
        self.__token_text = ""
        while char and (char.isalpha() or char.isdigit() or char == '_'):
            self.__token_text += char
            char = next(char_iter, None)

        if self.__token_text in Tokenizer.__keywords:
            token_type = Tokenizer.__keywords[self.__token_text]
        else:
            token_type = TokenType.Identifier
        self.__tokens.append(Token(self.__token_text, token_type, **self.__token_pos()))
        self.__pos += len(self.__token_text)

        return char

    def __tokenize_digit(self, char: str,
                         char_iter: Iterator[str]) -> str:
        self.__token_text = ""
        while char and char.isdigit():
            self.__token_text += char
            char = next(char_iter, None)

        self.__tokens.append(Token(self.__token_text, TokenType.Literal, **self.__token_pos()))
        self.__pos += len(self.__token_text)

        return char

    def tokenize(self):
        char_iter = itertools.chain.from_iterable(self.source)
        char = next(char_iter, None)
        while char:
            if char in (' ', '\t'):
                char = self.__tokenize_whitespace(char, char_iter)
            elif char == '\n':
                char = self.__tokenize_newline(char, char_iter)
            elif char == ':':
                char = self.__tokenize_colon(char, char_iter)
            elif char in Tokenizer.__operators:
                char = self.__tokenize_operator(char, char_iter)
            elif char.isalpha():
                char = self.__tokenize_alpha(char, char_iter)
            elif char.isdigit():
                char = self.__tokenize_digit(char, char_iter)
            elif char == ',':
                char = self.__tokenize_comma(char, char_iter)
            else:
                raise TokenizerError(f"Invalid token '{char}'", **self.__token_pos())

        return self.__tokens
