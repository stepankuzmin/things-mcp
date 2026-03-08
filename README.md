# Things MCP Server

A minimal FastMCP server that integrates with Things task manager on macOS. This server enables Claude Desktop to access your Things tasks directly.

## Requirements

- macOS with Things app installed
- `uv`

## Local Setup

```bash
# Install the pinned Python version with uv
uv python install 3.14

# Create the project environment in .venv using uv-managed Python
uv sync --managed-python --locked
```

This repo does not use system site-packages. Run everything through `uv`.

## Run Locally

```bash
uv run --managed-python python src/main.py
```

## Testing

```bash
uv run --managed-python pytest
```

## Codex Cloud

Codex Cloud does not auto-detect `uv` projects. Configure the environment manually:

- Setup script: `scripts/codex-cloud-setup.sh`
- Maintenance script: `scripts/codex-cloud-maintenance.sh`

This repo also includes `AGENTS.md`, which tells Codex to use `uv run --managed-python pytest` for validation.

## Usage with Claude Desktop

Add this to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Things": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/things-mcp",
        "--managed-python",
        "python",
        "src/main.py"
      ]
    }
  }
}
```

If you want to point the server at a specific exported or mounted database file, add an env var:

```json
{
  "mcpServers": {
    "Things": {
      "command": "uv",
      "args": [
        "run",
        "--directory", "/path/to/things-mcp",
        "--managed-python",
        "python",
        "src/main.py"
      ],
      "env": {
        "THINGS_DB_PATH": "/absolute/path/to/main.sqlite"
      }
    }
  }
}
```

To locate the default Things database on macOS:

```bash
./get_things_db_path.sh
```

## Docker

```bash
# Build the Docker image with uv-managed dependencies
docker build -t fastmcp-server .
```

Images are also built and published automatically to GitHub Container Registry on every push to `main` and when you push a Git tag:

- `ghcr.io/<owner>/things-mcp:latest`
- `ghcr.io/<owner>/things-mcp:<git-tag>` (published when you push a Git tag)

The Docker image also uses `uv`; it does not install dependencies into the system interpreter.

## Available Tools

- `things_list`: Lists items from Things with filters (todos, projects, areas, or tags)
- `things_get`: Gets a specific item by UUID

## Notes

This server integrates with Things using [things.py](https://github.com/thingsapi/things.py) library and uses the FastMCP framework to expose Things data to Claude Desktop.
