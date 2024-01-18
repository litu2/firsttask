# app/main.py (App entry point)
'''
from db.session import async_create_tables, async_session
# 一定要导入所有的模型，确保它们被注册到Base.metadata
import models.comment,models.user,models.advisor,models.order,models.coinflow_advisor,models.coinflow_user,models.tip

async def main():
    # 创建数据库表
    await async_create_tables()

    # 启动 web 服务代码，例如使用 uvicorn 或其他

if __name__ == '__main__':
    import asyncio
    asyncio.run(main())   
'''
import uvicorn

from middleware import token_validator_middleware
from fastapi import FastAPI
from api.api_v1.api import api_router


import nest_asyncio
nest_asyncio.apply()


app = FastAPI()

app.middleware("http")(token_validator_middleware)

app.include_router(api_router)
if __name__ == '__main__':
    uvicorn.run("main:app",host="127.0.0.1",port=8002)

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
