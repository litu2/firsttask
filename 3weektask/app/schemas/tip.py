#app/schemas/tip.py
'''
tip的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel ,Field
from typing import Optional
from datetime import datetime



class TipCreate(BaseModel):

    amount:Optional[float] = Field(...,example="20.0")
