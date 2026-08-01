import os
import time
from typing import Dict, Any, List


def transcribe_cloud(
    audio_path: str,
    api_key: str = None,
    model_name: str = "gemini-3.6-flash",
    fallback_models: List[str] = None
) -> Dict[str, Any]:
    """
    Transcribe un archivo de audio utilizando la API de Google Gemini.
    Intenta usar model_name (gemini-3.6-flash por defecto) y realiza fallback a modelos anteriores (gemini-3.5-flash) si falla.
    """
    key = api_key or os.getenv("GEMINI_API_KEY")
    if not key:
        raise ValueError(
            "No se encontró GEMINI_API_KEY. Definila en el archivo .env o como variable de entorno."
        )

    try:
        from google import genai
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
1. Proporciona la transcripción textual limpia y exacta en el idioma original hablado.
2. Si hay múltiples hablantes, identifícalos adecuadamente (Hablante 1, Hablante 2, etc.).
3. Incluye signos de puntuación y capitalización adecuados.
4. Al final, incluye la versión formateada en SRT con marcas de tiempo [HH:MM:SS,mmm --> HH:MM:SS,mmm].

Estructura tu respuesta exactamente así:
---TRANSCRIPCION_TEXTO---
[Aquí el texto plano completo]

---FORMATO_SRT---
[Aquí el bloque formateado en SRT]
"""

    models_to_try = [model_name]
    if fallback_models:
        for fb in fallback_models:
            if fb not in models_to_try:
                models_to_try.append(fb)
    else:
        default_fallbacks = ["gemini-3.5-flash", "gemini-2.5-flash"]
        for fb in default_fallbacks:
            if fb not in models_to_try:
                models_to_try.append(fb)

    last_error = None
    response = None
    successful_model = None

    for m in models_to_try:
        try:
            response = client.models.generate_content(
                model=m,
                contents=[audio_file, prompt]
            )
            successful_model = m
            break
        except Exception as e:
            last_error = e
            continue

    # Limpiar archivo en servidores de Gemini
    try:
        client.files.delete(name=audio_file.name)
    except Exception:
        pass

    if not response or not response.text:
        raise RuntimeError(f"Todos los modelos fallaron. Último error: {last_error}")

    full_output = response.text or ""
    
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
        "engine": f"Google Gemini ({successful_model})"
    }
