from sqlalchemy import Column, Table, ForeignKey, Index, Boolean, String, TIMESTAMP, Integer
from sqlalchemy.sql.schema import MetaData
from config.db import meta_data, engine

person_antecedent = Table(
    "person_antecedent", meta_data,
    Column("id", Integer, primary_key=True, nullable=False),
    Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
    Column("hypertension", Boolean, nullable=False),
    Column("diabetes", Boolean, nullable=False),
    Column("asthma", Boolean, nullable=False),
        Column("allergy_medicine_value", Boolean, nullable=False),
    Column("allergy_medicine_text", String(250), nullable=True),
        Column("allergy_foot_value", Boolean, nullable=False),
    Column("allergy_foot_text", String(250), nullable=True),
        Column("other_condition_value", Boolean, nullable=False),
    Column("other_condition_text", String(250), nullable=True),
        Column("operated_value", Boolean, nullable=False),
    Column("operated_text", String(250), nullable=True),
        Column("take_medicine_value", Boolean, nullable=False),
    Column("take_medicine_text", String(250), nullable=True),
        Column("religion_value", Boolean, nullable=False),
    Column("religion_text", String(250), nullable=True),
    Column("job_occupation", String(250), nullable=True),
        Column("disease_six_mounths_value", Boolean, nullable=False),
    Column("disease_six_mounths_text", String(250), nullable=True),
    Column("last_visit_medic", String(250), nullable=True),
    Column("visit_especiality", String(250), nullable=True),
    Column("created_at", TIMESTAMP, nullable=False)
)

# Crear la tabla solo si no existe
meta_data.create_all(engine, checkfirst=True)

# Crear índices solo si no existen
indexes = [
    Index('idx_allergy_medicine_text', person_antecedent.c.allergy_medicine_text),
    Index('idx_allergy_foot_text', person_antecedent.c.allergy_foot_text),
    Index('idx_other_condition_text', person_antecedent.c.other_condition_text),
    Index('idx_operated_text', person_antecedent.c.operated_text),
    Index('idx_take_medicine_text', person_antecedent.c.take_medicine_text),
    Index('idx_religion_text', person_antecedent.c.religion_text),
    Index('idx_job_occupation', person_antecedent.c.job_occupation),
    Index('idx_disease_six_mounths_text', person_antecedent.c.disease_six_mounths_text),
    Index('idx_last_visit_medic_text', person_antecedent.c.last_visit_medic),
    Index('idx_visit_especiality_text', person_antecedent.c.visit_especiality)
]

# Ejecutar la creación de índices
for index in indexes:
    index.create(bind=engine, checkfirst=True)



