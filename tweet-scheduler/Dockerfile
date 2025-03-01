FROM python:3.10-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the script
COPY tweet_scheduler.py .

# Create a directory for logs and history
RUN mkdir -p /app/data

# Set the working directory to the data directory
WORKDIR /app/data

# Run the script
CMD ["python", "/app/tweet_scheduler.py"]
