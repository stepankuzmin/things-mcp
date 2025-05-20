# Simple FastMCP Server

A minimal FastMCP server with tools for working with the Things 3 task manager.

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

### Things 3 Task Management Tools

These tools allow interaction with the Things 3 task manager application on macOS/iOS. They require access to the Things 3 SQLite database.

#### get_tasks

Retrieve tasks with flexible filtering options.

Example request:
```json
{
  "tool": "get_tasks",
  "input": {
    "status": "upcoming",
    "tag": "work",
    "limit": 10
  }
}
```

Example response:
```json
{
  "output": {
    "tasks": [
      {
        "uuid": "task-uuid-1",
        "title": "Finish project report",
        "status": "upcoming",
        "tags": ["work"]
      },
      ...
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
  "tool": "get_task_detail",
  "input": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "output": {
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
  "tool": "get_projects",
  "input": {
    "status": "upcoming",
    "area": "Work"
  }
}
```

Example response:
```json
{
  "output": {
    "projects": [
      {
        "uuid": "project-uuid-1",
        "title": "Q3 Planning",
        "status": "upcoming",
        "area": "Work"
      },
      ...
    ]
  }
}
```

#### get_areas

List organizational areas.

Example request:
```json
{
  "tool": "get_areas",
  "input": {
    "search": "Work"
  }
}
```

Example response:
```json
{
  "output": {
    "areas": [
      {
        "uuid": "area-uuid-1",
        "title": "Work"
      },
      ...
    ]
  }
}
```

#### get_tags

List all available tags.

Example request:
```json
{
  "tool": "get_tags",
  "input": {}
}
```

Example response:
```json
{
  "output": {
    "tags": [
      {
        "uuid": "tag-uuid-1",
        "title": "work"
      },
      {
        "uuid": "tag-uuid-2",
        "title": "personal"
      },
      ...
    ]
  }
}
```

#### create_task

Create a new task with optional metadata.

Example request:
```json
{
  "tool": "create_task",
  "input": {
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
  "output": {
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
  "tool": "complete_task",
  "input": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "output": {
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
  "tool": "cancel_task",
  "input": {
    "uuid": "task-uuid-1"
  }
}
```

Example response:
```json
{
  "output": {
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
  "tool": "update_task",
  "input": {
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
  "output": {
    "success": true,
    "uuid": "task-uuid-1"
  }
}
```