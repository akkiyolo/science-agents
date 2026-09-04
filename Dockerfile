# Stage 1: Build the frontend (Phaser/Webpack)
FROM node:20-alpine AS frontend-builder
WORKDIR /app/ui

# Copy package files and install dependencies
COPY science-agents-ui/package*.json ./
RUN npm install

# Copy source and build
COPY science-agents-ui/ ./
RUN npm run build

# Stage 2: Build the backend and serve the final application
FROM python:3.11-slim
WORKDIR /app

# Install system dependencies (needed for compiling some python packages if necessary)
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Install uv for fast dependency resolution
RUN pip install uv

# Copy python dependencies and install them
COPY science-agents-api/pyproject.toml ./
# Using uv to resolve and install the pyproject.toml dependencies globally in the container
RUN uv pip install --system -r pyproject.toml

# Copy backend source code
COPY science-agents-api/src ./src/
# Note: In production, environment variables should be injected by Render, 
# but we can copy .env if it exists for local fallback.
COPY .env* ./

# Copy built frontend from Stage 1 into the expected location
# main.py dynamically looks for a "ui_build" directory at the root level relative to src.
COPY --from=frontend-builder /app/ui/dist ./ui_build

# Set environment variables
ENV PYTHONPATH=/app/src
ENV PYTHONUNBUFFERED=1

# Expose port 8000
EXPOSE 8000

# Command to run the application using Uvicorn
CMD ["uvicorn", "science_agents.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
