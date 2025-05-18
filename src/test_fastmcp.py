import pytest
from unittest.mock import patch, MagicMock
import os
import json
from fastmcp.testing import TestClient
from main import app

client = TestClient(app)

def test_root():
    response = client.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "Simple FastMCP Server"}

def test_echo_tool():
    response = client.mcp_invoke(
        "echo",
        {"message": "Hello, world!"}
    )
    assert response.status_code == 200
    assert response.json() == {"echo": "Hello, world!"}

@pytest.mark.skipif(
    not os.path.exists(os.path.expanduser("~/Library/Group Containers/JLMPQHK86H.com.culturedcode.ThingsMac/Things Database.thingsdatabase/main.sqlite")) 
    and not os.environ.get("THINGS_DB_PATH"),
    reason="Things database not found"
)
def test_things_list_tool_real():
    """Test the things_list tool with actual Things database if available."""
    response = client.mcp_invoke(
        "things_list",
        {
            "entity_type": "todo",
            "include_completed": False,
            "include_canceled": False
        }
    )
    assert response.status_code == 200
    result = response.json()
    assert "items" in result
    assert "count" in result
    assert isinstance(result["items"], list)
    assert isinstance(result["count"], int)
    assert result["count"] == len(result["items"])

@patch("things.todos")
def test_things_list_tool_mocked(mock_todos):
    """Test the things_list tool with mocked Things data."""
    # Mock the things.todos function to return sample data
    mock_todos.return_value = [
        {"uuid": "test-uuid-1", "title": "Test Todo 1", "status": "incomplete"},
        {"uuid": "test-uuid-2", "title": "Test Todo 2", "status": "incomplete"}
    ]
    
    response = client.mcp_invoke(
        "things_list",
        {
            "entity_type": "todo",
            "include_completed": False,
            "include_canceled": False
        }
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["count"] == 2
    assert len(result["items"]) == 2
    assert result["items"][0]["title"] == "Test Todo 1"
    
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
    
    response = client.mcp_invoke(
        "things_get",
        {"uuid": "test-uuid-1"}
    )
    
    assert response.status_code == 200
    result = response.json()
    assert result["item"]["title"] == "Test Todo 1"
    
    # Verify the mock was called with the correct parameters
    mock_get.assert_called_once_with("test-uuid-1")

@patch("things.get")
def test_things_get_tool_not_found(mock_get):
    """Test the things_get tool when the item is not found."""
    # Mock the things.get function to return None (item not found)
    mock_get.return_value = None
    
    with pytest.raises(ValueError, match="not found"):
        client.mcp_invoke(
            "things_get",
            {"uuid": "nonexistent-uuid"}
        )