# 第一阶段：构建前端
FROM node:20-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY . .
RUN npm run build

# 第二阶段：运行后端
FROM python:3.11-slim
WORKDIR /app

COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY backend/ ./backend/
COPY --from=frontend /app/dist ./dist

EXPOSE 8000
CMD cd /app/backend && python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
