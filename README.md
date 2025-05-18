# Simple FastMCP Server with Things Integration

A minimal FastMCP server with an echo tool and Things task manager integration. This server can be used with Claude Desktop to access your Things tasks directly from Claude.

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
- `POST /mcp`: MCP endpoint for tool execution

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

#### Method 2: Using Docker (Advanced)

First make sure the Docker image is built by running:

```bash
docker build -t fastmcp-server .
```

Then add this to your `~/Library/Application Support/Claude/claude_desktop_config.json`:

```json
{
  "mcpServers": {
    "things_mcp": {
      "command": "docker",
      "args": [
        "run",
        "-p", "8000:8000",
        "--name", "claude-things-mcp",
        "--rm",
        "fastmcp-server"
      ]
    }
  }
}
```

**Note**: This will run a Docker container without mounting the Things database, but it will satisfy Claude Desktop's requirement for a valid configuration. You should still use Method 1 or run the server separately with `./run_things.sh` for actual integration with Things.

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

## Notes on Things Integration

This server integrates with the Things app on macOS using the [things.py](https://github.com/thingsapi/things.py) library. The library reads data from the Things database, so the Things app must be installed on the same machine where the server is running.

For Docker deployment on macOS:
- All scripts now dynamically locate the Things database
- No hardcoded paths or identifiers are used
- Set `THINGS_DB_PATH` environment variable to the location of the mounted database inside the container

For CI/CD environments:
- Tests may fail if Things is not available
- Consider mocking the things.py library for testing