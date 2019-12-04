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

from tokenizer import Tokenizer
from parser import Parser
from compiler import AsmGenerator
from ast import AstDumper
from enum import Enum
from typing import TextIO

class Operation(Enum):
    Compile = 1
    Interpret = 2
    DumpAst = 3

def run(srcfile: TextIO, outfile: TextIO, operation: Operation):
    if operation == Operation.Interpret:
        raise RuntimeError("Interpreter mode not yet implemeneted.")

    tokens = Tokenizer(srcfile).tokenize()
    ast = Parser().parse(tokens)
    if operation == Operation.DumpAst:
        AstDumper().dump(ast)
    elif operation == Operation.Compile:
        AsmGenerator(outfile).generate(ast)

