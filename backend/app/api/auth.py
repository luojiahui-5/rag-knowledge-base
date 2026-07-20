from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from ..core.database import get_db
from ..core.security import hash_password, verify_password, create_access_token, get_current_user
from ..models.user import User
from ..schemas.auth import LoginRequest, RegisterRequest, TokenResponse, UserInfo

router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(req: LoginRequest, db: AsyncSession = Depends(get_db)):
    # 支持账号或邮箱登录
    result = await db.execute(
        select(User).where((User.username == req.username) | (User.email == req.username))
    )
    user = result.scalar_one_or_none()
    if not user or not verify_password(req.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="账号或密码错误")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="账号已被禁用")

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.post("/register", response_model=TokenResponse)
async def register(req: RegisterRequest, db: AsyncSession = Depends(get_db)):
    # 检查邮箱是否已存在
    result = await db.execute(select(User).where(User.email == req.email))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该邮箱已被注册")

    # 检查用户名
    result = await db.execute(select(User).where(User.username == req.username))
    if result.scalar_one_or_none():
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="该用户名已被使用")

    user = User(
        username=req.username,
        email=req.email,
        hashed_password=hash_password(req.password),
        display_name=req.display_name or req.username,
        department=req.department,
        role="viewer",
    )
    db.add(user)
    await db.flush()
    await db.refresh(user)

    token = create_access_token({"sub": str(user.id), "role": user.role})
    return TokenResponse(
        access_token=token,
        user=UserInfo.model_validate(user),
    )


@router.get("/me", response_model=UserInfo)
async def get_me(current_user: User = Depends(get_current_user)):
    return UserInfo.model_validate(current_user)


@router.get("/users", response_model=list[UserInfo])
async def list_users(
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """获取所有用户（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可查看用户列表")
    result = await db.execute(select(User).order_by(User.created_at.desc()))
    return [UserInfo.model_validate(u) for u in result.scalars().all()]


@router.put("/users/{user_id}", response_model=UserInfo)
async def update_user(
    user_id: int,
    req: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """更新用户信息"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可修改用户")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")

    # 允许修改的字段
    for field in ["username", "email", "display_name", "role", "department", "is_active"]:
        if field in req:
            setattr(user, field, req[field])

    await db.flush()
    await db.refresh(user)
    return UserInfo.model_validate(user)


@router.delete("/users/{user_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """删除用户（仅管理员，不能删除自己）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    if user_id == current_user.id:
        raise HTTPException(status_code=400, detail="不能删除自己的账号")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    await db.delete(user)
    await db.flush()


@router.post("/users/{user_id}/reset-password")
async def reset_password(
    user_id: int,
    req: dict,
    db: AsyncSession = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """重置用户密码（仅管理员）"""
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="仅管理员可操作")
    result = await db.execute(select(User).where(User.id == user_id))
    user = result.scalar_one_or_none()
    if not user:
        raise HTTPException(status_code=404, detail="用户不存在")
    new_pwd = req.get("password", "")
    if len(new_pwd) < 6:
        raise HTTPException(status_code=400, detail="密码至少 6 位")
    user.hashed_password = hash_password(new_pwd)
    await db.flush()
    return {"message": "密码已重置"}
