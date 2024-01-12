#app/crud/crud_tip.py
'''
对订单打赏的crud操作
'''

from sqlalchemy.ext.asyncio import AsyncSession

from app.models.tip import Tip
from app.models.advisor import Advisor
from app.models.order import Order
from app.models.user import User

from app.schemas.tip import TipCreate
from fastapi import HTTPException
from sqlalchemy.future import select
async def create_tip(db:AsyncSession,user_id:int,order_id:int,tip_in:TipCreate):
    #import pdb; pdb.set_trace()     
    # 首先根据 order_id 查出 advisor_id
    advisor_id = await db.execute(select(Order.advisor_id).filter(Order.order_id == order_id))
    advisor_id = advisor_id.scalars().first()
    # 根据advisor_id 给advisor打赏
    advisor = await db.get(Advisor,advisor_id)
    user = await db.get(User,user_id) 

    if user.coin < tip_in.amount:
        raise ValueError("Insufficient balance !")
    # 金币变化
    try:
        user.coin -=tip_in.amount
        advisor.coin += tip_in.amount

        tip = Tip(user_id = user_id,order_id = order_id,advisor_id = advisor_id,amount = tip_in.amount)

        db.add(tip)
        await db.commit()
        await db.refresh(tip)
        return tip
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


