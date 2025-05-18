# FastMCP Server with Things Integration

A FastMCP-powered server with an echo tool and Things task manager integration. This server can be used with Claude Desktop to access your Things tasks directly from Claude. Built using the FastMCP 2.3.4 framework for simplified MCP development.

## Usage

### Running with Docker for Things Integration

For macOS users with Things app installed:

```bash
# Make the script executable if needed
chmod +x run_things.sh

# Run the server with Things database access
./run_things.sh
```

This script:
1. Automatically locates your Things database
2. Builds the Docker image if needed
3. Runs the container with the database mounted
4. Exposes the server on port 8000

### Manual Docker Setup

```bash
# Build the Docker image
docker build -t fastmcp-server .

# Run the container (without Things integration)
docker run -p 8000:8000 fastmcp-server

# Run with Things database (macOS) - get the path with the provided helper script
docker run -p 8000:8000 \
  -v "$(./get_things_db_path.sh):/things.db:ro" \
  -e THINGS_DB_PATH="/things.db" \
  fastmcp-server
```

### Local Development

```bash
# Install dependencies with uv
uv pip install -r requirements.txt

# Run the server
python src/main.py
```

## Things Database Utilities

### Finding the Database Path

To get the path to your Things database:

```bash
# Make the script executable if needed
chmod +x get_things_db_path.sh

# Print the database path
./get_things_db_path.sh
```

This can be used in other scripts or commands:

```bash
# Example: Open the database directly with sqlite3
sqlite3 "$(./get_things_db_path.sh)"
```

### Database Backup

To backup your Things database:

```bash
# Create a backup in the default location (~/ThingsBackups)
./backup_things_db.sh

# Or specify a custom backup directory
./backup_things_db.sh --dir /path/to/backup/dir
```

The script:
- Dynamically locates your Things database
- Creates timestamped SQLite backups
- Maintains a history of recent backups
- Automatically cleans up old backups (keeping 10 most recent)
- Uses SQLite's native backup functionality for data integrity

## Testing

You can run tests without having Python installed on your machine using Docker:

```bash
# Make the script executable if needed
chmod +x run_tests.sh

# Run tests
./run_tests.sh
```

This will build a test Docker image and run the pytest suite inside a container.

For local testing (if you have Python installed):

```bash
# Install development dependencies
uv pip install -r requirements.txt -r requirements-dev.txt

# Run tests
PYTHONPATH=. pytest -xvs src/test_main.py
```

## API Endpoints

- `GET /`: Health check endpoint
- `POST /mcp`: MCP endpoint for tool execution (automatically provided by FastMCP)
- `GET /docs`: Interactive API documentation (automatically provided by FastMCP)

## Available Tools

### Echo Tool

Echoes back the provided message.

Example request:
```json
{
  "tool": "echo",
  "input": {
    "message": "Hello, world!"
  }
}
```

Example response:
```json
{
  "output": {
    "echo": "Hello, world!"
  }
}
```

### Things List Tool

Retrieves a list of entities from the Things app.

Example request:
```json
{
  "tool": "things_list",
  "input": {
    "entity_type": "todo",
    "include_completed": false,
    "include_canceled": false
  }
}
```

Example response:
```json
{
  "output": {
    "items": [
      {
        "uuid": "example-uuid-1",
        "title": "Task 1",
        "status": "incomplete",
        "...": "..."
      },
      {
        "uuid": "example-uuid-2",
        "title": "Task 2",
        "status": "incomplete",
        "...": "..."
      }
    ],
    "count": 2
  }
}
```

Available entity types:
- `todo`: Retrieves todo items
- `project`: Retrieves projects
- `area`: Retrieves areas
- `tag`: Retrieves tags

### Things Get Tool

Retrieves a specific item from the Things app by its UUID.

Example request:
```json
{
  "tool": "things_get",
  "input": {
    "uuid": "example-uuid-1"
  }
}
```

Example response:
```json
{
  "output": {
    "item": {
      "uuid": "example-uuid-1",
      "title": "Task 1",
      "status": "incomplete",
      "...": "..."
    }
  }
}
```

## Using with Claude Desktop

To use this MCP server with Claude Desktop:

