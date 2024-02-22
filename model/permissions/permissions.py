from sqlalchemy import Column, Table, Integer, ForeignKey, String
from config.db import meta_data, engine
from model import user

permissions = ("permissions", meta_data,
               Column("permission_id", Integer, primary_key=True),
               Column("permission_name", String, nullable=False))

meta_data.create_all(engine)
