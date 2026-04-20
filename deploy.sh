#!/bin/bash
set -e

SERVER="lab-bananas"
APP_DIR="/var/www/joaoazuldev"

echo "🚀 Deploying to $SERVER..."

ssh "$SERVER" "
  cd $APP_DIR &&
  sudo chown -R \$(whoami):\$(whoami) . &&
  git pull origin main &&
  source .venv/bin/activate &&
  pip install -r requirements.txt --quiet &&
  (pkill -f 'python.*wsgi' || true) &&
  sleep 1 &&
  nohup python wsgi.py > app.log 2>&1 &
  sleep 2 &&
  if pgrep -f 'python.*wsgi' > /dev/null; then
    echo '✅ Deployed successfully!'
  else
    echo '❌ App failed to start. Last logs:'
    tail -20 app.log
    exit 1
  fi
"
