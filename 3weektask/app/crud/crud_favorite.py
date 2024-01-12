#app/crud/crud_favorite.py
'''
对收藏表的crud操作
'''

from sqlalchemy.ext.asyncio import AsyncSession
from app.models.favorite import Favorite
from app.models.advisor import Advisor
from fastapi import HTTPException
from sqlalchemy.future import select

async def create_favorite(db:AsyncSession,user_id:int,advisor_id:int):
    favorited = await db.execute(select(Favorite).filter(Favorite.user_id == user_id).filter(Favorite.advisor_id  == advisor_id))
    favorite = favorited.scalar_one_or_none()  # 获取查询结果

    if favorite:
        # 如果已经收藏，执行取消收藏的操作
        await db.delete(favorite)
        await db.commit()
        return {"msg": "取消收藏成功"}
    else:
        # 如果未收藏，执行添加收藏的操作
        favorite = Favorite(user_id=user_id, advisor_id=advisor_id)
        db.add(favorite)
        await db.commit()
        await db.refresh(favorite)
        return {"msg": "收藏成功"}
    
async def get_favorite(db:AsyncSession,user_id:int):
    #import pdb; pdb.set_trace();
    favorites = await db.execute(select(Favorite).filter(Favorite.user_id == user_id))
    if not favorites:
        raise {"msg":"暂无一人"} 
    
    favorites_result = []

    for favorite in favorites.scalars().all():
        advisor = await db.execute(select(Advisor).filter(Advisor.id == favorite.advisor_id))
        advisor_info = advisor.scalars().first()
        
        # 检查顾问信息是否存在
        if advisor_info:
            # 将顾问的姓名和个人简介添加到结果列表中
            favorites_result.append({
                "name": advisor_info.name,
                "bio": advisor_info.bio
            })

    return favorites_result
