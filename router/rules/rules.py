from fastapi import APIRouter, HTTPException, status
from fastapi.responses import RedirectResponse
from config.db import engine
from model.rules.rules import rules
from sqlalchemy import insert, select
from typing import List
from sqlalchemy import insert, select, func

rule = APIRouter(tags=['rules'], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})


#route en desarrollo...
@rule.post("/", tags=["rules"])
async def verify_rules():
    with engine.connect() as conn:
        query = conn.execute(rules.select()).fetchall()
        print(query)
        if query is not None:
            return RedirectResponse(url="/api/user/login", status_code=status.HTTP_301_MOVED_PERMANENTLY)
        rule_user = conn.execute(insert(rules).values(1,"usuario"))
        conn.execute(rule_user)
        conn.commit()
        rule_user = conn.execute(insert(rules).values(1,"doctor"))
        conn.execute(rule_user)
        conn.commit()
    return RedirectResponse(url="/api/user/login", status_code=status.HTTP_201_CREATED)

