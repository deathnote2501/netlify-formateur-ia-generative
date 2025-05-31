from typing import Optional
from sqlmodel import Field, SQLModel

class Persona(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    name: str = Field(unique=True, index=True)
    system_prompt: str
    description: Optional[str] = Field(default=None)
