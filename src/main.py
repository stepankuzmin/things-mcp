from fastmcp import FastMCP, Tool, ExecuteRequest, ExecuteResponse, ExecuteErrorResponse, Error
from fastmcp.models import ToolMetadata
import things
import uuid
from typing import Dict, Any, List, Optional
from datetime import datetime
import uvicorn

app = FastMCP(
    title="Things FastMCP Server",
    description="FastMCP 2.0 server for Things 3 integration",
    version="2.0.0"
)

# Tool-specific input parameters
class EchoParams:
    def __init__(self, message: str):
        self.message = message

class GetTasksParams:
    def __init__(self, status: Optional[str] = None, tag: Optional[str] = None, 
                 search: Optional[str] = None, area: Optional[str] = None,
                 project: Optional[str] = None, heading: Optional[str] = None,
                 limit: Optional[int] = None):
        self.status = status
        self.tag = tag
        self.search = search
        self.area = area
        self.project = project
        self.heading = heading
        self.limit = limit

class GetTaskDetailParams:
    def __init__(self, uuid: str):
        self.uuid = uuid

class GetProjectsParams:
    def __init__(self, status: Optional[str] = None, tag: Optional[str] = None,
                 search: Optional[str] = None, area: Optional[str] = None,
                 limit: Optional[int] = None):
        self.status = status
        self.tag = tag
        self.search = search
        self.area = area
        self.limit = limit

class GetAreasParams:
    def __init__(self, search: Optional[str] = None):
        self.search = search

class GetTagsParams:
    def __init__(self, search: Optional[str] = None):
        self.search = search

class CreateTaskParams:
    def __init__(self, title: str, notes: Optional[str] = None, 
                 tags: Optional[List[str]] = None, when: Optional[str] = None,
                 deadline: Optional[str] = None, checklist: Optional[List[str]] = None,
                 project: Optional[str] = None, area: Optional[str] = None,
                 heading: Optional[str] = None):
        self.title = title
        self.notes = notes
        self.tags = tags
        self.when = when
        self.deadline = deadline
        self.checklist = checklist
        self.project = project
        self.area = area
        self.heading = heading

class CompleteTaskParams:
    def __init__(self, uuid: str):
        self.uuid = uuid

class CancelTaskParams:
    def __init__(self, uuid: str):
        self.uuid = uuid

class UpdateTaskParams:
    def __init__(self, uuid: str, title: Optional[str] = None, 
                 notes: Optional[str] = None, tags: Optional[List[str]] = None,
                 when: Optional[str] = None, deadline: Optional[str] = None,
                 checklist: Optional[List[str]] = None):
        self.uuid = uuid
        self.title = title
        self.notes = notes
        self.tags = tags
        self.when = when
        self.deadline = deadline
        self.checklist = checklist

# Tool implementations
class EchoTool(Tool):
    name = "echo"
    description = "Echoes back the provided message"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = EchoParams(**params)
        return {"echo": validated_params.message}

class GetTasksTool(Tool):
    name = "get_tasks"
    description = "Retrieve tasks with flexible filtering options"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = GetTasksParams(**params)
        kwargs = {k: v for k, v in validated_params.__dict__.items() if v is not None}
        tasks = things.tasks(**kwargs)
        return {"tasks": tasks}

class GetTaskDetailTool(Tool):
    name = "get_task_detail"
    description = "Get detailed information about a specific task"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = GetTaskDetailParams(**params)
        task = things.get(validated_params.uuid)
        if not task:
            raise ValueError(f"Task with UUID {validated_params.uuid} not found")
        return {"task": task}

class GetProjectsTool(Tool):
    name = "get_projects"
    description = "Retrieve projects with filtering options"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = GetProjectsParams(**params)
        kwargs = {k: v for k, v in validated_params.__dict__.items() if v is not None}
        projects = things.projects(**kwargs)
        return {"projects": projects}

class GetAreasTool(Tool):
    name = "get_areas"
    description = "List organizational areas"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = GetAreasParams(**params)
        kwargs = {k: v for k, v in validated_params.__dict__.items() if v is not None}
        areas = things.areas(**kwargs)
        return {"areas": areas}

class GetTagsTool(Tool):
    name = "get_tags"
    description = "List all available tags"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = GetTagsParams(**params)
        kwargs = {k: v for k, v in validated_params.__dict__.items() if v is not None}
        tags = things.tags(**kwargs)
        return {"tags": tags}

class CreateTaskTool(Tool):
    name = "create_task"
    description = "Create a new task with optional metadata"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = CreateTaskParams(**params)
        kwargs = {k: v for k, v in validated_params.__dict__.items() if v is not None}
        task_uuid = things.create_todo(**kwargs)
        return {"uuid": task_uuid, "title": validated_params.title}

class CompleteTaskTool(Tool):
    name = "complete_task"
    description = "Mark a task as completed"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = CompleteTaskParams(**params)
        success = things.complete(validated_params.uuid)
        return {"success": success, "uuid": validated_params.uuid}

class CancelTaskTool(Tool):
    name = "cancel_task"
    description = "Mark a task as canceled"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = CancelTaskParams(**params)
        success = things.cancel(validated_params.uuid)
        return {"success": success, "uuid": validated_params.uuid}

class UpdateTaskTool(Tool):
    name = "update_task"
    description = "Update an existing task's attributes"
    version = "1.0.0"
    
    def execute(self, params: Dict[str, Any]) -> Dict[str, Any]:
        validated_params = UpdateTaskParams(**params)
        uuid = validated_params.uuid
        kwargs = {k: v for k, v in validated_params.__dict__.items() if k != "uuid" and v is not None}
        
        if not kwargs:
            raise ValueError("No update parameters provided")
        
        success = things.update(uuid, **kwargs)
        return {"success": success, "uuid": uuid}

# Register tools with the app
app.register_tool(EchoTool())
app.register_tool(GetTasksTool())
app.register_tool(GetTaskDetailTool())
app.register_tool(GetProjectsTool())
app.register_tool(GetAreasTool())
app.register_tool(GetTagsTool())
app.register_tool(CreateTaskTool())
app.register_tool(CompleteTaskTool())
app.register_tool(CancelTaskTool())
app.register_tool(UpdateTaskTool())

# Root endpoint for health check
@app.get("/")
async def root():
    return {
        "service": "Things FastMCP Server",
        "version": "2.0.0",
        "status": "healthy",
        "timestamp": datetime.now().isoformat()
    }

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
            return app.create_error_response(
                status_code=400,
                detail="Missing 'tool' parameter"
            )
        
        # Convert legacy request to FastMCP 2.0 format
        execute_request = ExecuteRequest(
            id=str(uuid.uuid4()),
            tool_name=tool_name,
            tool_params=input_data
        )
        
        # Execute the tool
        try:
            result = app.execute_tool(execute_request)
            
            # Convert FastMCP 2.0 response back to legacy format for backward compatibility
            if isinstance(result, ExecuteResponse):
                return {"output": result.response}
            else:
                # If it's an error response
                return app.create_error_response(
                    status_code=500 if result.error.code == "EXECUTION_ERROR" else 400,
                    detail=result.error.message
                )
        except ValueError as e:
            return app.create_error_response(status_code=400, detail=str(e))
        except Exception as e:
            return app.create_error_response(status_code=500, detail=str(e))
    
    except Exception as e:
        return app.create_error_response(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)