from fastapi import FastAPI, Depends # Ensure Depends is imported
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Imports for fastapi-users
import fastapi_users # Main import
from app.auth.transport import auth_backend
from app.auth.manager import get_user_manager # User manager
# Using default schemas, but explicit import for clarity and if customization is needed later
from fastapi_users.schemas import UserRead, UserCreate
from app.models.user_models import User # User model itself for type hinting and current_user

from app.db.session import create_db_and_tables
from app.api.endpoints import utils as utils_router
from app.api.endpoints import chat as chat_router

APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
STATIC_DIR_FOR_PYTHON_OPS = os.path.join(PROJECT_ROOT, "static") # Used for os.makedirs
ACTUAL_STATIC_MOUNT_DIR = "static" # Path relative to where uvicorn runs (project root)

VIDEOS_DIR = os.path.join(STATIC_DIR_FOR_PYTHON_OPS, "videos")
DEFAULT_PERSONA_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "default_persona")

os.makedirs(DEFAULT_PERSONA_VIDEOS_DIR, exist_ok=True)

app = FastAPI(title="AnimeMate API")

app.mount(f"/{ACTUAL_STATIC_MOUNT_DIR}", StaticFiles(directory=ACTUAL_STATIC_MOUNT_DIR), name="static")

origins = ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include fastapi-users routers
# Note: prefix="/auth/jwt" for login/logout if using JWT strategy named "jwt"
# and prefix="/auth" for registration.
app.include_router(
    fastapi_users.get_auth_router(auth_backend), # Provides /login, /logout
    prefix="/auth/jwt",
    tags=["auth"],
)
app.include_router(
    fastapi_users.get_register_router(UserRead, UserCreate), # Provides /register
    prefix="/auth",
    tags=["auth"],
)

# Optional routers (can be added if needed)
# app.include_router(
#     fastapi_users.get_reset_password_router(),
#     prefix="/auth",
#     tags=["auth"],
# )
# app.include_router(
#     fastapi_users.get_verify_router(UserRead), # For email verification
#     prefix="/auth",
#     tags=["auth"],
# )

# Define current_user dependency for protected routes
# By default, it requires active user. Can be configured:
# current_user = fastapi_users.current_user(active=True, verified=True, superuser=True)
current_active_user = fastapi_users.current_user(active=True)


@app.on_event("startup")
def on_startup():
    create_db_and_tables()

# Existing routers
app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["Utils"])
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"]) # Will be secured next

# New protected test route
@app.get("/users/me", response_model=UserRead, tags=["Users"]) # Changed tag to "Users"
async def authenticated_route(user: User = Depends(current_active_user)):
    return user
