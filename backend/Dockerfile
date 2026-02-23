FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create upload directory
RUN mkdir -p /tmp/uploads

COPY . .

# Expose port
EXPOSE 5000

# Run with debug mode (vulnerable!)
CMD ["python", "app.py"]
