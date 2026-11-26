from heapq import heappop, heappush
from itertools import count
from math import inf
from utils import Graph, Zone


State = tuple[Zone, int]


class Pathfinding:
    """Find minimum-time routes while respecting per-turn capacities."""

    def __init__(self, graph: Graph) -> None:
        """
        Initialize the pathfinding algorithm with a graph.

        Args:
            graph (Graph): The graph representing the zones and connections.
        """
        self.graph = graph.representation()
        self.drone_count = len(graph.drone)
        self.visited: list[Zone] = []
        self.not_visited = list(self.graph.keys())
        self.distance: dict[Zone, int | float] = {
            zone: inf for zone in self.not_visited
        }
        self.previous: dict[Zone, Zone] = {}
        self.path: list[Zone] = []
        self.start: Zone | None = None
        self.drone_id = 0
        self.schedule: dict[str, list[str]] = {}
        self.drone_schedules: dict[int, dict[str, list[str]]] = {}

        zone_by_name = {zone.name: zone for zone in self.graph}
        self._edge_capacities: dict[frozenset[Zone], int] = {}
        for connection in graph.connections:
            left = zone_by_name.get(connection.start)
            right = zone_by_name.get(connection.end)
            if left is not None and right is not None:
                self._edge_capacities[frozenset((left, right))] = int(
                    connection.max_link_capacity
                )

        self._drone_timelines: dict[int, dict[int, Zone]] = {}
        self._drone_edge_usage: dict[
            int, dict[int, frozenset[Zone]]
        ] = {}
        self._state_previous: dict[State, State | None] = {}
        self._root_turn: dict[State, int] = {}
        self._best_states: dict[Zone, State] = {}


    def _get_zone(self, value: str | Zone, role: str) -> Zone:
        """Retrieve a Zone object based on its name or return the Zone if already provided.

        Args:
            value (str | Zone): The name of the zone or a Zone object.
            role (str): A string indicating the role of the zone (e.g., "start" or "end").

        Returns:
            Zone: The corresponding Zone object.
        """

        if isinstance(value, str):
            zone = next(
                (zone for zone in self.graph if zone.name == value),
                None,
            )
        else:
            zone = value if value in self.graph else None
        if zone is None:
            raise ValueError(f"Unknown {role} zone: {value}")
        return zone


    def _zone_available(self, zone: Zone, turn: int, drone_id: int) -> bool:
        """Check if a zone is available for a drone at a specific turn.

        Args:
            zone (Zone): The zone to check.
            turn (int): The turn number to check.
            drone_id (int): The ID of the drone.

        Returns:
            bool: True if the zone is available, False otherwise.
        """

        occupied = sum(
            timeline.get(turn) is zone
            for other_id, timeline in self._drone_timelines.items()
            if other_id != drone_id
        )
        return occupied < int(zone.max_drones)

    def _edge_available(
        self,
        edge: frozenset[Zone],
        turn: int,
        drone_id: int,
    ) -> bool:
        """
        Check if an edge (connection between two zones) is available for a drone at a specific turn.

        Args:
            edge (frozenset[Zone]): The edge to check, represented as a frozenset of two Zone objects.
            turn (int): The turn number to check.
            drone_id (int): The ID of the drone.

        Returns:
            bool: True if the edge is available, False otherwise.
        """

        used = sum(
            usage.get(turn) == edge
            for other_id, usage in self._drone_edge_usage.items()
            if other_id != drone_id
        )
        return used < self._edge_capacities.get(edge, 1)

    def resolve(self, start: str | Zone, drone_id: int = 0) -> None:
        """
        Find the minimum-time route from the start zone for a specific drone.

        Args:
            start (str | Zone): The starting zone, either as a name (str) or a Zone object.
            drone_id (int): The ID of the drone for which to find the
        """

        start_zone = self._get_zone(start, "start")
        if drone_id < 0 or drone_id >= self.drone_count:
            raise ValueError(f"Unknown drone ID: {drone_id}")

        self.start = start_zone
        self.drone_id = drone_id
        self.visited = []
        self.not_visited = list(self.graph.keys())
        self.distance = {zone: inf for zone in self.not_visited}
        self.previous.clear()
        self.path = []
        self.schedule = {}
        self._state_previous = {}
        self._root_turn = {}
        self._best_states = {}

        other_timelines = [
            timeline
            for other_id, timeline in self._drone_timelines.items()
            if other_id != drone_id
        ]
        latest_reserved_turn = max(
            (max(timeline, default=0) for timeline in other_timelines),
            default=0,
        )
        horizon = latest_reserved_turn + 2 * len(self.graph) + 2

        queue: list[tuple[int, int, int, Zone]] = []
        sequence = count()
        for turn in range(1, horizon + 1):
            if self._zone_available(start_zone, turn, drone_id):
                state = (start_zone, turn)
                self._state_previous[state] = None
                self._root_turn[state] = turn
                heappush(
                    queue,
                    (turn, start_zone.priority, next(sequence), start_zone),
                )

        while queue:
            turn, _, _, zone = heappop(queue)
            state = (zone, turn)
            self.visited.append(zone)

            if zone not in self._best_states:
                self._best_states[zone] = state
                self.distance[zone] = turn - self._root_turn[state]
                if zone in self.not_visited:
                    self.not_visited.remove(zone)
                previous_state = self._state_previous[state]
                if previous_state is not None:
                    self.previous[zone] = previous_state[0]

            if turn >= horizon:
                continue

            wait_state = (zone, turn + 1)
            if self._zone_available(zone, turn + 1, drone_id):
                if wait_state in self._state_previous:
                    if self._state_previous[wait_state] is None:
                        self._state_previous[wait_state] = state
                        self._root_turn[wait_state] = self._root_turn[state]
                else:
                    self._state_previous[wait_state] = state
                    self._root_turn[wait_state] = self._root_turn[state]
                    heappush(
                        queue,
                        (turn + 1, zone.priority, next(sequence), zone),
                    )

            for neighbor in sorted(
                self.graph.get(zone, []),
                key=lambda item: (item.priority, item.name),
            ):
                duration = 2 if neighbor.type == "restricted" else 1
                arrival_turn = turn + duration
                if arrival_turn > horizon:
                    continue
                if any(
                    not self._zone_available(zone, intermediate, drone_id)
                    for intermediate in range(turn + 1, arrival_turn)
                ):
                    continue
                if not self._zone_available(neighbor, arrival_turn, drone_id):
                    continue

                edge = frozenset((zone, neighbor))
                if not self._edge_available(edge, arrival_turn, drone_id):
                    continue

                next_state = (neighbor, arrival_turn)
                if next_state in self._state_previous:
                    continue
                self._state_previous[next_state] = state
                self._root_turn[next_state] = self._root_turn[state]
                heappush(
                    queue,
                    (
                        arrival_turn,
                        neighbor.priority,
                        next(sequence),
                        neighbor,
                    ),
                )

    def get_shortest_path(self, end: str | Zone) -> list[Zone]:
        """
        Retrieve the shortest path from the start zone to the specified end zone for the current drone.

        Args:
            end (str | Zone): The ending zone, either as a name (str) or a Zone object.

        Returns:
            list[Zone]: A list of Zone objects representing the shortest path from the start to the end zone.
        """
        end_zone = self._get_zone(end, "end")
        if self.start is None:
            raise ValueError("Run resolve() before requesting a shortest path")
        if end_zone not in self._best_states:
            raise ValueError(f"No path to end zone: {end_zone.name}")

        current_state: State | None = self._best_states[end_zone]
        states: list[State] = []
        while current_state is not None:
            states.append(current_state)
            current_state = self._state_previous[current_state]
        states.reverse()

        timeline: dict[int, Zone] = {states[0][1]: states[0][0]}
        edge_usage: dict[int, frozenset[Zone]] = {}
        for (from_zone, from_turn), (to_zone, to_turn) in zip(
            states, states[1:]
        ):
            for intermediate in range(from_turn + 1, to_turn):
                timeline[intermediate] = from_zone
            timeline[to_turn] = to_zone
            if from_zone is not to_zone:
                edge_usage[to_turn] = frozenset((from_zone, to_zone))

        self.path = [timeline[turn] for turn in sorted(timeline)]
        self._drone_timelines[self.drone_id] = timeline
        self._drone_edge_usage[self.drone_id] = edge_usage
        self.schedule = {
            str(turn): [zone.name]
            for turn, zone in sorted(timeline.items())
        }
        self.drone_schedules[self.drone_id] = self.schedule.copy()

        for zone in self.graph:
            zone.status.pop(self.drone_id, None)
        for turn, zone in sorted(timeline.items()):
            zone.status.setdefault(self.drone_id, turn)
        return self.path
