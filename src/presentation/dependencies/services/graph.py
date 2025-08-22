from dishka import Provider, Scope, provide

from src.domain.services.graph import UndirectedGraph


class GraphProvider(Provider):
    scope = Scope.APP

    @provide
    def get_graph(self) -> UndirectedGraph:
        return UndirectedGraph()
