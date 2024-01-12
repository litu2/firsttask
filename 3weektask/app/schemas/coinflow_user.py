#app/schemas/coinflow_user.py
'''
coinflow_user的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel 
from typing import Optional
from datetime import datetime

class UsercoinFlow(BaseModel):
    amount : Optional[float]
    notes : Optional[str]
    is_income : Optional[bool]
    create_At : Optional[datetime]
