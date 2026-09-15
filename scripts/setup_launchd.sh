#!/usr/bin/env bash
set -e

PLIST_NAME="com.tradingbot.portfolio-monitor.plist"
SOURCE_PLIST="/Users/carlos/Documents/Investment/Bot/scripts/${PLIST_NAME}"
TARGET_DIR="${HOME}/Library/LaunchAgents"
TARGET_PLIST="${TARGET_DIR}/${PLIST_NAME}"

echo "=== Installing Trading Bot Background Daemon for macOS ==="

mkdir -p "${TARGET_DIR}"

# Unload if already loaded
if launchctl list | grep -q "com.tradingbot.portfolio-monitor"; then
    echo "Unloading existing launchd agent..."
    launchctl unload "${TARGET_PLIST}" 2>/dev/null || true
fi

# Copy plist
cp "${SOURCE_PLIST}" "${TARGET_PLIST}"
echo "Installed plist to ${TARGET_PLIST}"

# Load service
launchctl load "${TARGET_PLIST}"
echo "Successfully loaded ${PLIST_NAME} into launchd!"
echo "Schedule: Mon-Fri at 21:15 UK time (16:15 EST, market close)."
echo "Log file: /Users/carlos/Documents/Investment/Bot/data/launchd_output.log"
