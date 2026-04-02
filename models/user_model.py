# models/user_model.py
from pydantic import BaseModel, EmailStr
from typing import Optional, List
from datetime import datetime


class UserCreate(BaseModel):
    name:     str
    email:    EmailStr
    password: str  # hashed before storing


class UserResponse(BaseModel):
    id:              str
    name:            str
    email:           str
    connected_platforms: List[str] = []
    created_at:      datetime


class ConnectedPlatform(BaseModel):
    platform: str   # youtube | reddit | instagram | twitter | pinterest
    username: Optional[str] = None
    api_key:  Optional[str] = None
    connected_at: datetime = datetime.utcnow()
