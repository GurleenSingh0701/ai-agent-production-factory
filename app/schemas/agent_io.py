from pydantic import BaseModel, Field
from typing import Dict, Any

class AgentRequest(BaseModel):
    input: Dict[str, Any]

class AgentResponse(BaseModel):
    status: str
    data: Dict[str, Any]

class EmailInput(BaseModel):
    email_body: str = Field(description="I am unhappy with my recent order #12345, it arrived broken.")
    sender_name: str = Field(description="John Doe")

class EmailTriageOutput(BaseModel):
    category: str = Field(description="Complaint, Sales, Support, or Spam")
    priority: str = Field(description="High, Medium, Low")
    draft_response: str = Field(..., description="The generated professional response")
    sentiment: str = Field(..., description="Positive, Neutral, Negative")


# Specific schema for the Lead Gen Agent
class LeadQualification(BaseModel):
    company_name: str = Field(description="Name of the company")
    industry: str = Field(description="The industry they operate in")
    fit_score: int = Field(description="Score from 0-100 based on ICP match")
    reasoning: str = Field(description="Detailed explanation for the score")
    recommended_action: str = Field(description="e.g., 'Book Call', 'Nurture', 'Discard'")
