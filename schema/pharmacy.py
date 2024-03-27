from pydantic import BaseModel
from datetime import date, time
from enum import Enum
from typing import Optional

class DetailPharmacy(BaseModel):
    name: str
    details: str
    
class ContactPharmacy(BaseModel):
    name_direction: str 
    desc_direction: str 
    phone: str 
    opening: time 
    closing: time 
    coordinates: str
    
class Pharmacy(BaseModel):
    DetailPharmacy: DetailPharmacy
    ContactPharmacy: ContactPharmacy