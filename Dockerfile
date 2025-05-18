FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

# Install uv
RUN pip install uv

# Copy requirements first for better caching
COPY requirements.txt .

# Use uv to install dependencies with --system flag
RUN uv pip install --system -r requirements.txt

# Copy the rest of the code
COPY src/ src/

# Expose the port
EXPOSE 8000

# Run the server
CMD ["python", "src/main.py"]