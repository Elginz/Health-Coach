# ============================
# Stage 1: Build React frontend
# ============================
FROM node:20-alpine AS build-frontend
WORKDIR /app/frontend

# Copy and install dependencies
COPY frontend/package*.json ./
RUN npm ci --silent

# Copy source and build
COPY frontend/ ./
RUN npm run build


# ============================
# Stage 2: Build Python backend
# ============================
FROM python:3.10-slim AS final
WORKDIR /app

# Copy backend requirements
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy backend, agent logic, data, and static frontend files
COPY backend/ ./backend
COPY agent/ ./agent
COPY data/ ./data
COPY --from=build-frontend /app/frontend/dist ./backend/static

# Expose FastAPI port
EXPOSE 8000

# Start FastAPI app with Uvicorn
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
