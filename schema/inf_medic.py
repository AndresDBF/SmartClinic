from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class infMedicSchema(BaseModel):
    problem_patient: str
    patient: str
    id_atent: str
    doctor: str
    birthdate: date
    gender: str