from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import Optional, List

# Ensure these are present:
from app.models.user_models import User
from app.models.message_models import Message
from app.models.persona_models import Persona
from app.models.video_models import Video
from app.schemas.chat_schemas import ChatMessageCreate, ChatMessageResponse
from app.services.chat_service import get_ia_response
from app.db.session import get_session
import fastapi_users
current_active_user = fastapi_users.current_user(active=True)
BASE_URL = "http://localhost:8000"

import logging # New import
logger = logging.getLogger("AnimeMateApp.Chat") # Specific logger for this module


router = APIRouter()

@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    *,
    session: Session = Depends(get_session),
    chat_input: ChatMessageCreate,
    user: User = Depends(current_active_user)
):
    logger.info(f"Chat request received from user_id: {user.id} for persona_id: {chat_input.persona_id}")
    persona = session.get(Persona, chat_input.persona_id)
    if not persona:
        logger.warning(f"Persona not found for persona_id: {chat_input.persona_id} (requested by user_id: {user.id})")
        raise HTTPException(status_code=404, detail="Persona not found")

    # --- Fetch conversation history ---
    statement = (
        select(Message)
        .where(Message.user_id == user.id)
        .order_by(Message.timestamp.desc())
        .limit(10)
    )
    recent_messages_db = session.exec(statement).all()
    recent_messages_db.reverse()

    conversation_history = []
    for msg in recent_messages_db:
        prefix = "User: " if msg.is_from_user else "IA: "
        conversation_history.append(f"{prefix}{msg.content}")
    formatted_history = "\n".join(conversation_history)
    logger.debug(f"Formatted history for user_id {user.id}: {formatted_history[:200]}...")
    # --- End fetch conversation history ---

    try:
        service_response = await get_ia_response(
            user_message=chat_input.user_message,
            persona_system_prompt=persona.system_prompt,
            conversation_history=formatted_history
        )
        ia_text_response = service_response["text_response"]
        requested_emotion_action_key = service_response["requested_emotion_action_key"]

        video_url_to_play: Optional[str] = None
        video_statement = select(Video).where(Video.persona_id == persona.id).where(Video.emotion_action_key == requested_emotion_action_key)
        video_record = session.exec(video_statement).first()

        if video_record:
            video_url_to_play = f"{BASE_URL}/static/videos/{video_record.video_path}"

        user_db_message = Message(
            content=chat_input.user_message,
            is_from_user=True,
            user_id=user.id
        )
        session.add(user_db_message)

        ia_db_message = Message(
            content=ia_text_response,
            is_from_user=False,
            user_id=user.id
        )
        session.add(ia_db_message)

        session.commit()
        logger.info(f"Chat response successfully generated for user_id: {user.id}")
        return ChatMessageResponse(
            ia_response=ia_text_response,
            user_message_content=chat_input.user_message,
            persona_name=persona.name,
            video_url_to_play=video_url_to_play
        )
    except Exception as e:
        logger.error(f"Error processing chat for user_id {user.id}: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail="Error processing chat message.")
