import sys
from parsing import Parser
from utils import Graph
from shortest_path import Pathfinding
from pprint import pprint


def main() -> None:
    print("=== FLY-IN ===")
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        graph = Graph(parsed_map)
        p = Pathfinding(graph)
        for drone_id in range(p.drone_count):
            p.resolve("start", drone_id)
            p.get_shortest_path("goal")
        pprint([p.drone_schedules[drone_id]
                for drone_id in range(p.drone_count)])

    except Exception as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
