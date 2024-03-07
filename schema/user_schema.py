from fastapi import Path, Body, UploadFile, File
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional


#para registro
class UserSchema(BaseModel):
    id: Optional[int] = 1
    username: str
    email: EmailStr
    password: str
    name: str
    last_name: str
    gender: str
    birthdate: date
    tipid: str
    identification: int = Body()
    disabled: bool

class UserContact(BaseModel):
    id: Optional[int] = 1
    phone: str 
    country: str
    state: str
    direction: str
    
class UserImg(BaseModel):
    image: UploadFile = File()

    
#para editar perfil
class UserUpdated(BaseModel):
    username: str
    email: EmailStr
    name: str
    last_name: str
    gender: str
    birthdate: date
    tipid: str
    identification: int = Body()

class UserContactUpdated(BaseModel):
    phone: str 
    country: str
    state: str
    direction: str
    
class UserImageProfile(BaseModel):
    image: UploadFile = File()
    
class verify_email(BaseModel):
    verify_email: EmailStr
    
#pasando el password en privado
class DataUser(BaseModel):
    email: str
    password: str

    