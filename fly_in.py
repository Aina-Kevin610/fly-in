import sys
from parsing import Parser
from utils import Graph
from shortest_path import Pathfinding


def main() -> None:
    print("=== FLY-IN ===")
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        graph = Graph(parsed_map)
        p = Pathfinding(graph)
        p.resolve("start")
        print([x.name for x in p.get_shortest_path("goal")])
        
    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
    
