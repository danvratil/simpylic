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

import unittest
from io import StringIO
from ddt import ddt, data, unpack

from simpylic.tokenizer import Tokenizer, Token, TokenType


@ddt
class TestTokenizer(unittest.TestCase):

    @data(("return 10", [Token("return", TokenType.KeywordReturn, line=1, pos=1),
                         Token("10", TokenType.Literal, line=1, pos=8)]),
          ("10", [Token("10", TokenType.Literal, line=1, pos=1)]),
          ("return -12", [Token("return", TokenType.KeywordReturn, line=1, pos=1),
                          Token("-", TokenType.Minus, line=1, pos=8),
                          Token("12", TokenType.Literal, line=1, pos=9)]),
          ("1 + 2", [Token("1", TokenType.Literal, line=1, pos=1),
                     Token("+", TokenType.Plus, line=1, pos=3),
                     Token("2", TokenType.Literal, line=1, pos=5)]),
          ("5 > 4 and 3 < 5", [Token("5", TokenType.Literal, line=1, pos=1),
                               Token(">", TokenType.GreaterThan, line=1, pos=3),
                               Token("4", TokenType.Literal, line=1, pos=5),
                               Token("and", TokenType.KeywordAnd, line=1, pos=7),
                               Token("3", TokenType.Literal, line=1, pos=11),
                               Token("<", TokenType.LessThan, line=1, pos=13),
                               Token("5", TokenType.Literal, line=1, pos=15)]))
    @unpack
    def test_basic_tokenizer(self, code, tokens):
        buffer = StringIO()
        buffer.write(code)
        buffer.seek(0)
        output_tokens = Tokenizer(buffer).tokenize()
        self.assertListEqual(tokens, output_tokens)


if __name__ == '__main__':
    unittest.main()
