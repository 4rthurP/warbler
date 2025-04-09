#!/bin/bash

set -e  # Exit on error

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/script.py [/path/to/log]"
  exit 1
fi

SCRIPT="$1"

# Set up the virtual environment
export PATH="/var/app/.venv/bin:/usr/local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin"
export PYTHONPATH="/var/app/.venv/bin"
source /var/app/.venv/bin/activate

# Load environment variables from a file
if [ -f "/var/app/.env" ]; then
  export $(grep -v '^#' /var/app/.env | xargs)
fi

# Run the script
cd /var
/var/app/.venv/bin/python3 -u -m app.$SCRIPT >> /var/runner.log 2>&1