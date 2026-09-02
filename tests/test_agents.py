import pytest
import asyncio
from app.services.scraper import scrape_website
from app.agents.day_01_lead_gen import LeadGenAgent

from app.agents.day_02_email_triage import EmailTriageAgent
from app.agents.day_03_meeting_minutes import MeetingMinutesAgent

@pytest.mark.asyncio
async def test_scrape_website():
    res = await scrape_website("https://example.com")
    assert res["success"] is True
    assert "Example Domain" in res["scraped_text"]

@pytest.mark.asyncio
async def test_lead_gen_agent_structure():
    agent = LeadGenAgent()
    assert agent.graph is not None
    graph_nodes = agent.graph.nodes
    assert "scrape_website" in graph_nodes
    assert "research" in graph_nodes
    assert "evaluate" in graph_nodes
    assert "score" in graph_nodes

@pytest.mark.asyncio
async def test_email_triage_agent_structure():
    agent = EmailTriageAgent()
    assert agent.graph is not None
    graph_nodes = agent.graph.nodes
    assert "triage" in graph_nodes
    assert "draft" in graph_nodes

@pytest.mark.asyncio
async def test_meeting_minutes_agent_structure():
    agent = MeetingMinutesAgent()
    assert agent.workflow is not None
    graph_nodes = agent.workflow.nodes
    assert "summarize" in graph_nodes
    assert "extract_actions" in graph_nodes
    assert "extract_decisions" in graph_nodes
    assert "structure" in graph_nodes

def test_clean_json_string():
    from app.services.llm import clean_json_string
    sample_with_json_header = 'json\n{\n  "summary": "Meeting notes"\n}'
    assert clean_json_string(sample_with_json_header) == '{\n  "summary": "Meeting notes"\n}'

    sample_with_backticks = '```json\n{\n  "summary": "Meeting notes"\n}\n```'
    assert clean_json_string(sample_with_backticks) == '{\n  "summary": "Meeting notes"\n}'



