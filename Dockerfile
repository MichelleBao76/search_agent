FROM --platform=linux/amd64 python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy entire project so src/ stays in the path
COPY . .

ENV PORT=8080
EXPOSE 8080

# Start the FastAPI / Starlette app (adjust import path if you dropped src/)
CMD ["uvicorn", "src.rephraser_agent.rephraser_agent:app", "--host", "0.0.0.0", "--port", "8080"]


# FROM --platform=linux/amd64 python:3.11-slim

# WORKDIR /app

# COPY requirements.txt .
# RUN pip install --no-cache-dir -r requirements.txt

# COPY src/ .

# ENV PORT=8080

# EXPOSE 8080

# CMD ["sh", "-c", "uvicorn rephraser_agent.rephraser_agent:app --host 0.0.0.0 --port ${PORT}"]