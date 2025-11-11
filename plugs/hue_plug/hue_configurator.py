"""Configurator for adding new Philips Hue lights to the existing configuration."""
from __future__ import annotations

import logging
import threading
from typing import Dict, List, Tuple
from pathlib import Path

from phue import Bridge

from plugs.parent_configurator import ParentConfigurator

logger = logging.getLogger(__name__)


class HueConfigurator(ParentConfigurator):
    def __init__(self, config_file: str = "hue_configuration.json") -> None:
        # Resolve the config path relative to this file so it works regardless of the current working directory
        if not config_file or config_file == "hue_configuration.json":
            config_file = str(Path(__file__).with_name("hue_configuration.json"))
        super().__init__(config_file)
        self.config.setdefault("hue_lights", [])
        self._blinking_threads: Dict[str, Tuple[threading.Event, threading.Thread]] = {}

        bridge_ip = self.config.get("bridge_ip")
        if not bridge_ip:
            raise ValueError("The Hue configuration must define a 'bridge_ip'.")

        self.bridge = Bridge(bridge_ip)
        self.bridge.connect()

    @property
    def configured_lights(self) -> List[Dict]:
        """Return the list of already configured lights."""
        return self.config.get("hue_lights", [])

    def run(self) -> None:
        """Launch the interactive configuration flow."""
        non_configured = self._get_non_configured_lights()
        if not non_configured:
            print("All detected lights are already configured.")
            return

        for light in non_configured:
            self._configure_light(light)

        self.save_config_in_file()

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------
    def _get_non_configured_lights(self):
        ids = {str(light["id"]) for light in self.configured_lights}
        available_lights = self.bridge.lights
        non_configured_lights = [light for light in available_lights if str(light.light_id) not in ids]

        if non_configured_lights:
            non_configured_ids = [light.light_id for light in non_configured_lights]
            logger.info("Found %d non configured lights: %s", len(non_configured_ids), non_configured_ids)
        else:
            logger.info("No non configured lights detected.")

        return non_configured_lights

    def _configure_light(self, light) -> None:
        light_id = str(light.light_id)
        print("\nConfiguring light", light_id)
        print(f"Current Hue name: {light.name}")

        self._start_blinking(light_id)
        try:
            name = self._prompt_light_name(light.name)
            room = self._prompt_room()
            paired = self._prompt_paired(light_id)
        finally:
            self._stop_blinking(light_id)

        new_light_entry = {
            "id": light_id,
            "name": name,
            "room": room,
        }

        if paired:
            new_light_entry["paired"] = paired
            self._ensure_bidirectional_pairing(light_id, paired)

        self.configured_lights.append(new_light_entry)
        print(f"Light {light_id} configured as '{name}' in room '{room}'.")

    def _start_blinking(self, light_id: str) -> None:
        if light_id in self._blinking_threads:
            return

        stop_event = threading.Event()

        def _blink_loop() -> None:
            while not stop_event.is_set():
                try:
                    self.bridge.set_light(int(light_id), "alert", "lselect")
                except Exception:  # pragma: no cover - depends on hardware
                    logger.exception("Unable to trigger blinking for light %s", light_id)
                    break
                stop_event.wait(10)

        thread = threading.Thread(target=_blink_loop, name=f"hue-blink-{light_id}", daemon=True)
        self._blinking_threads[light_id] = (stop_event, thread)
        thread.start()

    def _stop_blinking(self, light_id: str) -> None:
        stop_event, thread = self._blinking_threads.pop(light_id, (None, None))

        if stop_event is not None:
            stop_event.set()
        if thread is not None:
            thread.join(timeout=2)

        try:
            self.bridge.set_light(int(light_id), "alert", "none")
        except Exception:  # pragma: no cover - depends on hardware
            logger.exception("Unable to stop blinking for light %s", light_id)

    def _prompt_light_name(self, default_name: str) -> str:
        while True:
            user_input = input(f"Enter a name for the light (default: {default_name}): ").strip()
            if not user_input:
                return default_name
            return user_input

    def _prompt_room(self) -> str:
        rooms = sorted({light["room"] for light in self.configured_lights if "room" in light})

        if rooms:
            print("Available rooms:")
            for index, room in enumerate(rooms, start=1):
                print(f"  {index}. {room}")
            print(f"  {len(rooms) + 1}. Add a new room")

            while True:
                choice = input("Select the room by entering its number: ").strip()
                if choice.isdigit():
                    index = int(choice)
                    if 1 <= index <= len(rooms):
                        return rooms[index - 1]
                    if index == len(rooms) + 1:
                        return self._prompt_new_room_name()
                print("Invalid selection. Please choose one of the listed options.")

        print("No rooms found in the configuration. Please enter a new room name.")
        return self._prompt_new_room_name()

    def _prompt_new_room_name(self) -> str:
        while True:
            room_name = input("Enter the name of the new room: ").strip()
            if room_name:
                return room_name
            print("Room name cannot be empty. Please try again.")

    def _prompt_paired(self, current_light_id: str) -> List[int]:
        options = {
            str(light["id"]): light["name"]
            for light in self.configured_lights
            if str(light.get("id")) != current_light_id
        }

        if not options:
            print("No other configured lights available for pairing.")
            return []

        print("Available lights for pairing:")
        for light_id, name in options.items():
            print(f"  {light_id}: {name}")

        while True:
            raw_selection = input(
                "Enter the IDs of the lights to pair with (comma separated, leave empty for none): "
            ).strip()

            if not raw_selection:
                return []

            selected_ids = [value.strip() for value in raw_selection.split(",") if value.strip()]
            invalid_ids = [value for value in selected_ids if value not in options]
            if invalid_ids:
                print(f"Unknown light IDs: {', '.join(invalid_ids)}. Please try again.")
                continue

            unique_ids = list(dict.fromkeys(selected_ids))
            return [int(light_id) for light_id in unique_ids]

    def _ensure_bidirectional_pairing(self, current_light_id: str, paired_ids: List[int]) -> None:
        """Update configured lights so pairing relationships are symmetrical."""
        current_id_int = int(current_light_id)

        for paired_id in paired_ids:
            paired_id_str = str(paired_id)
            for light in self.configured_lights:
                if str(light.get("id")) != paired_id_str:
                    continue

                peers = light.setdefault("paired", [])
                if current_id_int not in peers:
                    peers.append(current_id_int)
                break
            else:
                logger.warning(
                    "Configured light %s references unknown paired id %s",
                    current_light_id,
                    paired_id_str,
                )


def main() -> None:
    """Entry point used by the configurator launcher."""
    configurator = HueConfigurator()
    configurator.run()


if __name__ == "__main__":
    main()
