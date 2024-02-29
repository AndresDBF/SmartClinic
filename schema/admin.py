from fastapi import Path, Body, UploadFile, File
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional

class ListUserSchema(BaseModel):
    id: int
    username: str
    email: EmailStr
    password: str
    name: str
    last_name: str
    gender: str
    birthdate: date
    tipid: str
    identification: int
    disabled: bool
    phone: str 
    country: str
    state: str
    direction: str