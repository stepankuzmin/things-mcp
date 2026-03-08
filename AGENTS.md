# Codex Instructions

## Setup

- This repo uses `uv` only.
- Never install project dependencies into system Python.
- Use the Codex Cloud setup script at `scripts/codex-cloud-setup.sh`.
- If the environment resumes from cache, use `scripts/codex-cloud-maintenance.sh`.

## Commands

- Sync dependencies: `uv sync --managed-python --locked`
- Run tests: `uv run --managed-python pytest`
- Run server: `uv run --managed-python python src/main.py`

## Notes

- Tests are unit tests and do not require a live Things database.
- The runtime target is Python 3.14.
