import os 
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config.db import engine
from model.blacklist_token import blacklist_token

security = HTTPBearer()

SECRET_KEY="0d227dc4d6ac7f607f532c85f5d8770215f3aa12398645b3bb74f09f1ebcbd51"
ALGORITHM="HS256"

routelogout = APIRouter(tags=["logout"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

load_dotenv()

def add_revoked_token(black_token: str):
    with engine.connect() as conn:
        new_black_token = conn.execute(blacklist_token.insert().values(token=black_token))
        conn.commit()


def is_token_revoked(token: str):
    with engine.connect() as conn:
        query =  conn.execute(blacklist_token.select()
                              .where(blacklist_token.c.token==token)).first()
        
        if query is not None:
            return query


@routelogout.post("/logout")
async def logout(token: str):
    try:
       
        with engine.connect() as conn:
            add_revoked_token(token)
        return {"message": "Se ha Cerrado la Sesion"}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cerrar sesión")



async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials 
        if is_token_revoked(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Revocado")
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
      
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")
    
