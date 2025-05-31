from typing import Optional, TYPE_CHECKING
from datetime import datetime
from sqlmodel import Field, SQLModel, Relationship

if TYPE_CHECKING:
    from .user_models import User # Forward reference for type hinting

class Subscription(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: int = Field(foreign_key="user.id", unique=True, index=True) # unique=True enforces one-to-one from Subscription side

    stripe_customer_id: Optional[str] = Field(default=None, unique=True, index=True, nullable=True)
    stripe_subscription_id: Optional[str] = Field(default=None, unique=True, index=True, nullable=True)

    status: str # e.g., "active", "canceled", "incomplete", "past_due"
    current_period_end: Optional[datetime] = Field(default=None, nullable=True)

    created_at: datetime = Field(default_factory=datetime.utcnow, nullable=False)
    # For onupdate, SQLAlchemy's onupdate is needed. SQLModel might not directly translate this for all DBs without sa_column_kwargs.
    # For simplicity, updated_at can be handled at the application level if complex,
    # or use a simpler default_factory for now and rely on application logic to update it.
    # Let's use default_factory and ensure application logic updates it.
    updated_at: datetime = Field(default_factory=datetime.utcnow, sa_column_kwargs={"onupdate": datetime.utcnow}, nullable=False)

    # Relationship back to User
    user: Optional["User"] = Relationship(back_populates="subscription")
