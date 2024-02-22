from pydantic import BaseModel
from typing import List

class Role(BaseModel):
    role_name: str

class UserRole(BaseModel):
    user_id: int
    role_id: int

class UserRoles(BaseModel):
    roles: List[UserRole]
