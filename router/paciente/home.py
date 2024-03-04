import os
from fastapi import APIRouter, Request, HTTPException, status, Depends
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from sqlalchemy import select

from config.db import engine
from model.user import users
from model.images.user_image_profile import user_image_profile

from router.paciente.user import SECRET_KEY, ALGORITHM

from jose import jwt, JWTError

# Define un esquema para manejar la autenticación HTTP Bearer
security = HTTPBearer()
# Obtener la ruta absoluta del directorio raíz del proyecto
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))

userhome = APIRouter(tags=["userhome"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

# Definir la ruta absoluta de la carpeta de imágenes estáticas
img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))

# Montar la carpeta de imágenes estáticas
userhome.mount("/img", StaticFiles(directory=img_directory), name="img")

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials  # Obtiene el token de las credenciales
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Credenciales de Autenticacion Invalidas")
        # Puedes hacer alguna lógica adicional para verificar el usuario si es necesario
        return email
    except JWTError:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token Invalido")

@userhome.get("/api/home/{userid}")
async def user_home(userid: int, request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        # Obtener el usuario
        user = conn.execute(users.select().where(users.c.id == userid)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se ha encontrado el usuario")

        # Obtener la imagen del perfil del usuario
        image_row = conn.execute(user_image_profile.select().where(user_image_profile.c.user_id == userid)).first()
        if image_row is not None:
            file_path = f"./img/profile/{image_row.image_profile}.png"
            import os 
            if not os.path.exists(file_path):
                return {"error": "El archivo no existe"}
            
            image = FileResponse(file_path)
            
            base_url = str(request.base_url)
            image_url = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
            
            return {"id": userid, "image": image_url}
        return {"id": userid, "image": None}
    


