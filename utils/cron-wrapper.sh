#!/bin/bash
exec 2>&1
SCRIPT="$1"
shift       # remaining args -> "$@"
PID=$$
USER=$(whoami)
START_TIME=$(date '+%Y-%m-%d %H:%M:%S')

# Log start
echo "$START_TIME - START - $SCRIPT - PID: $PID - User: $USER"

# Run script with output streaming live to stdout
"$SCRIPT" "$@"
EXIT_CODE=$?

# Get system stats
END_TIME=$(date '+%Y-%m-%d %H:%M:%S')
LOAD_AVG=$(awk '{print $1, $2, $3}' /proc/loadavg)
MEM_USAGE=$(free -m | awk '/Mem:/ {printf "%.2f%%", $3/$2 * 100}')

# Log end
echo "$END_TIME - END - $SCRIPT - PID: $PID - Exit Code: $EXIT_CODE - Load Avg: $LOAD_AVG - Mem Usage: $MEM_USAGE"