from __future__ import annotations

from langgraph.graph import END, StateGraph
from langgraph.graph.state import CompiledStateGraph

from agent.nodes.analyze import analyze
from agent.nodes.ask import ask_question
from agent.nodes.check import check_completeness
from agent.nodes.draft import generate_draft
from agent.state import IssueState


def _route_after_check(state: IssueState) -> str:
    """Route based on completeness_status after the check node."""
    status = state.get("completeness_status", "insufficient")
    if status == "confirmed":
        return END
    if status == "sufficient":
        return "generate_draft"
    return "ask_question"


def create_graph() -> CompiledStateGraph:
    """Build and compile the issue-creation LangGraph."""
    graph = StateGraph(IssueState)

    graph.add_node("analyze", analyze)
    graph.add_node("check_completeness", check_completeness)
    graph.add_node("ask_question", ask_question)
    graph.add_node("generate_draft", generate_draft)

    graph.set_entry_point("analyze")
    graph.add_edge("analyze", "check_completeness")
    graph.add_conditional_edges("check_completeness", _route_after_check)
    graph.add_edge("ask_question", END)
    graph.add_edge("generate_draft", END)

    return graph.compile()
