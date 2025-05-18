import pytest
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock
import os
import json
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Simple FastMCP Server"}

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

@pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/main.sqlite")) 
    and not os.environ.get("THINGS_DB_PATH"),
    reason="Things database not found"
)
def test_things_list_tool_real():
    """Test the things_list tool with actual Things database if available."""
    response = client.post(
        "/mcp",
        json={
            "tool": "things_list",
            "input": {
                "entity_type": "todo",
                "include_completed": False,
                "include_canceled": False
            }
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "output" in result
    assert "items" in result["output"]
    assert "count" in result["output"]
    assert isinstance(result["output"]["items"], list)
    assert isinstance(result["output"]["count"], int)
    assert result["output"]["count"] == len(result["output"]["items"])

@patch("things.todos")
def test_things_list_tool_mocked(mock_todos):
    """Test the things_list tool with mocked Things data."""
    # Mock the things.todos function to return sample data
    mock_todos.return_value = [
        {"uuid": "test-uuid-1", "title": "Test Todo 1", "status": "incomplete"},
        {"uuid": "test-uuid-2", "title": "Test Todo 2", "status": "incomplete"}
    ]
    
    response = client.post(
        "/mcp",
        json={
            "tool": "things_list",
            "input": {
                "entity_type": "todo",
                "include_completed": False,
                "include_canceled": False
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["output"]["count"] == 2
    assert len(result["output"]["items"]) == 2
    assert result["output"]["items"][0]["title"] == "Test Todo 1"
    
    # Verify the mock was called with the correct parameters
    mock_todos.assert_called_once_with(include_completed=False, include_canceled=False)

@patch("things.get")
def test_things_get_tool_mocked(mock_get):
    """Test the things_get tool with mocked Things data."""
    # Mock the things.get function to return sample data
    mock_get.return_value = {
        "uuid": "test-uuid-1", 
        "title": "Test Todo 1", 
        "status": "incomplete"
    }
    
    response = client.post(
        "/mcp",
        json={
            "tool": "things_get",
            "input": {
                "uuid": "test-uuid-1"
            }
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["output"]["item"]["title"] == "Test Todo 1"
    
    # Verify the mock was called with the correct parameters
    mock_get.assert_called_once_with("test-uuid-1")

@patch("things.get")
def test_things_get_tool_not_found(mock_get):
    """Test the things_get tool when the item is not found."""
    # Mock the things.get function to return None (item not found)
    mock_get.return_value = None
    
    response = client.post(
        "/mcp",
        json={
            "tool": "things_get",
            "input": {
                "uuid": "nonexistent-uuid"
            }
        }
    )
    
    assert response.status_code == 404
    assert "not found" in response.json()["detail"]