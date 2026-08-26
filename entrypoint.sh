#!/usr/bin/env bash
set -e

# Setup virtual display
export DISPLAY=:99
export RESOLUTION="${RESOLUTION:-1440x900x24}"

# Start Xvfb virtual framebuffer
Xvfb :99 -screen 0 "$RESOLUTION" &
sleep 1

# Start lightweight window manager
fluxbox &
sleep 1

# Start x11vnc server
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 -bg

# Start noVNC web client on port 8080 (Fly.io standard port)
websockify --web /usr/share/novnc 8080 localhost:5900 &

# Auto-redirect root to vnc.html
if [ -f /usr/share/novnc/index.html ]; then
    cp /usr/share/novnc/vnc.html /usr/share/novnc/index.html 2>/dev/null || true
fi

echo "Starting Locus Math Engine..."
# Launch application
exec python main.py
