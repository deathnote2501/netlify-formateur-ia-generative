from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional # Ensure Optional is imported

# Imports for fastapi-users
import fastapi_users # Not directly used here but good for context
from app.models.user_models import User # User model for dependency

# Define current_user dependency (should match the one in main.py for consistency)
# For chat, we require an active user.
current_active_user = fastapi_users.current_user(active=True)


from app.db.session import get_session
from app.models.message_models import Message
from app.models.persona_models import Persona
from app.models.video_models import Video
from app.schemas.chat_schemas import ChatMessageCreate, ChatMessageResponse
from app.services.chat_service import get_ia_response

BASE_URL = "http://localhost:8000"

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    *,
    session: Session = Depends(get_session),
    chat_input: ChatMessageCreate,
    user: User = Depends(current_active_user) # Added dependency for authenticated user
):
    persona = session.get(Persona, chat_input.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    service_response = await get_ia_response(
        user_message=chat_input.user_message,
        persona_system_prompt=persona.system_prompt
    )
    ia_text_response = service_response["text_response"]
    requested_emotion_action_key = service_response["requested_emotion_action_key"]

    video_url_to_play: Optional[str] = None
    statement = select(Video).where(Video.persona_id == persona.id).where(Video.emotion_action_key == requested_emotion_action_key)
    video_record = session.exec(statement).first()

    if video_record:
        video_url_to_play = f"{BASE_URL}/static/videos/{video_record.video_path}"

    # Save user message, now associated with the authenticated user
    user_db_message = Message(
        content=chat_input.user_message,
        is_from_user=True,
        user_id=user.id # Associate message with user.id
    )
    session.add(user_db_message)

    # Save IA message
    # IA messages are not directly from a 'user' in the User table, so user_id remains None or is handled differently.
    # For now, user_id is appropriately None for AI messages as per model definition (Optional).
    ia_db_message = Message(
        content=ia_text_response,
        is_from_user=False,
        user_id=None # Explicitly None for IA, or could be user.id if we want to track who triggered the IA
    )
    session.add(ia_db_message)

    session.commit()

    return ChatMessageResponse(
        ia_response=ia_text_response,
        user_message_content=chat_input.user_message,
        persona_name=persona.name,
        video_url_to_play=video_url_to_play
    )
