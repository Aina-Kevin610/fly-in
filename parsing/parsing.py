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
        self.parsed: dict[str, int | str | list[str | None]] = {}
        self.lines = self.read_file()
        self.no_comment = self.remove_comment()
        # self.nb_drones = self.check_pattern()

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
            meta_pattern = re.fullmatch(
                r"\s*(hub|start_hub|end_hub)\s*:"
                r"\s*[^-]+\s*[+-]?\d+\s+[+-]?\d+"
                r"\s*\[(?:\s*\w+=\w+\s*){1,3}\]",
                data, re.IGNORECASE
            )
            pattern = re.fullmatch(r"\s*(hub|start_hub|end_hub)\s*:"
                                r"\s*[^-]+\s*[+-]?\d+\s+[+-]?\d+",
                                data, re.IGNORECASE
                                )
            if not (meta_pattern or pattern):
                raise ParseError("INVALID HUBS FORMAT")

        for data in body[nb_hubs:]:
            meta_pattern = re.fullmatch(r"\s*connection\s*:"
                                        r"\s*\w+-\s*\w+\s*"
                                        r"\[(?:\s*\w+=\w+\s*){1,3}\]",
                                        data, re.IGNORECASE
                                        )
            pattern = re.fullmatch(r"\s*connection\s*:"
                                r"\s*\w+-\s*\w+",
                                data, re.IGNORECASE
                                )
            if not (meta_pattern or pattern):
                raise ParseError("INVALID CONNECTIONS FORMAT")


if __name__ == "__main__":
    try:
        parse = Paser("map.txt")
        print(parse.check_pattern())
    except ParseError as e:
        print(f"Error - ", e)