# Stage 1: Build the React frontend
FROM node:18-alpine AS frontend
WORKDIR /app

# Copy package.json and lock file first to leverage Docker cache
COPY frontend/package.json ./
# Use wildcard (*) to make the lock file optional, preventing errors if it doesn't exist yet
COPY frontend/package-lock.json* ./
RUN npm install

# Copy the rest of the frontend source code
COPY frontend/ ./

# Build the application
RUN npm run build

# Stage 2: Create the final Python image
FROM python:3.11-slim
WORKDIR /app

# Copy Python dependencies and install
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code from the host
COPY backend ./backend
COPY agent ./agent
COPY data ./data

# Copy the built frontend static files from the 'frontend' stage
COPY --from=frontend /app/dist ./static

ENV PYTHONPATH=/app
EXPOSE 8000
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]