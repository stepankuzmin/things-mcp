# Simple FastMCP Server with Things Integration

A minimal FastMCP server with an echo tool and Things task manager integration.

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
1. Locates your Things database
2. Builds the Docker image if needed
3. Runs the container with the database mounted
4. Exposes the server on port 8000

### Manual Docker Setup

```bash
# Build the Docker image
docker build -t fastmcp-server .

# Run the container (without Things integration)
docker run -p 8000:8000 fastmcp-server

# Run with Things database (macOS)
docker run -p 8000:8000 \
  -v "$HOME/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/main.sqlite:/things.db:ro" \
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

## Notes on Things Integration

This server integrates with the Things app on macOS using the [things.py](https://github.com/thingsapi/things.py) library. The library reads data from the Things database, so the Things app must be installed on the same machine where the server is running.

For Docker deployment on macOS:
- The `run_things.sh` script handles mounting the database automatically
- Set `THINGS_DB_PATH` environment variable to the location of the mounted database inside the container

For CI/CD environments:
- Tests may fail if Things is not available
- Consider mocking the things.py library for testing