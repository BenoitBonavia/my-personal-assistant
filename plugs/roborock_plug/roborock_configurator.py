"""Interactive configurator for Roborock rooms using python-miio."""
from __future__ import annotations

from pathlib import Path
from typing import Dict, Iterable, List

from plugs.parent_configurator import ParentConfigurator

try:  # pragma: no cover - optional dependency during tests
    from miio import RoborockVacuum
except ImportError:  # pragma: no cover - optional dependency during tests
    RoborockVacuum = None


class RoborockConfigurator(ParentConfigurator):
    """Fetch the segment map from the vacuum and sync it with the config file."""

    def __init__(self, config_file: str = "roborock_configuration.json") -> None:
        if not config_file or config_file == "roborock_configuration.json":
            config_file = str(Path(__file__).with_name("roborock_configuration.json"))
        super().__init__(config_file)

        self.config.setdefault("rooms", [])
        self.ip = self.config.get("ip")
        self.token = self.config.get("token")

        if not self.ip or not self.token:
            raise ValueError("The Roborock configuration must define both 'ip' and 'token'.")
        if RoborockVacuum is None:
            raise RuntimeError(
                "python-miio is required to communicate with the vacuum. "
                "Install the dependency or run inside the configured environment."
            )

        self.vacuum: RoborockVacuum | None = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------
    @property
    def configured_rooms(self) -> List[Dict]:
        return self.config.get("rooms", [])

    def run(self) -> None:
        """Launch the interactive synchronization flow."""
        available_rooms = self._get_rooms_from_map()
        if not available_rooms:
            print("The vacuum did not report any rooms on its current map.")
            return

        known_ids = {int(room["id"]) for room in self.configured_rooms if "id" in room}
        rooms_to_configure = [room for room in available_rooms if int(room["id"]) not in known_ids]

        if not rooms_to_configure:
            print("Every room exposed by the vacuum is already configured.")
            return

        for room in rooms_to_configure:
            if not self._prompt_add_room(room):
                continue
            name = self._prompt_room_name(room["name"])
            entry = {"id": int(room["id"]), "name": name}
            self.configured_rooms.append(entry)
            print(f"Added room {entry['id']} as '{entry['name']}'.")

        self.save_config_in_file()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_rooms_from_map(self) -> List[Dict[str, str]]:
        while True:
            try:
                vacuum = self._ensure_vacuum()
                try:
                    mapping = vacuum.get_room_mapping()
                except AttributeError:
                    mapping = vacuum.send("get_room_mapping")
            except Exception as exc:  # pragma: no cover - requires hardware
                if not self._handle_connection_failure(exc):
                    raise SystemExit("Configuration aborted by user.") from exc
                continue

            rooms = self._normalize_mapping(mapping)
            rooms.sort(key=lambda item: int(item["id"]))
            return rooms

    def _ensure_vacuum(self) -> RoborockVacuum:
        if self.vacuum is None:
            self.vacuum = RoborockVacuum(self.ip, self.token)
        return self.vacuum

    def _normalize_mapping(self, mapping: object) -> List[Dict[str, str]]:
        if mapping is None:
            return []

        if hasattr(mapping, "rooms"):
            raw_rooms: Iterable = getattr(mapping, "rooms")
        elif isinstance(mapping, dict):
            raw_rooms = mapping.get("rooms") or mapping.get("room_mapping") or [mapping]
        elif isinstance(mapping, (list, tuple, set)):
            raw_rooms = mapping
        else:
            raw_rooms = [mapping]

        normalized: List[Dict[str, str]] = []
        for room in raw_rooms:
            room_id = self._extract_value(room, ("id", "room_id", "roomId"))
            if room_id is None:
                continue
            name = self._extract_value(
                room,
                ("name", "room_name", "user_room_name", "default_name"),
            )
            normalized.append({
                "id": int(room_id),
                "name": (name or f"Room {room_id}").strip(),
            })
        return normalized

    def _handle_connection_failure(self, exc: Exception) -> bool:
        print(f"Unable to communicate with the vacuum: {exc}")
        print("Choose an option: [r]etry, [e]dit connection settings, [q]uit")

        while True:
            choice = input("Your choice [r/e/q]: ").strip().lower()
            if choice in {"", "r", "retry"}:
                return True
            if choice in {"e", "edit"}:
                self._prompt_connection_settings()
                return True
            if choice in {"q", "quit"}:
                return False
            print("Invalid selection. Please enter 'r', 'e', or 'q'.")

    def _prompt_connection_settings(self) -> None:
        print("\nUpdate the Roborock connection settings. Leave blank to keep the current value.")
        new_ip = input(f"Vacuum IP [{self.ip}]: ").strip() or self.ip
        new_token = input(f"Vacuum token [{self.token}]: ").strip() or self.token

        if new_ip == self.ip and new_token == self.token:
            print("Connection settings unchanged.")
            return

        self.ip = new_ip
        self.token = new_token
        self.config["ip"] = new_ip
        self.config["token"] = new_token
        self.vacuum = None
        self.save_config_in_file()

    @staticmethod
    def _extract_value(source: object, attribute_names: Iterable[str]):
        for attribute in attribute_names:
            if isinstance(source, dict) and attribute in source:
                return source[attribute]
            if hasattr(source, attribute):
                return getattr(source, attribute)
        return None

    def _prompt_add_room(self, room: Dict[str, str]) -> bool:
        prompt = f"Add room '{room['name']}' (ID {room['id']})? [Y/n/q]: "
        while True:
            choice = input(prompt).strip().lower()
            if choice in {"", "y", "yes"}:
                return True
            if choice in {"n", "no"}:
                return False
            if choice in {"q", "quit"}:
                raise SystemExit("Configuration aborted by user.")
            print("Invalid choice. Please answer with 'y', 'n', or 'q'.")

    def _prompt_room_name(self, default_name: str) -> str:
        while True:
            user_input = input(f"Enter a name for the room (default: {default_name}): ").strip()
            if not user_input:
                return default_name
            return user_input


def main() -> None:
    configurator = RoborockConfigurator()
    configurator.run()


if __name__ == "__main__":
    main()
