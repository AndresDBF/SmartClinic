import os 
from dotenv import load_dotenv
from fastapi import APIRouter, HTTPException, status, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import jwt, JWTError
from config.db import engine
from model.blacklist_token import blacklist_token

security = HTTPBearer()

routelogout = APIRouter(tags=["logout"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

load_dotenv()

def add_revoked_token(black_token: str):
    with engine.connect() as conn:
        new_black_token = conn.execute(blacklist_token.insert().values(token=black_token))
        conn.commit()

# Función para verificar si un token está revocado
def is_token_revoked(token: str):
    with engine.connect() as conn:
        query =  conn.execute(blacklist_token.select()
                              .where(blacklist_token.c.token==token)).first()
        print(query)
        if query is not None:
            return query

# Lógica para cerrar sesión
@routelogout.post("/logout")
async def logout(token: str):
    try:
        # Agrega el token actual a la lista negra en la base de datos
        with engine.connect() as conn:
            add_revoked_token(token)
        return {"message": "Se ha Cerrado la Sesion"}
    except:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Error al cerrar sesión")


# Lógica para verificar el token
async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials  # Obtiene el token de las credenciales
        if is_token_revoked(token):
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Revocado")
        payload = jwt.decode(token, os.getenv("SECRET_KEY"), algorithms=[os.getenv("ALGORITHM")])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
        # Puedes hacer alguna lógica adicional para verificar el usuario si es necesario
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")
    
