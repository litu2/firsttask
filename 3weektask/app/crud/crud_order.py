#app/crud/crud_order.py
'''
对订单进行的crud操作
'''

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.order import Order
from app.models.user import User
from app.models.advisor import Advisor
from app.models.coinflow_user import Coinflow_user
from app.schemas.order import OrderCreate,OrderDisplay,OrderDetail,OrderInfo,ResponseContent,OrderStatus
from sqlalchemy.future import select
from fastapi import HTTPException
from datetime import datetime

async def create_coinflow_user(db: AsyncSession,Order_id:int,Is_income:bool,Notes:str,created_at=None):
    order = await db.get(Order,Order_id)
    #order = order.scalars().all()
    
    Amount=0.0
    if order.is_urgent:
        Amount+=order.amount
        Amount+=order.ext_amount
    else:
        Amount+=order.amount

    # 创建金币流记录对象
    coinflow = Coinflow_user(
                user_id=order.user_id,
                order_id=Order_id,
                amount=Amount,
                is_income=Is_income,  # 支出金币
                notes=Notes,  # 添加备注信息，可根据实际情况修改
                create_at=created_at if created_at else order.created_at
            )

    # 在数据库会话中添加金币流记录对象
    db.add(coinflow)

    #await db.commit()

    return {"msg":"下单成功！！"}



async def create_order(db: AsyncSession, user_id: int, advisor_id: int, order_in: OrderCreate):
    try:
        async with db.begin():
            user = await db.get(User,user_id)

            if user.coin < order_in.amount:
                raise ValueError("Insufficient balance !")
            if order_in.is_urgent and user.coin < (order_in.amount+order_in.ext_Amount):
                raise ValueError("Insufficient balance for urgent !")
            

            # 创建订单对象
            order = Order(
                user_id=user_id,
                advisor_id=advisor_id,
                basic_info=order_in.basic_Info,
                general_situ = order_in.general_Situ,
                specific_ques = order_in.specific_Ques,
                order_type=order_in.order_type,
                amount=order_in.amount,
                ext_amount = order_in.ext_Amount,
                status=order_in.status,
                is_urgent=order_in.is_urgent
            )

            db.add(order)
            # 金币变化
            if order_in.is_urgent:
                user.coin -= order_in.amount
                user.coin -= order_in.ext_Amount
            else:
                user.coin -= order_in.amount


            # 更新advisor表中的readings字段
            advisor = await db.get(Advisor, advisor_id)
            advisor.readings += 1
        # 提交会话以保存订单和更新用户金币余额
        await db.commit()

        # 刷新对象以确保数据已更新
        await db.refresh(order)
        
        # 返回创建的订单对象
        
        return order.order_id

    except Exception as e:
        await db.rollback()
        raise e
'''
async def get_user_order(db: AsyncSession, user_id:int):
    try:
        async with db.begin():
            order = await db.get(Order,user_id)
        return order
    except Exception as e:
        await db.rollback()
        raise e

'''
'''
async def get_user_order(db: AsyncSession, user_id: int):
    try:
        results = await db.execute(select(Order, Advisor).join(Advisor).where(Order.user_id == user_id))
        orders = results.scalars().all()
    return [
        OrderDisplay(
            order_id=order.order_id,
            advisor_name=order.advisor.name,  # 假设Advisor模型中有name字段
            basic_info=order.basic_info,
            order_type=order.order_type,
            status=order.status,
            created_at=order.created_at
               )
        for order in orders
    ]
    except Exception as e:
        await db.rollback()
        raise e
'''

