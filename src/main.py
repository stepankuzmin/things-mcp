from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
from enum import Enum
import things
import os

# Check if a custom Things database path is set
things_db_path = os.environ.get("THINGS_DB_PATH")
if things_db_path:
    things.set_database_path(things_db_path)

app = FastAPI()

class EchoInput(BaseModel):
    message: str

class EchoOutput(BaseModel):
    echo: str

class ThingsEntityType(str, Enum):
    TODO = "todo"
    PROJECT = "project"
    AREA = "area"
    TAG = "tag"

class ThingsListInput(BaseModel):
    entity_type: ThingsEntityType = Field(..., description="Type of Things entity to list (todo, project, area, tag)")
    include_completed: Optional[bool] = Field(False, description="Whether to include completed tasks")
    include_canceled: Optional[bool] = Field(False, description="Whether to include canceled tasks")
    
class ThingsListOutput(BaseModel):
    items: List[Dict[str, Any]]
    count: int

class ThingsGetInput(BaseModel):
    uuid: str = Field(..., description="UUID of the Thing to get")

class ThingsGetOutput(BaseModel):
    item: Dict[str, Any]

@app.get("/")
async def root():
    return {"message": "Simple FastMCP Server"}

@app.post("/mcp")
async def handle_mcp(body: Dict[str, Any]):
    try:
        tool_name = body.get("tool")
        input_data = body.get("input", {})
        
        if tool_name == "echo":
            validated_input = EchoInput(**input_data)
            result = EchoOutput(echo=validated_input.message)
            return {"output": result.model_dump()}
        
        elif tool_name == "things_list":
            validated_input = ThingsListInput(**input_data)
            items = []
            
            if validated_input.entity_type == ThingsEntityType.TODO:
                items = things.todos(
                    include_completed=validated_input.include_completed,
                    include_canceled=validated_input.include_canceled
                )
            elif validated_input.entity_type == ThingsEntityType.PROJECT:
                items = things.projects()
            elif validated_input.entity_type == ThingsEntityType.AREA:
                items = things.areas()
            elif validated_input.entity_type == ThingsEntityType.TAG:
                items = things.tags()
            
            result = ThingsListOutput(items=items, count=len(items))
            return {"output": result.model_dump()}
        
        elif tool_name == "things_get":
            validated_input = ThingsGetInput(**input_data)
            item = things.get(validated_input.uuid)
            if not item:
                raise HTTPException(status_code=404, detail=f"Item with UUID {validated_input.uuid} not found")
            
            result = ThingsGetOutput(item=item)
            return {"output": result.model_dump()}
        
        else:
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
            
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)