from fastapi import Path, Body, UploadFile, File
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional

class AntecedentSchema(BaseModel):
    hypertension: bool
    diabetes: bool
    asthma: bool
    allergy_medicine: str
    allergy_foot: str
    other_condition: str
    operated: str
    take_medicine: str
    religion: str
    job_occupation: str
    disease_six_mounths: str
    last_visit_medic: str
    visit_especiality: str

class PersonalHobbieSchema(BaseModel):
    consumed: str
    
class FamilyAntecedentSchema(BaseModel):
    disease_mother: str
    disease_father: str

class Antecedent: 
    hypertension: bool
    diabetes: bool
    asthma: bool
    allergy_medicine: str
    allergy_foot: str
    other_condition: str
    operated: str
    take_medicine: str
    religion: str
    job_occupation: str
    disease_six_mounths: str
    last_visit_medic: str
    visit_especiality: str
    consumed: str
    disease_mother: str
    disease_father: str