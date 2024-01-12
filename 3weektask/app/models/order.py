from sqlalchemy import Column,Integer, String,Boolean,Float,Enum,Text,DateTime,func
from app.db.base import Base
from app.db.session import async_engine
import enum
import datetime
from sqlalchemy import text
# 订单状态枚举类型定义
class OrderStatus(enum.Enum):
    pending = "pending"
    completed = "completed"
    expired = "expired"

# 订单类型枚举类型定义
class OrderType(enum.Enum):
    text  = "text"
    video  = "video"
    voice  = "voice"
    livechat = "livechat"

class Order(Base):
    __tablename__ = "orders"

    # 订单id
    order_id = Column(Integer, primary_key=True)
    # 用户id
    user_id = Column(Integer)
    # 顾问id
    advisor_id = Column(Integer)
    # 基础信息
    basic_info =Column(String(255))
    # 一般情况
    general_situ = Column(Text(), nullable=True)
    # 具体问题
    specific_ques = Column(String(200))
    # 问题类型字段，标识问题是文本、语音还是视频
    order_type = Column(Enum(OrderType), nullable=False)
    # 订单金额
    amount = Column(Float, nullable=False)
    # 额外金额
    ext_amount = Column(Float)
    # 订单状态
    status = Column(Enum(OrderStatus), default=OrderStatus.pending, nullable=False)
    # 是否加急
    is_urgent = Column(Boolean, default=False, nullable=False)
    # 是否加急过期
    is_urgent_ex =Column(Boolean, default=False, nullable=False)
    # 是否过期
    is_expired = Column(Boolean, default=False, nullable=False)
    # 订单内容
    response = Column(Text())
    # 订单创建时间
    created_at = Column(DateTime, default=func.now())
    # 订单过期时间
    expiredtime = Column(DateTime, server_default=text("(CURRENT_TIMESTAMP + INTERVAL 24 HOUR)"))
    #expiredtime = Column(DateTime, default=func.now() + datetime.timedelta(hours=24))
    # 订单更新时间
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())



