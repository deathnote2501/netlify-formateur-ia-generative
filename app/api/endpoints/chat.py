from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select # Make sure select is imported
from typing import Optional # Added for Optional type hint

from app.db.session import get_session
from app.models.message_models import Message
from app.models.persona_models import Persona
from app.models.video_models import Video # New import for Video model
from app.schemas.chat_schemas import ChatMessageCreate, ChatMessageResponse
from app.services.chat_service import get_ia_response
# Assuming the FastAPI app is served at http://localhost:8000
# and static files are mounted at /static
BASE_URL = "http://localhost:8000"

router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    *,
    session: Session = Depends(get_session),
    chat_input: ChatMessageCreate
):
    persona = session.get(Persona, chat_input.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Get structured response from service
    service_response = await get_ia_response(
        user_message=chat_input.user_message,
        persona_system_prompt=persona.system_prompt
    )
    ia_text_response = service_response["text_response"]
    requested_emotion_action_key = service_response["requested_emotion_action_key"]

    # Video selection logic
    video_url_to_play: Optional[str] = None
    statement = select(Video).where(Video.persona_id == persona.id).where(Video.emotion_action_key == requested_emotion_action_key)
    video_record = session.exec(statement).first()

    if video_record:
        # Ensure this path construction matches how static files are served
        video_url_to_play = f"{BASE_URL}/static/videos/{video_record.video_path}"
    else:
        # Optional: Fallback to a default neutral video for the persona if no specific action video is found
        # statement_neutral = select(Video).where(Video.persona_id == persona.id).where(Video.emotion_action_key == "neutral_loop") # Example key
        # neutral_video_record = session.exec(statement_neutral).first()
        # if neutral_video_record:
        #     video_url_to_play = f"{BASE_URL}/static/videos/{neutral_video_record.video_path}"
        pass # For now, if specific video not found, video_url_to_play remains None

    # Save user message
    user_db_message = Message(
        content=chat_input.user_message,
        is_from_user=True,
        # user_id can be added here if authentication is implemented
    )
    session.add(user_db_message)

    # Save IA message (text part)
    ia_db_message = Message(
        content=ia_text_response, # Use the text part of the service response
        is_from_user=False,
    )
    session.add(ia_db_message)

    session.commit()
    # session.refresh(user_db_message)
    # session.refresh(ia_db_message)

    return ChatMessageResponse(
        ia_response=ia_text_response, # Use the text part
        user_message_content=chat_input.user_message,
        persona_name=persona.name,
        video_url_to_play=video_url_to_play # Include the selected video URL
    )
