FROM python:3.12.7-slim AS builder
COPY --from=ghcr.io/astral-sh/uv:0.9.28 /uv /usr/local/bin/uv
WORKDIR /app
COPY pyproject.toml .python-version ./
RUN uv sync --no-dev --no-cache --no-install-project
COPY src/ ./src/
COPY kmcp.yaml ./

FROM python:3.12.7-slim
RUN groupadd -r mcpuser && useradd -r -g mcpuser mcpuser
WORKDIR /app
COPY --from=builder /app/.venv /app/.venv
COPY --from=builder /app/src /app/src
COPY --from=builder /app/kmcp.yaml /app/kmcp.yaml
ENV PATH="/app/.venv/bin:$PATH" PYTHONPATH=/app PYTHONUNBUFFERED=1 MCP_TRANSPORT_MODE=http HOST=0.0.0.0 PORT=3000
RUN chown -R mcpuser:mcpuser /app
USER mcpuser
EXPOSE 3000
CMD ["python", "src/main.py"]
