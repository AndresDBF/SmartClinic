from fastapi import FastAPI
from router.users.user import user

app = FastAPI()
app.title = "Documentación SmartClinic"

app.include_router(user)
