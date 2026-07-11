#!/bin/bash
# StumbleFeed API setup — Ubuntu (run as root)
# Usage: bash setup.sh
set -e

APP_DIR=/opt/stumblefeed

echo "=== StumbleFeed Setup ==="

# ── App directory ─────────────────────────────────────────────────────────────
echo "[1/4] Copying application..."
mkdir -p $APP_DIR
rsync -a --exclude='.git' --exclude='__pycache__' --exclude='*.pyc' \
  "$(cd "$(dirname "$0")/.." && pwd)"/ $APP_DIR/

cd $APP_DIR
mkdir -p data

# ── Python venv ───────────────────────────────────────────────────────────────
echo "[2/4] Installing Python dependencies..."
python3 -m venv venv
source venv/bin/activate
pip install --quiet -r requirements.txt

# ── .env ──────────────────────────────────────────────────────────────────────
if [ ! -f $APP_DIR/.env ]; then
  cat > $APP_DIR/.env <<'EOF'
YOUTUBE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
VK_ACCESS_TOKEN=
EOF
  echo ">>> Edit $APP_DIR/.env before starting the service <<<"
fi

chown -R www-data:www-data $APP_DIR

# ── Systemd ───────────────────────────────────────────────────────────────────
echo "[3/4] Configuring systemd service..."
cp $APP_DIR/deploy/stumblefeed.service /etc/systemd/system/stumblefeed.service
systemctl daemon-reload
systemctl enable stumblefeed

# ── Caddy ─────────────────────────────────────────────────────────────────────
echo "[4/4] Configuring Caddy..."
cat $APP_DIR/deploy/Caddyfile >> /etc/caddy/Caddyfile
mkdir -p /var/log/caddy
systemctl reload caddy

echo ""
echo "=== Done ==="
echo ""
echo "Next steps:"
echo "  1. nano $APP_DIR/.env  — fill in API keys"
echo "  2. systemctl start stumblefeed"
echo "  3. systemctl status stumblefeed"
