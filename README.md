# Transcriptor de Videos (YouTube, Instagram, TikTok)

Herramienta de línea de comandos (CLI) para descargar y transcribir videos de **YouTube**, **Instagram** y **TikTok** con la máxima fidelidad posible.

## Características

- ☁️ **Modo Cloud (Google Gemini API - Free Tier)**: Transcripción rápida y precisa usando la API gratuita de Gemini en Google AI Studio.
- 💻 **Modo Local (Faster-Whisper)**: Transcripción offline ejecutada en tu GPU o CPU utilizando modelos Whisper Large-v3 optimizados con CTranslate2.
- 🎬 **Soporte Multi-plataforma**: Extrae audio automáticamente usando `yt-dlp`.
- 📝 **Formatos de Salida**: Exporta tanto en texto plano (`.txt`) como en subtítulos formateados con marcas de tiempo (`.srt`).

## Requisitos e Instalación

1. Clonar o descargar el repositorio.
2. Obtener Python 3.10 o superior.
3. Instalar las dependencias necesarias:

```bash
pip install -r requirements.txt
```

4. Para usar el **Modo Cloud**, obtené tu API Key gratuita en [Google AI Studio](https://aistudio.google.com/) y definila en tu entorno o en un archivo `.env`:

```env
GEMINI_API_KEY=tu_clave_api_aqui
```

## Uso de la Herramienta CLI

### 1. Modo Interactivo
Ejecutá el script directamente y seguí las instrucciones en pantalla:

```bash
python transcriber.py
```

### 2. Modo por Argumentos

**Ejemplo Cloud (Gemini Free Tier):**
```bash
python transcriber.py --url "https://www.youtube.com/watch?v=XXXXX" --mode cloud
```

**Ejemplo Local (Faster-Whisper):**
```bash
python transcriber.py --url "https://www.tiktok.com/@user/video/XXXXX" --mode local --model large-v3
```

## Estructura del Proyecto

- `transcriber.py`: Interfaz principal CLI basada en `click` y `rich`.
- `cloud_engine.py`: Motor de transcripción remota vía API de Gemini.
- `local_engine.py`: Motor de transcripción local offline vía `faster-whisper`.
- `downloader.py`: Módulo de descarga y extracción de audio con `yt-dlp` e `imageio-ffmpeg`.
