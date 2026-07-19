#!/bin/bash
# StumbleFeed dev API setup — Ubuntu (run as root)
# Usage: bash setup-dev.sh
set -e

DEV_DIR=/opt/stumblefeed-dev
REPO=https://github.com/pigeoncorner/personafeed.git

echo "=== StumbleFeed Dev Setup ==="

# ── Clone or update repo ───────────────────────────────────────────────────────
if [ -d "$DEV_DIR/.git" ]; then
  echo "[1/4] Updating dev repo (git pull dev)..."
  cd $DEV_DIR
  git fetch origin
  git checkout dev
  git pull origin dev
else
  echo "[1/4] Cloning repo (dev branch)..."
  git clone --branch dev $REPO $DEV_DIR
  cd $DEV_DIR
fi

mkdir -p $DEV_DIR/data

# ── Python venv ───────────────────────────────────────────────────────────────
echo "[2/4] Installing Python dependencies..."
python3 -m venv $DEV_DIR/venv
source $DEV_DIR/venv/bin/activate
pip install --quiet -r $DEV_DIR/requirements.txt

# ── .env ──────────────────────────────────────────────────────────────────────
if [ ! -f $DEV_DIR/.env ]; then
  if [ -f /opt/stumblefeed/.env ]; then
    echo "Copying .env from prod..."
    cp /opt/stumblefeed/.env $DEV_DIR/.env
  else
    cat > $DEV_DIR/.env <<'EOF'
YOUTUBE_API_KEY=your_key_here
NEWS_API_KEY=your_key_here
VK_ACCESS_TOKEN=
EOF
    echo ">>> Edit $DEV_DIR/.env before starting the service <<<"
  fi
fi

chown -R www-data:www-data $DEV_DIR

# ── Systemd ───────────────────────────────────────────────────────────────────
echo "[3/4] Configuring systemd service..."
cp $DEV_DIR/deploy/stumblefeed-dev.service /etc/systemd/system/stumblefeed-dev.service
systemctl daemon-reload
systemctl enable stumblefeed-dev
systemctl restart stumblefeed-dev

# ── Caddy ─────────────────────────────────────────────────────────────────────
echo "[4/4] Configuring Caddy..."
if ! grep -q "dev-api.stumblefeed.me" /etc/caddy/Caddyfile; then
  cat $DEV_DIR/deploy/Caddyfile.dev >> /etc/caddy/Caddyfile
fi
mkdir -p /var/log/caddy
systemctl reload caddy

echo ""
echo "=== Done ==="
echo ""
echo "Dev API running at: https://dev-api.stumblefeed.me"
echo ""
echo "Next: add DNS A-record  dev-api.stumblefeed.me → $(curl -s ifconfig.me)"
echo ""
echo "To deploy new code from dev branch:"
echo "  cd $DEV_DIR && git pull origin dev && systemctl restart stumblefeed-dev"
