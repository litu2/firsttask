#app/crud/crud_comment.py
'''
对订单评论和评分的crud操作
'''

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.models.order import Order
from app.schemas.comment import CommentCreate
from fastapi import HTTPException
from sqlalchemy.future import select
async def create_comment(db:AsyncSession,user_id:int,order_id:int,comment_in:CommentCreate):
    result = await db.execute(
                select(Comment)
                .filter(Comment.user_id == user_id)
                .filter(Comment.order_id == order_id)
                )
    existing_comment = result.scalar_one_or_none()
    if existing_comment is not None:
        raise HTTPException(status_code=400, detail="User has already commented on this order")
    #import pdb; pdb.set_trace()
    # 首先根据 order_id 查出 advisor_id   
    advisor_id = await db.execute(select(Order.advisor_id).filter(Order.order_id == order_id)) 
    advisor_id = advisor_id.scalars().first()
    if not advisor_id :
        raise HTTPException(status_code=400,detail="unable advisor_id!")
    try:

        comment = Comment(user_id = user_id,
                      order_id = order_id,
                      advisor_id = advisor_id,    
                      context = comment_in.context,
                      rating = comment_in.rating
        )

        db.add(comment)
        await db.commit()
        await db.refresh(comment)
        return comment
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))




