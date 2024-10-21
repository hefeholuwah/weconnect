from sqlalchemy.orm import Session
from models.user import User, UserSession, DailyUsage
from datetime import datetime, timedelta

SESSION_LIMITS = {
    "guest": 10,  # 10 minutes for guests
    "authenticated": 30  # 30 minutes for authenticated users
}

def create_session(db: Session, user: User = None):
    """
    Create a new session for the user or guest.
    If user is None, the session is for a guest.
    """
    session = UserSession(
        user_id=user.id if user else None,
        session_start=datetime.utcnow()
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session

def end_session(db: Session, session: UserSession):
    """
    End the session and calculate the duration.
    """
    session.session_end = datetime.utcnow()
    session.session_duration = (session.session_end - session.session_start).total_seconds() // 60  # Convert to minutes
    db.commit()
    db.refresh(session)

def check_daily_usage(db: Session, user: User):
    """
    Check and return the user's daily usage for today.
    If there's no record, create one.
    """
    today = datetime.utcnow().date()
    usage = db.query(DailyUsage).filter(
        DailyUsage.user_id == user.id,
        DailyUsage.usage_date == today
    ).first()

    if not usage:
        usage = DailyUsage(user_id=user.id, usage_date=today, total_time_used=0)
        db.add(usage)
        db.commit()
        db.refresh(usage)

    return usage

def update_daily_usage(db: Session, user: User, session_duration: int):
    """
    Update the user's daily usage with the session duration.
    """
    usage = check_daily_usage(db, user)
    usage.total_time_used += session_duration
    db.commit()

def is_session_allowed(db: Session, user: User = None):
    """
    Check if the user (or guest) is allowed to start a new session.
    """
    if user:
        # Authenticated users
        usage = check_daily_usage(db, user)
        return usage.total_time_used < SESSION_LIMITS["authenticated"]
    else:
        # Guest users
        return True  # Guests always get a fresh 10-minute session
