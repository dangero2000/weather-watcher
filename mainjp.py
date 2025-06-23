import os
import uuid
import time
import requests
import configparser
import subprocess
import paramiko
import socket
from datetime import datetime, timedelta

# --- CONFIG ---
config = configparser.ConfigParser()
config.read("configjp.ini")

GEMINI_API_KEY = config["DEFAULT"]["gemini_api_key"]
TTS_VOICE = config["DEFAULT"]["tts_voice"]
TTS_RATE = config["DEFAULT"].get("tts_rate", "190")
TMP_DIR = config["paths"]["tmp_dir"]

SFTP_HOST = config["SFTP"].get("host", "").strip()
SFTP_PORT = config["SFTP"].getint("port", fallback=22)
SFTP_USER = config["SFTP"].get("username")
SFTP_PASS = config["SFTP"].get("password")
SFTP_REMOTE_PATH = config["SFTP"].get("remote_file_path")

# Use local IP if host is not set
if not SFTP_HOST:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        SFTP_HOST = s.getsockname()[0]
        s.close()
        print(f"[INFO] Using local IP for SFTP: {SFTP_HOST}")
    except Exception as e:
        raise RuntimeError(f"Could not determine local IP: {e}")

os.makedirs(TMP_DIR, exist_ok=True)

# --- Fetch weather alerts ---
def get_top_weather_alerts():
    print("[INFO] Fetching weather alerts...")
    url = "https://api.weather.gov/alerts/active"
    headers = {"User-Agent": "quirky-weathercaster"}
    try:
        response = requests.get(url, headers=headers, timeout=10)
        data = response.json()
        summaries = []
        for feature in data.get("features", []):
            props = feature.get("properties", {})
            area = props.get("areaDesc", "an unknown place")
            headline = props.get("headline", "Something's happening!")
            desc = props.get("description", "Details are scarce.")
            summaries.append(f"{headline} in {area}: {desc}")
            if len(summaries) >= 3:
                break
        return "\n\n".join(summaries) if summaries else "No juicy weather gossip right now."
    except Exception as e:
        return f"Weather API failed: {e}"

# --- Summarize using Gemini ---
def summarize_quirky(text):
    print("[INFO] Summarizing with Gemini...")
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={GEMINI_API_KEY}"
    headers = {'Content-Type': 'application/json'}
    prompt = (
    "あなたは風変わりで陽気なラジオの天気アナウンサーです。"
    "最大で三つまでの主要な気象警報を、ユーモラスでくだけた、そして鮮やかな方法で要約してください。警報がどの言語で書かれていても、日本語で要約してください。"
    "この要約は音読されるため、句読点はピリオド、カンマ、感嘆符、疑問符などの通常の記号のみを使用してください。"
    "アスタリスク、アットマーク、シャープ、絵文字などの特殊記号は、いかなる場合でも使用してはいけませんので、絶対に避けてください。数字はすべて文字で書き、略語は避けてください。"
    f"こちらが警報です:\n{text}"
    )
    payload = {"contents": [{"parts": [{"text": prompt}]}]}
    try:
        response = requests.post(url, headers=headers, json=payload)
        data = response.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"Gemini API error: {e}"

# --- Synthesize AIFF with macOS say ---
def synthesize(text, out_path):
    print("[INFO] Synthesizing speech...")
    cmd = ["say", "-v", TTS_VOICE, "-r", TTS_RATE, "-o", out_path, text]
    subprocess.run(cmd, check=True)

# --- Convert AIFF to MP3 ---
def convert_to_mp3(aiff_path, mp3_path):
    print("[INFO] Converting to MP3...")
    cmd = ["ffmpeg", "-y", "-i", aiff_path, "-acodec", "libmp3lame", "-b:a", "128k", mp3_path]
    subprocess.run(cmd, check=True)

# --- Upload via SFTP ---
def upload_file(local_path):
    print(f"[INFO] Uploading to SFTP: {SFTP_HOST}:{SFTP_REMOTE_PATH}")
    transport = paramiko.Transport((SFTP_HOST, SFTP_PORT))
    transport.connect(username=SFTP_USER, password=SFTP_PASS)
    sftp = paramiko.SFTPClient.from_transport(transport)
    sftp.put(local_path, SFTP_REMOTE_PATH)
    sftp.close()
    transport.close()
    print("[INFO] Upload successful.")

# --- Wait until XX:58 ---
def wait_until_next_upload_time():
    now = datetime.now()
    next_upload = now.replace(minute=58, second=0, microsecond=0)
    if now.minute >= 58:
        next_upload += timedelta(hours=1)
    wait_seconds = (next_upload - now).total_seconds()
    print(f"[INFO] Waiting {int(wait_seconds)} seconds until next upload at {next_upload.time()}...")
    time.sleep(wait_seconds)

# --- Main loop ---
def main():
    while True:
        wait_until_next_upload_time()
        alerts = get_top_weather_alerts()
        summary = summarize_quirky(alerts)
        print(f"[SUMMARY]\n{summary}\n")
        base = uuid.uuid4().hex
        aiff_path = os.path.join(TMP_DIR, f"{base}.aiff")
        mp3_path = os.path.join(TMP_DIR, f"{base}.mp3")
        try:
            synthesize(summary, aiff_path)
            convert_to_mp3(aiff_path, mp3_path)
            upload_file(mp3_path)
        except Exception as e:
            print(f"[ERROR] {e}")
        finally:
            for path in (aiff_path, mp3_path):
                if os.path.exists(path):
                    os.remove(path)

if __name__ == "__main__":
    main()