1. Start the server using the instructions above (preferably with `./run_things.sh`)
2. Open Claude Desktop on your Mac
3. Go to Settings > MCP Servers 
4. Click "Add Server"
5. Enter the following details:
   - Name: Things MCP
   - URL: http://localhost:8000/mcp
   - Click "Add Server"

### Claude Desktop Integration

There are two ways to connect this server to Claude Desktop:

#### Method 1: Using Claude Desktop Settings UI (Recommended)

1. Start the server using `./run_things.sh`
2. Open Claude Desktop
3. Go to Settings > MCP Servers
4. Click "Add Server"
5. Enter the following details:
   - Name: Things MCP
   - URL: http://localhost:8000/mcp
6. Click "Add Server"

#### Method 2: Using Docker with Claude Desktop (Advanced)

First build the Docker image:

```bash
docker build -t things-mcp-server .
```

Then get the path to your Things database:

```bash
./get_things_db_path.sh
```

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
        "-p", "8000:8000",
        "-v", "/path/to/your/things/database:/things.db:ro",
        "-e", "THINGS_DB_PATH=/things.db",
        "things-mcp-server"
      ]
    }
  }
}
```

Replace `/path/to/your/things/database` with the actual path returned by the `get_things_db_path.sh` script. This will start the MCP server with access to your Things database when Claude Desktop launches.

After saving this configuration, restart Claude Desktop and check the Developer tab in Settings to confirm the server is running.

### Example Claude Prompts and Responses

In your conversation with Claude, you can use natural language to interact with your Things data:

**Prompt Example 1:**
"Show me my incomplete tasks"

Claude will use the `things_list` tool with parameters:
```json
{
  "tool": "things_list",
  "input": {
    "entity_type": "todo",
    "include_completed": false,
    "include_canceled": false
  }
}
```

**Prompt Example 2:**
"Show me my project called Website Redesign"

Claude will first get projects and then find the specific one:
```json
{
  "tool": "things_list",
  "input": {
    "entity_type": "project"
  }
}
```

**Prompt Example 3:**
"List all my tasks with the tag 'High Priority'"

Claude will first get all tags and then find tasks with that tag:
```json
{
  "tool": "things_list",
  "input": {
    "entity_type": "tag"
  }
}
```

Claude will use the MCP server to fetch data directly from your Things app without requiring you to manually copy information.

## FastMCP Integration

This server uses [FastMCP](https://pypi.org/project/fastmcp/) version 2.3.4, a framework for quickly building MCP-compatible servers. FastMCP simplifies the process of creating tools and handling MCP requests, providing:

- Simplified tool definition with decorators
- Automatic tool schema generation
- Built-in parameter validation
- API documentation with Swagger UI
- Consistent error handling

## Notes on Things Integration

This server integrates with the Things app on macOS using the [things.py](https://github.com/thingsapi/things.py) library. The library reads data from the Things database, so the Things app must be installed on the same machine where the server is running.

For Docker deployment on macOS:
- All scripts now dynamically locate the Things database
- No hardcoded paths or identifiers are used
- Set `THINGS_DB_PATH` environment variable to the location of the mounted database inside the container

### Troubleshooting

If the Things MCP server doesn't appear in Claude Desktop's tools list:
1. Make sure your MCP server key is a human-readable name (e.g., "Things" instead of "things_mcp")
2. Verify the Docker container is running properly (check with `docker ps`)
3. Restart Claude Desktop to apply any configuration changes

If the Docker container doesn't stop when closing Claude Desktop:
1. Make sure you're using the `--name` parameter in your Docker configuration
2. The container name must match between starts and stops
3. If a container is stuck, you can manually remove it with `docker rm -f claude-things-mcp`

If you see a "Server disconnected" error in Claude Desktop:
1. Make sure the Docker container is running (check with `docker ps`)
2. Verify that port 8000 is accessible (try `curl http://localhost:8000`)
3. Check Docker logs with `docker logs claude-things-mcp`
4. Ensure there are no port conflicts (another service using port 8000)

If you have issues with the Things database connection:
- The server uses things.py version 0.0.15 (the API changed in newer versions)
- If you get an error about `set_database_path`, you need to update src/main.py to use:
  ```python
  # New API (things.py >= 0.0.15)
  things.database = things.Database(things_db_path)
  # Instead of the old API:
  # things.set_database_path(things_db_path)
  ```

For CI/CD environments:
- Tests may fail if Things is not available
- Consider mocking the things.py library for testing