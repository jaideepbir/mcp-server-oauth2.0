# syntax=docker/dockerfile:1
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt
# Default to Docker network service URL; can be overridden by compose env
ENV MCP_SERVER_URL=http://mcp-server:9000
COPY app /app/app
EXPOSE 8501
CMD ["streamlit", "run", "app/pages/1_Tools.py", "--server.port=8501", "--server.address=0.0.0.0"]
