import re

class Paser:
    """
    class that parse the map file
    """
    def __init__(self, filename: str) -> None:
        """constructor function

        Args:
            filename (str): name of the file containing the map
        """
        self.filename = filename
        self.parsed: dict[str, int | str | list[str | None]] = {}
        self.lines = self.read_file()
        self.no_comment = self.remove_comment()
        self.nb_drones = self.check_pattern()

    def read_file(self) -> list[str]:
        """this function that read the filename

        Returns:
            list[str]: list of the content of self.filename
        """
        content = ""

        with open(self.filename, "r") as f:
            content = f.read().splitlines()
        return content

    def remove_comment(self) -> list[str]:
        """this function set all charachter after '#' as ""

        Returns:
            list[str]: list of string that comments are ignored
        """
        result: list[str] = []
        for line in self.lines:
            result.append(re.sub(r"\s*#.*$", "", line))
        return [x for x in result if x != ""]

    def check_pattern(self) -> bool:
        hubs: list[str | None] = []
        connections: list[str | None] = []
        nb_drones = re.fullmatch(r"\s*nb_drones\s*:\s*\d+", self.no_comment[0], re.IGNORECASE)
        if not nb_drones:
            return False
        self.parsed["nb_drones"] = nb_drones.group().split(":")[1].strip()
        for data in self.no_comment[1:]:
            meta_pattern = re.fullmatch(
                r"\s*(hub|start_hub|end_hub)\s*:"
                r"\s*[^-]+\s*[+-]?\d+\s+[+-]?\d+"
                r"\s*\[(?:\s*\w+=\w+\s*){1,3}\]",
                data, re.IGNORECASE
            )
            pattern = re.fullmatch(r"\s*(hub|start_hub|end_hub)\s*:\s*[^-]+\s*[+-]?\d+\s+[+-]?\d+", data, re.IGNORECASE)
            if meta_pattern:
                hubs.append(meta_pattern.group())
            elif pattern:
                hubs.append(pattern.group())
        self.parsed["hubs"] = hubs
        for data in self.no_comment[1:]:
            meta_pattern = re.match(r"\s*connection\s*:\s*\w+-\s*\w+\s*\[.*\]", data, re.IGNORECASE)
            pattern = re.match(r"\s*connection\s*:\s*\w+-\s*\w+", data, re.IGNORECASE)
            if meta_pattern:
                connections.append(meta_pattern.group())
            elif pattern:
                connections.append(pattern.group())
        self.parsed["connections"] = connections
        return True


if __name__ == "__main__":
    parse = Paser("map.txt")
    print(parse.parsed["nb_drones"])
    print(parse.parsed["hubs"])
    print(parse.parsed["connections"])
    # print(parse.nb_drones)