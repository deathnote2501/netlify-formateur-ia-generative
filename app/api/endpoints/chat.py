from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session

from app.db.session import get_session
from app.models.message_models import Message
from app.models.persona_models import Persona  # Ensure this model is created
from app.schemas.chat_schemas import ChatMessageCreate, ChatMessageResponse
from app.services.chat_service import get_ia_response

router = APIRouter() # Will be prefixed in main.py or when included

@router.post("/", response_model=ChatMessageResponse)
async def send_message(
    *,
    session: Session = Depends(get_session),
    chat_input: ChatMessageCreate
):
    """
    Receive a user message, get a simulated IA response, and save both messages.
    """
    persona = session.get(Persona, chat_input.persona_id)
    if not persona:
        raise HTTPException(status_code=404, detail="Persona not found")

    # Get IA response from service
    ia_response_text = await get_ia_response(
        user_message=chat_input.user_message,
        persona_system_prompt=persona.system_prompt
    )

    # Save user message
    user_db_message = Message(
        content=chat_input.user_message,
        is_from_user=True,
        # user_id can be added here if authentication is implemented
    )
    session.add(user_db_message)

    # Save IA message
    ia_db_message = Message(
        content=ia_response_text,
        is_from_user=False,
        # user_id could also be associated with the user who initiated the chat, if needed
    )
    session.add(ia_db_message)

    session.commit()
    # Refresh to get IDs if needed, though not strictly necessary for this response
    # session.refresh(user_db_message)
    # session.refresh(ia_db_message)

    return ChatMessageResponse(
        ia_response=ia_response_text,
        user_message_content=chat_input.user_message,
        persona_name=persona.name
    )
