#!/usr/bin/env bash
set -euo pipefail

PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SERVICE_DIR="${HOME}/.config/systemd/user"
SERVICE_FILE="${SERVICE_DIR}/pi-assistant.service"

mkdir -p "${SERVICE_DIR}"
sed "s#%h/rpisupercompress#${PROJECT_DIR}#g" \
  "${PROJECT_DIR}/systemd/pi-assistant.service" > "${SERVICE_FILE}"

systemctl --user daemon-reload
systemctl --user enable pi-assistant.service
systemctl --user restart pi-assistant.service

echo "Installed and started pi-assistant.service"
echo "Logs: journalctl --user -u pi-assistant.service -f"
