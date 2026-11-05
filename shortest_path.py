from math import inf
from utils import Zone, Graph


class Pathfinding:
    """Class needed to find the shortest path"""

    def __init__(self, graph: Graph) -> None:
        """Initialize a Pathfinding object.

        args:
            graph (dict[Zone, list[Zone]]): The graph representation of the zones and their connections
        """
        self.graph = graph.representation()
        self.visited: list[Zone] = []
        self.not_visited = list(self.graph.keys())
        self.distance: dict[Zone, int] = {name: inf for name in self.not_visited}
        self.previous: dict[Zone, Zone] = {}
        self.path: list[Zone] = []


    def get_shortest_path(self, end: str | Zone) -> list[Zone]:
        """Get the shortest path from the start zone to the end zone

        Args:
            end (str | Zone): The end zone

        Raises:
            ValueError: If the end zone is unknown

        Returns:
            list[Zone]: The shortest path from the start zone to the end zone
        """
        if isinstance(end, str):
            end = next((zone for zone in self.graph if zone.name == end), None)
            if end is None:
                raise ValueError(f"Unknown end zone: {end!r}")

        if end not in self.graph:
            raise ValueError(f"Unknown end zone: {end}")

        current = end
        path: list[Zone] = []

        while current in self.previous:
            path.append(current)
            current = self.previous[current]

        path.append(current)
        self.path = list(reversed(path))
        return self.path

    def resolve(self, start: str | Zone) -> list[Zone]:
        """dijkstra algorithm to find the shortest path from the start zone to all other zones

        Args:
            start (str | Zone): The starting zone

        Raises:
            ValueError: If the start zone is unknown

        Returns:
            list[Zone]: The shortest path from the start zone to all other zones
        """
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
                key=lambda zone: (self.distance[zone], zone.priority)
            )

            if self.distance[current] == inf:
                break

            self.not_visited.remove(current)
            self.visited.append(current)
            for neighbor in self.graph.get(current, []):
                if neighbor in self.not_visited:
                    cost = 2 if neighbor.type == "restricted" else 1
                    new_distance = self.distance[current] + cost
                    if new_distance < self.distance[neighbor]:
                        self.distance[neighbor] = new_distance
                        self.previous[neighbor] = current
