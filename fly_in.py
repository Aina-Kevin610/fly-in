import sys
from parsing import Parser, ParseError
from utils import Graph, GraphError
from shortest_path import Pathfinding


def main() -> None:
    print("=== FLY-IN ===")
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        # print(parsed_map)
        graph = Graph(parsed_map).representation()
        p = Pathfinding(graph)
        p.resolve("start")
        
    except (ParseError, GraphError) as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
