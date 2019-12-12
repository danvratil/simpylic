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

from typing import Any

from .node import ExprNode


class ConstantNode(ExprNode):
    def __init__(self, value_type: str, value: Any):
        super().__init__()
        self.__type = value_type
        self.__value = value

    def __repr__(self):
        return f"ConstantNode(type={self.__type}, value={self.__value})"

    @property
    def value_type(self) -> str:
        return self.__type

    @property
    def value(self) -> Any:
        return self.__value
