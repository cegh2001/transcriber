import os
import math
from typing import Dict, Any


def format_timestamp(seconds: float) -> str:
    """Convierte segundos a formato SRT HH:MM:SS,mmm."""
    hours = math.floor(seconds / 3600)
    seconds %= 3600
    minutes = math.floor(seconds / 60)
    seconds %= 60
    milliseconds = math.floor((seconds - math.floor(seconds)) * 1000)
    seconds = math.floor(seconds)
    return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"


def transcribe_local(
    audio_path: str,
    model_size: str = "large-v3",
    device: str = "auto",
    compute_type: str = "default"
) -> Dict[str, Any]:
    """
    Transcribe un archivo de audio de forma local usando la librería faster-whisper.
    """
    try:
        from faster_whisper import WhisperModel
    except ImportError:
        raise ImportError(
            "Librería faster-whisper no instalada. Instalala con 'pip install faster-whisper'."
        )

    # Determinar device
    if device == "auto":
        try:
            import torch
            device_choice = "cuda" if torch.cuda.is_available() else "cpu"
        except ImportError:
            device_choice = "cpu"
    else:
        device_choice = device

    if compute_type == "default":
        compute_choice = "float16" if device_choice == "cuda" else "int8"
    else:
        compute_choice = compute_type

    # Cargar modelo Whisper
    model = WhisperModel(model_size, device=device_choice, compute_type=compute_choice)

    # Ejecutar transcripción
    segments, info = model.transcribe(audio_path, beam_size=5, word_timestamps=True)

    text_segments = []
    srt_blocks = []
    counter = 1

    for segment in segments:
        text_segments.append(segment.text.strip())
        start_str = format_timestamp(segment.start)
        end_str = format_timestamp(segment.end)
        srt_blocks.append(f"{counter}\n{start_str} --> {end_str}\n{segment.text.strip()}\n")
        counter += 1

    full_text = " ".join(text_segments)
    full_srt = "\n".join(srt_blocks)

    return {
        "text": full_text,
        "srt": full_srt,
        "language": info.language,
        "language_probability": info.language_probability,
        "engine": f"Faster-Whisper ({model_size} en {device_choice.upper()})"
    }
