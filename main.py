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

from tokenizer import Tokenizer

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('file', metavar='FILE', type=str, help='File to process')

    args = parser.parse_args()

    with open(args.file, 'r', encoding='utf-8') as file:
        tokens = Tokenizer(file).tokenize()
    print(tokens)

if __name__ == "__main__":
    main()
