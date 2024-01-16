#app/api/api_v1/endpoints/advisor.py
'''
和顾问有关的API
'''
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi.responses import Response
from datetime import timedelta
from app.crud.crud_advisor import get_advisor_by_mobile, create_advisor,update_advisor,update_advisor_workstatus,update_advisor_servicesetting,get_advisor
from app.crud.crud_order import ad_get_order_detail,make_order_response
from app.crud.crud_coinflow_advisor import get_ad_coinflow
from app.schemas.advisor import AdvisorCreate,AdvisorUpdate,AdvisorUpdateWorkstatus,AdvisorServiceSetting
from app.schemas.order import OrderInfo,AdvisorResponse,ResponseContent
from app.api.deps import get_async_db
from app.core.security import verify_password, create_access_token,get_current_advisor

router = APIRouter()


@router.post("/register",description="顾问注册")
async def advisor_register(advisor_in: AdvisorCreate, db: AsyncSession = Depends(get_async_db)):
    # 检查用户是否已经存在
    advisor = await get_advisor_by_mobile(db, mobile=advisor_in.mobile)  # 调用异步函数查询用户是否已存在
    if advisor:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Mobile already registered."
        )
    advisor_out = await create_advisor(db=db, advisor=advisor_in)  # 调用异步函数创建用户
    if not advisor_out:
        return {"msg":"注册失败！"}

    return {"msg":"注册成功！"}



@router.post("/login",description="顾问登录")
async def advisor_login(advisor_in: AdvisorCreate, db: AsyncSession = Depends(get_async_db)):
    # 根据用户提供的信息查询用户
    advisor = await get_advisor_by_mobile(db, mobile=advisor_in.mobile)

    # 检查用户是否存在，并验证密码
    if not advisor or not verify_password(advisor_in.password, advisor.hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid mobile or password"
        )

    # 创建访问令牌
    access_token = create_access_token(subject=advisor.id, expires_delta=timedelta(minutes=60*24*7))

    # 创建响应对象，设置响应头
    response = Response()
    response.headers["Authorization"] = f"Bearer {access_token}"
    response.headers["token_type"] = "bearer"

    # 返回响应
    return response


@router.get("/advisor",description="顾问主页")
async def advisor_get(db: AsyncSession = Depends(get_async_db),current_advisor: dict = Depends(get_current_advisor)):
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID")

    advisor = await get_advisor(db=db,advisor_id=advisor_id)
    return advisor





@router.put("/update", response_model=AdvisorUpdate,description="顾问更新个人数据")
async def advisor_update(
    advisor_in: AdvisorUpdate,
    db: AsyncSession = Depends(get_async_db),
    current_advisor: dict = Depends(get_current_advisor)
):
    # 从current_user字典中获取用户ID
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID")

    # 调用数据库操作函数更新用户资料，要求传入用户ID和新的用户信息
    advisor = await update_advisor(db=db, advisor_id=advisor_id, advisor_in=advisor_in)
    return advisor




@router.put("/update_workstatus",response_model=AdvisorUpdateWorkstatus,description="顾问更新接单状态")
async def advisor_update_workstatus(
        advisor_in: AdvisorUpdateWorkstatus,
        db:AsyncSession = Depends(get_async_db),
        current_advisor:dict = Depends(get_current_advisor)
):
    # 从current_user字典中获取用户ID
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID")

    advisor = await update_advisor_workstatus(db=db, advisor_id=advisor_id, advisor_in=advisor_in)
    return advisor


@router.put("/update_servicesetting",description="顾问更新服务设置")
async def advisor_update_servicesetting(
        advisor_in: AdvisorServiceSetting,
        db:AsyncSession = Depends(get_async_db),
        current_advisor:dict = Depends(get_current_advisor)
):
    # 从current_user字典中获取用户ID
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID")


    advisor = await update_advisor_servicesetting(db=db, advisor_id=advisor_id, advisor_in=advisor_in)
    return advisor

#  顾问获取某个订单详细信息
@router.get("/orders/details/{order_id}", response_model=OrderInfo)
async def order_details_get(
        order_id: int,
        current_advisor: dict = Depends(get_current_advisor),
        db: AsyncSession = Depends(get_async_db)
):
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID.")
    detail = await ad_get_order_detail(db=db,advisor_id=advisor_id , order_id=order_id)

    return detail
# 顾问回复订单
@router.patch("/orders/respond/{order_id}", response_model=ResponseContent)
async def order_response_make(
        order_id: int,
        response_in: AdvisorResponse,  # 接收的请求体
        current_advisor: dict = Depends(get_current_advisor),
        db: AsyncSession = Depends(get_async_db)  # 数据库依赖
):
    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID.")
    response = await make_order_response(db=db, advisor_id = advisor_id,order_id=order_id,new_response = response_in.response)

    return response


# 顾问查看自己金币流
@router.get("/get_ad_coinflow")
async def coinflow_ad_get(
        current_advisor: dict = Depends(get_current_advisor),
        db: AsyncSession = Depends(get_async_db)
):

    advisor_id = current_advisor.get("advisor_id")
    if advisor_id is None:
        raise HTTPException(status_code=400, detail="Invalid advisor ID.")
    coinflow = await get_ad_coinflow(db=db,advisor_id=int(advisor_id))
    return coinflow






