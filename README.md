# Things MCP Server

A minimal FastMCP server that integrates with Things task manager on macOS. This server enables Claude Desktop to access your Things tasks directly.

## Requirements

- macOS with Things app installed
- Docker

## Usage with Claude Desktop

Add this to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "Things": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--name", "claude-things-mcp",
        "--rm",
        "-v", "/path/to/your/things/database:/things.db:ro",
        "-e", "THINGS_DB_PATH=/things.db",
        "fastmcp-server"
      ]
    }
  }
}
```

Replace `/path/to/your/things/database` with the path to your Things database, typically found at:
`~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/main.sqlite`

## Building Locally

```bash
# Build the Docker image
docker build -t fastmcp-server .
```

## Available Tools

- `things_list`: Lists items from Things with filters (todos, projects, areas, or tags)
- `things_get`: Gets a specific item by UUID

## Notes

This server integrates with Things using [things.py](https://github.com/thingsapi/things.py) library and uses the FastMCP framework to expose Things data to Claude Desktop.