from fastapi import FastAPI
from router.users.user import user
from router.users.validate_image import img
#from router.rules.rules import rule

app = FastAPI()
app.title = "Documentación SmartClinic"

#app.include_router(rule)
app.include_router(user)
app.include_router(img)

