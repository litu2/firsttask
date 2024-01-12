# app/models/favorite.py

'''
SQLAlchemy
定义ORM映射类Favorite
'''

from sqlalchemy import Column, Integer
from app.db.base import Base
from app.db.session import async_engine


class Favorite(Base):
    __tablename__ = 'favorites'

    favorite_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    advisor_id = Column(Integer)
