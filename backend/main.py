"""
FastAPI wrapper around the agent loop.

Run from the backend/ directory with:
    uvicorn main:app --reload
"""

from fastapi import FastAPI
from pydantic import BaseModel

from agent.loop import run_agent

app = FastAPI(title="Longrest Agent API")


class RunAgentRequest(BaseModel):
    issue_description: str


class RunAgentResponse(BaseModel):
    summary: str


@app.post("/run-agent", response_model=RunAgentResponse)
def run_agent_endpoint(request: RunAgentRequest) -> RunAgentResponse:
    summary = run_agent(request.issue_description)
    return RunAgentResponse(summary=summary)
