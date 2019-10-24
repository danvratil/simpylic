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
from ddt import ddt, data, unpack
from io import StringIO

from tokenizer import Tokenizer, Token, TokenType

@ddt
class TestTokenizer(unittest.TestCase):

    @data(("return 10", [Token(TokenType.Identifier, text="return", line=1, pos=1),
                         Token(TokenType.Literal, text="10", line=1, pos=8)]),
          ("10", [Token(TokenType.Literal, text="10", line=1, pos=1)]),
          ("return -12", [Token(TokenType.Identifier, text="return", line=1, pos=1),
                          Token(TokenType.Operator, text="-", line=1, pos=8),
                          Token(TokenType.Literal, text="12", line=1, pos=9)]),
          ("1 + 2", [Token(TokenType.Literal, text="1", line=1, pos=1),
                     Token(TokenType.Operator, text="+", line=1, pos=3),
                     Token(TokenType.Literal, text="2" line=1, pos=5)]))
    @unpack
    def test_basic_tokenizer(self, code, tokens):
        buffer = StringIO()
        buffer.write(code)
        buffer.seek(0)
        output_tokens = Tokenizer(buffer).tokenize()
        self.assertListEqual(tokens, output_tokens)

if __name__ == '__main__':
    unittest.main()
