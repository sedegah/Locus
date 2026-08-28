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

# Ensure index.html automatically connects to noVNC session with scaling enabled
cat << 'EOF' > /usr/share/novnc/index.html
<!DOCTYPE html>
<html>
<head>
    <title>Locus — Math Engine</title>
    <meta http-equiv="refresh" content="0; url=vnc.html?autoconnect=true&resize=scale&reconnect=true&quality=9">
    <style>
        body {
            background-color: #090A0F;
            color: #FFC72C;
            font-family: 'Segoe UI', system-ui, -apple-system, sans-serif;
            display: flex;
            align-items: center;
            justify-content: center;
            height: 100vh;
            margin: 0;
        }
    </style>
</head>
<body>
    <h2>Launching Locus Math Engine...</h2>
</body>
</html>
EOF

# Start x11vnc server
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 -bg

# Start noVNC web client on port 8080 (Fly.io standard port)
websockify --web /usr/share/novnc 8080 localhost:5900 &

echo "Starting Locus Math Engine..."
# Launch application
exec python main.py
