import uuid # Will not be used for User ID, but fastapi-users might use it internally or for tokens
from typing import Optional

from fastapi import Depends, Request
from fastapi_users import BaseUserManager, IntegerIDMixin, exceptions, models, schemas # IntegerIDMixin for int User IDs

from app.core.config import settings
from app.models.user_models import User
from app.auth.db import get_user_db # This is SQLModelUserDatabase from the dependency
# If get_user_db itself is not async, this UserManager does not need to be fully async
# for all methods unless specific operations require it (like sending emails).
# However, fastapi-users BaseUserManager methods are often async.

SECRET = settings.SECRET_KEY

class UserManager(IntegerIDMixin, BaseUserManager[User, int]): # Use int for User ID type
    reset_password_token_secret = SECRET
    verification_token_secret = SECRET

    async def on_after_register(self, user: User, request: Optional[Request] = None):
        print(f"User {user.id} has registered: {user.email}") # Added email for clarity

    async def on_after_forgot_password(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"User {user.id} has forgotten their password. Reset token: {token}")

    async def on_after_request_verify(
        self, user: User, token: str, request: Optional[Request] = None
    ):
        print(f"Verification requested for user {user.id}. Verification token: {token}")

    # Optional: Custom logic for user creation, e.g., if you have custom UserCreate schema
    # async def create(
    #     self,
    #     user_create: schemas.UC, # This would be your custom UserCreate schema
    #     safe: bool = False,
    #     request: Optional[Request] = None,
    # ) -> models.UP: # This would be your User model
    #     # Example: log before creation
    #     print(f"Attempting to create user: {user_create.email}")
    #     # You might want to hash password here if not handled by superclass or model
    #     # Ensure all fields required by User model are present or handled
    #     created_user = await super().create(user_create, safe, request)
    #     print(f"User {created_user.email} created successfully.")
    #     return created_user

# The type annotation for user_db should match what get_user_db yields.
# SQLModelUserDatabase is a class, get_user_db yields an instance of it.
from fastapi_users_db_sqlmodel import SQLModelUserDatabase # For type hinting if needed

async def get_user_manager(user_db: SQLModelUserDatabase = Depends(get_user_db)):
    yield UserManager(user_db)
