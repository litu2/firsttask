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

from  app.schedulertask.check_orders  import check_orders,scheduler



app = FastAPI()

app.middleware("http")(token_validator_middleware)

app.include_router(api_router)

'''

# 启动事件
@app.on_event("startup")
async def on_startup():
    scheduler.add_job(check_orders,"interval",seconds=20)
    scheduler.start()

# 关闭事件
@app.on_event("shutdown")
async def on_shutdown():
    scheduler.shutdown()
'''
