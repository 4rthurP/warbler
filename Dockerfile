FROM python:3.14-slim

RUN apt-get update && apt-get install -y \
    libpq-dev \
    gcc \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove -y

RUN curl -LsSf https://astral.sh/uv/install.sh | sh

