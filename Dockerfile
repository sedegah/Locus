FROM python:3.12-slim

# Prevent interactive prompts during apt-get
ENV DEBIAN_FRONTEND=noninteractive
ENV PYTHONUNBUFFERED=1

# Install system dependencies: Tkinter, Xvfb, VNC, noVNC web interface, and fonts
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3-tk \
    tk-dev \
    tcl-dev \
    xvfb \
    x11vnc \
    fluxbox \
    novnc \
    websockify \
    fonts-dejavu-core \
    fonts-freefont-ttf \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Pre-configure noVNC root index.html to auto-connect with full canvas scaling
RUN ln -sf /usr/share/novnc/vnc.html /usr/share/novnc/index.html || true

WORKDIR /app

# Copy requirements and install python packages
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy source code and assets
COPY . .

# Ensure entrypoint is executable
RUN chmod +x entrypoint.sh

# Expose noVNC web streaming port
EXPOSE 8080

CMD ["./entrypoint.sh"]
