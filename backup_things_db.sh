#!/bin/bash
set -e

# Define date format for backup file naming
DATE_FORMAT=$(date +"%Y-%m-%d_%H-%M-%S")

# Default backup directory
BACKUP_DIR="$HOME/ThingsBackups"

# Parse command line arguments
while [[ "$#" -gt 0 ]]; do
    case $1 in
        -d|--dir) BACKUP_DIR="$2"; shift ;;
        -h|--help) 
            echo "Usage: $0 [options]"
            echo "Options:"
            echo "  -d, --dir DIR    Set backup directory (default: ~/ThingsBackups)"
            echo "  -h, --help       Show this help message"
            exit 0
            ;;
        *) echo "Unknown parameter: $1"; exit 1 ;;
    esac
    shift
done

# Find the Things database dynamically using the script
echo "Locating Things database..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
THINGS_DB=$("$SCRIPT_DIR/get_things_db_path.sh")

if [ $? -ne 0 ]; then
    echo "Error: Failed to locate Things database."
    exit 1
fi

echo "Found Things database at: $THINGS_DB"

# Create backup directory if it doesn't exist
mkdir -p "$BACKUP_DIR"

# Backup filename with timestamp
BACKUP_FILE="$BACKUP_DIR/things_backup_$DATE_FORMAT.sqlite"

# Copy the database (using sqlite3 to create a proper backup)
echo "Creating backup of Things database..."
sqlite3 "$THINGS_DB" ".backup '$BACKUP_FILE'"

# Check if backup was successful
if [ -f "$BACKUP_FILE" ]; then
    echo "Backup created successfully at: $BACKUP_FILE"
    echo "Backup size: $(du -h "$BACKUP_FILE" | cut -f1)"
else
    echo "Error: Backup failed."
    exit 1
fi

# List recent backups
echo -e "\nRecent backups:"
ls -lh "$BACKUP_DIR" | grep things_backup | tail -5

# Optional: You can add code here to clean up old backups if needed
# For example, to keep only the 10 most recent backups:
BACKUP_COUNT=$(ls -1 "$BACKUP_DIR"/things_backup_*.sqlite 2>/dev/null | wc -l)
if [ "$BACKUP_COUNT" -gt 10 ]; then
    echo -e "\nRemoving old backups (keeping 10 most recent)..."
    ls -t "$BACKUP_DIR"/things_backup_*.sqlite | tail -n +11 | xargs rm
    echo "Done cleaning up old backups."
fi