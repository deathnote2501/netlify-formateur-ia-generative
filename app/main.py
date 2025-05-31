from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.db.session import create_db_and_tables
from app.api.endpoints import utils as utils_router

app = FastAPI()

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
    create_db_and_tables()

app.include_router(utils_router.router, prefix="/api/v1/utils", tags=["utils"])

# Placeholder for other routers if needed in the future
# from app.api.endpoints import user_router, message_router # Example
# app.include_router(user_router.router, prefix="/api/v1/users", tags=["users"])
# app.include_router(message_router.router, prefix="/api/v1/messages", tags=["messages"])
