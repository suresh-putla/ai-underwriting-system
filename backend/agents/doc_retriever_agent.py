"""
Document Retriever Agent
LangGraph node that retrieves pending documents for a user
"""

from typing import TypedDict, List
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from db.database import Database


class DocRetrieverState(TypedDict):
    """State for document retriever agent"""
    username: str
    pending_documents: List[str]
    error: str | None
    output: str


def doc_retriever_node(state: DocRetrieverState) -> DocRetrieverState:
    """
    LangGraph node that retrieves pending documents for a user.

    Args:
        state: Current state containing username

    Returns:
        Updated state with pending_documents list
    """
    try:
        username = state.get("username")
        if not username:
            return {
                **state,
                "pending_documents": [],
                "error": "No username provided"
            }

        # Get database instance
        db = Database()

        # Retrieve pending documents
        pending_docs = db.get_pending_documents(username)

        # Extract doc_type from each dict
        doc_types = [doc["doc_type"] for doc in pending_docs]

        return {
            **state,
            "pending_documents": doc_types,
            "error": None
        }

    except Exception as e:
        return {
            **state,
            "pending_documents": [],
            "error": f"Error retrieving pending documents: {str(e)}"
        }
