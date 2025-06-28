#!/bin/sh
set -e

if [ $# -lt 3 ]; then
  echo "Usage: $0 host:port [host:port …] -- cmd args…"
  exit 1
fi

HOSTS=""
while [ "$1" != "--" ]; do
  HOSTS="$HOSTS $1"
  shift
done
shift

echo "🚀 Starting wait-for-it script..."

for hostport in $HOSTS; do
  host=$(echo "$hostport" | cut -d: -f1)
  port=$(echo "$hostport" | cut -d: -f2)
  echo "⏳ Waiting for ${host}:${port}…"

  max_attempts=60
  attempt=0

  while [ $attempt -lt $max_attempts ]; do
    if python3 -c "
import socket
try:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.settimeout(3)
    sock.connect(('$host', $port))
    sock.close()
    exit(0)
except:
    exit(1)
" 2>/dev/null; then
      echo "✅ ${host}:${port} is up"
      break
    fi

    attempt=$((attempt + 1))
    echo "…retrying ${host}:${port} (attempt ${attempt}/${max_attempts})"
    sleep 2

    if [ $attempt -eq $max_attempts ]; then
      echo "❌ Timeout waiting for ${host}:${port} after $((max_attempts * 2)) seconds"
      exit 1
    fi
  done
done

echo "🎉 All services are ready! Starting application..."
exec "$@"