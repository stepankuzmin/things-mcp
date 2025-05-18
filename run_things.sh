#!/bin/bash
set -e

# Find the Things database dynamically
echo "Locating Things database..."
GROUP_CONTAINERS="$HOME/Library/Group Containers"
THINGS_DB=$(find "$GROUP_CONTAINERS" -name "main.sqlite" -path "*ThingsMac/Things Database.thingsdatabase*" -type f 2>/dev/null | head -n 1)

if [ -z "$THINGS_DB" ]; then
    echo "Error: Things database not found."
    echo "Make sure Things is installed on your Mac."
    exit 1
fi

echo "Found Things database at: $THINGS_DB"

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
    -v "$THINGS_DB:/things.db:ro" \
    -e THINGS_DB_PATH="/things.db" \
    fastmcp-server

echo "Server running at http://localhost:8000"
echo "To view logs: docker logs -f fastmcp-server"
echo "To stop: docker stop fastmcp-server"