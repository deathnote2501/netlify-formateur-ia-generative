from typing import Optional, TYPE_CHECKING # Ensure TYPE_CHECKING is imported
from sqlmodel import Field, SQLModel, Relationship # Ensure Relationship is imported
from fastapi_users.db import SQLModelBaseUserDB

if TYPE_CHECKING:
    from .subscription_models import Subscription # Forward reference

class User(SQLModelBaseUserDB, table=True):
    email: str = Field(unique=True, index=True)
    # id, hashed_password, is_active, is_superuser, is_verified are inherited

    # Relationship to Subscription (one-to-one)
    # `sa_relationship_kwargs={"uselist": False}` makes it one-to-one from User side
    subscription: Optional["Subscription"] = Relationship(
        back_populates="user",
        sa_relationship_kwargs={"uselist": False}
    )

    # No other custom fields for User model for now
    pass
