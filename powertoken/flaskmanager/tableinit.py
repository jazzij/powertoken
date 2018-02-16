from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import tabledefs

engine = create_engine('sqlite:////export/scratch/ptdata/pt.db', echo=True, pool_pre_pring=True)

Session = sessionmaker(bind=engine)
session = Session()

session.add()