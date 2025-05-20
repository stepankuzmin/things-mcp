from fastapi import FastAPI, HTTPException, Request, Depends, status
from fastapi.responses import JSONResponse
from pydantic import BaseModel, Field, UUID4
from typing import Dict, Any, List, Optional, Literal, Union
import things
import uuid
import time
from datetime import datetime

app = FastAPI(
    title="Things FastMCP Server",
    description="FastMCP 2.0 server for Things 3 integration",
    version="2.0.0"
)

# FastMCP 2.0 Models
class FastMCPToolParams(BaseModel):
    pass

class FastMCPRequest(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), description="Unique request identifier")
    tool_name: str = Field(..., description="Name of the tool to execute")
    tool_params: Dict[str, Any] = Field(default_factory=dict, description="Parameters for the tool")
    
class FastMCPError(BaseModel):
    code: str = Field(..., description="Error code")
    message: str = Field(..., description="Error message")
    details: Optional[Dict[str, Any]] = Field(None, description="Additional error details")

class FastMCPResponse(BaseModel):
    id: str = Field(..., description="Request identifier (matches request id)")
    tool_name: str = Field(..., description="Name of the executed tool")
    response: Dict[str, Any] = Field(..., description="Tool response data")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "tool_name": "echo",
                "response": {
                    "echo": "Hello, world!"
                }
            }
        }

class FastMCPErrorResponse(BaseModel):
    id: str = Field(..., description="Request identifier (matches request id)")
    tool_name: str = Field(..., description="Name of the tool that failed")
    error: FastMCPError = Field(..., description="Error information")
    
    class Config:
        schema_extra = {
            "example": {
                "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
                "tool_name": "echo",
                "error": {
                    "code": "INVALID_PARAMETER",
                    "message": "Missing required parameter: message",
                    "details": {
                        "parameter": "message"
                    }
                }
            }
        }

class ToolMetadata(BaseModel):
    name: str
    description: str
    version: str = "1.0.0"
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

# Tool-specific models (input parameters)
class EchoInput(FastMCPToolParams):
    message: str = Field(..., description="Message to echo back")

class GetTasksInput(FastMCPToolParams):
    status: Optional[str] = Field(None, description="Filter by status: 'upcoming', 'completed', 'canceled', 'trash'")
    tag: Optional[str] = Field(None, description="Filter by tag name")
    search: Optional[str] = Field(None, description="Search term to filter tasks")
    area: Optional[str] = Field(None, description="Filter by area name")
    project: Optional[str] = Field(None, description="Filter by project title")
    heading: Optional[str] = Field(None, description="Filter by heading")
    limit: Optional[int] = Field(None, description="Limit the number of results")

class GetTaskDetailInput(FastMCPToolParams):
    uuid: str = Field(..., description="UUID of the task to retrieve")

class GetProjectsInput(FastMCPToolParams):
    status: Optional[str] = Field(None, description="Filter by status: 'upcoming', 'completed', 'canceled', 'trash'")
    tag: Optional[str] = Field(None, description="Filter by tag name")
    search: Optional[str] = Field(None, description="Search term to filter projects")
    area: Optional[str] = Field(None, description="Filter by area name")
    limit: Optional[int] = Field(None, description="Limit the number of results")

class GetAreasInput(FastMCPToolParams):
    search: Optional[str] = Field(None, description="Search term to filter areas")

class GetTagsInput(FastMCPToolParams):
    search: Optional[str] = Field(None, description="Search term to filter tags")

class CreateTaskInput(FastMCPToolParams):
    title: str = Field(..., description="Task title")
    notes: Optional[str] = Field(None, description="Task notes")
    tags: Optional[List[str]] = Field(None, description="List of tag names to assign")
    when: Optional[str] = Field(None, description="When to start the task (today, tomorrow, evening, etc.)")
    deadline: Optional[str] = Field(None, description="Deadline date (YYYY-MM-DD)")
    checklist: Optional[List[str]] = Field(None, description="Checklist items")
    project: Optional[str] = Field(None, description="Title of the project to add the task to")
    area: Optional[str] = Field(None, description="Title of the area to add the task to")
    heading: Optional[str] = Field(None, description="Heading under which to add this task")

class CompleteTaskInput(FastMCPToolParams):
    uuid: str = Field(..., description="UUID of the task to complete")

class CancelTaskInput(FastMCPToolParams):
    uuid: str = Field(..., description="UUID of the task to cancel")

