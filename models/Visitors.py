from sqlalchemy import Column, Integer, String
from api.deps import Base

class Visitors(Base):
    __tablename__ = "Visitors"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    surname = Column(String)
    second_name  = Column(String)
    org = Column(String)
    position = Column(String)
    qrcode = Column(String)
    is_check = Column(Integer)
    check_at = Column(Integer)

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)

