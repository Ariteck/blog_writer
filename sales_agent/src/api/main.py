import asyncio
import json
from fastapi import FastAPI, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from src.api.agents.agent import run_agent
from src.api.agents.blog_agent import run_blog_pipeline

app = FastAPI()

class AgentRequest(BaseModel):
    query: str

@app.get("/agent")
async def get_agent():
    return {"message": "Hello from the agent!"}

@app.post("/agent")
async def invoke_agent(request: AgentRequest):
    try:
        #data = await request.json()
        query_text = request.query
        print(f"Received query: {query_text}")
        # Await the coroutine directly with a 30-second timeout
        agent_result = await asyncio.wait_for(
            run_agent(query_text), 
            timeout=30.0
        )
        return agent_result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504, 
            detail="Agent processing timed out. Please try again."
        )
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))

@app.post("/blog")
async def invoke_blog_agent(request: AgentRequest):
    try:
        #data = await request.json()
        query_text = request.query
        print(f"Received query: {query_text}")
        # Await the coroutine directly with a 30-second timeout
        agent_result = await asyncio.wait_for(
            run_blog_pipeline(query_text),
            timeout=30.0
        )
        return agent_result
    except asyncio.TimeoutError:
        raise HTTPException(
            status_code=504, 
            detail="Agent processing timed out. Please try again."
        )
    except Exception as e:

        raise HTTPException(status_code=500, detail=str(e))