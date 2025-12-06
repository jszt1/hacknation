FROM python:3.10-slim
WORKDIR /app

COPY backend/requirements.txt requirements.txt

RUN pip install --no-cache-dir -r requirements.txt

COPY backend ./backend

RUN mkdir -p backend/uploads backend/csv
ENV APP_PORT=8000

CMD ["sh", "-c", "uvicorn backend.main:app --host 0.0.0.0 --port $APP_PORT"]