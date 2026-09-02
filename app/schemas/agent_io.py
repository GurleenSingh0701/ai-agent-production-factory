from pydantic import BaseModel, Field
from typing import Dict, Any, List, Optional

class AgentRequest(BaseModel):
    input: Dict[str, Any]

class AgentResponse(BaseModel):
    status: str
    data: Dict[str, Any]

# Day 1: Lead Gen
class LeadQualification(BaseModel):
    company_name: str = Field(description="Name of the company")
    industry: str = Field(description="The industry they operate in")
    fit_score: int = Field(description="Score from 0-100 based on ICP match")
    reasoning: str = Field(description="Detailed explanation for the score")
    recommended_action: str = Field(description="e.g., 'Book Call', 'Nurture', 'Discard'")

# Day 2: Email Triage
class EmailInput(BaseModel):
    email_body: str = Field(..., description="Email text to analyze and triage")
    sender_name: str = Field(..., description="Name of the email sender")

class EmailTriageOutput(BaseModel):
    category: str = Field(description="Complaint, Sales, Support, or Spam")
    priority: str = Field(description="High, Medium, Low")
    draft_response: str = Field(..., description="The generated professional response")
    sentiment: str = Field(..., description="Positive, Neutral, Negative")

# Day 3: Meeting Minutes
class ActionItem(BaseModel):
    assignee: str = Field(default="Unassigned", description="Who is responsible for the task")
    task: str = Field(default="", description="Clear description of what needs to be done")
    deadline: Optional[str] = Field(default=None, description="Mentioned date or timeframe, if any")

class MeetingMinutesResponse(BaseModel):
    summary: str = Field(default="", description="High-level overview of the meeting themes")
    action_items: List[ActionItem] = Field(default_factory=list, description="List of extracted tasks")
    key_decisions: List[str] = Field(default_factory=list, description="List of final decisions made")
