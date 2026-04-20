#!/bin/bash
set -e

SERVER="joa0bananas"
APP_DIR="/var/www/joaoazuldev"

echo "🚀 Deploying to $SERVER..."

ssh "$SERVER" bash -s <<'EOF'
set -e
cd /var/www/joaoazuldev

echo "📥 Pulling latest code..."
git pull origin main

echo "📦 Installing dependencies..."
source .venv/bin/activate
pip install -r requirements.txt --quiet

echo "🔄 Restarting app..."
pkill -f "python.*wsgi" || true
nohup python wsgi.py > /dev/null 2>&1 &

echo "✅ Deployed successfully!"
EOF
