#!/bin/bash

set -e  # Exit on error

if [ -z "$1" ]; then
  echo "Usage: $0 /path/to/script.py"
  exit 1
fi

SCRIPT="$1"

# Optional: Add log file location
LOGFILE="${2:-cron.log}"  # default to cron.log if not given

# Optional: Set environment
# export PATH="/home/youruser/.local/bin:$PATH"
# export PYTHONPATH="/home/youruser/myproject"

# Optional: Activate venv
source /var/app/.venv/bin/activate

# Run the script
python3 "$SCRIPT" >> "$LOGFILE" 2>&1
