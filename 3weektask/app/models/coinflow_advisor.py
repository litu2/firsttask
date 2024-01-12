# app/models/coinflow_advisor.py

'''
SQLAlchemy
定义ORM映射类Coinflow_advisor
'''

from sqlalchemy import Column, Integer, String, Date, Float, DateTime, func, Boolean
from app.db.base import Base
from app.db.session import async_engine


class Coinflow_advisor(Base):
    __tablename__ = 'coinflow_advisor'

    coinflow_id = Column(Integer, primary_key=True, index=True)
    advisor_id = Column(Integer)
    order_id = Column(Integer)
    amount = Column(Float, nullable=False)
    is_income = Column(Boolean, nullable=False)
    notes = Column(String(255))
    create_at = Column(DateTime, default=func.now())
