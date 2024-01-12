# app/models/coinflow_user.py

'''
SQLAlchemy
定义ORM映射类coinflow
'''

from sqlalchemy import Column, Integer, String, Date, Float, DateTime, func,Boolean
from app.db.base import Base
from app.db.session import async_engine


class Coinflow_user(Base):
    __tablename__ = 'coinflow_user'

    coinflow_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    order_id = Column(Integer)
    amount = Column(Float,nullable = False)
    is_income = Column(Boolean,nullable = False)
    notes = Column(String(255))
    create_at = Column(DateTime, default=func.now())


