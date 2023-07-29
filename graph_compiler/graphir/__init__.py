from __future__ import annotations

from typing import Dict


class GraphIR:
    def __init__(self):
        self.element_pool: Dict[str, Element] = dict()

    def contain(self, ename: str):
        return ename in self.element_pool

    def add_element(self, ename: str, config: dict, property: dict):
        self.element_pool[ename] = Element(ename, config, property)

    def add_edge(self, e1: str, e2: str):
        self.element_pool[e1].next.append(e2)

    def display(self):
        print("Elements:")
        for e in self.element_pool.values():
            e.display()
        print("--------------------")
        print("Edges:")
        for e in self.element_pool.values():
            for nxt in e.next:
                print(e.name, "->", nxt)


class Element:
    def __init__(self, name: str, config: dict, property: dict):
        self.name = name
        self.config = config
        self.property = property
        self.next = []

    def display(self):
        title_length = len(self.name) + 2
        print("=" * title_length)
        print(f" {self.name} ")
        print("=" * title_length)
        print("configs:")
        for cname, cvalue in self.config.items():
            print(f"    {cname} = {cvalue}")
        print("properties:")
        for pname, pvalue in self.property.items():
            print(f"    {pname} = {pvalue}")
