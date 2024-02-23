from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta_data, engine


roles = Table("roles", meta_data,
              Column("role_id", Integer, primary_key=True),
              Column("role_name", String(191), nullable=False, unique=True))

meta_data.create_all(engine)