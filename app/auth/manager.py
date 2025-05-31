import uuid
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas

from app.core.config import settings
from app.models.user_models import User
from app.auth.db import get_user_db
from fastapi_users_db_sqlmodel import SQLModelUserDatabase

import logging # New import
logger = logging.getLogger("AnimeMateApp.AuthManager") # Specific logger

SECRET = settings.SECRET_KEY

class UserManager(IntegerIDMixin, BaseUserManager[User, int]):
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        logger.info(f"User {user.id} (email: {user.email}) has registered.")

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"User {user.id} (email: {user.email}) has forgotten their password. Reset token requested.")
        # In real app, you'd log less sensitive info, e.g., just that a token was generated.

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        logger.info(f"Verification requested for user {user.id} (email: {user.email}). Verification token generated.")

async def get_user_manager(user_db: SQLModelUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
