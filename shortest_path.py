from __future__ import annotations
from math import inf
import heapq
from utils import Graph, Zone


class PathFinding:
    def __init__(self, graph: Graph) -> None:
        self.graph = graph.representation()
        self.turn = 0
        self.visited = []
        self.not_visited = [(hub.distance, hub.priority, hub.name) for hub in self.graph.keys()]
        heapq.heapify(self.not_visited)



import heapq
from math import inf
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from graph import Graph, Zone


class PathFinding:
    """Calcule les distances minimales depuis une zone de départ."""

    def __init__(self, graph: Graph) -> None:
        self.graph: dict[Zone, list[Zone]] = graph.representation()
        self.turn: int = 0
        self.visited: set[Zone] = set()
        self.not_visited: list[tuple[float, int, int, Zone]] = []

    def _resolve_start(self, start: str | Zone) -> Zone:
        if isinstance(start, str):
            zone = next(
                (z for z in self.graph if z.name == start),
                None,
            )
        else:
            zone = start if start in self.graph else None

        if zone is None:
            raise ValueError(f"Unknown zone: {start}")
        return zone

    def _step_cost(self, successor: Zone) -> float:
        if successor.type == "restricted":
            return 2.0
        return 1.0

    def resolve(self, start: str | Zone) -> list[Zone]:
        """Met à jour `zone.distance` pour chaque zone accessible depuis `start`."""
        zone = self._resolve_start(start)

        counter = 0
        self.visited = set()
        self.not_visited = []

        for hub in self.graph:
            hub.distance = 0.0 if hub == zone else inf
            # Légère pénalité de départage si priority == False/0, bonus si prioritaire
            priority_rank = 0 if hub.type == "priority" else 1
            heapq.heappush(
                self.not_visited,
                (hub.distance, priority_rank, counter, hub),
            )
            counter += 1

        while self.not_visited:
            current_dist, _, _, current = heapq.heappop(self.not_visited)

            if (
                current in self.visited
                or current_dist > current.distance
                or current_dist == inf
            ):
                continue

            self.visited.add(current)

            for successor in self.graph.get(current, []):
                if successor in self.visited or successor.type == "blocked":
                    continue

                new_dist = current.distance + self._step_cost(successor)

                if new_dist < successor.distance:
                    successor.distance = new_dist
                    priority_rank = 0 if successor.type == "priority" else 1
                    heapq.heappush(
                        self.not_visited,
                        (successor.distance, priority_rank, counter, successor),
                    )
                    counter += 1

        return list(self.graph.keys())
            