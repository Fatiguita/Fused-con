import os
import time
import json
import threading
import subprocess
import argparse
import logging
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, url_for, jsonify

# --- Setup ---
parser = argparse.ArgumentParser()
parser.add_argument('--verbose', action='store_true', help="Enable file logging")
args = parser.parse_args()

LOG_DIR = 'logs'
if not os.path.exists(LOG_DIR): os.makedirs(LOG_DIR)

logger = logging.getLogger('dvr')
logger.setLevel(logging.DEBUG if args.verbose else logging.INFO)
formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

# Console Handler
ch = logging.StreamHandler()
ch.setFormatter(formatter)
logger.addHandler(ch)

# File Handler (if verbose)
if args.verbose:
    fh = logging.FileHandler(os.path.join(LOG_DIR, 'dvr_system.log'))
    fh.setFormatter(formatter)
    logger.addHandler(fh)

app = Flask(__name__)
app.secret_key = 'termux_dvr_secret'

# --- Config ---
DEFAULT_CONFIG = {
    "output_dir": "/sdcard/Download/TwitchStreams",
    "check_interval": 60,
    "filename_format": "{date} - {title}",
    "theme": "theme-naruto",
    "manual_mode_global": False
}
CONFIG_FILE = 'config.json'
STREAMERS_FILE = 'streamers.json'

active_downloads = {}
status_log = {}
manual_awaiting = set()

# --- Helpers ---
def load_json(file, default):
    if not os.path.exists(file): return default
    try:
        with open(file, 'r') as f: return json.load(f)
    except: return default

def save_json(file, data):
    with open(file, 'w') as f: json.dump(data, f, indent=4)

def get_config():
    cfg = load_json(CONFIG_FILE, DEFAULT_CONFIG)
    for k, v in DEFAULT_CONFIG.items():
        if k not in cfg: cfg[k] = v
    return cfg

def send_notification(title, content):
    try:
        subprocess.run(["termux-notification", "--title", title, "--content", content])
    except: pass

def get_stream_metadata(streamer):
    try:
        cmd = ["streamlink", f"twitch.tv/{streamer}", "--json"]
        result = subprocess.run(cmd, capture_output=True, text=True)
        if result.returncode != 0: return None
        data = json.loads(result.stdout)
        if 'error' in data or not data.get('streams'): return None
        return data.get('metadata', {})
    except: return None

# --- Routes ---
@app.route('/')
def index():
    return render_template('index.html', streamers=load_json(STREAMERS_FILE, {}), status=status_log, theme=get_config()['theme'])

@app.route('/api/check_qualities', methods=['POST'])
def check_qualities_api():
    name = request.get_json().get('name', '').strip().lower()
    if not name: return jsonify({'error': 'No name'})
    
    try:
        result = subprocess.run(["streamlink", f"twitch.tv/{name}", "--json"], capture_output=True, text=True)
        if result.returncode != 0: return jsonify({'status': 'error', 'message': 'CLI Failed'})
        data = json.loads(result.stdout)
        
        if 'error' in data or not data.get('streams'):
            return jsonify({'status': 'offline'})
            
        qualities = list(data.get('streams', {}).keys())
        # Sort: Best -> 1080 -> ... -> Audio -> Worst
        def sort_key(q):
            if q == 'best': return 10000
            if q == 'worst': return -1
            if 'audio' in q: return 0
            m = re.search(r'\d+', q)
            return int(m.group()) if m else 1
        qualities.sort(key=sort_key, reverse=True)
        return jsonify({'status': 'online', 'qualities': qualities})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/open_folder', methods=['POST'])
def open_folder_api():
    try:
        subprocess.run(["termux-open", get_config()['output_dir']])
        return jsonify({'status': 'success'})
    except Exception as e: return jsonify({'status': 'error', 'message': str(e)})

@app.route('/api/open_file', methods=['POST'])
def open_file_api():
    filename = request.get_json().get('filename')
    path = os.path.join(get_config()['output_dir'], filename)
    if os.path.exists(path):
        subprocess.run(["termux-open", path])
        return jsonify({'status': 'success'})
    return jsonify({'status': 'error', 'message': 'File not found'})

@app.route('/record/<name>')
def manual_record_trigger(name):
    if name in manual_awaiting:
        manual_awaiting.remove(name)
        meta = get_stream_metadata(name)
        title = meta.get('title', 'Manual') if meta else 'Manual'
        start_recording(name, load_json(STREAMERS_FILE, {}).get(name, {}), get_config(), title)
    return redirect(url_for('index'))

