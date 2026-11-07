FROM python:3.12-slim

RUN apt-get update \
 && apt-get install -y --no-install-recommends ca-certificates \
 && rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY pyproject.toml ./
COPY ev_hunter ./ev_hunter
COPY main.py ./
RUN pip install --no-cache-dir ".[studio]" \
 && useradd --create-home --shell /usr/sbin/nologin agent \
 && chown -R agent:agent /app

USER agent

CMD ["agents", "run-worker"]
