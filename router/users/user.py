from fastapi import APIRouter, Response, status, HTTPException, Depends, Path, Form
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from schema.user_schema import UserSchema, DataUser
from schema.userToken import UserInDB, User, OAuth2PasswordRequestFormWithEmail
from config.db import engine
from model.user import users
from passlib.context import CryptContext
from sqlalchemy import insert, select, func
from werkzeug.security import generate_password_hash, check_password_hash
from typing import List, Union
from pydantic import ValidationError
from datetime import datetime,timedelta
from jose import jwt, JWTError

user = APIRouter(tags=['users'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

#instancia 
oauth2_scheme = OAuth2PasswordBearer("/api/user/login")

pwd_context = CryptContext(schemes=["pbkdf2_sha256"], deprecated="auto")

SECRET_KEY = "0d227dc4d6ac7f607f532c85f5d8770215f3aa12398645b3bb74f09f1ebcbd51"
ALGORITHM = "HS256"

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
    
    
def verify_username_email(username: str, email: str): 
    with engine.connect() as conn:
        query_user = conn.execute(users.select().where(users.c.username == username)).first()
        query_email = conn.execute(users.select().where(users.c.email == email)).first()
       
        if query_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este nombre de usuario no se encuentra disponible")
        if query_email is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Este Correo se encuentra en uso")
        if query_email is not None and query_user is not None:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El usuario y correo ya existen")
        else:
            return True


@user.post("/api/user/register", response_model=UserSchema, status_code=status.HTTP_201_CREATED)
async def create_user(data_user: UserSchema):
    try:
        with engine.connect() as conn:
            data_user.name = data_user.name.title()
            data_user.last_name = data_user.last_name.title()
            last_id = conn.execute(select(func.max(users.c.id))).scalar()
            if verify_username_email(data_user.username, data_user.email):
                if last_id is not None:
                    data_user.id = last_id + 1
                else:
                    data_user.id = 1 

                # Hashea la contraseña antes de almacenarla en la base de datos
                hashed_password = pwd_context.hash(data_user.password)
                data_user.password = hashed_password
                
                new_user = data_user.dict()
                stmt = insert(users).values(new_user)
                conn.execute(stmt)
                conn.commit()

                return {
                        "status": status.HTTP_200_OK,
                        "message": "Usuario creado"
                    }
    except ValidationError as e:
        raise HTTPException(status_code=400, detail=str(e))


async def verify_user_data(data_user: DataUser):
    try:
        
        if not data_user.email or not data_user.password:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="falta el usuario o contrasena")
        return data_user
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="debe ingresar usuario y contrasena")


#------------------Dependencias para token ------------------------------

def authenticate_user(email, password):
    user = get_user(email)
    print(user)
    if not user:
        raise HTTPException(status_code=401, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    if not verify_password(password, user.password):
        raise HTTPException(status_code=401, detail="No se pueden validar las credenciales", headers={"www-authenticate": "Bearer"})
    return user
def get_user(email):
    with engine.connect() as conn:
        result = conn.execute(users.select().where(users.c.email == email)).first()
        if result:
             #para que se devuelva el conjunto de datos de la base de datos
            print(result)
            return result
        return []
def verify_password(plane_password, hashed_password):
    print("entra en verify password")
    return pwd_context.verify(plane_password,hashed_password) #verificando que el texto plano sea igual que el encriptado

def create_token(data: dict, time_expire: Union[datetime,None] = None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() +  timedelta(minutes=15)#datetime.utcnow() trae la hora de ese instante
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=SECRET_KEY, algorithm=ALGORITHM)
    print("crea el token en la dependencia")
    return token_jwt

@user.post("/api/user/login", status_code=status.HTTP_200_OK)
async def user_login(email: str = Form(...), password: str = Form(...)):
    print(email)
    print(password)
    try:
        with engine.connect() as conn:
            result = conn.execute(users.select().where(users.c.email == email)).first()
            if result is not None:
                stored_password_hash = result[3]
                if pwd_context.verify(password, stored_password_hash):
                    print("entra en el if")
                    user = authenticate_user(email, password)
                    access_token_expires = timedelta(minutes=30)
                    access_token_jwt = create_token({"sub": user.email}, access_token_expires)
                    print("crea el token")
                    print(access_token_expires)
                    print(access_token_jwt)
                    return {
                        "access_token": access_token_jwt,
                        "token_types": "bearer"
                    }
                else:
                    print("entra en este else")
                    raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Contraseña incorrecta")
            else:
                print("entra en el otro else")
                raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Usuario incorrecto")
    except ValidationError:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no se ha encontrado usuarios")