async def get_user_orders(db: AsyncSession, user_id: int):
    try:
        # 第一步，获取所有订单信息
        result_orders = await db.execute(
            select(Order).where(Order.user_id == user_id)
        )
        orders = result_orders.scalars().all()

        # 收集所有相关的顾问ID
        advisor_ids = {order.advisor_id for order in orders}

        # 第二步，根据顾问ID获取顾问信息
        result_advisors = await db.execute(
            select(Advisor).where(Advisor.id.in_(advisor_ids))
        )
        advisors = result_advisors.scalars().all()

        # 将顾问信息以ID为键存储在字典中便于查找
        advisor_dict = {advisor.id: advisor for advisor in advisors}

        # 创建返回对象列表
        order_list = [
            OrderDisplay(
                order_id=order.order_id,
                advisor_name=advisor_dict[order.advisor_id].name if order.advisor_id in advisor_dict else None,
                basic_info=order.basic_info,
                order_type=order.order_type,
                status=order.status,
                created_at=order.created_at
            )
            for order in orders
        ]
        return order_list
    except Exception as e:
        # 数据库操作出现错误，回滚事务
        await db.rollback()
        # 重新抛出异常以便调用者可以处理
        raise e

async def get_order_detail(db: AsyncSession,user_id:int , order_id:int)-> OrderDetail:
    # 查询订单
    order_result = await db.execute(
        select(Order).where((Order.user_id == user_id) & (Order.order_id == order_id))
    )
    order = order_result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found.")

    # 查询顾问
    advisor_result = await db.execute(
        select(Advisor).where(Advisor.id == order.advisor_id)
    )
    advisor = advisor_result.scalars().first()

    advisor_name = advisor.name if advisor else None

    # 构建并返回OrderDetail对象
    return OrderDetail(
        order_Id=order.order_id,  # 注意属性名大小写需与OrderDetail模型一致
        advisor_Name=advisor_name,
        basic_Info=order.basic_info,
        general_Situ=order.general_situ,
        specific_Ques=order.specific_ques,
        order_Type=order.order_type,
        status=order.status,
        amount=order.amount,
        ext_Amount=order.ext_amount,
        response=order.response,
        created_At=order.created_at,
        updated_At=order.updated_at
    )


async def ad_get_order_detail(db: AsyncSession,advisor_id:int , order_id:int)->OrderInfo:
    # 检查订单是否存在，是否属于当前顾问
    order_result = await db.execute(
        select(Order).where((Order.order_id == order_id) & (Order.advisor_id == advisor_id))
    )
    order = order_result.scalars().first()

    if not order:
        raise HTTPException(status_code=404, detail="Order not found or does not belong to advisor.")

    # 返回订单详情数据
    return OrderInfo(
        order_Id=order.order_id,
        basic_Info=order.basic_info,
        general_Situ=order.general_situ,
        specific_Ques=order.specific_ques,
        order_Type=order.order_type,
        amount=order.amount,
        ext_Amount=order.ext_amount,
        status=order.status,
        is_Urgent=order.is_urgent,
        is_Expired=order.is_expired,
        created_At=order.created_at,
        response = order.response
    )

async def make_order_response(db: AsyncSession, advisor_id:int , order_id:int,new_response:str):
    # 在数据库中查找指定的订单
    order_select = select(Order).where(Order.order_id == order_id)

    # 执行 select 语句
    result = await db.execute(order_select)
    order =  result.scalars().first()
    
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")
    
    # 验证当前顾问是否与订单的顾问匹配
    #import pdb;pdb.set_trace()
    if order.advisor_id != int(advisor_id):
        raise HTTPException(status_code=403, detail="You don't have permission to update this order")
    # 验证当前订单是否过期
    if order.is_expired:
        raise HTTPException(status_code=400, detail="Order has expired and cannot be updated")
    
    # 判断订单类型是否为"completed"或"expired"
    if order.status.value  == OrderStatus.completed.value or order.status.value == OrderStatus.expired.value:

        raise HTTPException(status_code=400, detail="Order is already completed or expired")

    #import pdb;pdb.set_trace()

    # 更新订单的响应字段
    order.response = new_response
    # 更新订单的状态为completed
    order.status = "completed"



    # 获取对应的顾问对象
    advisor = await db.get(Advisor, advisor_id)
    # 使顾问的amount值增加，并根据订单是否紧急增加ext_amount
    if order.is_urgent  and order.is_urgent_ex==0:
        advisor.coin += order.ext_amount
    advisor.coin += order.amount
    # 使顾问的complete值加1
    advisor.complete += 1


    # 进行保存操作
    await db.commit()
    # 返回包含更新后的响应的实例
    return ResponseContent(response=new_response)
   



    
