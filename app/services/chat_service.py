from typing import Dict, Any, Optional # Added Optional

async def get_ia_response(
    user_message: str,
    persona_system_prompt: str,
    conversation_history: Optional[str] = None # New parameter
) -> Dict[str, Any]:
    text_response: str
    requested_emotion_action_key: str

    history_context = f" (Historique: '{conversation_history}')" if conversation_history else ""

    if "sauter" in user_message.lower():
        text_response = f"Réponse IA (simulée pour persona '{persona_system_prompt}'{history_context}): D'accord, je saute !"
        requested_emotion_action_key = "jump_test"
    else:
        text_response = f"Réponse IA (simulée pour persona '{persona_system_prompt}'{history_context}): J'ai bien reçu '{user_message}'."
        requested_emotion_action_key = "neutral_test"

    return {
        "text_response": text_response,
        "requested_emotion_action_key": requested_emotion_action_key
    }

# Example of how it might be extended later (pseudo-code for Gemini):
# from some_ai_library import GeminiClient
# from app.core.config import settings
# import json # Assuming Gemini might return a JSON string that needs parsing
#
# async def get_real_ia_response(user_message: str, persona_system_prompt: str, conversation_history: Optional[str] = None) -> Dict[str, Any]:
#     client = GeminiClient(api_key=settings.GEMINI_API_KEY)
#     try:
#         # This prompt needs to instruct Gemini to return a JSON with specific keys
#         structured_prompt_instruction = (
#             "Vous êtes un assistant IA. Répondez à l'utilisateur et déterminez une émotion/action clé appropriée. "
#             "Retournez votre réponse sous forme d'un objet JSON avec les clés 'text_response' (string) et 'requested_emotion_action_key' (string, ex: 'happy', 'curious', 'nod')."
#         )
#         history_for_prompt = f"\n\nConversation History:\n{conversation_history}" if conversation_history else ""
#         full_prompt = f"{structured_prompt_instruction}\n\nSystem Prompt pour Persona: {persona_system_prompt}{history_for_prompt}\n\nUser: {user_message}\nAI (JSON Response):"
#
#         raw_response = await client.generate_text(prompt=full_prompt, max_tokens=200) # or similar method
#
#         # Attempt to parse the response as JSON
#         try:
#             parsed_response = json.loads(raw_response.text)
#             if not isinstance(parsed_response, dict) or \
#                "text_response" not in parsed_response or \
#                "requested_emotion_action_key" not in parsed_response:
#                 # Fallback if JSON is not as expected
#                 return {"text_response": raw_response.text, "requested_emotion_action_key": "neutral_fallback"}
#             return parsed_response
#         except json.JSONDecodeError:
#             # Fallback if response is not valid JSON
#             return {"text_response": raw_response.text, "requested_emotion_action_key": "neutral_fallback"}
#
#     except Exception as e:
#         # Log error e
#         return {"text_response": "Désolé, une erreur s'est produite.", "requested_emotion_action_key": "error_fallback"}
