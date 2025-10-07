# Use a multi-stage build: backend + frontend static build (simplified)
FROM python:3.11-slim AS backend
WORKDIR /app
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r backend/requirements.txt
COPY backend ./backend
COPY agent ./agent
COPY data ./data
WORKDIR /app
ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
