import pytest
import uuid
from unittest.mock import patch, MagicMock
from main import app
from fastmcp.testclient import TestClient

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert "service" in response.json()
    assert response.json()["service"] == "Things FastMCP Server"
    assert response.json()["version"] == "2.0.0"
    assert response.json()["status"] == "healthy"
    assert "timestamp" in response.json()

def test_echo_tool():
    response = client.post(
        "/mcp",
        json={
            "tool": "echo",
            "input": {
                "message": "Hello, world!"
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "echo": "Hello, world!"
        }
    }

def test_invalid_tool():
    response = client.post(
        "/mcp",
        json={
            "tool": "invalid_tool",
            "input": {}
        }
    )
    assert response.status_code == 404

@patch('things.tasks')
def test_get_tasks(mock_tasks):
    # Mock data
    mock_tasks.return_value = [
        {"uuid": "1234", "title": "Test Task", "status": "upcoming"}
    ]
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_tasks",
            "input": {
                "status": "upcoming",
                "limit": 10
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "tasks": [{"uuid": "1234", "title": "Test Task", "status": "upcoming"}]
        }
    }
    mock_tasks.assert_called_once_with(status="upcoming", limit=10)

@patch('things.get')
def test_get_task_detail(mock_get):
    # Mock data
    task_uuid = "test-uuid"
    mock_get.return_value = {
        "uuid": task_uuid,
        "title": "Task Detail",
        "notes": "Task notes"
    }
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_task_detail",
            "input": {
                "uuid": task_uuid
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "task": {
                "uuid": task_uuid,
                "title": "Task Detail",
                "notes": "Task notes"
            }
        }
    }
    mock_get.assert_called_once_with(task_uuid)

@patch('things.get')
def test_get_task_detail_not_found(mock_get):
    # Task not found
    mock_get.return_value = None
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_task_detail",
            "input": {
                "uuid": "nonexistent-uuid"
            }
        }
    )
    assert response.status_code == 404

@patch('things.projects')
def test_get_projects(mock_projects):
    # Mock data
    mock_projects.return_value = [
        {"uuid": "proj-1", "title": "Test Project", "status": "upcoming"}
    ]
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_projects",
            "input": {
                "status": "upcoming"
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "projects": [{"uuid": "proj-1", "title": "Test Project", "status": "upcoming"}]
        }
    }
    mock_projects.assert_called_once_with(status="upcoming")

@patch('things.areas')
def test_get_areas(mock_areas):
    # Mock data
    mock_areas.return_value = [
        {"uuid": "area-1", "title": "Test Area"}
    ]
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_areas",
            "input": {
                "search": "Test"
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "areas": [{"uuid": "area-1", "title": "Test Area"}]
        }
    }
    mock_areas.assert_called_once_with(search="Test")

@patch('things.tags')
def test_get_tags(mock_tags):
    # Mock data
    mock_tags.return_value = [
        {"uuid": "tag-1", "title": "TestTag"}
    ]
    
    response = client.post(
        "/mcp",
        json={
            "tool": "get_tags",
            "input": {}
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "tags": [{"uuid": "tag-1", "title": "TestTag"}]
        }
    }
    mock_tags.assert_called_once_with()

