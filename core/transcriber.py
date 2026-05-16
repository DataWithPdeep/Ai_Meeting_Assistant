import os
import subprocess
import requests
import imageio_ffmpeg
from openai import OpenAI

from dotenv import load_dotenv
load_dotenv()

_ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()
print(f"✅ ffmpeg path: {_ffmpeg_exe}")

SARVAM_PIECE_SECONDS = 25
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")
SARVAM_STT_TRANSLATE_URL = "https://api.sarvam.ai/speech-to-text-translate"
SARVAM_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

client = OpenAI()  # OPENAI_API_KEY env se lega

# =========================================================
# OPENAI WHISPER API TRANSCRIPTION
# =========================================================

def transcribe_chunk_whisper(chunk_path: str) -> str:
    print(f"→ OpenAI Whisper API: {os.path.basename(chunk_path)}")
    with open(chunk_path, "rb") as audio_file:
        result = client.audio.transcriptions.create(
            model="whisper-1",
            file=audio_file
        )
    return result.text

# =========================================================
# SARVAM API (Hinglish) — same as before
# =========================================================

def _send_to_sarvam(piece_path: str) -> str:
    headers = {"api-subscription-key": SARVAM_API_KEY}
    with open(piece_path, "rb") as f:
        files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
        data = {"model": SARVAM_MODEL, "with_diarization": "false"}
        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers, files=files, data=data, timeout=120,
        )
    if not response.ok:
        print(f"❌ Sarvam Error: {response.status_code} — {response.text}")
        response.raise_for_status()
    return response.json().get("transcript", "")

def transcribe_chunk_sarvam(chunk_path: str) -> str:
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY not found in .env")

    result = subprocess.run(
        [_ffmpeg_exe, "-i", chunk_path],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE
    )
    stderr = result.stderr.decode()
    total_duration = None
    for line in stderr.split("\n"):
        if "Duration" in line:
            time_str = line.strip().split("Duration:")[1].split(",")[0].strip()
            h, m, s = time_str.split(":")
            total_duration = int(h) * 3600 + int(m) * 60 + float(s)
            break

    if total_duration is None:
        raise RuntimeError(f"❌ Could not detect duration: {chunk_path}")

    total_pieces = int(total_duration / SARVAM_PIECE_SECONDS) + 1
    full_text = ""

    for i in range(total_pieces):
        start = i * SARVAM_PIECE_SECONDS
        piece_path = f"{chunk_path}_sv_{i}.wav"
        subprocess.run(
            [_ffmpeg_exe, "-ss", str(start), "-i", chunk_path,
             "-t", str(SARVAM_PIECE_SECONDS), "-ac", "1", "-ar", "16000",
             "-y", piece_path],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        if not os.path.exists(piece_path) or os.path.getsize(piece_path) < 1000:
            if os.path.exists(piece_path):
                os.remove(piece_path)
            break
        try:
            print(f"→ Sarvam piece {i+1}/{total_pieces}")
            full_text += _send_to_sarvam(piece_path) + " "
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return full_text.strip()

# =========================================================
# ROUTER + TRANSCRIBE ALL — same as before
# =========================================================

def transcribe_chunk(chunk_path: str, language: str = "english") -> str:
    if language.lower() == "hinglish":
        return transcribe_chunk_sarvam(chunk_path)
    return transcribe_chunk_whisper(chunk_path)

def transcribe_all(chunks: list, language: str = "english") -> str:
    full_transcript = ""
    engine = "Sarvam AI" if language.lower() == "hinglish" else "OpenAI Whisper API"
    print(f"✅ Using {engine}")
    for i, chunk in enumerate(chunks):
        print(f"Transcribing chunk {i+1}/{len(chunks)}...")
        text = transcribe_chunk(chunk, language=language)
        full_transcript += text + " "
    print("✅ Transcription complete.")
    return full_transcript.strip()