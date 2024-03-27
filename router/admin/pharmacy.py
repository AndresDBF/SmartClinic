import hashlib
import os
from fastapi import APIRouter, status, HTTPException, Depends, Form, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles

from config.db import engine

from model.pharmacy import pharmacy
from model.pharmacy_contact import pharmacy_contact
from model.images.pharmacy_sample import pharmacy_sample
from model.images.pharmacy_image import pharmacy_image

from router.logout import get_current_user
from router.roles.roles import verify_rol_admin


from sqlalchemy import insert, select, func, or_, and_
from sqlalchemy.exc import IntegrityError

from starlette.requests import Request

from os import getcwd, remove

from jose import jwt, JWTError
from typing import Optional, List

from datetime import time, datetime

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..', '..'))
    
routepharmacy = APIRouter(tags=["Admin Routes"], responses={status.HTTP_404_NOT_FOUND: {"message": "Direccion No encontrada"}})

img_phar_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'pharmacy'))
img_galery_directory = os.path.abspath(os.path.join(project_root, 'SmartClinic', 'img', 'galery'))


routepharmacy.mount("/img", StaticFiles(directory=img_phar_directory), name="img")
routepharmacy.mount("/img", StaticFiles(directory=img_galery_directory), name="img")

@routepharmacy.get("/admin/list-pharmacy")
async def list_pharmacy(current_user: str = Depends(get_current_user)):
    verify_rol_admin(current_user)
    

@routepharmacy.post("/admin/create-new-pharmacy/")
async def create_new_pharmacy(
    request: Request,
    name: str = Form(..., description="Nombre de la Farmacia"),
    details: str = Form(..., description="Descripcion de la Farmacia"),
    name_direction: List[str] = Form(..., description="Titulo de la direccion"),
    desc_direction: List[str] = Form(..., description="Descripcion de la Direccion"),
    phone: List[str] = Form(..., description="Numero de Telefono"),
    opening: time = Form(..., description="Fecha y hora de apertura en formato HH:MM:SS"),
    closing: time = Form(..., description="Fecha y hora de cierre en formato HH:MM:SS"),
    coordinates: List[str] = Form(..., description="Coordenadas de la ubicacion"),
    image: UploadFile = File(..., description="Imagen principal"),
    sample: UploadFile = File(..., description="Imagen de muestra"),
    current_user: str = Depends(get_current_user)):
    
    opening = opening.strftime("%H:%M:%S")
    closing = closing.strftime("%H:%M:%S")
    sysdate = datetime.now()
    format_hour = sysdate.strftime("%H:%M:%S")
    if format_hour >= opening and format_hour <= closing:
        data_open = True
    else:   
        data_open = False
    with engine.connect() as conn:
        new_client = conn.execute(pharmacy.insert().values(name=name, details=details))
        conn.commit()
    id = new_client.lastrowid
    
    for name_dir, desc_dir, phon, coord in zip(name_direction, desc_direction, phone, coordinates): 
        with engine.connect() as conn:
            new_client = conn.execute(pharmacy_contact.insert().values(pharmacy_id=id,
                                                name_direction=name_dir,
                                                desc_direction=desc_dir,
                                                phone=phon,
                                                opening=opening,
                                                closing=closing,
                                                open= data_open,
                                                coordinates=coord,
                                                ))
            conn.commit()
    with engine.connect() as conn:
        if image.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            conn.execute(pharmacy.delete().where(pharmacy.c.id==id))
            conn.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen principal debe ser una imagen JPEG, JPG o PNG")
        if sample.content_type not in ["image/jpeg", "image/jpg", "image/png"]:
            conn.execute(pharmacy.delete().where(pharmacy.c.id==id))
            conn.commit()
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="La imagen de muestra debe ser una imagen JPEG, JPG o PNG")
        print("pasa los if")
        content_img = await image.read()
        content_samp = await sample.read()
        print("lee los archivos")
        img_hash = hashlib.sha256(content_img).hexdigest()
        samp_hash = hashlib.sha256(content_samp).hexdigest()
        print("encripta las fotos")
        with open(f"img/pharmacy/{img_hash}.png", "wb") as file_img:
            file_img.write(content_img)
        print("inserta la primera foto")
        with open(f"img/galery/{samp_hash}.png", "wb") as file_samp:
            file_samp.write(content_samp)   
        print("inserta la segunda foto")
        
        conn.execute(pharmacy_image.insert().values(pharmacy_id=id,
                                                    image_original=image.filename,
                                                    image=img_hash))
        conn.commit()
        conn.execute(pharmacy_sample.insert().values(pharmacy_id=id,
                                                    image_original=sample.filename,
                                                    image=samp_hash))
        conn.commit()
        print("inserta las fotos")
        file_path_img = f"./img/pharmacy/{img_hash}.png"
        file_path_samp = f"./img/galery/{samp_hash}.png"        

        image_ident = FileResponse(file_path_img)
        image_self = FileResponse(file_path_samp)
            
        base_url = str(request.base_url)
        image_url_ident = f"{base_url.rstrip('/')}/img/profile/{img_hash}.png"
        image_url_self = f"{base_url.rstrip('/')}/img/profile/{samp_hash}.png"        
        return JSONResponse(content={
                "saved": True,
                "message": "Farmacia creada correctamente"
        }, status_code=status.HTTP_201_CREATED)
        
    
  

    