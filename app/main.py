from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import create_db_and_tables
from app.api.endpoints import utils as utils_router
from app.api.endpoints import chat as chat_router # New import

app = FastAPI(title="AnimeMate API") # Added a title

# CORS Configuration
origins = [
    "*",  # Allow all origins for initial development
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
    create_db_and_tables() # This is for initial creation, Alembic handles migrations

app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["Utils"]) # Changed tag
app.include_router(chat_router.router, prefix="/api/v1/chat", tags=["Chat"]) # New router included

# Placeholder for other routers if needed in the future
# from app.api.endpoints import user_router # Example
# app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
