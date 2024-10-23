from fastapi import FastAPI, Depends, HTTPException, status, Form
from pydantic import BaseModel
from sqlalchemy.orm import Session
from .auth import router as auth_router
from .paystack_webhooks import router as paystack_router
from .chat import router as chat_router
from services.firebase_service import verify_firebase_token, create_user
from services.session_service import create_session, end_session, is_session_allowed, update_daily_usage
from app.database import get_db
from models.user import UserSession, User
from services.session_service import SESSION_LIMITS

app = FastAPI()

# Include routers
app.include_router(auth_router, prefix="/auth")
app.include_router(paystack_router, prefix="/paystack")
app.include_router(chat_router, prefix="/chat")

@app.get("/")
async def read_root():
    """Welcome message for the root endpoint."""
    return {"message": "Welcome to the Video Chat Platform!"}

async def get_current_user(token: str):
    """Extract and verify the user from the Firebase token."""
    user = await verify_firebase_token(token)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return user

@app.post("/login/")
async def authenticate_user(token: str = Form(...)):
    """Authenticate user via Firebase token."""
    user = await get_current_user(token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid Firebase token")
    return {"message": f"Authenticated {user['uid']}"}

@app.get("/protected/")
async def protected_route(user=Depends(get_current_user)):
    """A protected route that requires authentication."""
    return {"message": f"Welcome {user['uid']}, you're authenticated"}

class SignupRequest(BaseModel):
    """Schema for user signup request."""
    email: str
    password: str

@app.post("/signup/")
async def signup(signup_request: SignupRequest):
    """Sign up a user via Firebase."""
    try:
        user = await create_user(signup_request.email, signup_request.password)
        return {"message": f"User {user.uid} created successfully"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))



@app.post("/start_session/")
async def start_session(token: str = None, db: Session = Depends(get_db)):
    """
    Start a video session for a guest or authenticated user.
    """
    user = None
    if token:
        user = await get_current_user(token, db)

    # Check if the user is allowed to start a new session
    if not is_session_allowed(db, user):
        time_limit = SESSION_LIMITS["authenticated"] if user else SESSION_LIMITS["guest"]
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=f"Session limit reached. You are allowed {time_limit} minutes per day."
        )

    session = create_session(db, user)
    return {"message": "Session started", "session_id": session.id}


@app.post("/end_session/")
async def end_session(session_id: int, db: Session = Depends(get_db)):
    """
    End a session and calculate its duration.
    """
    session = db.query(UserSession).filter(UserSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    if session.session_end:
        raise HTTPException(status_code=400, detail="Session already ended")

    # End the session and calculate the duration
    end_session(db, session)

    # Update the user's daily usage if authenticated
    if session.user_id:
        user = db.query(User).filter(User.id == session.user_id).first()
        update_daily_usage(db, user, session.session_duration)

    return {"message": "Session ended", "duration": session.session_duration}