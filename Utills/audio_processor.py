import os
import glob
import subprocess
import imageio_ffmpeg
import yt_dlp

DOWNLOAD_DIR = "downloads"
os.makedirs(DOWNLOAD_DIR, exist_ok=True)

FFMPEG_EXE = imageio_ffmpeg.get_ffmpeg_exe()
FFMPEG_DIR = os.path.dirname(FFMPEG_EXE)


def download_youtube_audio(url: str) -> str:
    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(DOWNLOAD_DIR, "%(title)s.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "ffmpeg_location": FFMPEG_EXE,
        "quiet": False,
        # ✅ 403 fix — browser jaisa request bhejo
        "http_headers": {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
            "Accept-Language": "en-US,en;q=0.9",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Referer": "https://www.youtube.com/",
        },
        # ✅ Age-restricted videos ke liye
        "extractor_args": {
            "youtube": {
                "player_client": ["web", "android"],
            }
        },
        # ✅ Retry logic
        "retries": 5,
        "fragment_retries": 5,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.extract_info(url, download=True)

    wav_files = glob.glob(os.path.join(DOWNLOAD_DIR, "*.wav"))
    if not wav_files:
        raise FileNotFoundError("WAV file nahi mili!")

    latest = max(wav_files, key=os.path.getctime)
    print(f"✅ Download complete: {latest}")
    return latest


def convert_to_wav(input_path: str) -> str:
    output_path = os.path.splitext(input_path)[0] + "_converted.wav"

    subprocess.run(
        [FFMPEG_EXE, "-i", input_path,
         "-ac", "1", "-ar", "16000", "-y", output_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    print(f"✅ Converted: {output_path}")
    return output_path


def chunk_audio(wav_path: str, chunk_minutes: int = 10) -> list:

    result = subprocess.run(
        [FFMPEG_EXE, "-i", wav_path],
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )

    stderr = result.stderr.decode()
    duration = None

    for line in stderr.split("\n"):
        if "Duration" in line:
            time_str = line.strip().split("Duration:")[1].split(",")[0].strip()
            h, m, s = time_str.split(":")
            duration = int(h) * 3600 + int(m) * 60 + float(s)
            break

    if duration is None:
        raise RuntimeError(f"❌ Duration nahi mila! File check karo: {wav_path}")

    chunk_seconds = chunk_minutes * 60
    total_chunks = int(duration / chunk_seconds) + 1

    print(f"📊 Duration: {duration:.1f}s → {total_chunks} chunks banenge")

    chunks = []

    for i in range(total_chunks):
        start = i * chunk_seconds
        chunk_path = f"{wav_path}_chunk_{i}.wav"

        subprocess.run(
            [
                FFMPEG_EXE,
                "-ss", str(start),
                "-i", wav_path,
                "-t", str(chunk_seconds),
                "-ac", "1",
                "-ar", "16000",
                "-y",
                chunk_path
            ],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        if os.path.exists(chunk_path) and os.path.getsize(chunk_path) > 1000:
            chunks.append(chunk_path)
            print(f"  ✅ Chunk {i+1}/{total_chunks} ready")
        else:
            if os.path.exists(chunk_path):
                os.remove(chunk_path)

    print(f"✅ Total chunks bane: {len(chunks)}")
    return chunks


def process_input(source: str) -> list:
    if source.startswith("http://") or source.startswith("https://"):
        print("Detected YouTube URL. Downloading audio...")
        wav_path = download_youtube_audio(source)
    else:
        print("Detected local file. Converting to WAV...")
        wav_path = convert_to_wav(source)

    print("Chunking audio...")
    chunks = chunk_audio(wav_path)
    print(f"Audio ready — {len(chunks)} chunk(s) created.")
    return chunks
