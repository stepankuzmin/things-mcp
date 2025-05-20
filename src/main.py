from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional
import things

app = FastAPI()

class EchoInput(BaseModel):
    message: str

class EchoOutput(BaseModel):
    echo: str

class GetTasksInput(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status: 'upcoming', 'completed', 'canceled', 'trash'")
    tag: Optional[str] = Field(None, description="Filter by tag name")
    search: Optional[str] = Field(None, description="Search term to filter tasks")
    area: Optional[str] = Field(None, description="Filter by area name")
    project: Optional[str] = Field(None, description="Filter by project title")
    heading: Optional[str] = Field(None, description="Filter by heading")
    limit: Optional[int] = Field(None, description="Limit the number of results")

class GetTasksOutput(BaseModel):
    tasks: List[Dict[str, Any]]

class GetTaskDetailInput(BaseModel):
    uuid: str = Field(..., description="UUID of the task to retrieve")

class GetTaskDetailOutput(BaseModel):
    task: Dict[str, Any]

class GetProjectsInput(BaseModel):
    status: Optional[str] = Field(None, description="Filter by status: 'upcoming', 'completed', 'canceled', 'trash'")
    tag: Optional[str] = Field(None, description="Filter by tag name")
    search: Optional[str] = Field(None, description="Search term to filter projects")
    area: Optional[str] = Field(None, description="Filter by area name")
    limit: Optional[int] = Field(None, description="Limit the number of results")

class GetProjectsOutput(BaseModel):
    projects: List[Dict[str, Any]]

class GetAreasInput(BaseModel):
    search: Optional[str] = Field(None, description="Search term to filter areas")

class GetAreasOutput(BaseModel):
    areas: List[Dict[str, Any]]

class GetTagsInput(BaseModel):
    search: Optional[str] = Field(None, description="Search term to filter tags")

class GetTagsOutput(BaseModel):
    tags: List[Dict[str, Any]]

class CreateTaskInput(BaseModel):
    title: str = Field(..., description="Task title")
    notes: Optional[str] = Field(None, description="Task notes")
    tags: Optional[List[str]] = Field(None, description="List of tag names to assign")
    when: Optional[str] = Field(None, description="When to start the task (today, tomorrow, evening, etc.)")
    deadline: Optional[str] = Field(None, description="Deadline date (YYYY-MM-DD)")
    checklist: Optional[List[str]] = Field(None, description="Checklist items")
    project: Optional[str] = Field(None, description="Title of the project to add the task to")
    area: Optional[str] = Field(None, description="Title of the area to add the task to")
    heading: Optional[str] = Field(None, description="Heading under which to add this task")

class CreateTaskOutput(BaseModel):
    uuid: str
    title: str

class CompleteTaskInput(BaseModel):
    uuid: str = Field(..., description="UUID of the task to complete")

class CompleteTaskOutput(BaseModel):
    success: bool
    uuid: str

class CancelTaskInput(BaseModel):
    uuid: str = Field(..., description="UUID of the task to cancel")

class CancelTaskOutput(BaseModel):
    success: bool
    uuid: str

class UpdateTaskInput(BaseModel):
    uuid: str = Field(..., description="UUID of the task to update")
    title: Optional[str] = Field(None, description="New task title")
    notes: Optional[str] = Field(None, description="New task notes")
    tags: Optional[List[str]] = Field(None, description="New list of tag names to assign")
    when: Optional[str] = Field(None, description="New when date (today, tomorrow, evening, etc.)")
    deadline: Optional[str] = Field(None, description="New deadline date (YYYY-MM-DD)")
    checklist: Optional[List[str]] = Field(None, description="New checklist items")

class UpdateTaskOutput(BaseModel):
    success: bool
    uuid: str

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
        
        elif tool_name == "get_tasks":
            validated_input = GetTasksInput(**input_data)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            tasks = things.tasks(**kwargs)
            result = GetTasksOutput(tasks=tasks)
            return {"output": result.model_dump()}
        
        elif tool_name == "get_task_detail":
            validated_input = GetTaskDetailInput(**input_data)
            task = things.get(validated_input.uuid)
            if not task:
                raise HTTPException(status_code=404, detail=f"Task with UUID {validated_input.uuid} not found")
            result = GetTaskDetailOutput(task=task)
            return {"output": result.model_dump()}
        
        elif tool_name == "get_projects":
            validated_input = GetProjectsInput(**input_data)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            projects = things.projects(**kwargs)
            result = GetProjectsOutput(projects=projects)
            return {"output": result.model_dump()}
        
        elif tool_name == "get_areas":
            validated_input = GetAreasInput(**input_data)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            areas = things.areas(**kwargs)
            result = GetAreasOutput(areas=areas)
            return {"output": result.model_dump()}
        
        elif tool_name == "get_tags":
            validated_input = GetTagsInput(**input_data)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            tags = things.tags(**kwargs)
            result = GetTagsOutput(tags=tags)
            return {"output": result.model_dump()}
        
        elif tool_name == "create_task":
            validated_input = CreateTaskInput(**input_data)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            uuid = things.create_todo(**kwargs)
            result = CreateTaskOutput(uuid=uuid, title=validated_input.title)
            return {"output": result.model_dump()}
        
        elif tool_name == "complete_task":
            validated_input = CompleteTaskInput(**input_data)
            success = things.complete(validated_input.uuid)
            result = CompleteTaskOutput(success=success, uuid=validated_input.uuid)
            return {"output": result.model_dump()}
        
        elif tool_name == "cancel_task":
            validated_input = CancelTaskInput(**input_data)
            success = things.cancel(validated_input.uuid)
            result = CancelTaskOutput(success=success, uuid=validated_input.uuid)
            return {"output": result.model_dump()}
        
        elif tool_name == "update_task":
            validated_input = UpdateTaskInput(**input_data)
            uuid = validated_input.uuid
            kwargs = {k: v for k, v in validated_input.model_dump().items() if k != "uuid" and v is not None}
            
            if not kwargs:
                raise HTTPException(status_code=400, detail="No update parameters provided")
            
            success = things.update(uuid, **kwargs)
            result = UpdateTaskOutput(success=success, uuid=uuid)
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