FROM python:3.12-slim

# Make sure Python prints directly to stdout/stderr for best logs mayyyn
ENV PYTHONUNBUFFERED=1

# Set the working directory for the application
WORKDIR /app

# Install minimal system dependencies
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements first to take advantage of Docker layer caching
COPY requirements.txt .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application source code
COPY src ./src

# Expose the port the application will run on
EXPOSE 8080

# Start the FastAPI app using Uvicorn
CMD ["uvicorn", "main:app", "--app-dir", "src", "--host", "0.0.0.0", "--port", "8080"]