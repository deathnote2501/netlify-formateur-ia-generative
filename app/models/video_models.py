from typing import Optional
from sqlmodel import Field, SQLModel

class Video(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    persona_id: int = Field(foreign_key="persona.id")
    emotion_action_key: str = Field(index=True) # e.g., "happy", "jump", "neutral_loop"
    video_path: str # Relative path like "default_persona/happy.mp4"
    duration_seconds: Optional[float] = Field(default=None)
