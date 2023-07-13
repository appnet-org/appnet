from abc import ABC, abstractmethod


class BackendVariable:
    @abstractmethod
    def __init__(self) -> None:
        pass


class BackendType:
    @abstractmethod
    def __init__(self) -> None:
        pass

    @abstractmethod
    def __iter__(self):
        pass
