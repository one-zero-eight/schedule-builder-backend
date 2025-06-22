from dishka import Provider, Scope, provide

from src.application.graph import UndirectedGraph
from src.domain.interfaces.graph import IGraph


class GraphProvider(Provider):
    scope = Scope.REQUEST

    @provide
    def get_graph(self) -> IGraph:
        return UndirectedGraph()
