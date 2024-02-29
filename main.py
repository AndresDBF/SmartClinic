from fastapi import FastAPI
from model.user import users
from model.usercontact import usercontact
from model.images.user_image import user_image
from model.roles.roles import roles
from model.roles.user_roles import user_roles
from model.tip_consult import tip_consult
from model.patient_consult import patient_consult
from model.diagnostic import diagnostic
from model.inf_medic import inf_medic
from router.paciente.home import userhome
from router.admin.users_verify import uverify
from router.doctor import routedoc
from router.paciente.user import user
from router.paciente.validate_image import img
from router.paciente.verif_email import email
from router.roles.roles import routerol
from router.roles.user_roles import routeuserrol
from router.tipconsult import routetipco
from router.diagnostic import routediag
from router.inf_medic import routeim
from router.test_image import router

app = FastAPI()
app.title = "Documentación SmartClinic"

app.include_router(router)

app.include_router(userhome)
app.include_router(uverify)
app.include_router(user)
app.include_router(img)
app.include_router(email)
app.include_router(routedoc)
app.include_router(routerol)
app.include_router(routeuserrol)
app.include_router(routetipco)
app.include_router(routediag)
app.include_router(routeim)