class UpdateTaskInput(FastMCPToolParams):
    uuid: str = Field(..., description="UUID of the task to update")
    title: Optional[str] = Field(None, description="New task title")
    notes: Optional[str] = Field(None, description="New task notes")
    tags: Optional[List[str]] = Field(None, description="New list of tag names to assign")
    when: Optional[str] = Field(None, description="New when date (today, tomorrow, evening, etc.)")
    deadline: Optional[str] = Field(None, description="New deadline date (YYYY-MM-DD)")
    checklist: Optional[List[str]] = Field(None, description="New checklist items")

# Tool-specific output models
class EchoOutput(BaseModel):
    echo: str

class GetTasksOutput(BaseModel):
    tasks: List[Dict[str, Any]]

class GetTaskDetailOutput(BaseModel):
    task: Dict[str, Any]

class GetProjectsOutput(BaseModel):
    projects: List[Dict[str, Any]]

class GetAreasOutput(BaseModel):
    areas: List[Dict[str, Any]]

class GetTagsOutput(BaseModel):
    tags: List[Dict[str, Any]]

class CreateTaskOutput(BaseModel):
    uuid: str
    title: str

class CompleteTaskOutput(BaseModel):
    success: bool
    uuid: str

class CancelTaskOutput(BaseModel):
    success: bool
    uuid: str

class UpdateTaskOutput(BaseModel):
    success: bool
    uuid: str

# Error handling middleware
@app.middleware("http")
async def error_handler(request: Request, call_next):
    try:
        return await call_next(request)
    except Exception as e:
        # If this is already an HTTPException, we don't need to wrap it
        if isinstance(e, HTTPException):
            return JSONResponse(
                status_code=e.status_code,
                content={"detail": e.detail},
            )
        
        # Otherwise, log the exception and return a 500 error
        print(f"Unhandled exception: {str(e)}")
        return JSONResponse(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            content={"detail": "Internal server error"},
        )

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "service": "Things FastMCP Server",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

# Tool definitions for discovery
TOOL_DEFINITIONS = {
    "echo": ToolMetadata(
        name="echo",
        description="Echoes back the provided message",
        input_schema=EchoInput.model_json_schema(),
        output_schema=EchoOutput.model_json_schema(),
    ),
    "get_tasks": ToolMetadata(
        name="get_tasks",
        description="Retrieve tasks with flexible filtering options",
        input_schema=GetTasksInput.model_json_schema(),
        output_schema=GetTasksOutput.model_json_schema(),
    ),
    "get_task_detail": ToolMetadata(
        name="get_task_detail",
        description="Get detailed information about a specific task",
        input_schema=GetTaskDetailInput.model_json_schema(),
        output_schema=GetTaskDetailOutput.model_json_schema(),
    ),
    "get_projects": ToolMetadata(
        name="get_projects",
        description="Retrieve projects with filtering options",
        input_schema=GetProjectsInput.model_json_schema(),
        output_schema=GetProjectsOutput.model_json_schema(),
    ),
    "get_areas": ToolMetadata(
        name="get_areas",
        description="List organizational areas",
        input_schema=GetAreasInput.model_json_schema(),
        output_schema=GetAreasOutput.model_json_schema(),
    ),
    "get_tags": ToolMetadata(
        name="get_tags",
        description="List all available tags",
        input_schema=GetTagsInput.model_json_schema(),
        output_schema=GetTagsOutput.model_json_schema(),
    ),
    "create_task": ToolMetadata(
        name="create_task",
        description="Create a new task with optional metadata",
        input_schema=CreateTaskInput.model_json_schema(),
        output_schema=CreateTaskOutput.model_json_schema(),
    ),
    "complete_task": ToolMetadata(
        name="complete_task",
        description="Mark a task as completed",
        input_schema=CompleteTaskInput.model_json_schema(),
        output_schema=CompleteTaskOutput.model_json_schema(),
    ),
    "cancel_task": ToolMetadata(
        name="cancel_task",
        description="Mark a task as canceled",
        input_schema=CancelTaskInput.model_json_schema(),
        output_schema=CancelTaskOutput.model_json_schema(),
    ),
    "update_task": ToolMetadata(
        name="update_task",
        description="Update an existing task's attributes",
        input_schema=UpdateTaskInput.model_json_schema(),
        output_schema=UpdateTaskOutput.model_json_schema(),
    ),
}

# Tool discovery endpoint
@app.get("/fastmcp/v2/tools")
async def get_tools():
    return {
        "tools": [tool.model_dump() for tool in TOOL_DEFINITIONS.values()]
    }

