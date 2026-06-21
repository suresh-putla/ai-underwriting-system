"""
Orchestrator Agent
LangGraph workflow that orchestrates document submission status checking
"""

from typing import TypedDict, List
from langgraph.graph import StateGraph, END
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.doc_retriever_agent import doc_retriever_node, DocRetrieverState


def format_output_node(state: DocRetrieverState) -> DocRetrieverState:
    """
    Format the final output message based on pending documents.

    Args:
        state: Current state with pending_documents

    Returns:
        Updated state with formatted output message
    """
    if state.get("error"):
        state["output"] = f"Error: {state['error']}"
        return state

    pending_docs = state.get("pending_documents", [])

    if pending_docs:
        # Documents needed
        docs_list = ", ".join(pending_docs)
        state["output"] = f"Documents needed: {docs_list}"
    else:
        # All documents submitted
        state["output"] = "All required documents have been submitted successfully."

    return state


def build_orchestrator_graph() -> StateGraph:
    """
    Build the LangGraph workflow for document submission status.

    Returns:
        Compiled LangGraph workflow
    """
    # Define the state graph
    workflow = StateGraph(DocRetrieverState)

    # Add nodes
    workflow.add_node("retrieve_pending_docs", doc_retriever_node)
    workflow.add_node("format_output", format_output_node)

    # Define edges
    workflow.set_entry_point("retrieve_pending_docs")
    workflow.add_edge("retrieve_pending_docs", "format_output")
    workflow.add_edge("format_output", END)

    # Compile the graph
    return workflow.compile()


# Create the compiled graph instance
_orchestrator_graph = None


def get_orchestrator_graph() -> StateGraph:
    """Get or create the orchestrator graph instance"""
    global _orchestrator_graph
    if _orchestrator_graph is None:
        _orchestrator_graph = build_orchestrator_graph()
    return _orchestrator_graph


def run_orchestrator(username: str) -> str:
    """
    Entry point to run the orchestrator workflow.

    Args:
        username: Username to check pending documents for

    Returns:
        String message with document status
    """
    try:
        # Get the graph
        graph = get_orchestrator_graph()

        # Initialize state
        initial_state = {
            "username": username,
            "pending_documents": [],
            "error": None,
            "output": ""
        }

        # Run the graph
        result = graph.invoke(initial_state)

        # Return the output message
        return result.get("output", "No output generated")

    except Exception as e:
        return f"Error running orchestrator: {str(e)}"
