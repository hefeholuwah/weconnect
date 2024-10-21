from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from services.firebase_service import verify_firebase_token, create_user

router = APIRouter()

class SignupRequest(BaseModel):
    """Schema for user signup request."""
    email: str
    password: str

@router.post("/login/")
async def login(token: str):
    """Login route using Firebase token authentication."""
    user = await verify_firebase_token(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    return {"message": f"Logged in as {user['uid']}"}

@router.post("/signup/")
async def signup(signup_request: SignupRequest):
    """Sign up a user via Firebase."""
    try:
        user = await create_user(signup_request.email, signup_request.password)
        return {"message": f"User {user.email} signed up successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
