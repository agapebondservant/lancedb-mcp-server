FROM python:3.11-slim

RUN useradd -m -u 1001 appuser

USER root
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /app/ \
    && chown -R appuser:appuser /app

USER 1001
WORKDIR /app
COPY lancedb_mcp.py .
COPY lancedb_mcp_utils.py .
RUN chmod -R a+rX /app

EXPOSE 8080

CMD ["python", "lancedb_mcp.py"]