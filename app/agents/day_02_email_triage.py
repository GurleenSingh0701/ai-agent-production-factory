import json
from typing import Any, TypedDict
from langgraph.graph import StateGraph, END

# Import your specific LLM wrapper
from app.services.llm import call_llm 
from app.agents.base import BaseAgent
from app.schemas.agent_io import EmailInput, EmailTriageOutput

# Define the State for LangGraph
class AgentState(TypedDict):
    email_body: str
    sender_name: str
    category: str
    priority: str
    sentiment: str
    draft_response: str

class EmailTriageAgent(BaseAgent):
    def build_graph(self) -> StateGraph:
        workflow = StateGraph(AgentState)

        # Add Nodes (Note: these are now async)
        workflow.add_node("triage", self.triage_node)
        workflow.add_node("draft", self.draft_node)

        # Define Edges
        workflow.set_entry_point("triage")
        workflow.add_edge("triage", "draft")
        workflow.add_edge("draft", END)

        return workflow

    async def triage_node(self, state: AgentState):
        """
        Analyzes email and returns JSON categorization.
        Uses the json_mode=True feature of your call_llm wrapper.
        """
        prompt = f"""
        Analyze the following email from {state['sender_name']}:
        ---
        {state['email_body']}
        ---
        Categorize this email into one of these categories: Complaint, Sales, Support, Spam.
        Determine the priority (High, Medium, Low) and sentiment (Positive, Neutral, Negative).
        
        Return ONLY a JSON object with these keys:
        "category": "...",
        "priority": "...",
        "sentiment": "..."
        """
        
        # Using your async wrapper with json_mode enabled
        response_str = await call_llm(prompt, json_mode=True)
        
        try:
            data = json.loads(response_str)
        except json.JSONDecodeError:
            # Fallback in case LLM returns non-json
            data = {"category": "Support", "priority": "Medium", "sentiment": "Neutral"}

        return {
            "category": data.get("category", "Support"),
            "priority": data.get("priority", "Medium"),
            "sentiment": data.get("sentiment", "Neutral")
        }

    async def draft_node(self, state: AgentState):
        """
        Generates a response based on the category determined in the triage node.
        """
        style_guide = {
            "Complaint": "Empathetic, apologetic, and solution-oriented. Avoid defensive language.",
            "Sales": "Professional, enthusiastic, and focused on value proposition.",
            "Support": "Clear, instructional, patient, and helpful.",
            "Spam": "Short, polite, but firm refusal to engage."
        }
        
        style = style_guide.get(state['category'], "Professional and concise.")
        
        prompt = f"""
        You are a professional communications assistant. 
        Context: The email is categorized as {state['category']} with a {state['sentiment']} sentiment.
        Style Guide: {style}
        
        Original Email from {state['sender_name']}:
        {state['email_body']}
        
        Write a professional draft response. Sign off as 'The Team'.
        """
        
        # Using your async wrapper
        draft = await call_llm(prompt)
        return {"draft_response": draft}

    async def run(self, input_data: dict[str, Any] | EmailInput) -> dict[str, Any]:
        """
        Main entry point called by app/main.py.
        Validates input against EmailInput schema and returns validated EmailTriageOutput dict.
        """
        # Validate input using EmailInput schema
        if isinstance(input_data, EmailInput):
            validated_input = input_data
        else:
            validated_input = EmailInput.model_validate(input_data)

        initial_state: AgentState = {
            "email_body": validated_input.email_body,
            "sender_name": validated_input.sender_name,
            "category": "",
            "priority": "",
            "sentiment": "",
            "draft_response": ""
        }
        
        app = self.graph.compile()
        result = await app.ainvoke(initial_state)
        
        # Enforce type safety and schema validation on the output
        output = EmailTriageOutput(
            category=result.get("category", "Support"),
            priority=result.get("priority", "Medium"),
            sentiment=result.get("sentiment", "Neutral"),
            draft_response=result.get("draft_response", "")
        )
        return output.model_dump()
