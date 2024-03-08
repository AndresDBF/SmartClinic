from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from model.roles.roles import roles
from model.roles.user_roles import user_roles
from model.user import users
from model.usercontact import usercontact
from model.images.user_image import user_image
from model.roles.roles import roles
from model.roles.user_roles import user_roles
from model.tip_consult import tip_consult
from model.patient_consult import patient_consult
from model.diagnostic import diagnostic
from model.person_antecedent import person_antecedent 
from model.person_habit import personal_habit
from model.family_antecedent import family_antecedent
from model.medical_exam import medical_exam
from model.images.files_medical_exam_doc import files_medical_exam_doc
from model.images.files_medical_exam_pat import files_medical_exam_pat
from model.inf_medic import inf_medic

from model.blacklist_token import blacklist_token

from router.admin.list_user import luser
from router.admin.users_verify import uverify
from router.paciente.home import patienthome
from router.doctor.home import doctorhome
from router.admin.home import adminhome
from router.doctor.doctor import routedoc
from router.paciente.user import user
from router.paciente.validate_image import imageuser
from router.paciente.verif_email import email
from router.paciente.medic_exam import userexam
from router.roles.roles import routerol
from router.roles.user_roles import routeuserrol 
from router.paciente.tipconsult import routetipco
from router.doctor.diagnostic import routediag
from router.doctor.medical_exam import exam
from router.doctor.inf_medic import routeim
from router.paciente.antecedent import routeantec
from router.logout import routelogout
#from router.test_image import router

app = FastAPI()
app.title = "Documentación SmartClinic"
app.mount("/img/profile", StaticFiles(directory="img/profile"), name="profile_images")
app.mount("/img/medic", StaticFiles(directory="img/medic"), name="medic_exam")


app.include_router(luser)
app.include_router(uverify)
app.include_router(patienthome)
app.include_router(doctorhome)
app.include_router(adminhome)
app.include_router(routerol)
app.include_router(routeuserrol)

app.include_router(routeantec)

app.include_router(user)
app.include_router(imageuser)
app.include_router(email)
app.include_router(userexam)
app.include_router(routedoc)
app.include_router(routetipco)
app.include_router(routediag)
app.include_router(exam)
app.include_router(routeim)
app.include_router(routelogout)
#app.include_router(router)


