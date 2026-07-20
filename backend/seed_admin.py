"""创建管理员账号"""
import asyncio
from app.core.database import engine, AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import select


async def seed_admin():
    async with AsyncSessionLocal() as db:
        # 检查是否已存在
        result = await db.execute(
            select(User).where((User.username == "admin") | (User.email == "admin@rag.com"))
        )
        if result.scalar_one_or_none():
            print("管理员账号已存在，跳过创建")
            return

        admin = User(
            username="admin",
            email="admin@rag.com",
            hashed_password=hash_password("admin123"),
            display_name="系统管理员",
            role="admin",
            department="技术部",
            is_active=True,
        )
        db.add(admin)
        await db.commit()
        print("管理员账号创建成功！")
        print("  账号: admin")
        print("  密码: admin123")
        print("  角色: 超级管理员")


if __name__ == "__main__":
    asyncio.run(seed_admin())
