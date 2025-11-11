# Repository Guidelines

## Project Structure & Module Organization
`main.py` wires the speech recognizer, LLM routing, and speaker output; run in chat mode with `--chat` for quick manual loops. Configurable adapters ("plugs") sit under `plugs/`, each combining `<name>_manager.py`, `<name>_configurator.py`, and generated `<name>_documentation.json` for the LLM. Shared orchestration helpers (command parsing, logging, Sentry) live in `services/`, while concrete LLM drivers are grouped within `llm/`. Runtime logs go to `logs/`, and all assistant-wide settings (wake word, secrets, plug registry) live in `configuration.json`.

## Build, Test, and Development Commands
- `python -m venv .venv && source .venv/bin/activate`: standard virtualenv expected for local work.
- `pip install -r requirements.txt`: installs speech, Hue, Roborock, Home Assistant, and LLM SDK dependencies.
- `python main.py --chat`: text-only loop that exercises the full interpreter stack without microphone hardware.
- `python assistant_manager.py`: regenerates plug documentation JSON from manager docstrings when you add or rename plug commands.

## Coding Style & Naming Conventions
Follow PEP 8 with 4-space indents, single quotes for simple strings, and descriptive docstrings (triple quotes) that the documentation generator can parse. New plugs should mirror the existing pattern (`<device>_plug/<device>_manager.py`) and import from `plugs.parent_manager.ParentManager`. Keep configuration keys snake_case and align them with what managers expect (e.g., `manager_name`, `hue_lights`, `rooms`).

## Testing Guidelines
There is no committed automated suite yet; introduce targeted `pytest` modules under a future `tests/` directory, mirroring plug names (e.g., `tests/test_hue_manager.py`). Mock networked dependencies (Hue bridge, Home Assistant, Roborock) and use fixtures for `configuration.json` slices so tests stay deterministic. Run `pytest -q` locally before submitting; aim for coverage on new plug managers and configurators at a minimum.

## Commit & Pull Request Guidelines
Commits in the current history are short, imperative summaries (e.g., “Update config”). Match that tone and keep commits scoped to a single concern (new plug, config change, refactor). Pull requests should describe the scenario being automated, list impacted plugs/services, and call out any configuration migrations or new secrets. Link to relevant issues when possible and attach screenshots or console snippets for user-facing behavior changes.

## Security & Configuration Tips
Never commit personal tokens or bridge IPs; rely on `.env` plus `python-dotenv` and reference them inside `configuration.json` or plug configurators. Treat `logs/` as ephemeral and scrub it before sharing traces. When debugging new plugs, prefer synthetic configurations checked into `plugs/<name>_plug/sample_config.json` so other contributors can reproduce behavior without exposing live credentials.
