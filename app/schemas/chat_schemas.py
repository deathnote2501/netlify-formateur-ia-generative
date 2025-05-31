from typing import Optional # Ensure Optional is imported
from sqlmodel import SQLModel

class ChatMessageCreate(SQLModel):
    user_message: str
    persona_id: int

class ChatMessageResponse(SQLModel):
    ia_response: str
    user_message_content: str
    persona_name: str
    video_url_to_play: Optional[str] = None # New field added
