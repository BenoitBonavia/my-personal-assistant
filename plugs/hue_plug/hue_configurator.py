"""Configurator for adding new Philips Hue lights to the existing configuration."""
from __future__ import annotations

import logging
from typing import Dict, List

from phue import Bridge

from plugs.parent_configurator import ParentConfigurator

logger = logging.getLogger(__name__)


class HueConfigurator(ParentConfigurator):
    """Interactive configurator used to register new Hue lights."""

    def __init__(self, config_file: str = "plugs/hue_plug/hue_configuration.json") -> None:
        super().__init__(config_file)
        self.config.setdefault("hue_lights", [])

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

        self.configured_lights.append(new_light_entry)
        print(f"Light {light_id} configured as '{name}' in room '{room}'.")

    def _start_blinking(self, light_id: str) -> None:
        try:
            self.bridge.set_light(int(light_id), "alert", "lselect")
        except Exception:  # pragma: no cover - depends on hardware
            logger.exception("Unable to start blinking for light %s", light_id)

    def _stop_blinking(self, light_id: str) -> None:
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
        if not rooms:
            raise ValueError("No existing rooms found in the configuration. Cannot proceed.")

        print("Available rooms:")
        for index, room in enumerate(rooms, start=1):
            print(f"  {index}. {room}")

        while True:
            choice = input("Select the room by entering its number: ").strip()
            if choice.isdigit():
                index = int(choice)
                if 1 <= index <= len(rooms):
                    return rooms[index - 1]
            print("Invalid selection. Please choose one of the listed room numbers.")

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


if __name__ == "__main__":
    configurator = HueConfigurator()
    configurator.run()
