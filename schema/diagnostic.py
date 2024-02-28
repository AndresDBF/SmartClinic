from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class DiagnosticSchema(BaseModel):
    id: Optional[int] = 1
    problem_patient: str
    patient: str
    id_atent: str
    doctor: str
    birthdate: date
    gender: str