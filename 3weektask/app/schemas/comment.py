#app/schemas/comment.py
'''
comment的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel ,Field
from typing import Optional
from datetime import datetime





class CommentCreate(BaseModel):

    context: Optional[str] = Field(...,example="这个顾问回答地很棒")
    rating: Optional[float] = Field(...,example="5.0")


class CommentList(BaseModel):

    username : str 

    context : str

    rating : float

    create_at : datetime
     

