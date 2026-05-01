FROM python:3.11-slim
 
WORKDIR /app
 
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*
 
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Place the backend package under /app/backend so imports like `backend.xxx` work
COPY . /app/backend

# Ensure Python can import the `backend` package from /app
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
 
EXPOSE 8000
 
# FIXED: was "backend.main:app" — but context is ./backend so main.py is at /app/main.py
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]