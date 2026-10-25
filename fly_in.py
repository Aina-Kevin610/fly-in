import sys
from parsing import Parser, ParseError
from utils import Graph

def main() -> None:
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        graph = Graph(parsed_map)
        graph.representation()
        
        
    except ParseError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()