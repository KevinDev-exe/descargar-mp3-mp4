from __future__ import annotations
from typing import List, Callable
from domain.entities import Cancion, EstadoDescarga, FormatoDescarga
from interfaces.repositories import RepositorioCanciones, ServicioDescarga


class GestionarCanciones:

    def __init__(
        self,
        repositorio: RepositorioCanciones,
        servicio_descarga: ServicioDescarga,
        ruta_mp3: str,
        ruta_mp4: str,
    ):
        self._repo = repositorio
        self._servicio = servicio_descarga
        self._ruta_mp3 = ruta_mp3
        self._ruta_mp4 = ruta_mp4

    def obtener_lista(self) -> List[Cancion]:
        return self._repo.obtener_todas()

    def contar_pendientes(self) -> int:
        return sum(
            1 for c in self._repo.obtener_todas()
            if c.estado in (EstadoDescarga.PENDIENTE, EstadoDescarga.DESCARGANDO, EstadoDescarga.ERROR)
        )

    def contar_completadas(self) -> int:
        return sum(1 for c in self._repo.obtener_todas() if c.estado == EstadoDescarga.COMPLETADA)

    def agregar_cancion(self, url: str, formato: FormatoDescarga = FormatoDescarga.MP3) -> Cancion:
        titulo = self._servicio.obtener_titulo(url)
        cancion = Cancion(url=url, titulo=titulo, formato=formato)
        self._repo.agregar(cancion)
        self._repo.reordenar_numeros()
        return cancion

    def cambiar_formato(self, id_cancion: str, formato: FormatoDescarga) -> None:
        self._repo.actualizar_formato(id_cancion, formato)

    def eliminar_cancion(self, id_cancion: str) -> None:
        self._repo.eliminar(id_cancion)
        self._repo.reordenar_numeros()

    def descargar_todas(
        self,
        progreso_global: Callable[[int, int], None],
        progreso_individual: Callable[[str, float], None],
        cancion_completada: Callable[[str], None],
    ) -> None:
        canciones = self._repo.obtener_todas()
        pendientes = [
            c for c in canciones
            if c.estado in (EstadoDescarga.PENDIENTE, EstadoDescarga.ERROR)
        ]
        total = len(pendientes)
        completadas = 0

        for cancion in pendientes:
            self._repo.actualizar_estado(cancion.id, EstadoDescarga.DESCARGANDO)
            ruta = self._ruta_mp3 if cancion.formato == FormatoDescarga.MP3 else self._ruta_mp4
            try:
                self._servicio.descargar(
                    url=cancion.url,
                    ruta_destino=ruta,
                    formato=cancion.formato,
                    progreso=lambda p: progreso_individual(cancion.id, p),
                )
                self._repo.actualizar_estado(cancion.id, EstadoDescarga.COMPLETADA)
                completadas += 1
                cancion_completada(cancion.id)
            except Exception:
                self._repo.actualizar_estado(cancion.id, EstadoDescarga.ERROR)
                completadas += 1
            progreso_global(completadas, total)

    def es_url_valida(self, url: str) -> bool:
        import re
        patrones = [
            r'(https?://)?(www\.)?youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?youtu\.be/[\w-]+',
            r'(https?://)?(www\.)?youtube\.com/shorts/[\w-]+',
            r'(https?://)?music\.youtube\.com/watch\?v=[\w-]+',
            r'(https?://)?(www\.)?tiktok\.com/@[\w.-]+/video/[\d]+',
            r'(https?://)?vm\.tiktok\.com/[\w-]+',
            r'(https?://)?m\.tiktok\.com/v/[\d]+',
        ]
        return any(re.match(p, url.strip()) for p in patrones)
