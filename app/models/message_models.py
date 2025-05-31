from datetime import datetime
from typing import Optional
from sqlmodel import Field, SQLModel

class Message(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    user_id: Optional[int] = Field(default=None, foreign_key="user.id", nullable=True)
    content: str
    timestamp: datetime = Field(default_factory=datetime.utcnow)
