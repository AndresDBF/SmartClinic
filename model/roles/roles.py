from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import Integer, String
from config.db import meta_data, engine

roles = Table("roles", meta_data,
              Column("role_id", Integer, primary_key=True),
              Column("role_name", String(191), nullable=False, unique=True))


meta_data.create_all(engine)


with engine.connect() as conn:
    query = conn.execute(roles.select()).fetchall()
    if query is None:
        roles_data = [
            {"role_id": 1, "role_name": "Admin"},
            {"role_id": 2, "role_name": "Patient"},
            {"role_id": 3, "role_name": "Doctor"},
        ]
        conn.execute(roles.insert(), roles_data)
        conn.commit()