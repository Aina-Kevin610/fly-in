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
        self.lines = self.read_file()
        self.no_comment = self.remove_comment()

    def read_file(self) -> list[str]:
        """this function that read the filename

        Returns:
            str: the content of self.filename
        """
        content = ""

        with open(self.filename, "r") as f:
            content = f.read().splitlines()
        return content

    def remove_comment(self) -> list[str]:
        result: list[str] = []
        for line in self.lines:
            result.append(re.sub(r"\s*#.*$", "", line))
        return [x for x in result if x != ""]
             

if __name__ == "__main__":
    print(Paser("map.txt").no_comment)