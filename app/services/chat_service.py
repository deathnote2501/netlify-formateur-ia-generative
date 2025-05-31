async def get_ia_response(user_message: str, persona_system_prompt: str) -> str:
    """
    Simulates a response from an AI based on the user message and persona system prompt.
    For MVP, this does not call any external AI service.
    """
    # In a real scenario, this would involve an API call to a service like Gemini,
    # potentially using an SDK and handling API keys, errors, etc.

    # Simple simulation:
    simulated_response = f"Réponse IA (simulée pour persona avec prompt '{persona_system_prompt}'): J'ai bien reçu votre message '{user_message}'."

    return simulated_response

# Example of how it might be extended later (pseudo-code):
# from some_ai_library import GeminiClient
# from app.core.config import settings
#
# async def get_real_ia_response(user_message: str, persona_system_prompt: str) -> str:
#     client = GeminiClient(api_key=settings.GEMINI_API_KEY)
#     try:
#         # Constructing a prompt that combines the system prompt and user message
#         full_prompt = f"{persona_system_prompt}\n\nUser: {user_message}\nAI:"
#         response = await client.generate_text(prompt=full_prompt, max_tokens=150)
#         return response.text
#     except Exception as e:
#         # Log error e
#         return "Désolé, une erreur s'est produite lors de la communication avec l'IA."
