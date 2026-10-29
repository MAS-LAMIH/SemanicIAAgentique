from sqlalchemy import Column, Integer, String,DateTime
from database import Base 

class Event(Base):
    __tablename__ = "events"
    id = Column(Integer, primary_key=True, index=True, autoincrement=True)
    name = Column(String)
    date = Column(DateTime)
    description = Column(String)


