from fastapi import Depends # Ensure Depends is imported
from sqlmodel import Session # Using synchronous Session
from fastapi_users_db_sqlmodel import SQLModelUserDatabase

from app.db.session import get_session # Synchronous get_session
from app.models.user_models import User

def get_user_db(session: Session = Depends(get_session)): # Synchronous session
    yield SQLModelUserDatabase(session, User)
