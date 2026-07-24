FROM ghcr.io/astral-sh/uv:python3.14-bookworm-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    UV_PROJECT_ENVIRONMENT=/opt/venv \
    AZURE_CONFIG_DIR=/tmp/azure

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        unixodbc \
        curl \
        ca-certificates \
        gnupg \
    && curl -fsSL https://packages.microsoft.com/keys/microsoft.asc \
        | gpg --dearmor -o /usr/share/keyrings/microsoft-prod.gpg \
    && echo "deb [arch=amd64,arm64 signed-by=/usr/share/keyrings/microsoft-prod.gpg] https://packages.microsoft.com/debian/12/prod bookworm main" \
        > /etc/apt/sources.list.d/microsoft-prod.list \
    && apt-get update \
    && ACCEPT_EULA=Y apt-get install --no-install-recommends -y msodbcsql18 azure-cli \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /rootless

RUN groupadd --gid 1000 rootless                                              \
    && useradd --uid 1000 --gid 1000 --create-home --shell /bin/bash rootless \
    && mkdir -p                   /tmp/azure /opt/venv                        \
    && chown -R rootless:rootless /tmp/azure /opt/venv

COPY . .

USER rootless

RUN uv sync --no-dev --frozen

CMD ["uv", "run", "--no-sync", "python", "-m", "src.main"]
