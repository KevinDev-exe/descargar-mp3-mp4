from __future__ import annotations
from typing import List, Optional
from domain.entities import Cancion, EstadoDescarga, FormatoDescarga
from interfaces.repositories import RepositorioCanciones


class RepositorioEnMemoria(RepositorioCanciones):

    def __init__(self):
        self._canciones: List[Cancion] = []

    def agregar(self, cancion: Cancion) -> None:
        self._canciones.append(cancion)

    def eliminar(self, id_cancion: str) -> None:
        self._canciones = [c for c in self._canciones if c.id != id_cancion]

    def obtener_todas(self) -> List[Cancion]:
        return list(self._canciones)

    def obtener_por_id(self, id_cancion: str) -> Optional[Cancion]:
        for c in self._canciones:
            if c.id == id_cancion:
                return c
        return None

    def actualizar_estado(self, id_cancion: str, estado: EstadoDescarga) -> None:
        cancion = self.obtener_por_id(id_cancion)
        if cancion:
            cancion.estado = estado

    def actualizar_titulo(self, id_cancion: str, titulo: str) -> None:
        cancion = self.obtener_por_id(id_cancion)
        if cancion:
            cancion.titulo = titulo

    def actualizar_formato(self, id_cancion: str, formato: FormatoDescarga) -> None:
        cancion = self.obtener_por_id(id_cancion)
        if cancion:
            cancion.formato = formato

    def reordenar_numeros(self) -> None:
        for idx, cancion in enumerate(self._canciones, start=1):
            cancion.numero = idx
