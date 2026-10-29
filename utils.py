from typing import Any


class Drone:
    """class for one drone"""

    def __init__(self) -> None:
        """Initialize a Drone object."""
        self.position: tuple[int, int] = (0, 0)
        self.state: str | None = None
        self.path: list[str] = []


class Zone:
    """class for one zone"""
    def __init__(self, name: str,
                 positions: tuple[int, int],
                 metadata: dict[str, str | int]
                 ) -> None:
        """Initialize a Zone object

        Args:j
            name (str): name of the zone
            positions (tuple[int, int]): top-left and bottom-right
                coordinates of the zone
            metadata (dict[str, str  |  int]): additional
                information about the zone
        """
        self.name = name
        self.x1 = positions[0]
        self.y1 = positions[1]
        self.color = metadata["color"]
        self.type = metadata["zone"]
        self.max_drones = metadata["max_drones"]


class Connection:
    """class for one connection"""
    def __init__(self, connection_data: dict[str, Any]) -> None:
        """Initialize a Connection object

        Args:
            connection_data (dict[str, Any]): dictionary
            containing connection information
        """
        self.start = connection_data["start"]
        self.end = connection_data["end"]
        self.max_link_capacity = connection_data["max_link_capacity"]


class Graph:
    """class for the graph"""
    def __init__(self, parsed_map: dict[str, Any]) -> None:
        """Initialize a Graph object.

        Args:
            parsed_map: a parsed map
        """
        self.drone: list[Drone] = [Drone() for _ in
                                   range(int(parsed_map["nb_drones"]))]
        self.zone: list[Zone] = [Zone(
            zone["name"], (zone["x"], zone["y"]), zone["metadata"])
                                 for zone in parsed_map["hubs"]]
        self.connections: list[Connection] = [Connection(conn)
                                              for conn in
                                              parsed_map["connections"]]

    def representation(self) -> dict[str, list[str]]:
        """Creating a graph representation based on connection

        Returns:
            dict[str, list[str]]: dict of adjacency list
                                 representation of the graph
        """
        adjacency_list: dict[str, list[str]] = {}

        for connection in self.connections:
            if connection.start not in adjacency_list:
                adjacency_list[connection.start] = []
            if connection.end not in adjacency_list:
                adjacency_list[connection.end] = []

            adjacency_list[connection.start].append(connection.end)
            adjacency_list[connection.end].append(connection.start)

        return adjacency_list
