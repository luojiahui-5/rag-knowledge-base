"""创建管理员账号（独立脚本，使用 SQLite，无需 PostgreSQL）"""
import sqlite3
import os
from passlib.context import CryptContext

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

DB_PATH = os.path.join(os.path.dirname(__file__), "rag.db")


def seed():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    # 建表
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            email TEXT UNIQUE NOT NULL,
            hashed_password TEXT NOT NULL,
            display_name TEXT DEFAULT '',
            role TEXT DEFAULT 'viewer',
            department TEXT DEFAULT '',
            avatar_url TEXT DEFAULT '',
            is_active INTEGER DEFAULT 1,
            created_at TEXT DEFAULT (datetime('now')),
            updated_at TEXT DEFAULT (datetime('now'))
        )
    """)

    # 检查是否已存在
    cursor.execute("SELECT id FROM users WHERE username = ? OR email = ?", ("admin", "admin@rag.com"))
    if cursor.fetchone():
        print("管理员账号已存在，跳过创建")
        conn.close()
        return

    hashed = pwd_context.hash("admin123")
    cursor.execute(
        "INSERT INTO users (username, email, hashed_password, display_name, role, department, is_active) VALUES (?, ?, ?, ?, ?, ?, 1)",
        ("admin", "admin@rag.com", hashed, "系统管理员", "admin", "技术部"),
    )
    conn.commit()
    conn.close()

    print("=" * 40)
    print("  管理员账号创建成功！")
    print("  账号: admin")
    print("  密码: admin123")
    print("  角色: 超级管理员 (admin)")
    print("  数据库:", DB_PATH)
    print("=" * 40)


if __name__ == "__main__":
    seed()
