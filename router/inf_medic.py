from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response
from fastapi.responses import JSONResponse
from config.db import engine
from model.diagnostic import diagnostic
from model.user import users
from sqlalchemy import select, insert, func
from sqlalchemy.exc import IntegrityError

routeim = APIRouter(tags=["medical information"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@routeim.get("/doctor/infm/{id_diag}")
async def get_diag_of_infm(diagid: int):
    with engine.connect() as conn:
        query_diagnostic = conn.execute(diagnostic.select().where(diagnostic.c.id == diagid)).first()
        query_user = conn.execute(users.select().where(users.c.id == query_diagnostic.user_id)).first()
        
        print(query_diagnostic)
        data_diagnostic = {
                "id": diagid,
                "user_id": query_diagnostic[1],
                "name": query_diagnostic[2],
                "last_name": query_diagnostic[3],
                "atent_id": query_diagnostic[2],
                "doctor_name": query_diagnostic[3],
                "birthdate": query_user[6]
        }

    return data_diagnostic
