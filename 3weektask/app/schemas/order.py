#app/schemas/order.py
'''
order的Pydantic校验模型
各种校验数据模型
'''

from pydantic import BaseModel ,Field
from pydantic.types import constr
from typing import Optional
from datetime import datetime
import enum


# 订单状态枚举类型定义
class OrderStatus(str, enum.Enum):
    pending = "pending"
    completed = "completed"
    expired = "expired"


# 订单类型枚举类型定义
class OrderType(str, enum.Enum):
    text_consultation = "text"
    video_consultation = "video"
    voice_consultation = "voice"
    livetestchat_consultation = "livetestchat_consultation"


class OrderCreate(BaseModel):
    # 用户id
    #user_id: Optional[int] = Field(2)
    # 顾问id
    #advisor_id: Optional[int] = Field(1)
    # 基础信息
    basic_Info: Optional[str] = Field( None , example = "一些基础信息")
    # 一般情况
    general_Situ: Optional[str] = Field( None , example = "一些基础信息")
    # 具体问题
    specific_Ques : Optional[str] = Field( None , example="一些具体问题")
    # 问题类型字段，标识问题是文本、语音还是视频
    order_type: Optional[OrderType] = Field(None,example="text")
    # 订单金额
    amount: Optional[float] = Field(None,example="52")
    # 额外金额
    ext_Amount:Optional[float] = Field(None,example="0")
    # 订单类型
    status: Optional[OrderStatus] = Field("pending", example="pending")
    # 是否加急
    is_urgent: Optional[bool] = Field(False)

    class Config:
        use_enum_values = True  # 使枚举字段返回值


class OrderBase(BaseModel):
    pass
# 订单展示
class OrderDisplay(BaseModel):
    order_id: int
    advisor_name: Optional[str] = None
    basic_info: Optional[str] = None
    order_type: Optional[str] = None
    status: Optional[str] = None
    created_at: Optional[datetime] = None


class OrderDetail(BaseModel):
    order_Id: int
    advisor_Name: Optional[str] = None
    basic_Info: Optional[str] = None
    general_Situ: Optional[str] = None
    specific_Ques: Optional[str] = None
    order_Type: Optional[str] = None
    status: Optional[str] = None
    amount: Optional[float] = None
    ext_Amount: Optional[float] = None
    response: Optional[str] = None
    created_At: Optional[datetime] = None
    updated_At: Optional[datetime] = None


    
class OrderInfo(BaseModel):
    order_Id:int
    basic_Info: Optional[str]=None
    general_Situ: Optional[str]=None
    specific_Ques: Optional[str]=None
    order_Type: Optional[str] = None
    amount: Optional[float] = None
    ext_Amount: Optional[float] = None
    status: Optional[str] = None
    is_Urgent: Optional[bool] = None
    is_Expired: Optional[bool] = None
    created_At: Optional[datetime] = None
    reponse: Optional[str] = None
class Order(OrderBase):
    # 订单id
    order_id: int
    # 订单状态
    status: OrderStatus
    # 订单创建时间
    created_at: Optional[datetime]
    # 订单更新时间
    updated_at: Optional[datetime]

    class Config:
        from_attributes = True

# 定义顾问回复请求的模型
class AdvisorResponse(BaseModel):
    response: str  # 只包含需要更新的字段
class ResponseContent(BaseModel):
    response: str    

