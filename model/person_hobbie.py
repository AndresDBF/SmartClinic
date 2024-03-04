from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta_data, engine

person_hobbie = Table("person_hobbie", meta_data,
                      Column("id", Integer, primary_key=True, nullable=False),
                      Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                      Column("consumed", String(250), nullable=False))

meta_data.create_all(engine)