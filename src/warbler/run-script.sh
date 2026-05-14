#!/bin/bash

set -e  # Exit on error

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/script.py [/path/to/log]"
  exit 1
fi

SCRIPT="$1"

APP_PATH="${APP_PATH:-/var/app}"
cd "$APP_PATH"

# Set up the virtual environment
export PATH="$APP_PATH/.venv/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin"
export PYTHONPATH="$APP_PATH/.venv/bin"
source "$APP_PATH/.venv/bin/activate"

# Load .env safely
if [ -f "$APP_PATH/.env" ]; then
  set -a  # automatically export all variables
  source "$APP_PATH/.env"
  set +a
fi

# Run the script
cd /var
LOG_LOCATION="${WARBLER_LOG_PATH:-/var}"
.venv/bin/python3 -u -m app.$SCRIPT >> "$LOG_LOCATION"/runner.log 2>&1