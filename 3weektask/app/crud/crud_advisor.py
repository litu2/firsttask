#app/crud/crud_advisor.py
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.advisor import Advisor
from app.models.comment import Comment
from app.schemas.advisor import AdvisorCreate,AdvisorUpdate,AdvisorUpdateWorkstatus,AdvisorServiceSetting,AdvisorOut,AdvisorDetailed
from app.core.security import get_password_hash
from sqlalchemy import update
from fastapi import HTTPException
from sqlalchemy.future import select
from sqlalchemy.sql import func

#根据手机号查询顾问
async def get_advisor_by_mobile(db: AsyncSession,mobile: str):
    
    stmt = select(Advisor).filter(Advisor.mobile == mobile)
    result = await db.execute(stmt)
    advisor = result.scalars().first()
    
    return advisor

#创建顾问
async def create_advisor(db:AsyncSession,advisor:AdvisorCreate)->Advisor:
    hashed_password = get_password_hash(advisor.password)#对顾问的密码进行哈希处理
    db_advisor = Advisor(mobile=advisor.mobile,hashed_password=hashed_password)
    db.add(db_advisor)

    await db.commit()
    await db.refresh(db_advisor)
    return db_advisor

#更新顾问数据
async def update_advisor(db:AsyncSession, advisor_id :int,advisor_in :AdvisorUpdate):
    #根据id找到顾问
    result = await db.execute(select(Advisor).filter(Advisor.id == advisor_id))
    advisor = result.scalar_one_or_none()
    if not advisor:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,detail="Advisor not found"
                )

    
    advisor_data = advisor_in.dict(exclude_unset=True)
    for field, value in advisor_data.items():
        setattr(advisor, field, value)

    
    db.add(advisor)
    await db.commit()
    await db.refresh(advisor)
    return AdvisorUpdate(**advisor_data)

# 获取顾问主页数据
async def get_advisor(db:AsyncSession, advisor_id :int)->AdvisorOut:
    #根据id获取数据
    result = await db.execute(select(Advisor).filter(Advisor.id == advisor_id))
    advisor = result.scalar_one_or_none()
    if not advisor:
        raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,detail="Advisor not found"
                )
    advisor_data = AdvisorOut.from_orm(advisor)
    return advisor_data
   


#更新顾问接单状态
async def update_advisor_workstatus(db: AsyncSession, advisor_id: int, advisor_in: AdvisorUpdateWorkstatus):
    
    # 构建 SQL UPDATE 语句
    update_stmt = (
        update(Advisor)
        .where(Advisor.id == advisor_id)  # 定位到特定的顾问ID
        .values(workstatus=advisor_in.workstatus.value)  # 更新工作状态字段，使用枚举的值
        .execution_options(synchronize_session="fetch")  # 为了保持 ORM 会话的同步
    )
    
    # 执行更新操作
    await db.execute(update_stmt)
    
    # 提交事务以使更改生效
    await db.commit()
    
    # 获取更新后的顾问数据，返回这个顾问的实例
    updated_advisor_stmt = select(Advisor).where(Advisor.id == advisor_id)
    result = await db.execute(updated_advisor_stmt)
    updated_advisor = result.scalars().first()
    return updated_advisor



async def update_advisor_servicesetting(db: AsyncSession, advisor_id: int, advisor_in: AdvisorServiceSetting):
     # 构建一个字典来存储需更新的字段及其值
    update_values = advisor_in.dict(exclude_unset=True)

    # 如果没有提供任何更新，则不执行操作
    if not update_values:
        raise HTTPException(status_code=400, detail="No values provided for update")

    # 构建 SQL UPDATE 语句
    update_stmt = (
        update(Advisor).filter(Advisor.id == advisor_id).values(**update_values)
    )

    # 在数据库中执行更新操作
    await db.execute(update_stmt)

    # 提交事务使更新生效
    await db.commit()

    # 如果需要，可以在此处获取并返回更新后的资源
    # 注意：需要根据实际情况调整返回的数据结构
    return {"status": "success", "message": "Advisor service settings updated successfully"}




# 用户API调用 分页获取顾问列表
async def get_paged_advisors(db: AsyncSession, page: int, page_size: int = 4):
    # 计算要跳过的记录数
    skip = (page - 1) * page_size
    result = await db.execute(
        select(Advisor.id,Advisor.name,Advisor.bio).order_by(Advisor.id).offset(skip).limit(page_size)
    )
    advisors = result.all()
    return advisors


# 用户API调用 获取光标后的顾问列表
async def get_advisors_after_cursor(db: AsyncSession, cursor_id: int, limit: int = 4):
    result = await db.execute(
            select(Advisor.id,Advisor.name,Advisor.bio).filter(Advisor.id > cursor_id).order_by(Advisor.id).limit(limit)
    )
    advisors = result.all()
    return advisors


# 获取顾问主页信息
async def get_advisor_detail(db:AsyncSession,advisor_id :int):
    # 查询指定ID的顾问详细信息
    result = await db.execute(select(Advisor).filter(Advisor.id == advisor_id))
    advisor = result.scalar_one_or_none()
    
    if advisor is None:
        raise HTTPException(status_code=404, detail="Advisor not found")

    ontime = None
    if advisor.complete is not 0 and advisor.uncomplete is not 0:
        ontime = advisor.complete / (advisor.complete + advisor.uncomplete)
    # 查询顾问的评分记录并计算平均评分
    result = await db.execute(
        select(func.avg(Comment.rating))
        .where(Comment.advisor_id == advisor_id)
    )


    average_rating = result.scalar_one_or_none()
    #import pdb; pdb.set_trace();  
    advisor_detail = AdvisorDetailed(
        id=advisor.id,
        name=advisor.name,
        experience=advisor.experience,
        about= advisor.about,
        readings= advisor.readings,
        rating= average_rating,
        complete=advisor.complete,
        uncomplete=advisor.uncomplete,
        ontime=ontime,
        textReadingStatus=advisor.textReadingStatus,
        textReadingPrice=advisor.textReadingPrice,
        audioReadingStatus=advisor.audioReadingStatus,
        audioReadingPrice=advisor.audioReadingPrice,
        videoReadingStatus=advisor.videoReadingStatus,
        videoReadingPrice=advisor.videoReadingPrice,
        liveTextChatStatus=advisor.liveTextChatStatus,
        liveTextChatPrice=advisor.liveTextChatPrice
    )
   
    return advisor_detail



