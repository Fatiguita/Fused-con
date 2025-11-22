#!/bin/bash

echo "--- Fused-Con Termux Twitch DVR Installer ---"

# 1. Update System & Install Dependencies
echo "[*] Updating system packages..."
pkg update -y && pkg upgrade -y
echo "[*] Installing dependencies (Python, FFmpeg, XML libs)..."
pkg install python ffmpeg termux-api libxml2 libxslt clang binutils -y

# 2. Install Python Libraries
echo "[*] Installing Python libraries (this may take a moment)..."
pip install --upgrade pip
pip install flask requests streamlink

# 3. Setup Storage
echo "[*] Requesting storage access (Please Allow by typing Y and enter)..."
termux-setup-storage
sleep 10

# 4. Setup Termux:Boot
mkdir ~/.termux/boot/
mkdir ~/.termux/boot/logs/
BOOT_DIR="$HOME/.termux/boot"
SCRIPT_PATH="$(pwd)"

if [ -d "$BOOT_DIR" ]; then
    echo "[*] Setting up auto-start script..."
    
    cat <<EOT > "$BOOT_DIR/fusedcon.sh"
#!/data/data/com.termux/files/usr/bin/sh
termux-wake-lock
cd "$SCRIPT_PATH"
echo "Starting Twitch DVR..."
nohup python app.py --verbose &
EOT

    chmod +x "$BOOT_DIR/fusedcon.sh"
    ~/.termux/boot/fusedcon.sh
    echo "[✓] Auto-start configured! App will run on phone restart."
else
    echo "[!] Termux:Boot folder not found."
    echo "    Please install the 'Termux:Boot' app from F-Droid."
fi

# 5. Create Directories
mkdir -p logs

echo ""
echo "--- Installation Complete! ---"
echo "1. To start now: python app.py"
echo "2. Access via: http://localhost:5660"
echo "------------------------------"
