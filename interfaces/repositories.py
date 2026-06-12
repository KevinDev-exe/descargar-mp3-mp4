from __future__ import annotations
from abc import ABC, abstractmethod
from typing import List, Optional, Callable
from domain.entities import Cancion, EstadoDescarga, FormatoDescarga


class RepositorioCanciones(ABC):

    @abstractmethod
    def agregar(self, cancion: Cancion) -> None:
        ...

    @abstractmethod
    def eliminar(self, id_cancion: str) -> None:
        ...

    @abstractmethod
    def obtener_todas(self) -> List[Cancion]:
        ...

    @abstractmethod
    def obtener_por_id(self, id_cancion: str) -> Optional[Cancion]:
        ...

    @abstractmethod
    def actualizar_estado(self, id_cancion: str, estado: EstadoDescarga) -> None:
        ...

    @abstractmethod
    def actualizar_titulo(self, id_cancion: str, titulo: str) -> None:
        ...

    @abstractmethod
    def actualizar_formato(self, id_cancion: str, formato: FormatoDescarga) -> None:
        ...

    @abstractmethod
    def reordenar_numeros(self) -> None:
        ...


class ServicioDescarga(ABC):

    @abstractmethod
    def obtener_titulo(self, url: str) -> str:
        ...

    @abstractmethod
    def descargar(
        self,
        url: str,
        ruta_destino: str,
        formato: FormatoDescarga,
        progreso: Callable[[float], None],
    ) -> str:
        ...
