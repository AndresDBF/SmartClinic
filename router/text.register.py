import smtplib
from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response

from config.db import engine

from model.diagnostic import diagnostic
from model.user import users

from schema.inf_medic import infMedicSchema

from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError
from pydantic import EmailStr
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.utils import formataddr
from uuid import uuid4


test = APIRouter(tags=["prueba"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})



def send_verification_email(email, user_id):
    sender_email = "andres200605@gmail.com"
    sender_name = "Andres Becerra"
    subject = "Verificación de cuenta"
    verification_link = f"http://localhost:8000/api/verify/{user_id}"

    message = MIMEMultipart("alternative")
    message["From"] = sender_email
    message["To"] = email
    message["Subject"] = subject

    text = f"Para verificar tu cuenta, haz clic en el siguiente enlace: {verification_link}"
    html = f"<p>Para verificar tu cuenta, haz clic en el siguiente enlace: <a href='{verification_link}'>Verificar cuenta</a></p>"

    message.attach(MIMEText(text, "plain"))
    message.attach(MIMEText(html, "html"))
    print("hace el la verificacion de email")
    with smtplib.SMTP("smtp-gmail.com", 465) as server:
        server.starttls()
        print("inicia el server")
        server.login(sender_email, "uyxwtlitpottlrua")  # Coloca tu contraseña aquí
        server.send_message(message)

    
@test.get("/api/verify/{user_id}/")
async def verify_account(user_id: int):
    try:
        with engine.connect() as conn:
            user = conn.execute(select(users).where(users.c.id == user_id)).fetchone()
            if user:
                update_stmt = users.update().where(users.c.id == user.id).values(disabled=True)
                conn.execute(update_stmt)
                return {"message": "Cuenta verificada exitosamente."}
            else:
                raise HTTPException(status_code=404, detail="Usuario no encontrado.")
    except IntegrityError:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Error al verificar la cuenta.")
