import pytest
import asyncio
from app.services.scraper import scrape_website
from app.agents.day_01_lead_gen import LeadGenAgent

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
