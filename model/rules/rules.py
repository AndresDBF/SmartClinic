from sqlalchemy import Column, Table, Integer, ForeignKey, String
from config.db import meta_data, engine
from model import user

rules = Table("rules", meta_data,
              Column("role_id", Integer, primary_key=True),
              Column("role_name", Integer, unique=True))

meta_data.create_all(engine)