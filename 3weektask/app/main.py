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
from app.crud.crud_order import create_coinflow_user
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from datetime import datetime , timedelta
import asyncio
from sqlalchemy import and_
from fastapi import Depends
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from app.db.session import async_session
scheduler = AsyncIOScheduler()

# 定义定时任务
@scheduler.scheduled_job("interval", minutes=1)  # 每分钟检查一次
async def check_orders():
    async with async_session() as session:
        async with session.begin():
            # 查询加急订单是否过期,在符合条件的情况下返还用户金币
            expired_urgent_orders = await session.execute(
                select(Order).where(and_(
                    Order.is_urgent == True,
                    Order.is_urgent_ex == False,
                    Order.status == OrderStatus.pending.value,
                    Order.created_at < datetime.now() - timedelta(hours=1)
                ))
            )

            for order in expired_urgent_orders.scalars():
                user = await session.get(User, order.user_id)
                # 返还加急部分金额
                
                order.is_urgent_ex = True
                user.coin += order.ext_amount
                
                # 创建金币流记录
                await create_coinflow_user(session, order.order_id, True, "返还加急部分金额",created_at=datetime.now())
            # 查询过期的正常订单
            expired_orders = await session.execute(
                select(Order).where(and_(
                    Order.is_expired == False,
                    Order.status  == OrderStatus.pending.value,
                    Order.expiredtime < datetime.now()
                ))
            )
            #import pdb;pdb.set_trace()
            for order in expired_orders.scalars():
                user = await session.get(User, order.user_id)
                advisor = await session.get(Advisor, order.advisor_id)
                # 返还正常部分金额
                advisor.uncomplete +=1
                user.coin += order.amount
                order.status = OrderStatus.completed
                order.is_expired = True

                # 创建金币流记录
                await create_coinflow_user(session, order.order_id, True, "返还正常部分金额",created_at=datetime.now())
    await session.commit()
''' 
    # 创建金币流记录 (在会话提交后调用)
    for order in expired_urgent_orders.scalars():
        await create_coinflow_user(session, order.order_id, True, "返还加急部分金额",created_at=datetime.now())

    for order in expired_orders.scalars():
        await create_coinflow_user(session, order.order_id, True, "返还正常部分金额",created_at=datetime.now())
'''
    


app = FastAPI()

app.middleware("http")(token_validator_middleware)

app.include_router(api_router)









# 启动事件
@app.on_event("startup")
async def on_startup():
    scheduler.add_job(check_orders, "interval", minutes=1)
    scheduler.start()

# 关闭事件
@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
 
