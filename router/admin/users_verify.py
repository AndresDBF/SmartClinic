import os
from fastapi import APIRouter, Response, status, HTTPException, Depends
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.db import engine

from model.user import users
from model.usercontact import usercontact
from model.images.user_image import user_image
from model.notification import notifications
from model.roles.roles import roles


from model.lval import lval
from model.roles.user_roles import user_roles

from router.logout import get_current_user


from sqlalchemy import insert, select, func

from starlette.requests import Request

from os import getcwd, remove

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
uverify = APIRouter(tags=["Admin Verify User"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

img_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'profile'))


uverify.mount("/img", StaticFiles(directory=img_directory), name="img")

@uverify.get("/admin/veri-user/")
async def list_user_verify(request: Request, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user_notif = conn.execute(select(users.c.id,user_roles.c.role_id).
                                  select_from(users).
                                  join(user_roles, users.c.id==user_roles.c.user_id).
                                  where(users.c.email==current_user)).first()
        if user_notif[1] != 1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No esta autorizado para realizar esta accion")
       
        # Obtener usuarios sin verificar
        users_query = users.select().join(user_image, users.c.id == user_image.c.user_id).where(users.c.verify_ident == 0)
        user_rows = conn.execute(users_query).fetchall()
        
        # Verificar si se encontraron usuarios sin verificar
        if not user_rows:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado usuarios para verificarse")

        # Obtener datos de usuario y de contacto
        list_user = [
            {
                "id": rowus[0],
                "username": rowus[1],
                "email": rowus[2],
                "name": rowus[4],
                "last_name": rowus[5],
                "gender": rowus[6],
                "birthdate": rowus[7],
                "tipid": rowus[8],
                "identification": rowus[9],
                "disabled": rowus[10],
                "verify_ident": rowus[11]
            }
            for rowus in user_rows
        ]

        user_ids = [rowus[0] for rowus in user_rows]  # Lista de IDs de usuarios

        # Obtener datos de contacto de usuario
        user_contact_query = usercontact.select().where(usercontact.c.user_id.in_(user_ids))
        user_contact_rows = conn.execute(user_contact_query).fetchall()

        list_user_contact = [
            {
                "user_id": rowusc[0],
                "phone": rowusc[2],
                "country": rowusc[3],
                "state": rowusc[4],
                "direction": rowusc[5]
            }
            for rowusc in user_contact_rows
        ]
        
        role_user = conn.execute(select(roles.c.role_name, users.c.id)
                                 .select_from(users)
                                 .join(user_roles, users.c.id==user_roles.c.user_id)
                                 .join(roles, user_roles.c.role_id==roles.c.role_id)
                                 .where(users.c.id.in_(user_ids))).fetchall()
        list_tip_rol = [
            {
                "id_role": rowrl[1],
                "role_name": rowrl[0]
            }
            for rowrl in role_user
        ]
        # Combinar datos de usuario y contacto
        data_list = []
        for userdata in list_user:
            user_id = userdata["id"]
            user_contact_data = next((usercdata for usercdata in list_user_contact if usercdata["user_id"] == user_id), None)
            user_role_data = next((userrole for userrole in list_tip_rol if userrole["id_role"] == user_id), None)
            
            if user_contact_data:
                full_user_data = {**user_role_data, **userdata, **user_contact_data}
            else:
                full_user_data = userdata
            # Obtener la imagen del perfil del usuario
            image_row = conn.execute(
                user_image.select()
                .where(user_image.c.user_id == user_id)
                .order_by(user_image.c.id.desc())  # Ordenar por ID de imagen descendente
            ).first()
            
            if image_row:
                file_path_ident = f"./img/profile/{image_row.image_ident}.png"
                file_path_self = f"./img/profile/{image_row.image_self}.png"

                if not os.path.exists(file_path_ident):
                    return {"error": "El archivo de identidad no existe"}
                if not os.path.exists(file_path_self):
                    return {"error": "El archivo de selfie no existe"}

                image_ident = FileResponse(file_path_ident)
                image_self = FileResponse(file_path_self)

                base_url = str(request.base_url)
                image_url_ident = f"{base_url.rstrip('/')}/img/profile/{image_row.image_ident}.png"
                image_url_self = f"{base_url.rstrip('/')}/img/profile/{image_row.image_self}.png"
                
                image_ident_url = f"{str(request.base_url).rstrip('/')}/img/profile/{image_row.image_ident}.png"
                image_self_url = f"{str(request.base_url).rstrip('/')}/img/profile/{image_row.image_self}.png"
                full_user_data["url_ident"] = image_ident_url
                full_user_data["url_self"] = image_self_url
            else:
                full_user_data["url_ident"] = None
                full_user_data["url_self"] = None
            data_list.append(full_user_data)

    return data_list

    
@uverify.put("/admin/veri-user/{user_id}/")
async def verify_user(user_id: int, current_user: str = Depends(get_current_user)):

    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        user_notif = conn.execute(select(users.c.id,user_roles.c.role_id).
                                  select_from(users).
                                  join(user_roles, users.c.id==user_roles.c.user_id).
                                  where(users.c.email==current_user)).first()
        if user_notif[1] != 1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No esta autorizado para realizar esta accion")
       
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
        query_user = conn.execute(users.select().join(user_image, users.c.id == user_image.c.user_id).where(users.c.verify_ident == 0).where(user_image.c.user_id == user_id)).first()
        if not query_user:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=f"El id del usuario no existe o no exiten archivos de imagenes")
        conn.execute(users.update().where(users.c.id == user_id).values(verify_ident=True))
        conn.commit()
        tipval = conn.execute(lval.select().where(lval.c.tipval=="PRNOTF").where(lval.c.description=="Media")).first()
        
        conn.execute(notifications.insert().values(user_id_receives=user_id, 
                                                   user_id_send=user_notif[0], 
                                                   message="El administrador ha verificado las identidades de tu cuenta SmartClinic",
                                                   priority=tipval[2]))
        conn.commit()
        
        # Obtener el registro actualizado
        #updated_role = conn.execute(roles.select().where(roles.c.role_id == rol_id)).first()          
    return Response(content="Se ha verificado la identidad del Usuario", status_code=status.HTTP_200_OK)
        
