FROM python:3.12-slim

ENV PYTHONUNBUFFERED=1
ENV PORT=8080

WORKDIR /app

# Install computational libraries
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source and web assets
COPY . .

# Expose web application port
EXPOSE 8080

# Start Locus native web server
CMD ["python", "server.py"]
