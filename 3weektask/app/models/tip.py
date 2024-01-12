# app/models/tip.py

'''
SQLAlchemy
定义ORM映射类Tip
'''

from sqlalchemy import Column, Integer, String, Date, Float, DateTime, func
from app.db.base import Base
from app.db.session import async_engine


class Tip(Base):
    __tablename__ = 'tips'

    tip_id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer)
    order_id = Column(Integer)
    advisor_id = Column(Integer)
    amount = Column(Float,nullable = False)
    create_at = Column(DateTime, default=func.now())
