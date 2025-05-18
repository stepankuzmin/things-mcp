#!/bin/bash
set -e

# Find the Things database dynamically using the script
echo "Locating Things database..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THINGS_DB=$("$SCRIPT_DIR/get_things_db_path.sh")

if [ $? -ne 0 ]; then
    echo "Error: Failed to locate Things database."
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