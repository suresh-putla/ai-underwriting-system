"""
Borrower-related API endpoints for document submission and status.
"""

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from typing import List
from db.database import Database

router = APIRouter()


# ========== Request/Response Models ==========

class SubmittedDocsResponse(BaseModel):
    """Response model for GET /submitted-docs"""
    user_id: str
    documents: list[dict]
    count: int


class UpdateDocumentStatusRequest(BaseModel):
    """Request model for updating document status"""
    user_id: str
    doc_type: str
    status: str


# ========== API Endpoints ==========

@router.get("/borrower/get-docs", response_model=SubmittedDocsResponse)
async def get_submitted_docs(user_id: str):
    """
    Get all submitted loan documents for a specific user.

    Args:
        user_id: Username of the user (query parameter)

    Returns:
        List of submitted documents with DOC_TYPE and STATUS

    Raises:
        HTTPException 400: If user_id is not provided
    """
    if not user_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="user_id query parameter is required"
        )

    db = Database()
    documents = db.get_submitted_docs_by_user(user_id)

    return SubmittedDocsResponse(
        user_id=user_id,
        documents=documents,
        count=len(documents)
    )


@router.put("/borrower/update-doc-status")
async def update_document_status(request: UpdateDocumentStatusRequest):
    """
    Update the status of a submitted document.

    Valid statuses: 'Pending', 'Evaluating', 'Under Review', 'Valid', 'Not Valid'
    """
    valid_statuses = ['Pending', 'Evaluating', 'Under Review', 'Valid', 'Not Valid']

    if request.status not in valid_statuses:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}"
        )

    db = Database()

    try:
        success = db.update_document_status(request.user_id, request.doc_type, request.status)

        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"No document found for user '{request.user_id}' with type '{request.doc_type}'"
            )

        return {
            "success": True,
            "message": f"Document status updated to '{request.status}'",
            "user_id": request.user_id,
            "doc_type": request.doc_type,
            "status": request.status
        }

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update document status: {str(e)}"
        )
