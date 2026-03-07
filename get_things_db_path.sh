#!/bin/bash
set -e

GROUP_CONTAINERS="$HOME/Library/Group Containers"
THINGS_DB=$(find "$GROUP_CONTAINERS" -name "main.sqlite" -path "*ThingsMac/ThingsData*/Things Database.thingsdatabase*" -type f 2>/dev/null | head -n 1)

if [ -z "$THINGS_DB" ]; then
    echo "Error: Things database not found" >&2
    echo "Make sure Things is installed on your Mac" >&2
    exit 1
fi

echo "$THINGS_DB"
