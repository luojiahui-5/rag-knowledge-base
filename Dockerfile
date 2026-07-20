FROM node:20-slim AS frontend
WORKDIR /app
COPY package.json package-lock.json ./
RUN npm install
COPY index.html vite.config.js tailwind.config.js postcss.config.js ./
COPY src ./src
RUN npx vite build

FROM python:3.11-slim
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend/
COPY --from=frontend /app/dist ./dist
WORKDIR /app/backend
EXPOSE 8000
CMD python -m uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}
