"""
Agents API Module
REST API endpoints for LangGraph agent workflows
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional
from pathlib import Path
import sys

# Add parent directory to path for imports
sys.path.append(str(Path(__file__).parent.parent))

from agents.orchestrator_agent import run_orchestrator

# Create router
router = APIRouter()


class DocsSubmissionRequest(BaseModel):
    """Request model for document submission status check"""
    username: str = Field(..., description="Username to check document status for", min_length=1)


class DocsSubmissionResponse(BaseModel):
    """Response model for document submission status"""
    username: str
    status: str
    message: str


@router.post("/docs-submission", response_model=DocsSubmissionResponse)
async def docs_submission(request: DocsSubmissionRequest) -> DocsSubmissionResponse:
    """
    Check document submission status for a user.

    This endpoint uses a LangGraph workflow to:
    1. Retrieve pending documents for the user
    2. Return either a list of needed documents or confirmation that all are submitted

    Args:
        request: Contains username to check

    Returns:
        Document submission status message
    """
    try:
        username = request.username

        # Run the orchestrator workflow
        result_message = run_orchestrator(username)

        # Determine status based on result
        if "Documents needed:" in result_message:
            status = "pending"
        elif "All required documents" in result_message:
            status = "complete"
        elif "Error" in result_message:
            status = "error"
        else:
            status = "unknown"

        return DocsSubmissionResponse(
            username=username,
            status=status,
            message=result_message
        )

    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error checking document submission status: {str(e)}"
        )
