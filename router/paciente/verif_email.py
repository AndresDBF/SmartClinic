from fastapi import APIRouter, Response, status, HTTPException, Depends, Path, Form, UploadFile, File, Request
from fastapi.responses import JSONResponse

from config.db import engine

from model.user import users
from model.usercontact import usercontact
from model.images.user_image_profile import user_image_profile

from sqlalchemy import insert, select, func
from sqlalchemy.exc import IntegrityError

from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from router.logout import get_current_user
        
email = APIRouter(tags=["Verify Email"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

email.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")
    
@email.get("/api/verify/{user_id}", response_class=HTMLResponse)
async def verify_account(user_id: int, request: Request):
    print("entra en verificacion")
    print(user_id)
    try:
        with engine.connect() as conn:
            user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()
            if user:
                update_stmt = users.update().where(users.c.id == user.id).values(disabled=True)
                conn.execute(update_stmt)
                conn.commit()
                return templates.TemplateResponse("index.html", {
                    "request": request
                })
            else:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al verificar la cuenta.")

@email.get("/api/user/veriaccount/{user_id}")
async def veri_email_ident(user_id: int,  current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id == user_id)).first()
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El id del usuario no se ha encontrado")
        if user.disabled:
            if user.verify_ident:
                return JSONResponse(content={
                                    "email": True,
                                    "identif": True,
                                    "message_email": "verificado",
                                    "message_identif": "verificado"
                                }, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={
                                    "email": True,
                                    "identif": False,
                                    "message_email": "verificado",
                                    "message_identif": "EN PROCESO"
                                }, status_code=status.HTTP_200_OK)
        else:
            if user.verify_ident:
                return JSONResponse(content={
                                    "email": False,
                                    "identif": True,
                                    "message_email": "EN PROCESO",
                                    "message_identif": "verificado"
                                }, status_code=status.HTTP_200_OK)
            else:
                return JSONResponse(content={
                                        "email": False,
                                        "identif": False,
                                        "message_email": "EN PROCESO",
                                        "message_identif": "EN PROCESO"
                                    }, status_code=status.HTTP_200_OK)