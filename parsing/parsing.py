import pprint
import re


class ParseError(Exception):
    """A specific error, raised when a parsing error occure

    Args:
        Exception (Exception): A buil-in class that ParseError inherit
    """

    def __init__(self, messages: str) -> None:
        """constructor function

        Args:
            messages (str): Message shown to specify the error
        """
        super().__init__(messages)


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
        self.parsed: dict[str, int | str | list[dict[str, str]]] = {}
        self.lines = self.read_file()
        self.no_comment = self.remove_comment()
        self.check = False
        self.hub_name: list[str] = []

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

    def check_pattern(self) -> None:
        """function that check only if the pattern
        of the file is set as excpected

        Raises:
            ParseError: raise exception when number of drone's pattern is wrong
            ParseError: raise exception when number of hubs and connection not equal to len(self.no_comment)
            ParseError: raise exception when any hub's pattern is wrong
            ParseError: raise exception when any connection's pattern is wrong
        """
        nb_drones = re.fullmatch(r"\s*nb_drones\s*:\s*\d+",
                                self.no_comment[0],
                                re.IGNORECASE
                                )
        if not nb_drones:
            raise ParseError("INVALID NUMBER OF DRONES FORMAT")
        self.parsed["nb_drones"] = nb_drones.group().split(":")[1].strip()

        body = self.no_comment[1:]
        nb_hubs = sum(1 for line in body if re.match(
            r"\s*(hub|start_hub|end_hub)\s*:", line, re.IGNORECASE))
        nb_conns = sum(1 for line in body if re.match(
            r"\s*connection\s*:", line, re.IGNORECASE))
        if nb_hubs + nb_conns != len(body):
            raise ParseError("UNKNOWN LINE TYPE")

        for data in body[:nb_hubs]:
            pattern = re.fullmatch(r"\s*(hub|start_hub|end_hub)\s*:"
                                r"\s*[^\s-$]+\s+[+-]?\d+\s+[+-]?\d+"
                                r"(?:\s*\[(?:\s*\w+=\w+\s*){1,3}\])?"
                                r"\s*",
                                data, re.IGNORECASE
                                )
            if not pattern:
                raise ParseError("INVALID HUBS FORMAT")

        for data in body[nb_hubs:]:
            pattern = re.fullmatch(r"\s*connection\s*:"
                                r"\s*\w+-\s*\w+"
                                r"(?:\s*\[(?:\s*\w+=\w+\s*){1,3}\])?",
                                data, re.IGNORECASE
                                )
            if not pattern:
                raise ParseError("INVALID CONNECTIONS FORMAT")
        self.check = True


    def to_dict(self) -> None:
        """transform a list containing the map line by line to a dict
        nothing verified yet. And update self.parsed
        """
        if self.check_pattern == False:
            return
        self.parsed["nb_drones"] = self.no_comment[0].split(":")[1]
        hubs: list[dict[str, str]] = []
        body = self.no_comment[1:]
        nb_hubs = sum(1 for line in body if re.match(
            r"\s*(hub|start_hub|end_hub)\s*:", line, re.IGNORECASE))
        nb_conns = sum(1 for line in body if re.match(
            r"\s*connection\s*:", line, re.IGNORECASE))
        for hub in body[:nb_hubs]:
            default_metadata = ["zone=normal", "max_drones=1", "color=none"]
            parts = hub.split(" ", 4)
            hubs.append({
                "name": parts[1],
                "x": parts[2],
                "y": parts[3],
                "metadata": parts[4].replace("[", "").replace("]", "").split() if len(parts) > 4 else default_metadata,
            })
            self.hub_name.append(parts[1])
        self.parsed["hubs"] = hubs
        conns: list[dict[str, str]] = []
        for conn in body[nb_hubs + 1:]:
            default_metadata = "max_link_capacity=1"
            parts = conn.split(" ", 2)
            start, end = parts[1].split("-", 1)
            conns.append({
                "start": start,
                "end": end,
                "metadata": parts[2].replace("[", "").replace("]", "") if len(parts) > 2 else default_metadata,
            })
        self.parsed["connections"] = conns


    def validate(self):
        self.to_dict()
        zone_type = ["normal", "blocked", "restricted", "priority"]
        color = ["red", "green"]
        if "start" not in self.hub_name or "goal" not in self.hub_name:
            raise ParseError("Start hub or End_hub not valid")
        position = [(d["x"], d["y"]) for d in self.parsed["hubs"]]
        if len(position) != len(set(position)):
            raise ParseError("Coordinates are not valid")
        missing_name = [x for x in self.parsed["connections"] if x["start"] not in self.hub_name or x["end"] not in self.hub_name]
        if len(missing_name) > 0:
            raise ParseError("Unknown name found on connection")

        body = self.no_comment[1:]
        nb_hubs = sum(1 for line in body if re.match(
            r"\s*(hub|start_hub|end_hub)\s*:", line, re.IGNORECASE))
        nb_conns = sum(1 for line in body if re.match(
            r"\s*connection\s*:", line, re.IGNORECASE))
        for hub in body[:nb_hubs]:
            for data in hub["metadata"]:
                k, v = data.split("=")
                if (k.lower() == "color" and v.lower() not in color) or (k.lower() == "zone" and v.lower() not in zone_type) or (k.lower() == "max_drones" and int(v)):
                    raise ParseError("Metadata error")
                else:
                    raise ParseError("Unknown Metadata")

        pprint.pprint(self.parsed, indent=2)


if __name__ == "__main__":
    try:
        parse = Paser("map.txt")
        parse.validate()
        print(parse.hub_name)
    except ParseError as e:
        print(f"Error - ", e)