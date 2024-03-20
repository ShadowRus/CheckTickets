from sqlalchemy import Column, Integer, String
from api.deps import Base

from pydantic import BaseModel, HttpUrl, Field
from typing import Sequence, List, Optional



class Visitors(Base):
    __tablename__ = "Visitors"
    id = Column(Integer, primary_key=True, index=True)
    surname = Column(String)
    name = Column(String)
    organization = Column(String)
    position = Column(String)
    regQR = Column(String)
    templ_name = Column(String)
    is_print = Column(Integer)
    is_check = Column(Integer)
    check_status = Column(String)
    check_in = Column(String)
    is_manual = Column(Integer)

class Users(Base):
    __tablename__ = "Users"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String)
    code = Column(String)

class Devices(Base):
    __tablename__="Devices"
    id = Column(Integer,primary_key=True,index=True)
    is_connected = Column(String)
    ip = Column(String,index=True)
    printer_id = Column(Integer,index=True)
    label_id = Column(Integer)

class Template(Base):
    __tablename__ = "PrintTemplates"
    id = Column(Integer, primary_key=True, index=True)
    templ_name = Column(String)
    templ_data = Column(String)
    is_default = Column(Integer)


class TemplateResponse(BaseModel):
    name:str=Field(default=None)
    label: str = Field()
    is_default: int = Field(default=0)


class PrinterService(Base):
    __tablename__="Printer"
    id = Column(Integer, primary_key=True, index=True)
    print_name = Column(String)
    url = Column(String)
    port = Column(Integer)
    type = Column(Integer)
    # 1 - net printer, 2 - printer service pdt
    is_default = Column(Integer)
    is_online = Column(Integer)

class PrinterRespone(BaseModel):
    name: str=Field()
    url: str=Field()
    port:int= Field(default=9100)
    type:int=Field(default=1)
    is_default: int=Field(default = 0)

