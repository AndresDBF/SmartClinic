from fastapi import FastAPI
from router.users.user import user
from router.users.validate_image import img
from router.roles.roles import routerol
from router.roles.user_roles import routeuserrol

app = FastAPI()
app.title = "Documentación SmartClinic"

app.include_router(user)
app.include_router(routerol)
app.include_router(routeuserrol)
app.include_router(img)

