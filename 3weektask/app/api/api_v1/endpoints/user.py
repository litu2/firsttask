#api/api_v1/endpoint/user.py
'''
和用户有关的API
'''
from fastapi import APIRouter, Depends, HTTPException,status,Query,Path
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response
from datetime import timedelta

from app.crud.crud_user import get_user_by_mobile, create_user,update_user
from app.crud.crud_advisor import get_advisors_after_cursor,get_paged_advisors,get_advisor_detail
from app.crud.crud_order import create_order, get_user_orders,get_order_detail,create_coinflow_user
from app.crud.crud_comment import create_comment
from app.crud.crud_tip import create_tip
from app.crud.crud_favorite import create_favorite, get_favorite
from app.crud.crud_coinflow_user import get_user_coinflow

from app.schemas.user import UserCreate,UserLogin,UserUpdate,UserCreateOut
from app.schemas.advisor import AdvisorList,AdvisorDetailed
from app.schemas.order import OrderCreate,OrderDisplay,OrderDetail
from app.schemas.comment import CommentCreate
from app.schemas.tip import TipCreate
from app.schemas.coinflow_user import UsercoinFlow

from app.api.deps import get_async_db
from app.core.security import verify_password,create_access_token,get_current_user
from typing import List


router = APIRouter()

# 用户注册接口
@router.post("/register",description="用户注册")
async def user_register(user_in: UserCreate, db: AsyncSession = Depends(get_async_db)):
    #import pdb; pdb.set_trace(); 
    # 检查用户是否已经存在
    user = await get_user_by_mobile(db, mobile=user_in.mobile)
    if user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile already registered."
        )
       
    user_out = await create_user(db=db, user=user_in)  
    return user_out


# 用户登录接口
@router.post("/login",description="用户登录")
async def user_login(user_in: UserLogin, db: AsyncSession = Depends(get_async_db)):
    # 查询用户
    user = await get_user_by_mobile(db, mobile=user_in.mobile)
    # 检查用户，验证密码
    if not user or not verify_password(user_in.hashed_password, user.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile or password"
        )

    # 创建访问令牌
    access_token = create_access_token(subject=user.id, expires_delta=timedelta(minutes=60*24*7))
    # 创建响应对象，设置响应头
    response = Response()
    response.headers["Authorization"] = f"Bearer {access_token}"
    response.headers["token_type"] = "bearer"

  
    return response


# 用户修改个人信息接口
#@router.put("/update",response_model=UserUpdate,description="用户修改个人信息")
@router.put("/update",description="用户修改个人信息")
async def user_update(user_in:UserUpdate,
                      db:AsyncSession = Depends(get_async_db),
                      current_user:dict =Depends(get_current_user)
                      ):
    # 从current_user字典中获取用户ID
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    # 调用数据库操作函数更新用户资料,要求传入用户ID和新的用户信息
    user = await update_user(db=db, user_id=user_id, user_in=user_in)
    return user


# 用户获取顾问列表接口
@router.get("/get_advisor",response_model=List[AdvisorList],description="获取顾问列表")
async def user_getadvisorlist(
    cursor_id: int = Query(None), # cursor_id参数：用作下一批数据开始点的标识
    limit: int = Query(4, ge=1,le=4), # limit参数：每次加载的顾问数量
    db: AsyncSession = Depends(get_async_db)
):
    if cursor_id is not None:
        advisors = await get_advisors_after_cursor(db=db, cursor_id=cursor_id, limit=limit)
    else:
        # 如果没有提供cursor_id，则从头开始
        advisors = await get_paged_advisors(db=db, page=1, page_size=limit)
    return [AdvisorList(id=advisor.id,name=advisor.name, bio=advisor.bio) for advisor in advisors]


# 用户查看顾问主页接口
@router.get("/advisor/{advisor_id}", response_model=AdvisorDetailed,description= "查看顾问主页")
async def advisor_detail(
    advisor_id: int = Path(..., title="The ID of the advisor to get details for"),
    db: AsyncSession = Depends(get_async_db)
):
    advisordetail = await get_advisor_detail(db=db,advisor_id=advisor_id)
    
    return advisordetail    


# 用户下单
@router.post("/place_order/{advisor_id}",description= "用户下单")
async def place_an_order(
        order_in : OrderCreate,
        advisor_id: int = Path(..., title="The ID of the advisor to get details for"),
        current_user:dict =Depends(get_current_user),
        db:AsyncSession =Depends(get_async_db)
):
    # 从current_user字典中获取用户ID
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    order_id  = await create_order(db=db,user_id=user_id,advisor_id=advisor_id,order_in=order_in)
    
    order = await create_coinflow_user(db=db,Order_id=order_id,Is_income=False,Notes="Order fees")
    
    await db.commit()

    return order


# 用户查看订单
@router.get("/get_orders",response_model=List[OrderDisplay],description= "用户查看订单")
async def orders_user_get(db:AsyncSession =Depends(get_async_db),current_user:dict =Depends(get_current_user)):
    # 从current_user字典中获取用户ID
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID")

    order = await get_user_orders(db=db,user_id=user_id)
    return order


# 用户查看订单详情
@router.get("/get_orders/{order_id}",response_model=OrderDetail,description= "用户查看订单详情")
async def order_detail_get(
        order_id: int,
        current_user: dict = Depends(get_current_user),
        db: AsyncSession = Depends(get_async_db)
):
    # 获取当前用户的ID
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")



    detail =  await get_order_detail(db=db,user_id=user_id,order_id=order_id)

    return detail


# 用户评分&评论接口
@router.post("/comment",description= "用户评分，评论")
async def comment_create(comment_in: CommentCreate,order_id: int,current_user: dict = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    # 从token中解析出当前用户id
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    comment = await create_comment(db=db,user_id=int(user_id),order_id=order_id,comment_in=comment_in)

    return comment


# 用户打赏接口
@router.post("/tip",description= "用户打赏")
async def tip_create(tip_in: TipCreate,order_id: int ,current_user: dict = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
    # 从token中解析出当前用户ID
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detal="Invalid user ID.")

    tip = await create_tip(db=db,user_id=int(user_id),order_id=order_id,tip_in=tip_in)


    if not tip:
        return{"msg":"打赏失败"}
    return {"msg":"打赏成功"}


# 用户收藏接口

@router.post("/favorite",description= "用户收藏")
async def favorite_create(advisor_id: int,current_user: dict = Depends(get_current_user),db: AsyncSession = Depends(get_async_db)):
     # 从token中解析出当前用户id
     user_id = current_user.get("user_id")
     if user_id is None:
         raise HTTPException(status_code=400, detail="Invalid user ID.")

     favorite = await create_favorite(db=db,user_id=int(user_id),advisor_id=advisor_id)
     
     return favorite

# 用户查看收藏列表
@router.get("/get_favorite",description= "查看收藏列表")
async def favorate_get(db: AsyncSession = Depends(get_async_db),current_user: dict = Depends(get_current_user)):
    # 从token中解析出当前用户id
    #import pdb; pdb.set_trace();
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    favorite = await get_favorite(db=db,user_id = int(user_id))

    return favorite

# 用户金币流接口
@router.get("/coinflow",description= "查看用户金币流")
async def conflow_get(db: AsyncSession = Depends(get_async_db),current_user: dict = Depends(get_current_user)):
    user_id = current_user.get("user_id")
    if user_id is None:
        raise HTTPException(status_code=400, detail="Invalid user ID.")

    coinflow = await get_user_coinflow(db=db,user_id=int(user_id))

    return coinflow

