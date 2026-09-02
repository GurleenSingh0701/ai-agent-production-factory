from fastapi import FastAPI, HTTPException
from app.schemas.agent_io import AgentRequest, AgentResponse
from app.agents.day_01_lead_gen import LeadGenAgent 
from app.agents.day_02_email_triage import EmailTriageAgent 
from app.agents.day_03_meeting_minutes import MeetingMinutesAgent
import uvicorn

app = FastAPI(title="AI Agent Production Factory")

AGENTS = {
    "lead_gen": LeadGenAgent(),
    "email_triage": EmailTriageAgent(),
    "meeting_minutes": MeetingMinutesAgent(),
}

@app.post("/run/{agent_id}", response_model=AgentResponse)
async def run_agent(agent_id: str, request: AgentRequest):
    if agent_id not in AGENTS:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    try:
        agent = AGENTS[agent_id]
        result = await agent.run(request.input)
        return {"status": "success", "data": result}
    except Exception as e:
        return {"status": "error", "data": {"error": str(e)}}

@app.get("/health")
async def health_check():
    return {"status": "awake", "message": "Agent Factory is running!"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
