from fastapi import APIRouter, File, HTTPException, status, Form, Response, Depends, Request
from fastapi.responses import JSONResponse
from fastapi import Query

from config.db import engine

from model.user import users
from model.notification import notifications

from router.logout import get_current_user

from datetime import datetime

from sqlalchemy import select, insert, func
#from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError

from typing import Optional

notify = APIRouter(tags=["Notifications"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

""" @notify.get("/user/notifications/")
async def get_list_notifications(user_id: int, skip: int = 0, limit: int = 25, current: str = Depends(get_current_user)):
    with engine.connect() as conn:
        query = (
            select(notifications.c.id, notifications.c.message, notifications.c.show)
            .where(notifications.c.user_id_receives == user_id)
            .order_by(notifications.c.show.asc(), notifications.c.created_at.asc())
            .offset(skip)
            .limit(limit)
        )
        notification = conn.execute(query).fetchall()
        
        if not notification:
            return {"message": "No hay notificaciones disponibles"}, status.HTTP_404_NOT_FOUND
        
        list_notification = [
            {
                "notif_id": row[0],
                f"notification {index+1}": row[1],
                "show_point": row[2]
            }
            for index, row in enumerate(notification)
        ]
        return list_notification """

    
@notify.put("/user/update/notification/")
async def update_notifications(notif_id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(notifications.update().
                     where(notifications.c.id == notif_id)
                     .values(show=False))
        conn.commit()
        return JSONResponse(content={
            "touch_notification": True})

@notify.get("/user/notifications/")
async def get_list_notifications(request: Request, user_id: int, page: Optional[int] = Query(1, ge=1), current_user: str = Depends(get_current_user)):
    page_size = 25
    
    with engine.connect() as conn:
        query = (
            select(notifications.c.id, notifications.c.message, notifications.c.show)
            .where(notifications.c.user_id_receives == user_id)
            .order_by(notifications.c.show.asc(), notifications.c.created_at.asc())
        )
        
        notifications_total = conn.execute(query).fetchall()
        total_notifications = len(notifications_total)
        
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
        
    notifications_page = notifications_total[start_index:end_index]
    
    if not notifications_page:
        return {"message": "No hay notificaciones disponibles"}, status.HTTP_404_NOT_FOUND
    
    list_notification = [
        {
        "notif_id": row[0],
        f"notification {index+1}": row[1],
        "show_point": row[2]
        }
        for index, row in enumerate(notifications_page)
    ]
    
    # Calcular el número total de páginas
    total_pages = total_notifications // page_size
    if total_notifications % page_size != 0:
        total_pages += 1
    
    # Construir los links para la paginación
    base_url = str(request.base_url)

    next_page = f"{base_url.rstrip('/')}/user/notifications/?user_id={user_id}&page={page + 1}" if page < total_pages else None
    previous_page = f"{base_url.rstrip('/')}/user/notifications/?user_id={user_id}&page={page - 1}" if page > 1 else None
    
    # Construir la respuesta JSON incluyendo la información de paginación
    data_noti = {
        "links":{
        "next": next_page,
        "previous": previous_page
        },
        "data": list_notification,
        "total": total_notifications,
    }
    
    return data_noti