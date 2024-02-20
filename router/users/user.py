from fastapi import APIRouter, Response, status
from schema.user_schema import UserSchema, DataUser
from config.db import conn
from config.db import engine
from model.user import users
from passlib.context import CryptContext
from sqlalchemy import insert, select, func
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List


user = APIRouter(tags=['users'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

@user.get("/")
async def root():
    return "pruebas"

@user.get("/api/user", response_model=list[UserSchema])
async def get_users():
    with engine.connect() as conn:
        result = conn.execute(users.select()).fetchall()
        result2 = conn.execute(select(users.c.id, users)).first()
        print(result2)
        return result
    
@user.get("/api/user/{user_id}", response_model=UserSchema, status_code=status.HTTP_200_OK)
async def get_user(user_id: str):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.id == user_id)).first()         
        return result

@user.post("/api/user/register", status_code=status.HTTP_201_CREATED)
async def create_user(data_user: UserSchema):
    with engine.connect() as conn:
        data_user.name = data_user.name.title()
        data_user.last_name = data_user.last_name.title()
        last_id = conn.execute(select(func.max(users.c.id))).scalar()
        if last_id is not None:
            data_user.id = last_id + 1
        else:
            data_user.id = 1 
        new_user = data_user.dict()   
        
        # Hashea la contraseña antes de almacenarla en la base de datos
        hashed_password = pwd_context.hash(data_user.password)
        new_user["password"] = hashed_password
        
        stmt = insert(users).values(new_user)
        conn.execute(stmt)
        conn.commit()

        return Response(status_code=status.HTTP_201_CREATED)

@user.post("/api/user/login", status_code=status.HTTP_200_OK)     
async def user_login(data_user: DataUser):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.email == data_user.email)).first()
        print(result)
        if result is not None:
            # Verifica la contraseña ingresada con el hash almacenado en la base de datos
            if pwd_context.verify(data_user.password, result[3]):
                return {
                    "status": status.HTTP_200_OK, 
                    "message": "Access success"
                }
        return {"status": status.HTTP_401_UNAUTHORIZED, 
                "message": "Access Unauthorizeds"}







