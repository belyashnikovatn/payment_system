FROM python:3.9

WORKDIR /app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Install netcat for DB wait check
RUN apt-get update && apt-get install -y netcat-traditional

# Copy app code and startup script
COPY . .

ENV PYTHONPATH=/app

# Make script executable
RUN chmod +x start.sh

CMD ["./start.sh"]
