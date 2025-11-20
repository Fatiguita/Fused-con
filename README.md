
# 📼 Fused-Con Termux Twitch DVR
(coded with AI gemini 3.0)
> **A fully autonomous Twitch Recorder running entirely on your Android phone.**

[![Termux](https://img.shields.io/badge/Platform-Termux-green.svg)](https://termux.dev/en/)
[![Python](https://img.shields.io/badge/Python-3.x-blue.svg)](https://www.python.org/)
[![Streamlink](https://img.shields.io/badge/Backend-Streamlink-purple.svg)](https://streamlink.github.io/)

Turn your Android device into a dedicated DVR server. This Flask web application runs locally in Termux, monitors your favorite Twitch streamers, and automatically records their broadcasts to your device's storage.

---

## ✨ Features

*   **📱 100% Local:** Runs on your phone. No VPS or PC required.
*   **🧠 Smart Quality:** Choose specific qualities (e.g., 1080p60). If unavailable, it automatically falls back to the next best option.
*   **📂 Auto-Organization:** Creates separate folders for each streamer (`/Downloads/TwitchStreams/shroud/`).
*   **🔔 Notifications:** Get notified when a recording starts or when a streamer goes live (Manual Mode).
*   **🎨 13 UI Themes:** Includes **Naruto**, **Cyberpunk**, **Matrix**, **Windows 95**, and more.
*   **⏯️ Integrated Library:** Browse recordings and open them directly in your favorite player (VLC, MX Player) or File Manager.
*   **🔋 Battery Efficient:** "Audio Only" mode supported for podcast-style recording (approx 60MB/hour).
*   **🚀 Auto-Start:** Automatically launches in the background when you reboot your phone (requires Termux:Boot).

---

## 🛠️ Prerequisites

You need the following apps installed on your Android device:

1.  **[Termux](https://f-droid.org/en/packages/com.termux/)** (From F-Droid, **not** Play Store)
2.  **[Termux:API](https://f-droid.org/en/packages/com.termux.api/)** (App + Package)
3.  **[Termux:Boot](https://f-droid.org/en/packages/com.termux.boot/)** (For auto-start on reboot)

> **⚠️ Important:** Ensure you disable "Battery Optimizations" for Termux and Termux:Boot in your Android Settings, or the system will kill the recording in the background.
> Also make sure to enter both extension Apps (Termx:API | Termux:Boot) and follow guides

---

## 📥 Installation

Open Termux and run these commands:

### 1. Clone the Repository
```bash
git clone https://github.com/Fatiguita/Fused-con
cd Fused-con
```

### 2. Run the Installer
This script automates the installation of Python, FFmpeg, Streamlink, and fixes common XML compilation errors.
```bash
chmod +x setup.sh
./setup.sh
```

*During installation, you will be asked to allow Storage Permissions. Tap **Allow**.*

### 3. Start the App
```bash
python app.py
```

---

## 🖥️ Usage

1.  Open your mobile browser (Chrome, Firefox, etc.).
2.  Go to: **`http://localhost:5660`**
3.  **Add a Streamer:**
    *   Type the channel name (e.g., `kai cenat`).
    *   Click **🔍** to see if they are live and what qualities are available.
    *   Select format (`mp4`, `mkv`, `ts`) and Quality.
    *   *Optional:* Check **"Prompt me"** to receive a notification instead of auto-recording.

### 📂 Where are files saved?
By default, recordings are saved to:
`/sdcard/Download/TwitchStreams/STREAMER_NAME/`

You can change this path in the **Settings** tab.

---

## 🎨 Themes

Customize the look of your DVR in the **Settings** tab. Included presets:

| Theme | Description |
| :--- | :--- |
| **🔥 Naruto** | Ninja orange & black style. |
| **🤖 Cyberpunk** | Neon yellow & blue high-contrast. |
| **💻 Terminal** | Matrix style green-on-black. |
| **🧛 Dracula** | Purple, dark, and contrasty. |
| **🌴 Retro** | Vaporwave aesthetic (Purple/Cyan). |
| **💾 90s** | Windows 95 classic gray look. |
| **📝 Paper** | Minimalist black & white manga style. |

...and 6 more!

---

## 🔧 Troubleshooting

**1. "Permission Denied" error?**
Run this command in Termux:
```bash
termux-setup-storage
```

**2. Recording stops when I lock my screen.**
Android is killing the process.
1.  Go to Android Settings -> Apps -> Termux -> Battery -> **Unrestricted**.
2.  Pull down your notification bar and make sure "Termux" is showing a "Wake lock held" notification.

**3. Streamlink "403 Forbidden" or "No streams found".**
Twitch updates their API frequently. Update the backend:
```bash
pip install --upgrade streamlink
```

**4. Videos won't play in Gallery.**
Ensure you have a video player installed (like VLC). The "Open" button uses Android's native "Share/Open With" intent.

---

## 📜 License

This project is open-source. Feel free to modify and distribute.
