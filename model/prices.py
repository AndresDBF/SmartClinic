from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Date
from config.db import engine, meta_data

prices = Table("prices",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("user_id", Integer, ForeignKey("users.id"), nullable=False),
                   Column("tip_page", String(20), nullable=False),
                   Column("bank", String(60), nullable=False),
                   Column("method_page", String(60), nullable=False),
                   Column("tipconsult",String(30), nullable=False)
)

meta_data.create_all(engine, checkfirst=True)