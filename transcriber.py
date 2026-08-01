import os
import sys
import click
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

load_dotenv()

from downloader import extract_audio
from cloud_engine import transcribe_cloud
from local_engine import transcribe_local

console = Console()


def save_results(result: dict, output_dir: str, base_filename: str):
    """Guarda la transcripción en archivos .txt y .srt."""
    os.makedirs(output_dir, exist_ok=True)

    txt_path = os.path.join(output_dir, f"{base_filename}.txt")
    srt_path = os.path.join(output_dir, f"{base_filename}.srt")

    with open(txt_path, "w", encoding="utf-8") as f:
        f.write(result.get("text", ""))

    if result.get("srt"):
        with open(srt_path, "w", encoding="utf-8") as f:
            f.write(result.get("srt", ""))

    return txt_path, srt_path


@click.command()
@click.option("--url", "-u", type=str, help="URL del video de YouTube, Instagram o TikTok.")
@click.option(
    "--mode",
    "-m",
    type=click.Choice(["cloud", "local"], case_sensitive=False),
    help="Modo de transcripción: 'cloud' (Gemini API) o 'local' (faster-whisper).",
)
@click.option(
    "--model",
    "-md",
    type=str,
    default=None,
    help="Modelo a usar (ej. 'gemini-3.6-flash' para cloud, o 'large-v3'/'medium'/'turbo' para local).",
)
@click.option("--output-dir", "-o", type=str, default="outputs", help="Directorio para guardar los resultados.")
def main(url: str, mode: str, model: str, output_dir: str):
    """
    Transcriptor de alta fidelidad para videos de YouTube, Instagram y TikTok.
    Soporta modo Cloud (Gemini Free Tier) y modo Local (Faster-Whisper).
    """
    console.print(
        Panel.fit(
            "[bold cyan]Transcriptor de Video (YouTube, Instagram, TikTok)[/bold cyan]\n"
            "[dim]Soporte Dual-Modo: Cloud (Gemini) / Local (Faster-Whisper)[/dim]",
            border_style="cyan",
        )
    )

    # Modo interactivo si faltan argumentos
    if not url:
        url = Prompt.ask("[bold yellow]Ingresá la URL del video[/bold yellow]")

    if not mode:
        mode = Prompt.ask(
            "[bold yellow]Seleccioná el modo de transcripción[/bold yellow]",
            choices=["cloud", "local"],
            default="cloud",
        )

    # Configuración por defecto del modelo según el modo
    if not model:
        if mode.lower() == "cloud":
            model = "gemini-3.6-flash"
        else:
            model = "large-v3"

    # Paso 1: Descargar audio
    with console.status("[bold green]Descargando audio del video con yt-dlp...[/bold green]", spinner="dots"):
        try:
            audio_path = extract_audio(url)
            console.print(f"[bold green][OK] Audio descargado correctamente:[/bold green] {audio_path}")
        except Exception as e:
            console.print(f"[bold red][ERROR] Error al descargar el audio:[/bold red] {e}")
            sys.exit(1)

    # Paso 2: Transcribir
    result = {}
    with console.status(
        f"[bold blue]Procesando transcripción en modo {mode.upper()} con {model}...[/bold blue]",
        spinner="earth",
    ):
        try:
            if mode.lower() == "cloud":
                result = transcribe_cloud(audio_path, model_name=model)
            else:
                result = transcribe_local(audio_path, model_size=model)
            console.print(f"[bold green][OK] Transcripción completada exitosamente con {result.get('engine')}![/bold green]")
        except Exception as e:
            console.print(f"[bold red][ERROR] Error durante la transcripción:[/bold red] {e}")
            sys.exit(1)
        finally:
            # Limpiar archivo de audio temporal
            if os.path.exists(audio_path):
                try:
                    os.remove(audio_path)
                except Exception:
                    pass

    # Paso 3: Guardar resultados
    base_name = "transcription"
    txt_path, srt_path = save_results(result, output_dir, base_name)

    # Mostrar tabla resumen
    table = Table(title="Archivos Generados")
    table.add_column("Tipo", style="cyan")
    table.add_column("Ruta del Archivo", style="magenta")

    table.add_row("Texto Plano (.txt)", txt_path)
    if result.get("srt"):
        table.add_row("Subtítulos SRT (.srt)", srt_path)

    console.print(table)

    # Vista previa del texto
    console.print("\n[bold yellow]Vista Previa de la Transcripción:[/bold yellow]")
    preview_text = result.get("text", "")[:600]
    if len(result.get("text", "")) > 600:
        preview_text += "..."
    console.print(Panel(preview_text, border_style="dim"))


if __name__ == "__main__":
    main()
