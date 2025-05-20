# Things FastMCP Server

A FastMCP 2.0 server with tools for working with the Things 3 task manager.

## Usage

### Running with Docker

```bash
# Build the Docker image
docker build -t fastmcp-server .

# Run the container
docker run -p 8000:8000 fastmcp-server
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

### Base Endpoints

- `GET /`: Health check endpoint
- `GET /fastmcp/v2/tools`: FastMCP 2.0 tool discovery endpoint
- `POST /fastmcp/v2/execute`: FastMCP 2.0 tool execution endpoint
- `POST /mcp`: Legacy MCP endpoint (for backward compatibility)

## FastMCP 2.0 Interface

This server implements the FastMCP 2.0 specification, which provides a standardized interface for executing tools:

### Tool Discovery

To discover available tools, make a GET request to `/fastmcp/v2/tools`:

```
GET /fastmcp/v2/tools
```

Response:
```json
{
  "tools": [
    {
      "name": "echo",
      "description": "Echoes back the provided message",
      "version": "1.0.0",
      "input_schema": {
        "properties": {
          "message": {
            "description": "Message to echo back",
            "type": "string"
          }
        },
        "required": ["message"]
      },
      "output_schema": {
        "properties": {
          "echo": {
            "type": "string"
          }
        },
        "required": ["echo"]
      }
    },
    // Other tools...
  ]
}
```

### Tool Execution

To execute a tool, make a POST request to `/fastmcp/v2/execute` with the following structure:

```
POST /fastmcp/v2/execute
```

Request:
```json
{
  "id": "request-id-1234",
  "tool_name": "echo",
  "tool_params": {
    "message": "Hello, FastMCP 2.0!"
  }
}
```

Successful Response:
```json
{
  "id": "request-id-1234",
  "tool_name": "echo",
  "response": {
    "echo": "Hello, FastMCP 2.0!"
  }
}
```

Error Response:
```json
{
  "id": "request-id-1234",
  "tool_name": "unknown_tool",
  "error": {
    "code": "TOOL_NOT_FOUND",
    "message": "Tool 'unknown_tool' not found",
    "details": null
  }
}
```

## Available Tools

### Echo Tool

Echoes back the provided message.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "echo",
  "tool_params": {
    "message": "Hello, world!"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "echo",
  "response": {
    "echo": "Hello, world!"
  }
}
```

### Things 3 Task Management Tools

These tools allow interaction with the Things 3 task manager application on macOS/iOS. They require access to the Things 3 SQLite database.

#### get_tasks

Retrieve tasks with flexible filtering options.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_tasks",
  "tool_params": {
    "status": "upcoming",
    "tag": "work",
    "limit": 10
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_tasks",
  "response": {
    "tasks": [
      {
        "uuid": "task-uuid-1",
        "title": "Finish project report",
        "status": "upcoming",
        "tags": ["work"]
      },
      // Other tasks...
    ]
  }
}
```

Available filters:
- `status`: Filter by task status ("upcoming", "completed", "canceled", "trash")
- `tag`: Filter by tag name
- `search`: Text search across task titles
- `area`: Filter by area name
- `project`: Filter by project title
- `heading`: Filter by task heading
- `limit`: Maximum number of tasks to return

#### get_task_detail

Get detailed information about a specific task.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_task_detail",
  "tool_params": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_task_detail",
  "response": {
    "task": {
      "uuid": "task-uuid-1",
      "title": "Finish project report",
      "notes": "Include Q3 metrics in the analysis",
      "status": "upcoming",
      "tags": ["work", "reports"],
      "checklist": [
        "Add executive summary",
        "Include Q3 metrics",
        "Add recommendations"
      ]
    }
  }
}
```

#### get_projects

Retrieve projects with filtering options.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_projects",
  "tool_params": {
    "status": "upcoming",
    "area": "Work"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_projects",
  "response": {
    "projects": [
      {
        "uuid": "project-uuid-1",
        "title": "Q3 Planning",
        "status": "upcoming",
        "area": "Work"
      },
      // Other projects...
    ]
  }
}
```

#### get_areas

List organizational areas.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_areas",
  "tool_params": {
    "search": "Work"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_areas",
  "response": {
    "areas": [
      {
        "uuid": "area-uuid-1",
        "title": "Work"
      },
      // Other areas...
    ]
  }
}
```

#### get_tags

List all available tags.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_tags",
  "tool_params": {}
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "get_tags",
  "response": {
    "tags": [
      {
        "uuid": "tag-uuid-1",
        "title": "work"
      },
      {
        "uuid": "tag-uuid-2",
        "title": "personal"
      },
      // Other tags...
    ]
  }
}
```

#### create_task

Create a new task with optional metadata.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "create_task",
  "tool_params": {
    "title": "Write quarterly report",
    "notes": "Include metrics from Q3",
    "tags": ["work", "reports"],
    "when": "today",
    "deadline": "2025-06-30",
    "checklist": [
      "Gather data",
      "Create draft",
      "Review with team"
    ],
    "project": "Quarterly Planning"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "create_task",
  "response": {
    "uuid": "new-task-uuid",
    "title": "Write quarterly report"
  }
}
```

#### complete_task

Mark a task as completed.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "complete_task",
  "tool_params": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "complete_task",
  "response": {
    "success": true,
    "uuid": "task-uuid-1"
  }
}
```

#### cancel_task

Mark a task as canceled.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "cancel_task",
  "tool_params": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "cancel_task",
  "response": {
    "success": true,
    "uuid": "task-uuid-1"
  }
}
```

#### update_task

Update an existing task's attributes.

Example request:
```json
{
  "id": "request-id-1234",
  "tool_name": "update_task",
  "tool_params": {
    "uuid": "task-uuid-1",
    "title": "Updated task title",
    "notes": "Updated notes content",
    "tags": ["updated-tag"],
    "when": "tomorrow",
    "deadline": "2025-07-15"
  }
}
```

Example response:
```json
{
  "id": "request-id-1234",
  "tool_name": "update_task",
  "response": {
    "success": true,
    "uuid": "task-uuid-1"
  }
}
```

## Legacy Support

The server maintains backward compatibility with the previous MCP format through the `/mcp` endpoint. This allows existing clients to continue working while new clients can take advantage of the FastMCP 2.0 interface.