class Pathfinding:
    """Class needed to find the shortest path"""

    def __init__(self, graph: dict[str, list[str]]) -> None:
        self.graph = graph
        self.visited = []
        self.not_visited = self.graph.keys()

    def resolve(self, start: str):
        
        while self.not_visited:
