#!/bin/bash

# Exit on error
set -e

export DEBIAN_FRONTEND=noninteractive

# --- Configuration ---
APP_DIR="/opt/browser-use-server"
GITHUB_REPO="https://github.com/derLars/Browser-use-LXC-deploy.git"
SERVICE_FILE="/etc/systemd/system/browser-use.service"
USER="root" # Running as root for simplicity in LXC, browser-use handles sandbox flags if configured

# --- Logging ---
log() {
    echo "[$(date +'%Y-%m-%d %H:%M:%S')] - $1"
}

log "=== Starting Browser-use Server Installation/Update ==="

# --- System Dependencies ---
log "[1/5] Installing system dependencies..."
apt-get update
apt-get install -y \
    python3 python3-pip python3-venv python3-dev \
    git curl wget \
    libasound2 libatk-bridge2.0-0 libcups2 libdrm2 libxkbcommon0 libxcomposite1 libxdamage1 libxfixes3 libxrandr2 libgbm1 libpango-1.0-0 libcairo2 # Common Playwright deps

# --- Application Setup ---
log "[2/5] Setting up application directory..."

if [ -d "$APP_DIR" ]; then
    log "Directory $APP_DIR exists. Updating..."
    cd "$APP_DIR"
    # Check if it's a git repo
    if [ -d ".git" ]; then
        git pull
    else
        log "Warning: $APP_DIR is not a git repository. Skipping git pull."
    fi
else
    log "Cloning repository..."
    git clone "$GITHUB_REPO" "$APP_DIR"
fi

cd "$APP_DIR"

# Ensure we are in the directory
if [ ! -f "requirements.txt" ]; then
    log "ERROR: requirements.txt not found in $APP_DIR. Did the clone succeed?"
    exit 1
fi

# --- Python Environment ---
log "[3/5] Setting up Python virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi

# Upgrade pip inside venv
./venv/bin/pip install --upgrade pip

log "Installing Python dependencies..."
./venv/bin/pip install -r requirements.txt

# --- Playwright Setup ---
log "[4/5] Installing Playwright browsers and dependencies..."
# Use the explicit path to the binary in the venv
./venv/bin/playwright install --with-deps chromium

# --- Service Setup ---
log "[5/5] Configuring systemd service..."

cat > "$SERVICE_FILE" <<EOF
[Unit]
Description=Browser-use Server
After=network.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$APP_DIR
ExecStart=$APP_DIR/venv/bin/uvicorn server:app --host 0.0.0.0 --port 8000 --timeout-keep-alive 1200
Restart=always
RestartSec=5
Environment=PYTHONUNBUFFERED=1
TimeoutStartSec=60
TimeoutStopSec=30

[Install]
WantedBy=multi-user.target
EOF

systemctl daemon-reload
systemctl enable browser-use.service
systemctl restart browser-use.service

log "=== Installation Complete ==="
log "Service is running on port 8000."
log "Check status with: systemctl status browser-use.service"
