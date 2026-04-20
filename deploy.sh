#!/bin/bash
set -e

SERVER="lab-bananas"
APP_DIR="/var/www/joaoazuldev"

echo "🚀 Deploying to $SERVER..."

ssh "$SERVER" "cd $APP_DIR && git pull origin main && source .venv/bin/activate && pip install -r requirements.txt --quiet && (pkill -f 'python.*wsgi' || true) && nohup python wsgi.py > /dev/null 2>&1 & echo '✅ Deployed successfully!'"
