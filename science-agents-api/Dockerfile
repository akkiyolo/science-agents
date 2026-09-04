FROM python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy project files
COPY pyproject.toml ./
COPY src/ ./src/
COPY scripts/ ./scripts/

# Install dependencies
RUN uv pip install --system -e .

# Expose port
EXPOSE 8000

# Run the API
CMD ["uvicorn", "science_agents.infrastructure.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
