""" from fastapi import FastAPI, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from pydantic import BaseModel
from typing import Union #para unir varios datos 
from passlib.context import CryptContext 
from datetime import datetime,timedelta
from jose import jwt, JWTError


fake_users_db = {
    "andres": {
        "username": "andres",
        "full_name": "Andres Becerra",
        "email": "andres200605@gmail.com",
        "hashed_password": "$2a$12$k9JEFKuRePELFHFxlLJpu.juuoI3zLeRSqUgEfdWJqdWfYDEPHTIK",
        "disabled": False,
    }
}

app = FastAPI()

#instancia 
oauth2_scheme = OAuth2PasswordBearer("/token")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

SECRET_KEY = "0d227dc4d6ac7f607f532c85f5d8770215f3aa12398645b3bb74f09f1ebcbd51"
ALGORITHM = "HS256"

#schemas
class User(BaseModel):
    username: str
    full_name: Union[str, None] = None
    email: Union[str, None] = None
    disabled: Union[bool, None] = None

#creamos un schema diferente para el password
class UserInDB(User):
    hashed_password:str
    
    
#para obtener el usuario
def get_user(db, username):
    if username in db:
        user_data = db[username] #para que se devuelva el conjunto de datos de la base de datos
        return UserInDB(**user_data) #
    return []

def verify_password(plane_password, hashed_password):
    return pwd_context.verify(plane_password,hashed_password) #verificando que el texto plano sea igual que el encriptado


def authenticate_user(db, username, password):
    user = get_user(db, username)
    if not user:
        raise HTTPException(status_code=401, detail="could not validate credentials", headers={"www-authenticate": "Bearer"})
    if not verify_password(password, user.hashed_password):
        raise HTTPException(status_code=401, detail="could not validate credentials", headers={"www-authenticate": "Bearer"})
    return user

def create_token(data: dict, time_expire: Union[datetime,None] = None):
    data_copy = data.copy()
    if time_expire is None:
        expires = datetime.utcnow() +  timedelta(minutes=15)#datetime.utcnow() trae la hora de ese instante
    else:
        expires = datetime.utcnow() + time_expire
    data_copy.update({"exp": expires})
    token_jwt = jwt.encode(data_copy, key=SECRET_KEY, algorithm=ALGORITHM)
    print(token_jwt)
    return token_jwt

#para traer el usuario que verdaderamente existe
def get_user_current(token: str = Depends(oauth2_scheme)):
    try:
        token_decode = jwt.decode(token, key=SECRET_KEY, algorithms=[ALGORITHM])
        username = token_decode.get("sub") #devuelve un diccionario para que devuelva el user que tomamos de sub en la funcion anterior
        if username == None:
            raise HTTPException(status_code=401, detail="could not validate credentials", headers={"www-authenticate": "Bearer"})
    
    except JWTError:
        raise HTTPException(status_code=401, detail="could not validate credentials", headers={"www-authenticate": "Bearer"})
    user = get_user(fake_users_db, username)
    if not user:
        raise HTTPException(status_code=401, detail="could not validate credentials", headers={"www-authenticate": "Bearer"})
    return user

#garantizar que el usuario no halla expirado
def get_user_disabled_current(user: User = Depends(get_user_current)):
    if user.disabled:
        raise HTTPException(status_code=400, detail="cInactive User")
    return user

 


@app.get("/")
async def root():
    return "hola mundo"

@app.get("/users/me")
async def user(user: User = Depends(get_user_disabled_current)): #el depends es una funcion de dependencias 
    #lo que se pasa como token se vera reflejado especificamente en el diccionario del access_token en la funcion login
    
    return user

@app.post("/token")
async def login(form_data: OAuth2PasswordRequestForm = Depends()): #el form es un formulario predeterminado de fastapi
    user = authenticate_user(fake_users_db,form_data.username,form_data.password)
    access_token_expires = timedelta(minutes=30) 
    access_token_jwt = create_token({"sub": user.username}, access_token_expires) #sub es la identidad que se quiere identificar en este caso el username
   
    return {
        "access_token": access_token_jwt,
        "token_type": "bearer"
    } """