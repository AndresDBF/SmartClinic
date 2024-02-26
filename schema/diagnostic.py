from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class DiagnosticSchema(BaseModel):
    id: Optional[int] = 1
    patient: str
    id_atent: str
    doctor: str
    birthdate: date
    gender: str


class problem_patient(str, Enum):
    Resfriado = "Resfriado"
    Diabetes = "Diabetes"
    Covid = "Covid19"