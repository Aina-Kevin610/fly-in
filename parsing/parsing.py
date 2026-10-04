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
        self.parsed: dict[str, int | str] = {}
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
        nb_drones = re.fullmatch(r"\s*nb_drones\s*:\s*\d+", self.no_comment[0], re.IGNORECASE)
        if not nb_drones:
            return False
        self.parsed["nb_drones"] = nb_drones.group().split(":")[1].strip()
        
        return True

             

if __name__ == "__main__":
    parse = Paser("map.txt")
    print(parse.parsed)