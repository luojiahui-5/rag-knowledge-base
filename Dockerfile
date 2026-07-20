FROM python:3.11-slim

WORKDIR /app

# 安装 Node.js + curl
RUN apt-get update && apt-get install -y curl && \
    curl -fsSL https://deb.nodesource.com/setup_20.x | bash - && \
    apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*

# 后端依赖
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 前端依赖 + 构建（Vite dist 输出到顶层 dist/）
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# Railway 通过 $PORT 环境变量传入端口
EXPOSE 8000
CMD cd /app/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
