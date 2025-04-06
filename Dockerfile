FROM python:3.13.2-slim

# Set build arguments from .env file
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER="app"
ARG WORKDIR="/var/app"
ARG CRON_SCHEDULE
ARG ENV_PATH="../.env"
ARG CRON_LOG_PATH="/var/log/cron.log"


RUN apt-get update && apt-get install -y \
    build-essential \
    curl \
    python3-venv \
    cmake \
    cron \
    && rm -rf /var/lib/apt/lists/* \
    && apt autoremove -y

# Create the group and user
RUN groupadd -g ${GROUP_ID} ${USER} && \
useradd -u ${USER_ID} -g ${USER} -m -s /bin/bash ${USER}

# Set permissions
RUN if [ ! -z "$CRON_SCHEDULE" ]; then \
        echo "Running scheduler install"; \
        echo "${CRON_SCHEDULE} ${USER} ${WORKDIR}/run.sh ${WORKDIR}/run.py" > /etc/cron.d/${USER}-cron \
        && touch /var/log/cron.log \
        && chmod 666 /var/log/cron.log; \
    else \
        echo "Skipping scheduler setup"; \
    fi

WORKDIR ${WORKDIR}
COPY . .
COPY ./pyproject.toml .
COPY ./uv.lock .
COPY ${ENV_PATH} .env
COPY ${CRON_LOG_PATH} /var/log/cron.log

#Setup uv
RUN pip install uv \
    && uv sync \
    && uv tool install fastapi 

CMD service cron start && uv run --all-packages fastapi dev main.py