@app.route('/add', methods=['POST'])
def add():
    name = request.form.get('name').strip().lower()
    if name:
        data = load_json(STREAMERS_FILE, {})
        data[name] = {"quality": request.form.get('quality'), "format": request.form.get('format'), "manual": 'manual' in request.form}
        save_json(STREAMERS_FILE, data)
    return redirect(url_for('index'))

@app.route('/delete/<name>')
def delete(name):
    data = load_json(STREAMERS_FILE, {})
    if name in data: del data[name]; save_json(STREAMERS_FILE, data)
    return redirect(url_for('index'))

@app.route('/stop/<name>')
def stop(name):
    if name in active_downloads:
        active_downloads[name].terminate()
        del active_downloads[name]
        status_log[name] = "🛑 Stopped"
    return redirect(url_for('index'))

@app.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        cfg = get_config()
        cfg['output_dir'] = request.form.get('output_dir')
        cfg['check_interval'] = int(request.form.get('check_interval'))
        cfg['filename_format'] = request.form.get('filename_format')
        cfg['theme'] = request.form.get('theme')
        cfg['manual_mode_global'] = 'manual_mode_global' in request.form
        save_json(CONFIG_FILE, cfg)
        return redirect(url_for('index'))
    return render_template('settings.html', config=get_config(), theme=get_config()['theme'])

@app.route('/gallery')
def gallery():
    cfg = get_config()
    files = []
    base_dir = cfg['output_dir']
    if os.path.exists(base_dir):
        for root, dirs, filenames in os.walk(base_dir):
            for f in filenames:
                if f.endswith(('.mp4', '.mkv', '.ts')):
                    rel_dir = os.path.relpath(root, base_dir)
                    files.append(f if rel_dir == '.' else os.path.join(rel_dir, f))
        files.sort(key=lambda x: os.path.getmtime(os.path.join(base_dir, x)), reverse=True)
    return render_template('gallery.html', files=files, theme=get_config()['theme'])

# --- Logic ---
def worker():
    logger.info("Worker started.")
    while True:
        cfg = get_config()
        streamers = load_json(STREAMERS_FILE, {})
        for name, settings in streamers.items():
            if name in active_downloads:
                if active_downloads[name].poll() is None:
                    status_log[name] = "🔴 Recording"
                    continue
                else:
                    del active_downloads[name]
                    status_log[name] = "🏁 Finished"
            
            if name in manual_awaiting:
                status_log[name] = "⚠️ Waiting User"
                continue

            metadata = get_stream_metadata(name)
            if metadata:
                title = metadata.get('title', 'Unknown')
                is_manual = settings.get('manual', False) or cfg['manual_mode_global']
                if is_manual:
                    if name not in manual_awaiting:
                        manual_awaiting.add(name)
                        send_notification(f"{name} Live", title)
                    status_log[name] = "⚠️ Live (Waiting)"
                else:
                    start_recording(name, settings, cfg, title)
            else:
                status_log[name] = "⚪ Offline"
        time.sleep(int(cfg['check_interval']))

def start_recording(name, settings, cfg, title="Unknown"):
    now = datetime.now()
    safe_title = "".join([c for c in title if c.isalnum() or c in " -_"]).strip()
    filename = cfg['filename_format'].format(author=name, title=safe_title, date=now.strftime("%Y-%m-%d"), time=now.strftime("%H-%M"), HH=now.strftime("%H"))
    ext = settings.get('format', 'mp4')
    
    # Folder per streamer
    save_dir = os.path.join(cfg['output_dir'], name)
    os.makedirs(save_dir, exist_ok=True)
    full_path = os.path.join(save_dir, f"{filename}.{ext}")

    cmd = ["streamlink", "--output", full_path, "--twitch-disable-ads", "--force", f"twitch.tv/{name}", f"{settings.get('quality', 'best')},best"]
    try:
        proc = subprocess.Popen(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        active_downloads[name] = proc
        status_log[name] = "🟢 Starting..."
        send_notification(f"Recording {name}", filename)
    except Exception as e:
        status_log[name] = "❌ Error"
        logger.error(f"Start failed: {e}")

threading.Thread(target=worker, daemon=True).start()

if __name__ == '__main__':
    logging.getLogger('werkzeug').setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=5660, debug=True)
