from fastapi import APIRouter, File, UploadFile, HTTPException, status, Form, Response, Depends
from fastapi.responses import JSONResponse

from config.db import engine

from model.user import users
from model.notification import notifications

from router.logout import get_current_user

from datetime import datetime

from sqlalchemy import select, insert, func
#from fastapi_pagination.ext.sqlalchemy import paginate
from sqlalchemy.exc import IntegrityError

notify = APIRouter(tags=["Notifications"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

@notify.get("/user/notifications/")
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
        return list_notification

    
@notify.put("/user/update/notification/")
async def update_notifications(notif_id: int, current_user: str = Depends(get_current_user)):
    with engine.connect() as conn:
        conn.execute(notifications.update().
                     where(notifications.c.id == notif_id)
                     .values(show=False))
        conn.commit()
        return JSONResponse(content={
            "touch_notification": True})
    