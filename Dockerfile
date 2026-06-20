# Multi-stage build for LOUS application

# Stage 1: Build frontend
FROM node:20-alpine AS frontend-builder

WORKDIR /app/frontend

# Copy frontend package files
COPY frontend/package*.json ./

# Install ALL dependencies (including devDependencies needed for build)
RUN npm ci

# Copy frontend source
COPY frontend/ ./

# Build frontend
RUN npm run build

# Verify build output
RUN ls -la dist/ && ls -la dist/assets/

# Stage 2: Backend with Python
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies (including curl for healthcheck)
RUN apt-get update && apt-get install -y \
    gcc \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy backend requirements
COPY backend/requirements.txt ./backend/

# Install Python dependencies
RUN pip install --no-cache-dir -r backend/requirements.txt

# Copy backend source
COPY backend/ ./backend/

# Copy test file for debugging
COPY test.html ./test.html

# Copy built frontend from previous stage
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

# Verify frontend files were copied
RUN ls -la ./frontend/dist/ && echo "Frontend files copied successfully"

# Create necessary directories
RUN mkdir -p backend/db backend/data/chroma

# Expose ports
EXPOSE 8000

# Set working directory to backend
WORKDIR /app/backend

# Run the application
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
