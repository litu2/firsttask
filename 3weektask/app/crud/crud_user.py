#app/crud/crud_user.py
'''
对用户进行的crud操作
'''
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.schemas.user import UserCreate,UserUpdate
from app.core.security import get_password_hash
from sqlalchemy.future import select


# 根据手机号查询用户
async def get_user_by_mobile(db: AsyncSession, mobile: str):
    
    stmt = select(User).filter(User.mobile == mobile)
    result = await db.execute(stmt)
    user =  result.scalars().first()
    
    return user


#  创建用户
async def create_user(db: AsyncSession, user: UserCreate):
    # 密码哈希
    hashed_password = get_password_hash(user.password)  
    # 创建User模型对象 
    db_user = User(mobile=user.mobile,hashed_password=hashed_password)

    db.add(db_user)  
    await db.commit()  
    await db.refresh(db_user)

    return {"msg":"create successful"}  



async def update_user(db: AsyncSession, user_id: int, user_in: UserUpdate):
    # 首先尝试找到用户
    result = await db.execute(select(User).filter(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="User not found"
        )

    # 取用户提交的数据更新用户对象
    user_data = user_in.dict(exclude_unset=True)
    for field, value in user_data.items():
        setattr(user, field, value)

    db.add(user)  
    await db.commit()  
    await db.refresh(user)  
    # return UserUpdate(**user_data)
    return {"msg":"修改成功"}
