import operator
from typing import Annotated, TypedDict, List, Optional
from langgraph.graph import StateGraph, END
from app.services.llm import LiteLLMService 
from app.schemas.agent_io import MeetingMinutesResponse

class AgentState(TypedDict):
    transcript: str
    summaries: Annotated[List[str], operator.add]
    action_items_raw: Annotated[List[str], operator.add]
    decisions_raw: Annotated[List[str], operator.add]
    final_output: Optional[MeetingMinutesResponse]

class MeetingMinutesAgent:
    def __init__(self):
        self.llm = LiteLLMService()
        self.workflow = self._build_graph()

    def _chunk_text(self, text: str, chunk_size: int = 10000):
        return [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    async def summarize_node(self, state: AgentState):
        chunks = self._chunk_text(state["transcript"])
        summaries = [await self.llm.complete(f"Summarize this segment: {c}") for c in chunks]
        return {"summaries": summaries}

    async def extract_actions_node(self, state: AgentState):
        chunks = self._chunk_text(state["transcript"])
        actions = [await self.llm.complete(f"Extract action items (Who: Task): {c}") for c in chunks]
        return {"action_items_raw": actions}

    async def extract_decisions_node(self, state: AgentState):
        chunks = self._chunk_text(state["transcript"])
        decisions = [await self.llm.complete(f"Extract key decisions: {c}") for c in chunks]
        return {"decisions_raw": decisions}

    async def structure_node(self, state: AgentState):
        prompt = f"""
        Create a professional JSON object from these notes.
        Summaries: {" ".join(state['summaries'])}
        Actions: {"\n".join(state['action_items_raw'])}
        Decisions: {"\n".join(state['decisions_raw'])}
        Return ONLY valid JSON matching the MeetingMinutesResponse schema.
        """
        response = await self.llm.complete_json(prompt, response_model=MeetingMinutesResponse)
        return {"final_output": response}

    def _build_graph(self):
        builder = StateGraph(AgentState)
        builder.add_node("summarize", self.summarize_node)
        builder.add_node("extract_actions", self.extract_actions_node)
        builder.add_node("extract_decisions", self.extract_decisions_node)
        builder.add_node("structure", self.structure_node)
        
        builder.set_entry_point("summarize")
        builder.add_edge("summarize", "extract_actions")
        builder.add_edge("extract_actions", "extract_decisions")
        builder.add_edge("extract_decisions", "structure")
        builder.add_edge("structure", END)
        return builder.compile()

    async def run(self, input_data: dict):
        transcript = input_data.get("transcript", "")
        if not transcript:
            raise ValueError("Transcript is required")
            
        initial_state: AgentState = {
            "transcript": transcript, 
            "summaries": [], 
            "action_items_raw": [], 
            "decisions_raw": [], 
            "final_output": None
        }
        result = await self.workflow.ainvoke(initial_state)
        # Convert Pydantic model to dict for FastAPI
        return result["final_output"].model_dump() if result.get("final_output") else {}
