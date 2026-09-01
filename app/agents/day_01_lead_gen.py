from typing import TypedDict, Dict, Any
from langgraph.graph import StateGraph, END
from app.agents.base import BaseAgent
from app.services.llm import call_llm
from app.services.scraper import scrape_website
import json
import re
import ast

def parse_json_from_llm(text: str) -> Dict[str, Any]:
    if not text:
        return {"error": "Empty LLM response"}
    
    # Direct json loads
    try:
        return json.loads(text)
    except Exception:
        pass

    # Strip markdown code blocks
    cleaned = text.strip()
    if cleaned.startswith("```"):
        lines = cleaned.splitlines()
        if lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].startswith("```"):
            lines = lines[:-1]
        cleaned = "\n".join(lines).strip()
        try:
            return json.loads(cleaned)
        except Exception:
            pass

    # Extract matching {...} block using regex
    match = re.search(r"(\{[\s\S]*\})", text)
    if match:
        block = match.group(1)
        try:
            return json.loads(block)
        except Exception:
            pass
        try:
            val = ast.literal_eval(block)
            if isinstance(val, dict):
                return val
        except Exception:
            pass

    return {"error": "Failed to parse JSON", "raw_response": text[:300]}

# 1. Define the State
class AgentState(TypedDict):
    url: str
    icp: str  # Ideal Customer Profile
    scraped_content: str
    research_notes: str
    evaluation: str
    final_json: Dict[str, Any]

class LeadGenAgent(BaseAgent):
    def build_graph(self):
        workflow = StateGraph(AgentState)

        # --- NODE 1: Scrape Website (Power-Up) ---
        async def scrape_website_node(state: AgentState):
            scrape_res = await scrape_website(state['url'])
            return {"scraped_content": scrape_res.get("scraped_text", "")}

        # --- NODE 2: Research ---
        async def research_node(state: AgentState):
            prompt = f"""
            Research the following company URL: {state['url']}
            
            LIVE SCRAPED WEBSITE CONTENT:
            {state.get('scraped_content', 'No content scraped.')}
            
            Based on the live scraped website data above, identify their core product, target audience, and business model.
            Provide a concise, factual summary of their business.
            """
            res = await call_llm(prompt)
            return {"research_notes": res}

        # --- NODE 3: Evaluate ---
        async def evaluate_node(state: AgentState):
            prompt = f"""
            COMPARE THE RESEARCH AGAINST THE ICP:
            Research: {state['research_notes']}
            Ideal Customer Profile (ICP): {state['icp']}
            
            Analyze the gaps and overlaps. Does this company fit the ICP? 
            Be critical and objective.
            """
            res = await call_llm(prompt)
            return {"evaluation": res}

        # --- NODE 4: Score (The structured output node) ---
        async def score_node(state: AgentState):
            prompt = f"""
            Based on the following evaluation, provide a final lead qualification in JSON format.
            Evaluation: {state['evaluation']}
            
            Return ONLY a valid raw JSON object (no markdown code blocks, no ```json, no explanations) with these exact keys: 
            "company_name", "industry", "fit_score", "reasoning", "recommended_action".
            Example format:
            {{"company_name": "Example Inc", "industry": "Technology", "fit_score": 85, "reasoning": "Fits target profile", "recommended_action": "Book Call"}}
            """
            res = await call_llm(prompt, json_mode=True)
            return {"final_json": parse_json_from_llm(res)}

        # Define the Graph connections
        workflow.add_node("scrape_website", scrape_website_node)
        workflow.add_node("research", research_node)
        workflow.add_node("evaluate", evaluate_node)
        workflow.add_node("score", score_node)

        workflow.set_entry_point("scrape_website")
        workflow.add_edge("scrape_website", "research")
        workflow.add_edge("research", "evaluate")
        workflow.add_edge("evaluate", "score")
        workflow.add_edge("score", END)

        return workflow

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        app = self.graph.compile()
        # We expect input_data to have 'url' and 'icp'
        result = await app.ainvoke(input_data)
        return result["final_json"]
