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

import argparse
from sys import stdout

from tokenizer import Tokenizer
from parser import Parser
from ast import AstDumper
from compiler import AsmGenerator

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=str, help='File to process.')
    parser.add_argument('-o', dest='output', metavar='OUTFILE', type=str, help='File to write assembly into.')
    group = parser.add_mutually_exclusive_group(required = True)
    group.add_argument('-c', dest='compile', action='store_true',
                       help='Compile the code into assembly.')
    group.add_argument('-i', dest='interpret', action='store_true',
                       help='Interpret the program.')

    args = parser.parse_args()

    if args.interpret:
        raise RuntimeError("Intepreter mode not yet implemented.")

    with open(args.file, 'r', encoding='utf-8') as file:
        tokens = Tokenizer(file).tokenize()

    ast = Parser().parse(tokens)
    #AstDumper.dump(ast)

    if args.compile:
        is_stdout = not args.output or args.output == '-'
        with stdout if is_stdout else open(args.output, 'w', encoding='utf-8') as outfile:
            AsmGenerator(outfile).generate(ast)

if __name__ == "__main__":
    main()
