from abc import ABC, abstractmethod


class IGraph(ABC):
    @abstractmethod
    def create_graph(self, vertices_number: int) -> None:
        pass

    @abstractmethod
    def add_edge(self, start: int, end: int) -> None:
        pass

    @abstractmethod
    def get_connected_components(self) -> list[list[int]]:
        pass
