#!/usr/bin/env bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(dirname "$SCRIPT_DIR")"
PLIST_NAME="com.tradingbot.portfolio-monitor.plist"
SOURCE_PLIST="${SCRIPT_DIR}/${PLIST_NAME}"
TARGET_DIR="${HOME}/Library/LaunchAgents"
TARGET_PLIST="${TARGET_DIR}/${PLIST_NAME}"

echo "=== Installing Trading Bot Background Daemon for macOS ==="

mkdir -p "${TARGET_DIR}"

# Unload if already loaded
if launchctl list | grep -q "com.tradingbot.portfolio-monitor"; then
    echo "Unloading existing launchd agent..."
    launchctl unload "${TARGET_PLIST}" 2>/dev/null || true
fi

# Dynamically generate plist with current user's paths
cat <<EOF > "${TARGET_PLIST}"
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE plist PUBLIC "-//Apple//DTD PLIST 1.0//EN" "http://www.apple.com/DTDs/PropertyList-1.0.dtd">
<plist version="1.0">
<dict>
    <key>Label</key>
    <string>com.tradingbot.portfolio-monitor</string>
    
    <key>ProgramArguments</key>
    <array>
        <string>/bin/zsh</string>
        <string>${PROJECT_ROOT}/scripts/run_scheduled_cycle.sh</string>
    </array>
    
    <!-- Run at 21:15 UK time (16:15 EST, 15m after US market close) -->
    <key>StartCalendarInterval</key>
    <array>
        <dict><key>Weekday</key><integer>1</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
        <dict><key>Weekday</key><integer>2</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
        <dict><key>Weekday</key><integer>3</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
        <dict><key>Weekday</key><integer>4</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
        <dict><key>Weekday</key><integer>5</integer><key>Hour</key><integer>21</integer><key>Minute</key><integer>15</integer></dict>
    </array>

    <key>StandardOutPath</key>
    <string>${PROJECT_ROOT}/data/launchd_output.log</string>
    <key>StandardErrorPath</key>
    <string>${PROJECT_ROOT}/data/launchd_error.log</string>
</dict>
</plist>
EOF

echo "Installed plist to ${TARGET_PLIST}"

# Load service
launchctl load "${TARGET_PLIST}"
echo "Successfully loaded ${PLIST_NAME} into launchd!"
echo "Schedule: Mon-Fri at 21:15 UK time (16:15 EST, market close)."
echo "Log file: ${PROJECT_ROOT}/data/launchd_output.log"
