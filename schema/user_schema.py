from pydantic import BaseModel, constr
from datetime import datetime
from typing import Optional

class UserSchema(BaseModel):
    id: Optional[int] = 1
    username: str
    email: str
    password: str
    name: str
    last_name: str
    gender: str
    tipid: str
    identification: int
    disabled: bool
 

#pasando el password en privado
class DataUser(BaseModel):
    email: str
    password: str

    