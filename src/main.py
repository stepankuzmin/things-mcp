from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Dict, Any

app = FastAPI()

class EchoInput(BaseModel):
    message: str

class EchoOutput(BaseModel):
    echo: str

@app.get("/")
async def root():
    return {"message": "Simple FastMCP Server"}

@app.post("/mcp")
async def handle_mcp(body: Dict[str, Any]):
    try:
        tool_name = body.get("tool")
        
        # Check for invalid tool first
        if tool_name != "echo":
            raise HTTPException(status_code=404, detail=f"Tool {tool_name} not found")
        
        input_data = body.get("input", {})
        validated_input = EchoInput(**input_data)
        result = EchoOutput(echo=validated_input.message)
        return {"output": result.model_dump()}
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)