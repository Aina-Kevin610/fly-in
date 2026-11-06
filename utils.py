from typing import Any


class GraphError(Exception):
    """Personal Exception done for all graph error

    Args:
        Exception (_type_): the built-in Exception class
    """
    def __init__(self, *args: str):
        """constructor"""
        super().__init__(*args)


class Drone:
    """class for one drone"""

    def __init__(self) -> None:
        """Initialize a Drone object."""
        self.x = 0
        self.y = 0
        self.state: bool = False
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
        self.priority = 0 if self.type == "priority" else 1
        self.max_drones = metadata["max_drones"]
        self.status: list[int] = []


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

    def representation(self) -> dict[Zone, list[Zone]]:
        """Creating a graph representation based on connection
        and removing all blocked zone

        Returns:
            dict[Zone, list[Zone]]: dict of adjacency list
                                 representation of the graph
        """
        adjacency_list: dict[Zone, list[Zone]] = {}
        zone_by_name: dict[str, Zone] = {zone.name: zone for zone in self.zone}

        for connection in self.connections:
            start_zone = zone_by_name.get(connection.start)
            end_zone = zone_by_name.get(connection.end)
            if start_zone is None or end_zone is None:
                continue

            if start_zone not in adjacency_list:
                adjacency_list[start_zone] = []
            if end_zone not in adjacency_list:
                adjacency_list[end_zone] = []

            adjacency_list[start_zone].append(end_zone)
            adjacency_list[end_zone].append(start_zone)

        for hub in self.zone:
            if hub.type == "blocked":
                for neighbors in adjacency_list.values():
                    if hub in neighbors:
                        neighbors.remove(hub)
                adjacency_list.pop(hub, None)

        start_zone = zone_by_name.get("start")
        goal_zone = zone_by_name.get("goal")
        if start_zone is None or goal_zone is None:
            raise GraphError("Inaccessible mandatory zone")
        if not adjacency_list.get(start_zone) or not adjacency_list.get(goal_zone):
            raise GraphError("Inaccessible mandatory zone")
        return adjacency_list
