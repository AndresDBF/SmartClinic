from sqlalchemy import Column, Table
from sqlalchemy.sql.sqltypes import String, Integer, Boolean, DateTime, Numeric, Date
from config.db import engine, meta_data

users = Table("users", meta_data,
              Column("id", Integer, primary_key= True),
              Column("username", String(191), nullable= False),
              Column("email", String(191), nullable= False),
              Column("password", String(191), nullable=False),
              Column("name", String(191), nullable= False),
              Column("last_name", String(191), nullable= False),
              Column("birthdate", Date, nullable= False),
              Column("gender", String(1), nullable= False, default="M"),
              Column("tipid", String(1), nullable= False, default="V"),
              Column("identification", Numeric, nullable= False),
              Column("disabled", Boolean, nullable= False, default=False),
              Column("verify_ident", Boolean, nullable=False, default=False)
              )

meta_data.create_all(engine)
