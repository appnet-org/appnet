from abc import ABC, abstractmethod
from typing import Any, Optional, TypeVar, Union

from compiler.frontend.visitor import Visitor

from .visitor import Visitor, accept


class Node(ABC):
    def __init__(self, name: str) -> None:
        self.name = name

    def accept(self, visitor: Visitor, ctx):
        return visitor.visitOther(self, ctx)


class Statement(Node):
    def __init__(self, name: str, type: str) -> None:
        super().__init__(name)
        self.type = type

    def accept(self, visitor: Visitor, ctx):
        return visitor.visitStatement(self, ctx)
