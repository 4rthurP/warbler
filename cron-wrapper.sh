#!/bin/bash



LOG_FILE="/var/log/cron_monitor.log"
SCRIPT="$1"
PID=$$
USER=$(whoami)
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Log start
echo "$START_TIME - START - $SCRIPT - PID: $PID - User: $USER"

# Run script and capture output
OUTPUT=$($SCRIPT 2>&1)
EXIT_CODE=$?

# Get system stats
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
LOAD_AVG=$(awk '{print $1, $2, $3}' /proc/loadavg)
MEM_USAGE=$(free -m | awk '/Mem:/ {printf "%.2f%%", $3/$2 * 100}')

# Log output
echo "$OUTPUT"

# Log end
echo "$END_TIME - END - $SCRIPT - PID: $PID - Exit Code: $EXIT_CODE - Load Avg: $LOAD_AVG - Mem Usage: $MEM_USAGE"