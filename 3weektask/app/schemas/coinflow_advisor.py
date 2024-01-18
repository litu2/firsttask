#app/schemas/coinflow_advisor.py
'''
coinflow_advisor的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel
from typing import Optional
from datetime import datetime

calss AdvisorcoinFlow(BaseModel):
    amount : float
    notes : str
    is_income : bool
    create_At : datetime
