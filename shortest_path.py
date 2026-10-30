from math import inf


class 


class Pathfinding:
    """Class needed to find the shortest path"""

    def __init__(self, graph: dict[str, list[str]]) -> None:
        self.graph = graph
        self.visited: list[str] = []
        self.not_visited = list(self.graph.keys())
        self.distance = {name: inf for name in self.not_visited}
        self.previous: dict[str, str] = {}

    def resolve(self, start: str) -> None:
        self.distance[start] = 0

        while self.not_visited:
            current = min(
                self.not_visited,
                key=lambda name: self.distance[name]
            )

            if self.distance[current] == inf:
                break

            self.not_visited.remove(current)
            self.visited.append(current)

            for s in self.graph[current]:
                if s in self.not_visited:
                    new_distance = self.distance[current] + 1
                    if new_distance < self.distance[s]:
                        self.distance[s] = new_distance
                        self.previous[s] = current

        print(self.visited)
        print(self.not_visited)
        print(self.distance)
        print(self.previous)
