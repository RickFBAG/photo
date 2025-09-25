#!/usr/bin/env bash
set -euo pipefail

APP_DIR="$(cd "$(dirname "$0")/.." && pwd)"
SERVICE_NAME="inky-board.service"

cat >/tmp/$SERVICE_NAME <<EOF
[Unit]
Description=Inky Smart Display
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
WorkingDirectory=$APP_DIR
ExecStart=/usr/bin/python3 $APP_DIR/run.py
Restart=on-failure
User=pi

[Install]
WantedBy=multi-user.target
EOF

sudo mv /tmp/$SERVICE_NAME /etc/systemd/system/$SERVICE_NAME
sudo systemctl daemon-reload
sudo systemctl enable $SERVICE_NAME
echo "Service installed. Start with: sudo systemctl start $SERVICE_NAME"

