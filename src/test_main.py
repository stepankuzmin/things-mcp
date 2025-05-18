import pytest
from fastapi.testclient import TestClient
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