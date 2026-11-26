import sys
from parsing import Parser
from utils import Graph
from shortest_path import PathFinding
from pprint import pprint


def main() -> None:
    print("=== FLY-IN ===")
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        graph = Graph(parsed_map)
        # pprint(graph.representation())
        # print(type({isinstance(str, x.name):[z.name for z in y] for x, y in graph.representation().items()}["start"][0]))
        # for x in graph.representation():
        #     print(x.name, end="")
        #     print([a.name for a in x.values()])
        # print(p.not_visited)

        p = PathFinding(graph)

        p.resolve("start")
        print([x.distance for x in graph.zone])

    except ValueError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
