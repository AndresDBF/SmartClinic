from sqlalchemy import Column, Table, Integer, ForeignKey, String
from config.db import meta_data, engine
from model import user

user_roles = Table("user_roles", meta_data,
              Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
              Column("role_id", Integer, ForeignKey("roles.role_id"), nullable=False)
)


meta_data.create_all(engine)


