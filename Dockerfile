FROM python:3.11-slim

USER root
COPY requirements.txt .
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt \
    && mkdir -p /app/.cache \
    && useradd -m -u 1001 appuser \
    && chown -R appuser:appuser /app

WORKDIR /app
COPY lancedb_mcp.py .
COPY lancedb_mcp_utils.py .
COPY lancedb_query_utils.py .
RUN chmod -R a+rX /app

USER 1001
EXPOSE 8080

CMD ["python", "lancedb_mcp.py"]