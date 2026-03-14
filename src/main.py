import os
from enum import Enum

import things
from anyio import BrokenResourceError
from fastmcp import FastMCP


def _build_things_database() -> things.Database:
    filepath = os.environ.get("THINGS_DB_PATH") or os.environ.get("THINGSDB")
    if filepath:
        # Keep the upstream env var in sync for any internals that still read it.
        os.environ["THINGSDB"] = filepath

    return things.Database(filepath=filepath)


THINGS_DATABASE = _build_things_database()

# Initialize FastMCP
app = FastMCP("Things MCP")

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
            include_canceled=include_canceled,
            database=THINGS_DATABASE,
        )
    elif entity_type == ThingsEntityType.PROJECT:
        items = things.projects(database=THINGS_DATABASE)
    elif entity_type == ThingsEntityType.AREA:
        items = things.areas(database=THINGS_DATABASE)
    elif entity_type == ThingsEntityType.TAG:
        items = things.tags(database=THINGS_DATABASE)
    
    return {"items": items, "count": len(items)}

@app.tool(description="Gets a specific item from Things by UUID")
def things_get(uuid: str) -> dict:
    item = things.get(uuid, database=THINGS_DATABASE)
    if not item:
        raise ValueError(f"Item with UUID {uuid} not found")
    
    return {"item": item}

def _is_broken_resource_group(exc: BaseExceptionGroup) -> bool:
    for subexc in exc.exceptions:
        if isinstance(subexc, BaseExceptionGroup):
            if not _is_broken_resource_group(subexc):
                return False
            continue
        if not isinstance(subexc, BrokenResourceError):
            return False
    return True

def main() -> None:
    try:
        app.run(transport="stdio")
    except KeyboardInterrupt:
        pass
    except BaseExceptionGroup as exc:
        if not _is_broken_resource_group(exc):
            raise

if __name__ == "__main__":
    main()
