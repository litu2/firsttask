#app/models/comment.py
'''

SQLAlchemy
定义ORM映射类comment

'''


from sqlalchemy import Column,  Integer,String,Date,Float,DateTime,func
from app.db.base import Base
from app.db.session import async_engine




class Comment(Base):
    __tablename__ = 'comments'

    comment_id = Column(Integer,primary_key=True,index=True)
    
    user_id = Column(Integer)

    order_id = Column(Integer)

    advisor_id = Column(Integer)

    context = Column(String(255),nullable=False)

    rating = Column(Float)

    create_at = Column(DateTime,default=func.now())












