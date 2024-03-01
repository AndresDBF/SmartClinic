from fastapi import APIRouter, Response, status, HTTPException, Request, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse

from config.db import engine

from model.user import users
from model.usercontact import usercontact
from model.images.user_image_profile import user_image_profile

from model.images.user_image_profile import user_image_profile

from router.paciente.home import get_current_user

from sqlalchemy import insert, select, func
from sqlalchemy.exc import IntegrityError

from os import getcwd

uverify = APIRouter(tags=["Admin Verify User"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})
""" 
uverify.mount("/img", StaticFiles(directory="img"), name="img")
 """
@uverify.get("/admin/veri/user")
async def list_user_verify(current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.verify_ident == 0)).fetchall()
        user_contact = conn.execute(usercontact.select().
                                    join(users, usercontact.c.user_id == users.c.id).
                                    where(users.c.verify_ident == 0)).fetchall()
        list_user = [
            {
            "id": rowus[0],
            "username": rowus[1],
            "email":rowus[2],
            "name": rowus[4],
            "last_name": rowus[5],
            "gender": rowus[6],
            "birthdate": rowus[7],
            "tipid": rowus[8],
            "identification": rowus[9],
            "disabled": rowus[10]
            }
        for rowus in user
        ]
        list_user_contact = [
            {
                "phone": rowusc[2],
                "country": rowusc[3],
                "state": rowusc[4],
                "direction": rowusc[5]
            }
            for rowusc in user_contact
        ]
        data_list = []
        for userdata, usercdata in zip(list_user, list_user_contact):
            full_user_data = {**userdata, **usercdata}
            data_list.append(full_user_data)
        return data_list
    
@uverify.get("/admin/veri/user/{user_id}")
async def verify_user(user_id: int):
    pass
        