@patch('things.create_todo')
def test_create_task(mock_create_todo):
    # Mock data
    task_uuid = "new-task-uuid"
    mock_create_todo.return_value = task_uuid
    
    response = client.post(
        "/mcp",
        json={
            "tool": "create_task",
            "input": {
                "title": "New Task",
                "notes": "Task notes",
                "when": "today"
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "uuid": task_uuid,
            "title": "New Task"
        }
    }
    mock_create_todo.assert_called_once_with(title="New Task", notes="Task notes", when="today")

@patch('things.complete')
def test_complete_task(mock_complete):
    # Mock data
    task_uuid = "task-to-complete"
    mock_complete.return_value = True
    
    response = client.post(
        "/mcp",
        json={
            "tool": "complete_task",
            "input": {
                "uuid": task_uuid
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "success": True,
            "uuid": task_uuid
        }
    }
    mock_complete.assert_called_once_with(task_uuid)

@patch('things.cancel')
def test_cancel_task(mock_cancel):
    # Mock data
    task_uuid = "task-to-cancel"
    mock_cancel.return_value = True
    
    response = client.post(
        "/mcp",
        json={
            "tool": "cancel_task",
            "input": {
                "uuid": task_uuid
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "success": True,
            "uuid": task_uuid
        }
    }
    mock_cancel.assert_called_once_with(task_uuid)

@patch('things.update')
def test_update_task(mock_update):
    # Mock data
    task_uuid = "task-to-update"
    mock_update.return_value = True
    
    response = client.post(
        "/mcp",
        json={
            "tool": "update_task",
            "input": {
                "uuid": task_uuid,
                "title": "Updated Title",
                "notes": "Updated notes"
            }
        }
    )
    assert response.status_code == 200
    assert response.json() == {
        "output": {
            "success": True,
            "uuid": task_uuid
        }
    }
    mock_update.assert_called_once_with(task_uuid, title="Updated Title", notes="Updated notes")

def test_update_task_no_params():
    response = client.post(
        "/mcp",
        json={
            "tool": "update_task",
            "input": {
                "uuid": "some-uuid"
                # No other parameters provided
            }
        }
    )
    assert response.status_code == 400
    assert "No update parameters provided" in response.json()["detail"]

# FastMCP 2.0 Tests

def test_fastmcp_tools_discovery():
    response = client.get("/fastmcp/v2/tools")
    assert response.status_code == 200
    tools = response.json()["tools"]
    assert len(tools) > 0
    # Verify that each tool has the required fields
    for tool in tools:
        assert "name" in tool
        assert "description" in tool
        assert "version" in tool
        assert "input_schema" in tool
        assert "output_schema" in tool

def test_fastmcp_echo_execute():
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "echo",
            "tool_params": {
                "message": "Hello, FastMCP 2.0!"
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "echo"
    assert result["response"]["echo"] == "Hello, FastMCP 2.0!"

def test_fastmcp_invalid_tool():
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "non_existent_tool",
            "tool_params": {}
        }
    )
    assert response.status_code == 200  # FastMCP 2.0 returns 200 with error object
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "non_existent_tool"
    assert "error" in result
    assert result["error"]["code"] == "TOOL_NOT_FOUND"

@patch('things.tasks')
def test_fastmcp_get_tasks(mock_tasks):
    # Mock data
    mock_tasks.return_value = [
        {"uuid": "1234", "title": "Test Task", "status": "upcoming"}
    ]
    
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "get_tasks",
            "tool_params": {
                "status": "upcoming",
                "limit": 10
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "get_tasks"
    assert result["response"]["tasks"] == [{"uuid": "1234", "title": "Test Task", "status": "upcoming"}]
    mock_tasks.assert_called_once_with(status="upcoming", limit=10)

@patch('things.get')
def test_fastmcp_get_task_detail(mock_get):
    # Mock data
    task_uuid = "test-uuid-fastmcp"
    mock_get.return_value = {
        "uuid": task_uuid,
        "title": "FastMCP Task",
        "notes": "Task notes"
    }
    
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "get_task_detail",
            "tool_params": {
                "uuid": task_uuid
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "get_task_detail"
    assert result["response"]["task"]["uuid"] == task_uuid
    assert result["response"]["task"]["title"] == "FastMCP Task"
    mock_get.assert_called_once_with(task_uuid)

@patch('things.get')
def test_fastmcp_get_task_detail_not_found(mock_get):
    # Task not found
    mock_get.return_value = None
    
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "get_task_detail",
            "tool_params": {
                "uuid": "nonexistent-uuid"
            }
        }
    )
    assert response.status_code == 200  # FastMCP 2.0 returns 200 with error object
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "get_task_detail"
    assert "error" in result
    assert result["error"]["code"] == "EXECUTION_ERROR"

@patch('things.update')
def test_fastmcp_update_task_no_params(mock_update):
    task_uuid = "task-without-params"
    
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "update_task",
            "tool_params": {
                "uuid": task_uuid
                # No other parameters provided
            }
        }
    )
    assert response.status_code == 200  # FastMCP 2.0 returns 200 with error object
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "update_task"
    assert "error" in result
    assert result["error"]["code"] == "EXECUTION_ERROR"
    assert "No update parameters provided" in result["error"]["message"]
    mock_update.assert_not_called()

@patch('things.create_todo')
def test_fastmcp_create_task(mock_create_todo):
    # Mock data
    task_uuid = "new-fastmcp-task-uuid"
    mock_create_todo.return_value = task_uuid
    
    test_id = str(uuid.uuid4())
    response = client.post(
        "/fastmcp/v2/execute",
        json={
            "id": test_id,
            "tool_name": "create_task",
            "tool_params": {
                "title": "New FastMCP Task",
                "notes": "Task created via FastMCP 2.0",
                "when": "today"
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert result["id"] == test_id
    assert result["tool_name"] == "create_task"
    assert result["response"]["uuid"] == task_uuid
    assert result["response"]["title"] == "New FastMCP Task"
    mock_create_todo.assert_called_once_with(
        title="New FastMCP Task", 
        notes="Task created via FastMCP 2.0", 
        when="today"
    )