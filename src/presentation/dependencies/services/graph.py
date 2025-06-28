from dishka import Provider, Scope, provide

from src.domain.interfaces.graph import IGraph
from src.domain.interfaces.services.graph import UndirectedGraph


class GraphProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_graph(self) -> IGraph:
        return UndirectedGraph()
