# Simple FastMCP Server

A minimal FastMCP server with a single echo tool.

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