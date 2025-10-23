FROM python:3.11-slim

ENV MCP_TRANSPORT=http
ENV MCP_HOST=0.0.0.0
ENV MCP_PORT=8080

USER 1001

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

WORKDIR /app
COPY lancedb_mcp.py .
COPY lancedb_mcp_utils.py .

EXPOSE 8080

CMD ["python", "lancedb_mcp.py"]

RUN pip install --upgrade pip \
	&& pip install -r requirements.txt