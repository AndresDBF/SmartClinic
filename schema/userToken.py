from fastapi.security import OAuth2PasswordRequestForm
from pydantic import BaseModel
from datetime import datetime
from typing import Optional, Union


class User(BaseModel):
    username: str
    name: Union[str, None] = None
    last_name: Union[str,None] = None
    gender: Union[str, None] = None
    tipid: Union[str, None] = None
    identification: Union[str, None] = None    
    disabled: Union[bool, None] = None 

#creamos un schema diferente para el password
class UserInDB(User):
    password:str
    
#para tomar el email en el form data
class OAuth2PasswordRequestFormWithEmail(OAuth2PasswordRequestForm):
    email: str