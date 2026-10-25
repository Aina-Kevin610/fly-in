from typing import Any

class Drone:
    """class for one drone"""

    def __init__(self) -> None:
        """Initialize a Drone object."""
        self.position = (0, 0)
        self.path: list[str] = []


class Zone:
    """class for one zone"""
    def __init__(self, name: str, positions: tuple[int, int], metadata: dict[str, str | int]) -> None:
        """Initialize a Zone object

        Args:
            name (str): name of the zone
            positions (tuple[int, int]): top-left and bottom-right coordinates of the zone
            metadata (dict[str, str  |  int]): additional information about the zone
        """
        self.name = name
        self.x1 = positions[0]
        self.y1 = positions[1]
        self.color = metadata["color"]
        self.type = metadata["type"]
        self.max_drones = metadata["max_drones"]


class Connection:
    """class for one connection"""
    def __init__(self, connection_data: dict[str, Any]) -> None:
        """Initialize a Connection object

        Args:
            connection_data (dict[str, Any]): dictionary containing connection information
        """
        self.start = connection_data["start"]
        self.end = connection_data["end"]
        self.max_link_capacity = connection_data["max_link_capacity"]


class Graph:
    """class for the graph"""
    def __init__(self) -> None:
        """Initialize a Graph object."""
        self.zones: list[Zone] = []
        self.connections: list[Connection] = []

    def _representation(self) -> None:
        # adjacency_list = {}
        zone_name: list["str"] = [x["name"] for x in self.zones]
        print(zone_name)