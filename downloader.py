import os
import tempfile
import yt_dlp
import imageio_ffmpeg


def get_ffmpeg_path() -> str:
    """Obtiene la ruta del ejecutable de FFmpeg mediante imageio-ffmpeg si no está en PATH."""
    try:
        return imageio_ffmpeg.get_ffmpeg_exe()
    except Exception:
        return "ffmpeg"


def extract_audio(url: str, output_dir: str = None) -> str:
    """
    Descarga el audio de un video de YouTube, Instagram o TikTok usando yt-dlp.
    Retorna la ruta absoluta del archivo WAV generado.
    """
    if not output_dir:
        output_dir = tempfile.gettempdir()

    ffmpeg_exe = get_ffmpeg_path()
    ffmpeg_dir = os.path.dirname(ffmpeg_exe) if os.path.isabs(ffmpeg_exe) else None

    out_template = os.path.join(output_dir, "extracted_audio_%(id)s.%(ext)s")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': out_template,
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'wav',
            'preferredquality': '192',
        }],
        'ffmpeg_location': ffmpeg_dir or ffmpeg_exe,
        'quiet': True,
        'no_warnings': True,
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        info = ydl.extract_info(url, download=True)
        filename = ydl.prepare_filename(info)
        base, _ = os.path.splitext(filename)
        wav_path = base + ".wav"

        if os.path.exists(wav_path):
            return wav_path
        elif os.path.exists(filename):
            return filename
        else:
            raise FileNotFoundError("No se pudo encontrar el archivo de audio extraído.")
