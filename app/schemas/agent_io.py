from pydantic import BaseModel, Field
from typing import Dict, Any

class AgentRequest(BaseModel):
    input: Dict[str, Any]

class AgentResponse(BaseModel):
    status: str
    data: Dict[str, Any]

# Specific schema for the Lead Gen Agent
class LeadQualification(BaseModel):
    company_name: str = Field(description="Name of the company")
    industry: str = Field(description="The industry they operate in")
    fit_score: int = Field(description="Score from 0-100 based on ICP match")
    reasoning: str = Field(description="Detailed explanation for the score")
    recommended_action: str = Field(description="e.g., 'Book Call', 'Nurture', 'Discard'")
