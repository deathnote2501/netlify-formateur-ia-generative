from sqlmodel import SQLModel

class ChatMessageCreate(SQLModel):
    user_message: str
    persona_id: int

class ChatMessageResponse(SQLModel):
    ia_response: str
    user_message_content: str
    persona_name: str
