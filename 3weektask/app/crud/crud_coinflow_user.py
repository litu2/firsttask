#app/crud/crud_coinflow_user.py
'''
用户coinflow的crud
'''
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.coinflow_user import Coinflow_user
from fastapi import HTTPException
from sqlalchemy.future import select



async def get_user_coinflow(db:AsyncSession,user_id:int):
    coinflow_result = await db.execute(select(Coinflow_user).filter(Coinflow_user.user_id==user_id))

    coinflow = coinflow_result.scalars().all()

    if not coinflow:
        raise {"msg":"暂无记录"}

    return coinflow






