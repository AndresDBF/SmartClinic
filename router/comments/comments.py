import os
from fastapi import APIRouter, File, HTTPException, status, Form, Response, Depends, Request, Query
from fastapi.responses import FileResponse, JSONResponse

from config.db import engine

from model.user import users
from model.images.user_image_profile import user_image_profile
from model.comments import comments
from model.history_comments import history_comments
from model.notification import notifications

from router.logout import get_current_user

from datetime import datetime

from sqlalchemy import select, insert, func, or_, and_

from sqlalchemy.exc import IntegrityError
from typing import Optional


routecomments = APIRouter(tags=["Comments"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

#REVISAR ESTE CODIGO CON EL FRONTED
@routecomments.get("/api/comments/")
async def history_comments_users(doc_id: int, patient_id, request: Request, page: Optional[int] = Query(1, ge=1), current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        ver_ident_us_pat = conn.execute(comments.select()
                                        .where(comments.c.user_id_patient == patient_id)
                                        .where(comments.c.user_id_doctor == doc_id)).first()
        print(ver_ident_us_pat)
    if ver_ident_us_pat is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No esta autorizado para entrar a esta conversacion")
    page_size = 25
    with engine.connect() as conn:
        query = (
            select(history_comments.c.id, history_comments.c.message, user_image_profile.c.image_profile)
            .select_from(history_comments)
            .join(users, history_comments.c.user_id == users.c.id)
            .join(user_image_profile, users.c.id == user_image_profile.c.user_id)
            .where(
                or_(
                    history_comments.c.user_id == doc_id,
                    history_comments.c.user_id == patient_id
                )
            )
            .order_by(history_comments.c.created_at.asc())
        )
        
        history_total = conn.execute(query).fetchall()
        total_history = len(history_total)
    
        
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
        
    history_page = history_total[start_index:end_index]
    
    if not history_page:
        return {"message": "No existencomentarios"}, status.HTTP_404_NOT_FOUND
    
    list_history = [
        {
            "notif_id": row[0],
            f"notification {index+1}": row[1],
            "show_point": row[2]
        }
        for index, row in enumerate(history_page)
    ]
    
    data_list = []
    with engine.connect() as conn:
        for list in list_history:
            user_id = list["id"]
            full_data = {**list}
            image_row = conn.execute(user_image_profile.select()
                                    .where(user_image_profile.c.user_id == user_id)
                                    .order_by(user_image_profile.c.id.desc())).first()
                
            if image_row:
                file_path_prof = f"./img/profile/{image_row.image_profile}.png"
                if not os.path.exists(file_path_prof):
                    return {"error": "La imagen de perfil no existe"}

                prof_img = FileResponse(file_path_prof)
                base_url = str(request.base_url)
                image_url_prof = f"{base_url.rstrip('/')}/img/profile/{image_row.image_profile}.png"
                
                full_data["url_prof_img"] = image_url_prof
                
            else:
                
                full_data["url_prof_img"] = None
            data_list.append(full_data)
    
    
    total_pages = total_history // page_size
    if total_history % page_size != 0:
        total_pages += 1
    
    base_url = str(request.base_url)

    next_page = f"{base_url.rstrip('/')}/user/notifications/?doc_id={doc_id}&?patient_id={patient_id}page={page + 1}" if page < total_pages else None
    previous_page = f"{base_url.rstrip('/')}/user/notifications/?doc_id={doc_id}&?patient_id={patient_id}page={page - 1}" if page > 1 else None
    
    data_noti = {
        "links":{
        "next": next_page,
        "previous": previous_page
        },
        "data": data_list,
        "total": total_history,
    }
    
    return data_noti

@routecomments.post("/api/create/comment/") 
async def create_comment(user_id: int, message: str = Form(...)):
    with engine.connect() as conn: 
        ver_us = conn.execute(users.select().where(users.c.id==user_id)).first()
        if ver_us is None:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="no se ha encontrado el usuario")
        conn.execute(comments.insert().values(user_id=user_id, message=message))
        conn.commit()
    return JSONResponse(content={
        "created": True,
        "message": "mensaje enviado"
    }, status_code=status.HTTP_201_CREATED)
    


    
    
    
    
    
        
        