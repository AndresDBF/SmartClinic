from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta_data, engine


family_antecedent = Table("family_antecedent", meta_data, 
                          Column("id", Integer, primary_key=True, nullable=False),
                          Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                          Column("disease_mother", String(250), nullable=False),
                          Column("disease_father", String(250), nullable=False)
)

meta_data.create_all(engine)