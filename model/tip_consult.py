from sqlalchemy import Column, Table, ForeignKey
from sqlalchemy.sql.sqltypes import String, Integer, Date
from config.db import engine, meta_data

tip_consult = Table("tip_consult",meta_data,
                   Column("id",Integer,primary_key=True,nullable=False),
                   Column("tipconsult",String(30), nullable=False)
)

meta_data.create_all(engine)