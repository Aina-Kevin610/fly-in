from math import inf

from utils import Zone


class Pathfinding:
    """Class needed to find the shortest path"""

    def __init__(self, graph: dict[Zone, list[Zone]]) -> None:
        self.graph = graph
        self.visited: list[Zone] = []
        self.not_visited = list(self.graph.keys())
        self.distance: dict[Zone, float] = {name: inf for name in self.not_visited}
        self.previous: dict[Zone, Zone] = {}

    def resolve(self, start: str | Zone) -> None:
        if isinstance(start, str):
            start = next((zone for zone in self.graph if zone.name == start), None)
            if start is None:
                raise ValueError(f"Unknown start zone: {start!r}")

        if start not in self.graph:
            raise ValueError(f"Unknown start zone: {start}")

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

            for neighbor in self.graph.get(current, []):
                if neighbor in self.not_visited:
                    new_distance = self.distance[current] + 1
                    if new_distance < self.distance[neighbor]:
                        self.distance[neighbor] = new_distance
                        self.previous[neighbor] = current
