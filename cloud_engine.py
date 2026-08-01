import os
import time
from typing import Dict, Any


def transcribe_cloud(audio_path: str, api_key: str = None, model_name: str = "gemini-2.5-flash") -> Dict[str, Any]:
    """
    Transcribe un archivo de audio utilizando la API de Google Gemini (Free Tier).
    Retorna un diccionario con el texto transcribido y formato SRT/VTT.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY. Definila como variable de entorno o pasala al comando."
        )

    # Importar google-genai
    try:
        from google import genai
        from google.genai import types
        client = genai.Client(api_key=key)
    except ImportError:
        raise ImportError(
            "Librería google-genai no encontrada. Instalala con 'pip install google-genai'."
        )

    # Subir archivo de audio a la API de Gemini
    audio_file = client.files.upload(file=audio_path)

    # Esperar si requiere procesamiento
    while audio_file.state.name == "PROCESSING":
        time.sleep(2)
        audio_file = client.files.get(name=audio_file.name)

    if audio_file.state.name == "FAILED":
        raise RuntimeError(f"Error procesando el archivo de audio en Gemini: {audio_file.error.message}")

    prompt = """Procesa el archivo de audio adjunto y genera una transcripción con la MÁXIMA FIDELIDAD posible.
Instrucciones:
1. Proporciona la transcripción textual limpia y exacta en el idioma original hablada.
2. Si hay múltiples hablantes, identifícalos adecuadamente (Hablante 1, Hablante 2, etc.).
3. Incluye signos de puntuación y capitalización adecuados.
4. Al final, incluye la versión formateada en SRT con marcas de tiempo [HH:MM:SS,mmm --> HH:MM:SS,mmm].

Estructura tu respuesta exactamente así:
---TRANSCRIPCION_TEXTO---
[Aquí el texto plano completo]

---FORMATO_SRT---
[Aquí el bloque formateado en SRT]
"""

    response = client.models.generate_content(
        model=model_name,
        contents=[audio_file, prompt]
    )

    # Limpiar archivo en servidores de Gemini despues del uso
    try:
        client.files.delete(name=audio_file.name)
    except Exception:
        pass

    full_output = response.text or ""
    
    # Parsear respuesta
    text_part = full_output
    srt_part = ""

    if "---TRANSCRIPCION_TEXTO---" in full_output and "---FORMATO_SRT---" in full_output:
        parts = full_output.split("---FORMATO_SRT---")
        text_part = parts[0].replace("---TRANSCRIPCION_TEXTO---", "").strip()
        srt_part = parts[1].strip()

    return {
        "text": text_part,
        "srt": srt_part,
        "raw_response": full_output,
        "engine": f"Google Gemini ({model_name})"
    }
