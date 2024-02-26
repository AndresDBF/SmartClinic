from fastapi import Path, Body
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional

class UserSchema(BaseModel):
    id: Optional[int] = 1
    username: str
    email: EmailStr
    verify_email: EmailStr
    password: str
    name: str
    last_name: str
    gender: str
    birthdate: date
    tipid: str
    identification: int = Body()
    disabled: bool
    
class verify_email(BaseModel):
    verify_email: EmailStr
    
class UserContact(BaseModel):
    id: Optional[int] = 1
    phone: str 
    country: str
    state: str
    direction: str
    
#pasando el password en privado
class DataUser(BaseModel):
    email: str
    password: str

    