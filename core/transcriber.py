import os
import subprocess
import requests
import imageio_ffmpeg
import whisper

from dotenv import load_dotenv

# =========================================================
# LOAD ENV
# =========================================================

load_dotenv()

# =========================================================
# FFMPEG SETUP
# =========================================================
# Streamlit Cloud Compatible
# No manual ffmpeg copying needed

_ffmpeg_exe = imageio_ffmpeg.get_ffmpeg_exe()

print(f"✅ ffmpeg path: {_ffmpeg_exe}")

# =========================================================
# CONFIG
# =========================================================

WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")

SARVAM_PIECE_SECONDS = 25

SARVAM_API_KEY = os.getenv("SARVAM_API_KEY")

SARVAM_STT_TRANSLATE_URL = (
    "https://api.sarvam.ai/speech-to-text-translate"
)

SARVAM_MODEL = os.getenv(
    "SARVAM_STT_MODEL",
    "saaras:v2.5"
)

print(f"✅ Whisper Model: {WHISPER_MODEL}")

# =========================================================
# GLOBAL MODEL
# =========================================================

_model = None

# =========================================================
# LOAD WHISPER MODEL
# =========================================================

def load_model():

    global _model

    if _model is None:

        print(f"Loading Whisper model: {WHISPER_MODEL} ...")

        _model = whisper.load_model(
            WHISPER_MODEL
        )

        print("✅ Whisper model loaded.")

    return _model

# =========================================================
# WHISPER TRANSCRIPTION
# =========================================================

def transcribe_chunk_whisper(chunk_path: str) -> str:

    model = load_model()

    result = model.transcribe(
        chunk_path,
        task="transcribe",
        fp16=False
    )

    return result["text"]

# =========================================================
# SARVAM API REQUEST
# =========================================================

def _send_to_sarvam(piece_path: str) -> str:

    headers = {
        "api-subscription-key": SARVAM_API_KEY
    }

    with open(piece_path, "rb") as f:

        files = {
            "file": (
                os.path.basename(piece_path),
                f,
                "audio/wav"
            )
        }

        data = {
            "model": SARVAM_MODEL,
            "with_diarization": "false"
        }

        response = requests.post(
            SARVAM_STT_TRANSLATE_URL,
            headers=headers,
            files=files,
            data=data,
            timeout=120,
        )

    if not response.ok:

        print(f"\n❌ Sarvam Error: {response.status_code}")

        print(f"Response: {response.text}\n")

        response.raise_for_status()

    return response.json().get(
        "transcript",
        ""
    )

# =========================================================
# SARVAM TRANSCRIPTION
# =========================================================

def transcribe_chunk_sarvam(chunk_path: str) -> str:

    if not SARVAM_API_KEY:

        raise RuntimeError(
            "SARVAM_API_KEY not found in .env"
        )

    # =====================================================
    # GET AUDIO DURATION
    # =====================================================

    result = subprocess.run(
        [_ffmpeg_exe, "-i", chunk_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stderr = result.stderr.decode()

    total_duration = None

    for line in stderr.split("\n"):

        if "Duration" in line:

            time_str = (
                line.strip()
                .split("Duration:")[1]
                .split(",")[0]
                .strip()
            )

            h, m, s = time_str.split(":")

            total_duration = (
                int(h) * 3600
                + int(m) * 60
                + float(s)
            )

            break

    if total_duration is None:

        raise RuntimeError(
            f"❌ Could not detect duration: {chunk_path}"
        )

    # =====================================================
    # SPLIT AUDIO
    # =====================================================

    total_pieces = (
        int(total_duration / SARVAM_PIECE_SECONDS) + 1
    )

    full_text = ""

    for i in range(total_pieces):

        start = i * SARVAM_PIECE_SECONDS

        piece_path = (
            f"{chunk_path}_sv_{i}.wav"
        )

        subprocess.run(
            [
                _ffmpeg_exe,
                "-ss",
                str(start),
                "-i",
                chunk_path,
                "-t",
                str(SARVAM_PIECE_SECONDS),
                "-ac",
                "1",
                "-ar",
                "16000",
                "-y",
                piece_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        # =================================================
        # CHECK FILE
        # =================================================

        if (
            not os.path.exists(piece_path)
            or os.path.getsize(piece_path) < 1000
        ):

            if os.path.exists(piece_path):

                os.remove(piece_path)

            break

        # =================================================
        # API CALL
        # =================================================

        try:

            print(
                f"→ Sarvam piece "
                f"{i + 1}/{total_pieces}"
            )

            full_text += (
                _send_to_sarvam(piece_path)
                + " "
            )

        finally:

            if os.path.exists(piece_path):

                os.remove(piece_path)

    return full_text.strip()

# =========================================================
# MAIN TRANSCRIBE ROUTER
# =========================================================

def transcribe_chunk(
    chunk_path: str,
    language: str = "english"
) -> str:

    if language.lower() == "hinglish":

        return transcribe_chunk_sarvam(
            chunk_path
        )

    return transcribe_chunk_whisper(
        chunk_path
    )

# =========================================================
# TRANSCRIBE ALL CHUNKS
# =========================================================

def transcribe_all(
    chunks: list,
    language: str = "english"
) -> str:

    full_transcript = ""

    engine = (
        "Sarvam AI"
        if language.lower() == "hinglish"
        else "Whisper"
    )

    print(f"✅ Using {engine}")

    for i, chunk in enumerate(chunks):

        print(
            f"Transcribing chunk "
            f"{i + 1}/{len(chunks)}..."
        )

        text = transcribe_chunk(
            chunk,
            language=language
        )

        full_transcript += text + " "

    print("✅ Transcription complete.")

    return full_transcript.strip()