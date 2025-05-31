from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles # New import
import os # New import

from app.db.session import create_db_and_tables
from app.api.endpoints import utils as utils_router
from app.api.endpoints import chat as chat_router

# Determine base path for static files relative to app/main.py
# main.py is in app/, static/ is at project root, so ../static
APP_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(APP_DIR)
STATIC_DIR_FOR_PYTHON_OPS = os.path.join(PROJECT_ROOT, "static") # Path for os.makedirs

VIDEOS_DIR = os.path.join(STATIC_DIR_FOR_PYTHON_OPS, "videos")
DEFAULT_PERSONA_VIDEOS_DIR = os.path.join(VIDEOS_DIR, "default_persona")

os.makedirs(DEFAULT_PERSONA_VIDEOS_DIR, exist_ok=True)

app = FastAPI(title="AnimeMate API")

# Mount static files directory
# This path is relative to where uvicorn is run (project root)
app.mount("/static", StaticFiles(directory="static"), name="static")


# CORS Configuration
origins = [
    "*",
]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
def on_startup():
    create_db_and_tables()

app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["Utils"])
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"])
