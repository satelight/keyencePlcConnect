from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.schema import Column
from sqlalchemy.types import Integer,String

engine = create_engine("sqlite:///app.sqlite3")
Base = declarative_base()

class Test(Base):
    __tablename__ = "test"
    id = Column(Integer,primary_key=True,autoincrement=True)
    name = Column(String(255))
    age = Column(Integer)

Base.metadata.create_all(engine)


