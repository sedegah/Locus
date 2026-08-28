#!/usr/bin/env bash
set -e

# Setup virtual display
export DISPLAY=:99
export RESOLUTION="${RESOLUTION:-1440x900x24}"

# Start Xvfb virtual framebuffer
echo "Starting Xvfb..."
Xvfb :99 -screen 0 "$RESOLUTION" -ac +extension GLX +render -noreset &
sleep 1

# Start lightweight window manager
echo "Starting window manager..."
fluxbox &
sleep 1

# Create an instant JavaScript redirect index.html in noVNC folder
cat << 'EOF' > /usr/share/novnc/index.html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <title>Locus — Math Engine</title>
    <script>
        window.location.replace("vnc.html?autoconnect=true&resize=scale&reconnect=true&quality=9");
    </script>
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
        a { color: #00E5FF; text-decoration: underline; }
    </style>
</head>
<body>
    <div style="text-align: center;">
        <h2>Launching Locus Math Engine...</h2>
        <p>If not redirected automatically, <a href="vnc.html?autoconnect=true&resize=scale&reconnect=true&quality=9">click here to open</a>.</p>
    </div>
</body>
</html>
EOF

# Start x11vnc server
echo "Starting x11vnc..."
x11vnc -display :99 -forever -nopw -shared -rfbport 5900 -bg
sleep 1

# Start noVNC web client on port 8080 (Fly.io standard port)
echo "Starting websockify on port 8080..."
websockify --web /usr/share/novnc 8080 localhost:5900 &

echo "Starting Locus Desktop Engine..."
# Launch application
exec python main.py
