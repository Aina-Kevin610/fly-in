class Drone:
    def __init__(self):
        self.position = (0, 0)


class Zone:
    def __init__(self, name: str, positions: tuple[int, int], metadata: dict[str, str | int]):
        self.name = name
        self.x1 = positions[0]
        self.y1 = positions[1]
        self.color = metadata["color"]
        self.type = metadata["type"]
        self.max_drones = metadata["max_drones"]