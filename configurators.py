"""Interactive launcher for plug configurators."""
from __future__ import annotations

import importlib
from dataclasses import dataclass
from pathlib import Path
from typing import Callable, List, Sequence


REPO_ROOT = Path(__file__).resolve().parent
PLUGS_DIR = REPO_ROOT / "plugs"


@dataclass(frozen=True)
class ConfiguratorEntry:
    display_name: str
    module_name: str
    file_path: Path


def discover_configurators() -> List[ConfiguratorEntry]:
    """Return configurator modules found under plugs/*/*_configurator.py."""
    if not PLUGS_DIR.exists():
        return []

    entries: List[ConfiguratorEntry] = []
    for package_dir in sorted(PLUGS_DIR.iterdir()):
        if not package_dir.is_dir() or not (package_dir / "__init__.py").exists():
            continue

        for cfg_file in sorted(package_dir.glob("*_configurator.py")):
            module_name = f"plugs.{package_dir.name}.{cfg_file.stem}"
            base_name = cfg_file.stem.replace("_configurator", "").replace("_", " ").strip() or cfg_file.stem
            display_name = base_name.title()
            entries.append(ConfiguratorEntry(display_name, module_name, cfg_file))

    return entries


def prompt_user(entries: Sequence[ConfiguratorEntry]) -> ConfiguratorEntry | None:
    """Display configurators and return the selected entry (or None to exit)."""
    if not entries:
        print("No configurators found in plug packages.")
        return None

    print("Available configurators:")
    for idx, entry in enumerate(entries, start=1):
        print(f"  {idx}. {entry.display_name} ({entry.module_name})")
    print("  q. Quit")

    while True:
        choice = input("Select a configurator to launch: ").strip().lower()
        if choice in {"q", "quit", ""}:
            return None
        if choice.isdigit():
            index = int(choice)
            if 1 <= index <= len(entries):
                return entries[index - 1]
        print("Invalid selection. Enter a number from the list or 'q' to quit.")


def load_main_callable(entry: ConfiguratorEntry) -> Callable[[], None]:
    """Import the configurator module and fetch its main() callable."""
    module = importlib.import_module(entry.module_name)
    main_callable = getattr(module, "main", None)
    if not callable(main_callable):
        raise AttributeError(f"{entry.module_name} does not expose a callable main()")
    return main_callable


def run_configurator(entry: ConfiguratorEntry) -> None:
    """Execute the selected configurator."""
    try:
        main_callable = load_main_callable(entry)
    except Exception as exc:  # pragma: no cover - interactive runner
        print(f"Unable to load configurator '{entry.display_name}': {exc}")
        return

    print(f"Starting configurator '{entry.display_name}'...\n")
    main_callable()


def main() -> None:
    """Entry point for launching configurators from the command line."""
    entries = discover_configurators()
    selection = prompt_user(entries)
    if selection is None:
        print("No configurator selected. Exiting.")
        return
    run_configurator(selection)


if __name__ == "__main__":
    main()
