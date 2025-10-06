# Stage 1: Build the React frontend
FROM node:18-alpine AS build
WORKDIR /app/frontend
COPY frontend/package*.json ./
RUN npm install
COPY frontend/ ./
RUN npm run build

# Stage 2: Build the Python backend
FROM python:3.10-slim AS final
WORKDIR /app
COPY --from=build /app/frontend/dist ./static
COPY backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY backend/ ./backend
COPY agent/ ./agent
COPY data/ ./data

# Expose the port the app runs on
EXPOSE 8000

# Run the application
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]