from pydantic_settings import BaseSettings
from typing import Optional # Ensure Optional is imported

class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str # Used by fastapi-users and JWT

    # Stripe Settings
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str
    STRIPE_PRICE_ID_MONTHLY: Optional[str] = None
    STRIPE_PRICE_ID_YEARLY: Optional[str] = None
    FRONTEND_DOMAIN: str = "http://localhost:5173" # Default for SvelteKit dev

    class Config:
        env_file = ".env"
        env_file_encoding = 'utf-8' # Added for good measure

settings = Settings()
