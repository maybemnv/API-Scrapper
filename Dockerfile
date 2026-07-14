FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends git && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN pip install --no-cache-dir uv

WORKDIR /app

COPY pyproject.toml uv.lock .python-version ./
ENV UV_PYTHON=3.11
RUN uv sync --locked


FROM python:3.11-slim AS runtime

RUN apt-get update && apt-get install -y --no-install-recommends git ca-certificates && \
    apt-get clean && rm -rf /var/lib/apt/lists/*

RUN groupadd -r sniffer && useradd -r -g sniffer -m -d /home/sniffer sniffer

WORKDIR /app

COPY --from=builder /app/.venv /opt/venv
COPY --chown=sniffer:sniffer . .

ENV PATH=/opt/venv/bin:$PATH
ENV PYTHONUNBUFFERED=1

USER sniffer

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8080/health')"

ENTRYPOINT ["python", "main.py"]
