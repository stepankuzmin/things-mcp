from fastmcp import FastMCP
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field
import things
import os

# Check if a custom Things database path is set
things_db_path = os.environ.get("THINGS_DB_PATH")
if things_db_path:
    # Use the Database class to set the database path
    things.database = things.Database(things_db_path)

# Initialize FastMCP
app = FastMCP(title="Things MCP")

# Echo Tool
@app.tool(description="Echoes back the provided message")
def echo(message: str) -> dict:
    return {"echo": message}

# Define Things Tools
class ThingsEntityType(str, Enum):
    TODO = "todo"
    PROJECT = "project"
    AREA = "area"
    TAG = "tag"

@app.tool(description="Lists entities from Things (todos, projects, areas, tags)")
def things_list(
    entity_type: ThingsEntityType, 
    include_completed: bool = False, 
    include_canceled: bool = False
) -> dict:
    items = []
    
    if entity_type == ThingsEntityType.TODO:
        items = things.todos(
            include_completed=include_completed,
            include_canceled=include_canceled
        )
    elif entity_type == ThingsEntityType.PROJECT:
        items = things.projects()
    elif entity_type == ThingsEntityType.AREA:
        items = things.areas()
    elif entity_type == ThingsEntityType.TAG:
        items = things.tags()
    
    return {"items": items, "count": len(items)}

@app.tool(description="Gets a specific item from Things by UUID")
def things_get(uuid: str) -> dict:
    item = things.get(uuid)
    if not item:
        raise ValueError(f"Item with UUID {uuid} not found")
    
    return {"item": item}

# Health check tool
@app.tool(description="Health check")
def health_check() -> dict:
    return {"message": "Simple FastMCP Server"}

if __name__ == "__main__":
    # Run with stdio transport (default)
    app.run()