
from fastapi import Path, Body, UploadFile, File
from pydantic import BaseModel, constr, EmailStr
from datetime import datetime, date
from typing import Optional
from pydantic import Field

class AntecedentSchema(BaseModel):
    hypertension: bool
    diabetes: bool
    asthma: bool
    allergy_medicine_value: bool = Field(default=False)
    allergy_medicine_text: str = Field(default=None)
    allergy_foot_value: bool = Field(default=False)  # Agregar este campo
    allergy_foot_text: str = Field(default=None)
    other_condition_value: bool = Field(default=False)
    other_condition_text: str = Field(default=None)
    operated_value: bool = Field(default=False)
    operated_text: str = Field(default=None)
    take_medicine_value: bool = Field(default=False)
    take_medicine_text: str = Field(default=None)
    religion_value: bool = Field(default=False)
    religion_text: str = Field(default=None)
    job_occupation: str  = Field(default=None)
    disease_six_mounths_value: bool = Field(default=False)
    disease_six_mounths_text: str = Field(default=None)
    last_visit_medic: str = Field(default=None)
    visit_especiality: str = Field(default=None)


class PersonalHobbieSchema(BaseModel):
    consumed_text: str = Field(default=None)

class FamilyAntecedentSchema(BaseModel):
    disease_mother_value: bool = Field(default=False)
    disease_mother_text: str = Field(default=None)
    disease_father_value: bool = Field(default=False)
    disease_father_text: str = Field(default=None)

class Antecedent(BaseModel):
    antecedent: AntecedentSchema
    personal_hobbie: PersonalHobbieSchema
    family_antecedent: FamilyAntecedentSchema