#!/bin/bash
# ===== 企业级智能知识库 RAG 系统 - 阿里云部署脚本 =====
set -e
echo ">>> 更新系统..."
apt-get update -qq && apt-get install -y -qq git python3 python3-pip python3-venv nginx curl 2>/dev/null

# Node.js 20
if ! command -v node &>/dev/null; then
  echo ">>> 安装 Node.js..."
  curl -fsSL https://deb.nodesource.com/setup_20.x | bash -
  apt-get install -y -qq nodejs
fi

# 拉取代码
echo ">>> 拉取代码..."
cd /opt
if [ -d rag-knowledge-base ]; then
  cd rag-knowledge-base && git pull
else
  git clone https://github.com/luojiahui-5/rag-knowledge-base.git
  cd rag-knowledge-base
fi

# 后端依赖
echo ">>> 安装后端依赖..."
pip3 install -r backend/requirements.txt

# 前端构建
echo ">>> 构建前端..."
npm install && npm run build

# 初始化数据库 + 管理员
cd backend
python3 -c "
from app.core.database import engine, Base, AsyncSessionLocal
from app.core.security import hash_password
from app.models.user import User
from sqlalchemy import select
import asyncio

async def init():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    async with AsyncSessionLocal() as db:
        r = await db.execute(select(User).where(User.username == 'admin'))
        if not r.scalar_one_or_none():
            db.add(User(username='admin', email='admin@rag.com', hashed_password=hash_password('admin123'), display_name='管理员', role='admin', is_active=True))
            await db.commit()
            print('管理员账号已创建: admin / admin123')
        else:
            print('管理员已存在')

asyncio.run(init())
"

# Systemd 服务
echo ">>> 配置后台服务..."
cat > /etc/systemd/system/rag-api.service << 'EOF'
[Unit]
Description=RAG Knowledge Base API
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/rag-knowledge-base/backend
ExecStart=python3 -m uvicorn app.main:app --host 127.0.0.1 --port 8000
Restart=always

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable rag-api
systemctl restart rag-api

# Nginx 反代
echo ">>> 配置 Nginx..."
cat > /etc/nginx/sites-available/rag << 'EOF'
server {
    listen 80;
    server_name _;

    location /api {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location / {
        root /opt/rag-knowledge-base/dist;
        index index.html;
        try_files $uri $uri/ /index.html;
    }
}
EOF

ln -sf /etc/nginx/sites-available/rag /etc/nginx/sites-enabled/
rm -f /etc/nginx/sites-enabled/default
nginx -t && systemctl restart nginx

# 防火墙
ufw allow 80
ufw allow 443
ufw --force enable 2>/dev/null || true

echo ""
echo "=============================="
echo "  部署完成！"
echo "  外网地址: http://8.138.175.235"
echo "  账号: admin"
echo "  密码: admin123"
echo "=============================="
