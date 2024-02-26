from fastapi import FastAPI
from model.user import users
from model.usercontact import usercontact
from model.images.user_image import user_image
from model.roles.roles import roles
from model.roles.user_roles import user_roles
from model.diagnostic import diagnostic
from router.users.user import user
from router.users.validate_image import img
from router.roles.roles import routerol
from router.roles.user_roles import routeuserrol
from router.diagnostic import routediag

app = FastAPI()
app.title = "Documentación SmartClinic"

app.include_router(user)
app.include_router(routerol)
app.include_router(routeuserrol)
app.include_router(img)
app.include_router(routediag)

