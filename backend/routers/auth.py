from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel
from db.database import Database

router = APIRouter()

class AuthRequest(BaseModel):
    username: str
    password: str

class AuthResponse(BaseModel):
    success: bool
    message: str
    username: str = None
    role: str = None

@router.post("/user-auth", response_model=AuthResponse)
async def authenticate_user(auth_request: AuthRequest):
    """
    Authenticate user against SQLite database
    Legacy endpoint for frontend compatibility
    """
    try:
        db = Database()

        # Authenticate user
        user = db.authenticate_user(auth_request.username, auth_request.password)

        if user:
            return AuthResponse(
                success=True,
                message="Authentication successful",
                username=user['username'],
                role=user.get('role', 'user')
            )
        else:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Invalid username or password"
            )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Authentication error: {str(e)}"
        )
