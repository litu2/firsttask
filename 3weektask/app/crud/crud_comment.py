#app/crud/crud_comment.py
'''
对订单评论和评分的crud操作
'''

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.comment import Comment
from app.models.order import Order
from app.models.user import User
from app.schemas.comment import CommentCreate,CommentList
from fastapi import HTTPException
from sqlalchemy.future import select
import redis
import json
from datetime import datetime
redis_conn = redis.Redis(host='localhost', port=6379, db=1)


class CommentListEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)


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


async def get_comment(db: AsyncSession,advisor_id:int):
    redis_key = f"comments:{advisor_id}"
    cached_data =  redis_conn.get(redis_key)
    
    if cached_data:
        comment_list = json.loads(cached_data.decode())

        return comment_list
    data = await db.execute(select(Comment).where(Comment.advisor_id==advisor_id))
    comment_data = data.scalars().all()

    if not comment_data:
        raise HTTPException(status_code=404,detail="comment not found!")
    
    comment_list = []

    for comment in comment_data:
        user  =  await db.get(User,comment.user_id)
        #user  = user.scalars().first()
        username = user.name if user.name else "Unknown User"
        '''
        comment_list.append(
            CommentList(
                username=username,
                context=comment.context,
                rating=comment.rating,
                create_at=comment.create_at,
            )
        )
        '''
        comment_entry = CommentList(
            username=username,
            context=comment.context,
            rating=comment.rating,
            create_at=comment.create_at,
        )
        comment_list.append(comment_entry.dict())
    comment_list_json = json.dumps(comment_list, cls=CommentListEncoder)
    redis_conn.set(redis_key,comment_list_json,ex=3600)

    return comment_list
         




