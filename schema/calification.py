from fastapi import Path
from enum import Enum

class StarsDoctor(str, Enum):
    mala = "Mala"
    buena = "Buena"
    muybuena = "Muy Buena"
    excelente = "Excelente"
    
class ExperienceDoctor(str, Enum):
    regular = "Regular"
    amigable = "Amigable"
    entretenida = "Entretenida"
    fantastica = "Fantastica"
  