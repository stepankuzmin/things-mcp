#!/bin/bash
set -e

# Default Things database location on macOS
THINGS_DB_PATH="$HOME/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/main.sqlite"

# Check if the database exists
if [ ! -f "$THINGS_DB_PATH" ]; then
    echo "Error: Things database not found at $THINGS_DB_PATH"
    echo "Make sure Things is installed on your Mac."
    exit 1
fi

# Build the Docker image if it doesn't exist
if ! docker images | grep -q fastmcp-server; then
    echo "Building Docker image..."
    docker build -t fastmcp-server .
fi

# Stop any existing container
docker stop fastmcp-server 2>/dev/null || true
docker rm fastmcp-server 2>/dev/null || true

# Run the Docker container with Things database mounted
echo "Starting FastMCP server with Things integration..."
docker run -d --name fastmcp-server \
    -p 8000:8000 \
    -v "$THINGS_DB_PATH:/things.db:ro" \
    -e THINGS_DB_PATH="/things.db" \
    fastmcp-server

echo "Server running at http://localhost:8000"
echo "To view logs: docker logs -f fastmcp-server"
echo "To stop: docker stop fastmcp-server"