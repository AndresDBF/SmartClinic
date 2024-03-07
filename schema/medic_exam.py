from pydantic import BaseModel
from datetime import date
from enum import Enum
from typing import Optional

class MedicExamSchema(BaseModel):
    description: str
    image: str
    