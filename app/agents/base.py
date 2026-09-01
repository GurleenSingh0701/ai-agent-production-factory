from abc import ABC, abstractmethod
from typing import Any, Dict
from langgraph.graph import StateGraph

class BaseAgent(ABC):
    def __init__(self):
        self.graph = self.build_graph()

    @abstractmethod
    def build_graph(self) -> StateGraph:
        """Define the LangGraph logic here"""
        pass

    async def run(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute the agent graph"""
        # This is where you'll call the compiled graph.invoke()
        app = self.graph.compile()
        return await app.ainvoke(input_data)
