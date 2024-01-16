# app/main.py (App entry point)
'''
from db.session import async_create_tables, async_session
# 一定要导入所有的模型，确保它们被注册到Base.metadata
import models.comment 

async def main():
    # 创建数据库表
    await async_create_tables()

    # 启动 web 服务代码，例如使用 uvicorn 或其他

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())   

'''
from app.middleware import token_validator_middleware
from fastapi import FastAPI
from app.api.api_v1.api import api_router


import nest_asyncio
nest_asyncio.apply()

from app.api.deps import get_async_db
from app.models.user import User
from app.models.order import Order,OrderStatus
from app.models.advisor import Advisor
from app.models.coinflow_user import Coinflow_user
from app.models.coinflow_advisor import Coinflow_advisor

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime , timedelta
import asyncio
from sqlalchemy import and_
from fastapi import Depends
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
scheduler = AsyncIOScheduler()
'''
# 定义定时任务
@scheduler.scheduled_job("interval",seconds=20)  # 每分钟检查一次
async def check_orders():
    async with async_session() as session:
        # import pdb;pdb.set_trace();
        # 查询加急订单是否过期,在符合条件的情况下返还用户金币
        expired_urgent_orders = await session.execute(
        select(Order).filter(and_(Order.is_urgent == True,
                                 Order.is_urgent_ex == False,
                                 Order.status == OrderStatus.pending.value,
                                 Order.created_at < datetime.now() - timedelta(hours=1)
                ))
            )
        if expired_urgent_orders.scalars().all():
            for order1 in expired_urgent_orders.scalars().all():
                user = await session.get(User, order1.user_id)
                # 返还加急部分金额
                
                order1.is_urgent_ex = True
                user.coin += order1.ext_amount
                
                # 创建金币流记录
                usercoinflow = Coinflow_user(user_id=order1.user_id,order_id=order1.order_id,amount=order1.ext_amount,is_income=True,notes="返还订单加急部分金额",create_at=datetime.now()) 
                session.add(usercoinflow)
                await session.commit()  # 提交事务
        else:
            print("加急：此次无数据需处理")
            pass


        # 查询过期的正常订单
        expired_orders = await session.execute(
                select(Order).filter(and_(
                    Order.is_expired == False,
                    Order.status  == OrderStatus.pending.value,
                    Order.expiredtime < datetime.now()
                ))
            )
        if expired_orders.scalars().all():
            #import pdb;pdb.set_trace()
            for order2 in expired_orders.scalars().all():
                user = await session.get(User, order2.user_id)
                advisor = await session.get(Advisor, order2.advisor_id)
                # 返还正常部分金额
                advisor.uncomplete +=1
                user.coin += order2.amount
                order2.status = OrderStatus.completed
                order2.is_expired = True

                # 创建金币流记录
                advisorcoinflow = Coinflow_advisor(advisor_id=order2.advisor_id,order_id=order2.order_id,amount=order2.amount,is_income=True,notes="返回订单基础部分金额",create_at=datetime.now())
                session.add(advisorcoinflow)
                #await create_coinflow_user(session, order.order_id, True, "返还正常部分金额",created_at=datetime.now())
                await session.commit()
        else:
            print("基础：此次无数据需处理")
            pass

        await session.commit()
    
'''



import logging

# 导入包和模块

logger = logging.getLogger(__name__)

# 定义定时任务
@scheduler.scheduled_job("interval", seconds=20)
async def check_orders():
    async with async_session() as session:
        try:
            # import pdb;pdb.set_trace();
            # 查询加急订单是否过期，在符合条件的情况下返还用户金币
            expired_urgent_orders = await session.execute(
                select(Order).filter(and_(
                    Order.is_urgent == True,
                    Order.is_urgent_ex == False,
                    Order.status == OrderStatus.pending.value,
                    Order.created_at < datetime.now() - timedelta(hours=1)
                ))
            )
            expired_urgent_orders_list = None
            expired_urgent_orders_list = expired_urgent_orders.scalars().all()
            if expired_urgent_orders_list:
                urgentcoinflows = [] # 创建空列表用于存储 Coinflow_user 对象
                for order1 in expired_urgent_orders_list:
                    user = await session.get(User, order1.user_id)
                    # 返还加急部分金额

                    order1.is_urgent_ex = True
                    user.coin += order1.ext_amount

                    # 创建金币流记录
                    usercoinflow = Coinflow_user(user_id=order1.user_id, order_id=order1.order_id,
                                                amount=order1.ext_amount, is_income=True,
                                                notes="返还订单加急部分金额", create_at=datetime.now())
                    urgentcoinflows.append(usercoinflow) # 将对象添加到列表中
                session.add_all(urgentcoinflows)
            else:
                logger.info("加急：此次无数据需处理")

            # 查询过期的正常订单
            expired_orders = await session.execute(
                select(Order).filter(and_(
                    Order.is_expired == False,
                    Order.status == OrderStatus.pending.value,
                    Order.expiredtime < datetime.now()
                ))
            )
            expired_orders_list = None
            expired_orders_list = expired_orders.scalars().all()
            if expired_orders_list:
                advisorcoinflows = []
                for order2 in expired_orders_list:
                    user = await session.get(User, order2.user_id)
                    advisor = await session.get(Advisor, order2.advisor_id)
                    # 返还正常部分金额
                    advisor.uncomplete += 1
                    user.coin += order2.amount
                    order2.status = OrderStatus.completed
                    order2.is_expired = True

                    # 创建金币流记录
                    advisorcoinflow = Coinflow_advisor(advisor_id=order2.advisor_id, order_id=order2.order_id,
                                                       amount=order2.amount, is_income=True,
                                                       notes="返回订单基础部分金额", create_at=datetime.now())
                    advisorcoinflows.append(advisorcoinflow)
                session.add_all(advisorcoinflows)
            
            if expired_urgent_orders_list or expired_orders_list:
                await session.commit()    
            else:
                logger.info("基础：此次无数据需处理")

            await session.commit()
        except Exception as e:
            logger.error(f"定时任务发生错误：{str(e)}")

1



















app = FastAPI()

app.middleware("http")(token_validator_middleware)

app.include_router(api_router)









# 启动事件
@app.on_event("startup")
async def on_startup():
    scheduler.add_job(check_orders, "interval",seconds= 20)
    scheduler.start()

# 关闭事件
@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()

