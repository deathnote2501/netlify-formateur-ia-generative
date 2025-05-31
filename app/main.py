from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import fastapi_users
import logging # New import

# --- Logging Configuration ---
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)
logger = logging.getLogger("AnimeMateApp") # Specific logger name for the app
# --- End Logging Configuration ---


# User and Auth related imports
from app.auth.transport import auth_backend
from fastapi_users.schemas import UserRead, UserCreate
from app.models.user_models import User

from app.db.session import create_db_and_tables

# Endpoint Routers
from app.api.endpoints import utils as utils_router
from app.api.endpoints import chat as chat_router
from app.api.endpoints import stripe_webhooks as stripe_webhooks_router
from app.api.endpoints import subscriptions as subscriptions_router


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
    tags=["Auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate),
    prefix="/auth",
    tags=["Auth"],
)

# --- Application Routers ---
app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["Utils"])
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"])

# --- Stripe Routers ---
app.include_router(
    subscriptions_router.router,
    prefix="/api/v1/subscriptions",
    tags=["Subscriptions"]
)
app.include_router(
    stripe_webhooks_router.router,
    prefix="/webhooks",
    tags=["Stripe Webhooks"]
)


# Protected test route (already present)
current_active_user = fastapi_users.current_user(active=True)
@app.get("/users/me", response_model=UserRead, tags=["Users"])
async def authenticated_route(user: User = Depends(current_active_user)):
    return user

@app.on_event("startup")
def on_startup():
    logger.info("AnimeMate Application startup complete. Initializing database tables...")
    create_db_and_tables()
    logger.info("Database tables initialization process finished.")
