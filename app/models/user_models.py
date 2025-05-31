from typing import Optional # Keep for clarity, though Optional might come from base
from sqlmodel import Field, SQLModel # SQLModel might not be needed if SQLModelBaseUserDB brings it
from fastapi_users.db import SQLModelBaseUserDB

class User(SQLModelBaseUserDB, table=True): # SQLModelBaseUserDB already inherits from SQLModel
    # SQLModelBaseUserDB provides:
    # id: ID (which will be int due to not using UUID mixin)
    # email: EmailStr
    # hashed_password: str
    # is_active: bool = True
    # is_superuser: bool = False
    # is_verified: bool = False

    # We only need to add/override fields if they are custom or need different attributes
    # than SQLModelBaseUserDB provides by default for SQLModel.
    # For example, SQLModelBaseUserDB might not set unique=True or index=True at the DB level by default.
    email: str = Field(unique=True, index=True) # Re-declare to ensure DB constraints if not handled by base

    # If your original User model had other custom fields, they should be added here.
    # For this plan, the required fields are covered by SQLModelBaseUserDB or re-declared for constraints.
    pass # No other custom fields for now
