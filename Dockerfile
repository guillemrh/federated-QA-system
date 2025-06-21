FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy code (we'll mount volumes too)
COPY . .

ENV PYTHONPATH=/app

# Default command (will be overridden per service)
CMD ["uvicorn", "legal_node.main:app", "--host", "0.0.0.0", "--port", "8001"]
