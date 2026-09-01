FROM python:3.11-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the entire project
COPY . .

# Make the startup script executable
RUN chmod +x start.sh

# Hugging Face Spaces uses port 7860 by default
EXPOSE 7860

# Run the startup script
CMD ["./start.sh"]
