import sys
from parsing import Parser, ParseError
from utils import Drone, Zone, Connection, Graph

def main() -> None:
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        drone_list = [Drone() for _ in range(int(parsed_map["nb_drones"]))]
        
        print(drone_list)
        
    except ParseError as e:
        print(f"Error: {e}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()