@uverify.delete("/admin/decli-user/{user_id}/")
async def decline_user(request: Request, user_id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        user_notif = conn.execute(select(users.c.id,user_roles.c.role_id).
                                  select_from(users).
                                  join(user_roles, users.c.id==user_roles.c.user_id).
                                  where(users.c.email==current_user)).first()
        if user_notif[1] != 1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No esta autorizado para realizar esta accion")
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
        image_row = conn.execute(user_image.select().where(user_image.c.user_id == user_id)).first()
        if image_row is not None:
            if image_row:
                file_path_ident = f"./img/profile/{image_row.image_ident}.png"
                file_path_self = f"./img/profile/{image_row.image_self}.png"
                if not os.path.exists(file_path_ident):
                    return {"error": "El archivo de identidad no existe"}
                if not os.path.exists(file_path_self):
                    return {"error": "El archivo de selfie no existe"}
                image_ident = FileResponse(file_path_ident)
                image_self = FileResponse(file_path_self)

                base_url = str(request.base_url)
                try:
                    remove(f"./img/profile/{image_row.image_ident}.png")
                    remove(f"./img/profile/{image_row.image_self}.png")
                    conn.execute(user_image.delete().where(user_image.c.user_id == user_id))
                    conn.commit()
                    conn.execute(lval.select().where(lval.c.tipval=="PRNOTF").where(lval.c.description=="Alta")).first()
        
                    conn.execute(notifications.insert().values(user_id_receives=user_id, 
                                                            user_id_send=user_notif[0], 
                                                            message="El administrador ha declindado la verificacion las identidades de tu cuenta SmartClinic",
                                                            priority=lval[2]))
                    conn.commit()
                    return JSONResponse(content={
                    "removed": True,
                    "message": "Verificacion de usuario declinada"
                }, status_code=status.HTTP_200_OK)
                except FileNotFoundError: 
                    return JSONResponse(content={
                        "removed": False,
                        "message": "File not Found"
                    }, status_code=status.HTTP_404_NOT_FOUND)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado archivos del usuario para declinar")
        
@uverify.delete("/admin/request-user/{user_id}/")
async def decline_user(request: Request, user_id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        user = conn.execute(users.select().where(users.c.id==user_id)).first()
        user_notif = conn.execute(select(users.c.id,user_roles.c.role_id).
                                  select_from(users).
                                  join(user_roles, users.c.id==user_roles.c.user_id).
                                  where(users.c.email==current_user)).first()
        if user_notif[1] != 1:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="No esta autorizado para realizar esta accion")
        if user is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="El usuario no existe")
        image_row = conn.execute(user_image.select().where(user_image.c.user_id == user_id)).first()
        if image_row is not None:
            if image_row:
                file_path_ident = f"./img/profile/{image_row.image_ident}.png"
                file_path_self = f"./img/profile/{image_row.image_self}.png"
                if not os.path.exists(file_path_ident):
                    return {"error": "El archivo de identidad no existe"}
                if not os.path.exists(file_path_self):
                    return {"error": "El archivo de selfie no existe"}
                image_ident = FileResponse(file_path_ident)
                image_self = FileResponse(file_path_self)

                base_url = str(request.base_url)
                try:
                    remove(f"./img/profile/{image_row.image_ident}.png")
                    remove(f"./img/profile/{image_row.image_self}.png")
                    conn.execute(user_image.delete().where(user_image.c.user_id == user_id))
                    conn.commit()
                    conn.execute(lval.select().where(lval.c.tipval=="PRNOTF").where(lval.c.description=="Alta")).first()
        
                    conn.execute(notifications.insert().values(user_id_receives=user_id, 
                                                            user_id_send=user_notif[0], 
                                                            message="El administrador ha solicitado nuevamente tu identidad",
                                                            priority=lval[2]))
                    conn.commit()
                    return JSONResponse(content={
                    "removed": True,
                    "message": "Verificacion de usuario declinada"
                }, status_code=status.HTTP_200_OK)
                except FileNotFoundError: 
                    return JSONResponse(content={
                        "removed": False,
                        "message": "File not Found"
                    }, status_code=status.HTTP_404_NOT_FOUND)
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se han encontrado archivos del usuario para declinar")
        