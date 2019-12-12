from typing import Callable

from .node import Node

class AstError(RuntimeError):
    pass

class AstDumper:
    @staticmethod
    def dump(node: Node, depth: int = 0):
        node.traverse(depth)


class AstVisitor:
    def __init__(self, ast: Node, callback: Callable):
        self.__ast = ast
        self.__callback = callback

    def visit(self):
        self.__ast.visit(self.__callback)
