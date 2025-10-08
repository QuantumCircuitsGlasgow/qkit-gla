#!/usr/bin/env bash
LOG_DIR=".precommit_logs"
mkdir -p "$LOG_DIR"
LOG_FILE="$LOG_DIR/black.log"

echo "Running black..." > "$LOG_FILE"

failed=0
for file in "$@"; do
    if ! black "$file" >/dev/null 2>>"$LOG_FILE"; then
        echo "❌ Failed: $file" >> "$LOG_FILE"
        failed=1
    else
        echo "✅ Passed: $file" >> "$LOG_FILE"
    fi
done

exit $failed