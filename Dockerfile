FROM python:3.14-slim

# Set build arguments from .env file
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER="app"
ARG WORKDIR="/var/app"
ARG CRON_SCHEDULE='* * * * *'
ARG SCHEDULE_TOKEN
ARG ENV_PATH="../.env"


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
RUN if [ ! -z "$SCHEDULE_TOKEN" ]; then \
        echo "Running scheduler install"; \
        echo "${CRON_SCHEDULE} ${USER} CRON_TOKEN=${SCHEDULE_TOKEN} $(which php) ${WORKDIR}/schedule.php >> /var/log/cron.log 2>&1" > /etc/cron.d/pz-cron \
        && touch /var/log/cron.log \
        && chmod 666 /var/log/cron.log; \
    else \
        echo "Skipping scheduler setup"; \
    fi

WORKDIR ${WORKDIR}
COPY . .
COPY ${ENV_PATH} .env

#Setup uv
RUN pip install uv \
    && uv sync \
    && uv tool install fastapi 

CMD service cron start && uv run --all-packages fastapi dev main.py