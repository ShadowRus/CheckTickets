from sqlalchemy import Column, Integer, String
from api.deps import Base

from pydantic import BaseModel,Field
from typing import Sequence, List, Optional

class CRPT(Base):
    __tablename__ = "CRPT"
    id = Column(Integer, primary_key=True, index=True)
    dm_base64= Column(String)
    dm_serial=Column(String)
    print_at= Column(String)
    is_verify = Column(String)

class DMCode(BaseModel):
    dm_base64: str=Field()
    dm: str=Field()