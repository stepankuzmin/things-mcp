#!/bin/bash
set -e

# Build the test Docker image
docker build -t fastmcp-test -f Dockerfile.test .

# Run tests in the container
docker run --rm fastmcp-test