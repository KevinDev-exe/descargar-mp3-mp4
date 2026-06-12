"""
Melodia — MP3 & MP4 Downloader

Sistema de escritorio para descargar musica y videos desde YouTube.
Arquitectura limpia (Clean Architecture) con interfaz grafica moderna.

Autor: Kevin Agreda
"""

from __future__ import annotations
import os

from infrastructure.repositorio_memoria import RepositorioEnMemoria
from infrastructure.servicio_youtube import ServicioYouTubeDL
from use_cases.gestor_canciones import GestionarCanciones
from presentation.app import VentanaPrincipal


def _obtener_rutas_descargas() -> tuple[str, str]:
    """
    Crea la estructura de carpetas:
      ~/Downloads/MP3 & MP4 Downloader/
        +-- music mp3/
        +-- videos mp4/

    Las carpetas se crean solo si es necesario.
    Retorna (ruta_mp3, ruta_mp4).
    """
    base = os.path.join(os.path.expanduser("~"), "Downloads", "MP3 & MP4 Downloader")
    ruta_mp3 = os.path.join(base, "music mp3")
    ruta_mp4 = os.path.join(base, "videos mp4")
    # No creamos las carpetas aqui; se crean al descargar
    return ruta_mp3, ruta_mp4


def main():
    repositorio = RepositorioEnMemoria()
    servicio_descarga = ServicioYouTubeDL()
    ruta_mp3, ruta_mp4 = _obtener_rutas_descargas()

    caso_uso = GestionarCanciones(
        repositorio=repositorio,
        servicio_descarga=servicio_descarga,
        ruta_mp3=ruta_mp3,
        ruta_mp4=ruta_mp4,
    )

    app = VentanaPrincipal(caso_uso=caso_uso)
    app.protocol("WM_DELETE_WINDOW", app.cerrar)
    app.mainloop()


if __name__ == "__main__":
    main()
