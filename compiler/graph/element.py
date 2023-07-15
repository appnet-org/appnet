from typing import Dict, List, Optional, Set, Tuple, Union

from compiler.protobuf import Proto


class Element:
    def __init__(self, name: str, sql: Tuple[str, str], proto: Proto):
        self.name = name
        self.sql = sql
        self.proto = proto
        self.prev: List[Element] = []
        self.next: List[Element] = []
