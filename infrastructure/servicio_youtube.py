from __future__ import annotations
import os
import re
import subprocess
import json
import threading
import sys
from typing import Callable
from domain.entities import FormatoDescarga
from interfaces.repositories import ServicioDescarga


def _encontrar_ytdlp() -> str:
    candidatos = [
        os.path.join(os.path.dirname(sys.executable), "Scripts", "yt-dlp.exe"),
        os.path.join(sys.exec_prefix, "Scripts", "yt-dlp.exe"),
        os.path.join(os.environ.get("APPDATA", ""), "Python", "Python313", "Scripts", "yt-dlp.exe"),
        "yt-dlp",
        "yt-dlp.exe",
    ]
    for c in candidatos:
        if c and (os.path.isfile(c) or c in ("yt-dlp", "yt-dlp.exe")):
            return c
    return "yt-dlp"


def _encontrar_ffmpeg() -> str | None:
    candidatos = [
        os.path.join(os.path.expanduser("~"), ".ffmpeg", "ffmpeg.exe"),
        "ffmpeg.exe",
        "ffmpeg",
    ]
    for c in candidatos:
        if c and os.path.isfile(c):
            return os.path.dirname(os.path.abspath(c))
    return None


_YTDLP = _encontrar_ytdlp()
_FFMPEG_DIR = _encontrar_ffmpeg()


class ServicioYouTubeDL(ServicioDescarga):

    _TIMEOUT_SECS = 120

    def obtener_titulo(self, url: str) -> str:
        try:
            resultado = subprocess.run(
                [_YTDLP, "--dump-json", "--no-warnings", "--ignore-errors", url.strip()],
                capture_output=True,
                timeout=self._TIMEOUT_SECS,
            )
            salida = (resultado.stdout or resultado.stderr or b"").decode("utf-8", errors="replace").strip()
            for linea in salida.split("\n"):
                linea = linea.strip()
                if linea.startswith("{"):
                    datos = json.loads(linea)
                    titulo = datos.get("title", "Cancion desconocida")
                    return self._limpiar_titulo(titulo)
        except Exception:
            pass
        return "Cancion desconocida"

    def descargar(
        self,
        url: str,
        ruta_destino: str,
        formato: FormatoDescarga,
        progreso: Callable[[float], None],
    ) -> str:
        os.makedirs(ruta_destino, exist_ok=True)

        if formato == FormatoDescarga.MP4:
            return self._descargar_video(url, ruta_destino, progreso)
        return self._descargar_audio(url, ruta_destino, progreso)

    def _descargar_audio(
        self, url: str, ruta_destino: str, progreso: Callable[[float], None]
    ) -> str:
        cmd = [
            _YTDLP,
            "--extract-audio",
            "--audio-format", "mp3",
            "--audio-quality", "0",
            "--output", os.path.join(ruta_destino, "%(title)s.%(ext)s"),
            "--no-warnings",
            "--newline",
            "--no-playlist",
            url.strip(),
        ]
        if _FFMPEG_DIR:
            cmd.insert(1, _FFMPEG_DIR)
            cmd.insert(1, "--ffmpeg-location")
        return self._ejecutar_descarga(cmd, progreso)

    def _descargar_video(
        self, url: str, ruta_destino: str, progreso: Callable[[float], None]
    ) -> str:
        return self._ejecutar_descarga(
            [
                _YTDLP,
                "--format", "best[ext=mp4]",
                "--output", os.path.join(ruta_destino, "%(title)s.%(ext)s"),
                "--no-warnings",
                "--newline",
                "--no-playlist",
                url.strip(),
            ],
            progreso,
        )

    def _ejecutar_descarga(
        self, comando: list[str], progreso: Callable[[float], None]
    ) -> str:
        evento_fin = threading.Event()

        def _monitorear_progreso(proc: subprocess.Popen):
            patron = r"(\d+\.?\d*)%"
            try:
                for linea_bytes in proc.stdout or []:
                    linea = linea_bytes.decode("utf-8", errors="replace")
                    m = re.search(patron, linea)
                    if m:
                        progreso(float(m.group(1)))
            except Exception:
                pass
            finally:
                evento_fin.set()

        proceso = subprocess.Popen(
            comando,
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            encoding=None,
        )

        hilo = threading.Thread(target=_monitorear_progreso, args=(proceso,), daemon=True)
        hilo.start()

        proceso.wait()
        evento_fin.wait(timeout=10)
        progreso(100.0)

        return os.path.dirname(comando[comando.index("--output") + 1]) if "--output" in comando else ""

    @staticmethod
    def _limpiar_titulo(titulo: str) -> str:
        invalidos = r'[<>:"/\\|?*]'
        titulo = re.sub(invalidos, "", titulo)
        return titulo.strip()[:120] or "Cancion"
