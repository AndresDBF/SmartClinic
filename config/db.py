from sqlalchemy import create_engine, MetaData

engine = create_engine("mysql+pymysql://root:@localhost:3306/smartclinic")

conn = engine.connect()

meta_data = MetaData()