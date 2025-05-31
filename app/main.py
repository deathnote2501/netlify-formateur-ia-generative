from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import fastapi_users

# User and Auth related imports
from app.auth.transport import auth_backend
# from app.auth.manager import get_user_manager # Not directly used in main.py for router setup
from fastapi_users.schemas import UserRead, UserCreate
from app.models.user_models import User

from app.db.session import create_db_and_tables

# Endpoint Routers
from app.api.endpoints import utils as utils_router
from app.api.endpoints import chat as chat_router
from app.api.endpoints import stripe_webhooks as stripe_webhooks_router # New import
from app.api.endpoints import subscriptions as subscriptions_router     # New import


APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
STATIC_DIR_FOR_PYTHON_OPS = os.path.join(PROJECT_ROOT, "static")
ACTUAL_STATIC_MOUNT_DIR = "static"

VIDEOS_DIR = os.path.join(STATIC_DIR_FOR_PYTHON_OPS, "videos")
DEFAULT_PERSONA_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "default_persona")
os.makedirs(DEFAULT_PERSONA_VIDEOS_DIR, exist_ok=True)

app = FastAPI(title="AnimeMate API")

app.mount(f"/{ACTUAL_STATIC_MOUNT_DIR}", StaticFiles(directory=ACTUAL_STATIC_MOUNT_DIR), name="static")

origins = ["*"] # Configure as needed for production
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- Authentication Routers ---
app.include_router(
    fastapi_users.get_auth_router(auth_backend),
    prefix="/auth/jwt",
    tags=["Auth"], # Capitalized Tag
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"], # Capitalized Tag
)

# --- Application Routers ---
app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["Utils"])
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"])

# --- Stripe Routers ---
app.include_router(
    subscriptions_router.router,
    prefix="/api/v1/subscriptions", # Added /api/v1 prefix for consistency
    tags=["Subscriptions"]
)
app.include_router(
    stripe_webhooks_router.router,
    prefix="/webhooks", # Webhooks often don't have /api/v1 prefix
    tags=["Stripe Webhooks"]
)


# Protected test route (already present)
current_active_user = fastapi_users.current_user(active=True)
@app.get("/users/me", response_model=UserRead, tags=["Users"])
async def authenticated_route(user: User = Depends(current_active_user)):
    return user

@app.on_event("startup")
def on_startup():
    create_db_and_tables()
