#app/schemas/favorite.py

'''
favorite的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel ,Field
from typing import Optional
from datetime import datetime



class Favorite(BaseModel):
    pass
