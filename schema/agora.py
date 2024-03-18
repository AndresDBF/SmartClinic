from fastapi import Path, Body, UploadFile, File
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional

class User(BaseModel):
    user_id: str
    token: Optional[str] = None

users_db = {}

class TokenAndChannelResponse(BaseModel):
    token: str
    channel_id: str
