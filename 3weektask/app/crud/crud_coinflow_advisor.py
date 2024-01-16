#app/crud/crud_coinflowadvisor.py
'''
对顾问金币的crud操作
'''
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.coinflow_advisor import Coinflow_advisor
from fastapi import HTTPException
from sqlalchemy.future import select


async def get_ad_coinflow(db: AsyncSession,advisor_id:int):
    coinflow_result = await db.execute(select(Coinflow_advisor).filter(Coinflow_advisor.advisor_id==advisor_id))

    coinflow = coinflow_result.scalars().all()

    if not coinflow:
        raise HTTPException(status_code=404, detail="Order not found or does not belong to advisor.")

    return coinflow

