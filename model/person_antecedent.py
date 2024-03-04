from sqlalchemy import Column, Table, ForeignKey, Index, func
from sqlalchemy.sql.sqltypes import Integer, String, Boolean, TIMESTAMP
from config.db import meta_data, engine


person_antecedent = Table("person_antecedent",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("hypertension", Boolean, nullable=False),
                   Column("diabetes", Boolean, nullable=False),
                   Column("asthma", Boolean, nullable=False),
                   Column("allergy_medicine", String(250), nullable=False),
                   Column("allergy_foot", String(250), nullable=False),
                   Column("other_condition", String(250), nullable=False),
                   Column("operated", String(250), nullable=False),
                   Column("take_medicine", String(250), nullable=False),
                   Column("religion", String(250), nullable=False),
                   Column("job_occupation", String(250), nullable=False),
                   Column("disease_six_mounths", String(250), nullable=False),
                   Column("last_visit_medic", String(250), nullable=False),
                   Column("visit_especiality", String(250), nullable=False),
                   Column("created_at", TIMESTAMP, nullable=False)
)

Index("search_antecedent", 
      person_antecedent.c.allergy_medicine, 
      person_antecedent.c.allergy_foot, 
      person_antecedent.c.other_condition, 
      person_antecedent.c.operated, 
      person_antecedent.c.take_medicine, 
      person_antecedent.c.religion, 
      person_antecedent.c.job_occupation, 
      person_antecedent.c.disease_six_mounths, 
      person_antecedent.c.last_visit_medic, 
      person_antecedent.c.visit_especiality, 
      person_antecedent.c.created_at
)

meta_data.create_all(engine)