# Main execution endpoint
@app.post("/fastmcp/v2/execute", response_model=Union[FastMCPResponse, FastMCPErrorResponse])
async def execute_tool(request: FastMCPRequest):
    tool_name = request.tool_name
    
    try:
        if tool_name not in TOOL_DEFINITIONS:
            return FastMCPErrorResponse(
                id=request.id,
                tool_name=tool_name,
                error=FastMCPError(
                    code="TOOL_NOT_FOUND",
                    message=f"Tool '{tool_name}' not found",
                )
            )
            
        # Process the request based on the tool name
        if tool_name == "echo":
            validated_input = EchoInput(**request.tool_params)
            result = EchoOutput(echo=validated_input.message)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "get_tasks":
            validated_input = GetTasksInput(**request.tool_params)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            tasks = things.tasks(**kwargs)
            result = GetTasksOutput(tasks=tasks)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "get_task_detail":
            validated_input = GetTaskDetailInput(**request.tool_params)
            task = things.get(validated_input.uuid)
            if not task:
                return FastMCPErrorResponse(
                    id=request.id,
                    tool_name=tool_name,
                    error=FastMCPError(
                        code="RESOURCE_NOT_FOUND",
                        message=f"Task with UUID {validated_input.uuid} not found",
                        details={"uuid": validated_input.uuid}
                    )
                )
            result = GetTaskDetailOutput(task=task)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "get_projects":
            validated_input = GetProjectsInput(**request.tool_params)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            projects = things.projects(**kwargs)
            result = GetProjectsOutput(projects=projects)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "get_areas":
            validated_input = GetAreasInput(**request.tool_params)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            areas = things.areas(**kwargs)
            result = GetAreasOutput(areas=areas)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "get_tags":
            validated_input = GetTagsInput(**request.tool_params)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            tags = things.tags(**kwargs)
            result = GetTagsOutput(tags=tags)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "create_task":
            validated_input = CreateTaskInput(**request.tool_params)
            kwargs = {k: v for k, v in validated_input.model_dump().items() if v is not None}
            uuid = things.create_todo(**kwargs)
            result = CreateTaskOutput(uuid=uuid, title=validated_input.title)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "complete_task":
            validated_input = CompleteTaskInput(**request.tool_params)
            success = things.complete(validated_input.uuid)
            result = CompleteTaskOutput(success=success, uuid=validated_input.uuid)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "cancel_task":
            validated_input = CancelTaskInput(**request.tool_params)
            success = things.cancel(validated_input.uuid)
            result = CancelTaskOutput(success=success, uuid=validated_input.uuid)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
            
        elif tool_name == "update_task":
            validated_input = UpdateTaskInput(**request.tool_params)
            uuid = validated_input.uuid
            kwargs = {k: v for k, v in validated_input.model_dump().items() if k != "uuid" and v is not None}
            
            if not kwargs:
                return FastMCPErrorResponse(
                    id=request.id,
                    tool_name=tool_name,
                    error=FastMCPError(
                        code="INVALID_PARAMETERS",
                        message="No update parameters provided",
                        details={"uuid": uuid}
                    )
                )
            
            success = things.update(uuid, **kwargs)
            result = UpdateTaskOutput(success=success, uuid=uuid)
            return FastMCPResponse(
                id=request.id,
                tool_name=tool_name,
                response=result.model_dump()
            )
    
    except Exception as e:
        # Handle validation errors and other exceptions
        return FastMCPErrorResponse(
            id=request.id,
            tool_name=tool_name,
            error=FastMCPError(
                code="EXECUTION_ERROR",
                message=str(e),
                details={"exception_type": type(e).__name__}
            )
        )

# Legacy endpoint for backward compatibility
@app.post("/mcp")
async def legacy_mcp(body: Dict[str, Any]):
    """
    Legacy endpoint that transforms the request to the new FastMCP 2.0 format
    and forwards it to the new endpoint.
    """
    try:
        tool_name = body.get("tool")
        input_data = body.get("input", {})
        
        if not tool_name:
            raise HTTPException(status_code=400, detail="Missing 'tool' parameter")
        
        # Convert legacy request to FastMCP 2.0 format
        fastmcp_request = FastMCPRequest(
            id=str(uuid.uuid4()),
            tool_name=tool_name,
            tool_params=input_data
        )
        
        # Forward to the new endpoint handler
        result = await execute_tool(fastmcp_request)
        
        # Convert FastMCP 2.0 response back to legacy format for backward compatibility
        if isinstance(result, FastMCPResponse):
            return {"output": result.response}
        else:
            # If it's an error response
            raise HTTPException(
                status_code=500 if result.error.code == "EXECUTION_ERROR" else 400,
                detail=result.error.message
            )
    
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)