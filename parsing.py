import re
import sys
from typing import Any


class ParseError(ValueError):
    """Raised when a map file does not match the expected Fly-in format."""


class Parser:
    """Parse and validate a Fly-in map file."""

    VALID_ZONE_TYPES = {"normal", "blocked", "restricted", "priority"}
    ZONE_METADATA_KEYS = {"zone", "color", "max_drones"}
    CONNECTION_METADATA_KEYS = {"max_link_capacity"}

    def __init__(self, filename: str) -> None:
        self.filename = filename
        self.lines = self._read_file()
        self.cleaned_lines = self._remove_comments()
        self.parsed: dict[str, Any] = {}

    def _read_file(self) -> list[str]:
        """Read the map file line by line."""
        with open(self.filename, "r") as file:
            return file.read().splitlines()

    def _remove_comments(self) -> list[str]:
        """Remove comments starting with '#', keeping the remaining lines."""
        cleaned: list[str] = []
        for line in self.lines:
            without_comment = re.sub(r"\s*#.*$", "", line)
            if without_comment.strip():
                cleaned.append(without_comment.strip())
        return cleaned

    def parse_metadata(
        self,
        metadata_block: str,
        allowed_keys: set[str],
        context: str,
    ) -> dict[str, str | int]:
        """Parse a metadata block like [zone=normal color=red max_drones=2]."""
        if not metadata_block.strip():
            return {}

        metadata: dict[str, str | int] = {}
        for item in metadata_block.split():
            if "=" not in item:
                raise ParseError(f"{context} metadata is invalid: '{item}'")
            key, value = item.split("=", 1)
            key_name = key.lower()
            if key_name not in allowed_keys:
                raise ParseError(f"{context} metadata key is invalid: '{key_name}'")
            if key_name in metadata:
                raise ParseError(f"{context} metadata key is duplicated: '{key_name}'")
            if key_name == "zone":
                zone_type = value.lower()
                if zone_type not in self.VALID_ZONE_TYPES:
                    raise ParseError(
                        f"{context} zone type is invalid: '{value}'"
                    )
                metadata[key_name] = zone_type
            elif key_name in {"max_drones", "max_link_capacity"}:
                if not re.fullmatch(r"\d+", value):
                    raise ParseError(
                        f"{context} capacity must be a positive integer: '{value}'"
                    )
                capacity = int(value)
                if capacity <= 0:
                    raise ParseError(
                        f"{context} capacity must be strictly positive: '{value}'"
                    )
                metadata[key_name] = capacity
            else:
                if not re.fullmatch(r"[^\s-]+", value):
                    raise ParseError(
                        f"{context} color value is invalid: '{value}'"
                    )
                metadata[key_name] = value
        return metadata

    def _parse_hub_line(self, line: str, line_number: int) -> dict[str, Any]:
        """Parse a zone definition line."""
        pattern = re.compile(
            r"^\s*(hub|start_hub|end_hub)\s*:\s*([^\s-]+)\s+(-?\d+)\s+(-?\d+)"
            r"(?:\s*\[(.*)\])?\s*$",
            re.IGNORECASE,
        )
        match = pattern.fullmatch(line)
        if match is None:
            raise ParseError(f"Line {line_number}: invalid hub declaration")

        kind, name, x_text, y_text, metadata_block = match.groups()
        kind = kind.lower()
        x_value = int(x_text)
        y_value = int(y_text)

        metadata = self.parse_metadata(
            metadata_block or "",
            self.ZONE_METADATA_KEYS,
            f"{kind} '{name}'",
        )

        clean_metadata: dict[str, str | int] = {
            "zone": metadata.get("zone", "normal"),
            "color": metadata.get("color", "none"),
            "max_drones": metadata.get("max_drones", 1),
        }

        if kind in {"start_hub", "end_hub"}:
            clean_metadata["max_drones"] = 1

        return {
            "type": kind,
            "name": name,
            "x": x_value,
            "y": y_value,
            "metadata": clean_metadata,
        }

    def _parse_connection_line(self, line: str, line_number: int) -> dict[str, Any]:
        """Parse a connection definition line."""
        pattern = re.compile(
            r"^\s*connection\s*:\s*([^\s-]+)-([^\s-]+)"
            r"(?:\s*\[(.*)\])?\s*$",
            re.IGNORECASE,
        )
        match = pattern.fullmatch(line)
        if match is None:
            raise ParseError(f"Line {line_number}: invalid connection declaration")

        left_name, right_name, metadata_block = match.groups()
        metadata = self.parse_metadata(
            metadata_block or "",
            self.CONNECTION_METADATA_KEYS,
            f"connection '{left_name}-{right_name}'",
        )

        return {
            "start": left_name,
            "end": right_name,
            "max_link_capacity": metadata.get("max_link_capacity", 1),
        }

    def parse(self) -> dict[str, Any]:
        """Parse and validate the entire map file."""
        if not self.cleaned_lines:
            raise ParseError("Empty map file")

        first_line = self.cleaned_lines[0]
        first_match = re.fullmatch(r"\s*nb_drones\s*:\s*(\d+)\s*", first_line, re.IGNORECASE)
        if first_match is None:
            raise ParseError("Line 1: invalid nb_drones declaration")
        nb_drones = int(first_match.group(1))
        if nb_drones <= 0:
            raise ParseError("Line 1: the number of drones must be a positive integer")

        hubs: list[dict[str, Any]] = []
        connections: list[dict[str, Any]] = []
        seen_hub_names: set[str] = set()
        seen_connections: set[tuple[str, str]] = set()
        for line_number, line in enumerate(self.cleaned_lines[1:], start=2):
            if re.match(r"\s*(hub|start_hub|end_hub)\s*:\s*", line, re.IGNORECASE):
                parsed_hub = self._parse_hub_line(line, line_number)
                hub_name = parsed_hub["name"]
                if hub_name in seen_hub_names:
                    raise ParseError(f"Line {line_number}: duplicate hub name '{hub_name}'")
                seen_hub_names.add(hub_name)
                hubs.append(parsed_hub)
                continue

            if re.match(r"\s*connection\s*:", line, re.IGNORECASE):
                parsed_connection = self._parse_connection_line(line, line_number)
                start_name = parsed_connection["start"]
                end_name = parsed_connection["end"]
                if start_name == end_name:
                    raise ParseError(
                        f"Line {line_number}: a connection cannot link a hub to itself"
                    )
                normalized = tuple(sorted((start_name, end_name)))
                if normalized in seen_connections:
                    raise ParseError(
                        f"Line {line_number}: duplicate connection '{start_name}-{end_name}'"
                    )
                seen_connections.add(normalized)
                connections.append(parsed_connection)
                continue
            raise ParseError(f"Line {line_number}: unknown instruction type")

        if not any(hub["type"] == "start_hub" for hub in hubs):
            raise ParseError("A start_hub is required")
        if not any(hub["type"] == "end_hub" for hub in hubs):
            raise ParseError("An end_hub is required")
        if sum(1 for hub in hubs if hub["type"] == "start_hub") != 1:
            raise ParseError("There must be exactly one start_hub")
        if sum(1 for hub in hubs if hub["type"] == "end_hub") != 1:
            raise ParseError("There must be exactly one end_hub")

        hub_by_name = {hub["name"]: hub for hub in hubs}
        for connection in connections:
            if connection["start"] not in hub_by_name:
                raise ParseError(
                    f"Connection '{connection['start']}-{connection['end']}' uses an unknown hub name"
                )
            if connection["end"] not in hub_by_name:
                raise ParseError(
                    f"Connection '{connection['start']}-{connection['end']}' uses an unknown hub name"
                )

        self.parsed = {
            "nb_drones": nb_drones,
            "hubs": hubs,
            "connections": connections,
            "start": next(hub["name"] for hub in hubs if hub["type"] == "start_hub"),
            "end": next(hub["name"] for hub in hubs if hub["type"] == "end_hub"),
        }
        return self.parsed


Paser = Parser


if __name__ == "__main__":
    file_to_parse = sys.argv[1] if len(sys.argv) > 1 else "parsing/map.txt"
    try:
        parser = Parser(file_to_parse)
        parsed_map = parser.parse()
        print(parsed_map)
    except ParseError as e:
        print(f"Error: {e}")
        raise SystemExit(1)