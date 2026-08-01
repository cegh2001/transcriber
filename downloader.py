import os
import subprocess
import tempfile
import uuid
import yt_dlp
import imageio_ffmpeg


def get_ffmpeg_path() -> str:
    """Obtiene la ruta del ejecutable de FFmpeg mediante imageio-ffmpeg."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def extract_audio(url: str, output_dir: str = None) -> str:
    """
    Descarga el video/audio de un enlace (YouTube, Instagram, TikTok) con yt-dlp
    y convierte el audio a formato WAV (16kHz mono) usando FFmpeg directamente.
    """
    if not output_dir:
        output_dir = tempfile.gettempdir()

    ffmpeg_exe = get_ffmpeg_path()
    session_id = uuid.uuid4().hex[:8]
    raw_template = os.path.join(output_dir, f"media_{session_id}_%(id)s.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best[vcodec^=h264]/best[acodec!=none]/best',
        'outtmpl': raw_template,
        'quiet': True,
        'no_warnings': True,
        'overwrites': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        raw_filepath = ydl.prepare_filename(info)

    base, _ = os.path.splitext(raw_filepath)
    wav_path = base + "_16k.wav"

    # Convertir a 16kHz WAV mono usando FFmpeg directamente
    cmd = [
        ffmpeg_exe,
        "-y",
        "-i", raw_filepath,
        "-vn",
        "-ar", "16000",
        "-ac", "1",
        "-c:a", "pcm_s16le",
        wav_path
    ]

    subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, check=True)

    # Eliminar archivo multimedia crudo descargado
    if os.path.exists(raw_filepath) and raw_filepath != wav_path:
        try:
            os.remove(raw_filepath)
        except Exception:
            pass

    return wav_path
