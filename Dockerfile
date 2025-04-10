FROM python:3.13.2-slim

# Set build arguments from .env file
ARG USER_ID=1000
ARG GROUP_ID=1000
ARG USER="app"
ARG WORKDIR="/var"
ARG CRON_SCHEDULE="1 * * * *"
ARG ENV_PATH=".env"


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
        echo "${CRON_SCHEDULE} root ${WORKDIR}/run-script.sh run_watchers >> /home/app/cron.log" > /etc/crontab; \
    fi

# Copy the application files
WORKDIR ${WORKDIR}/app
COPY ./src .
COPY ./src/run-script.sh ../run-script.sh

#Setup uv
RUN pip install uv \
    && uv sync \
    && uv tool install fastapi 

RUN chown -R ${USER}:${USER} ${WORKDIR}/app

CMD service cron start && uv run --all-packages fastapi run main.py