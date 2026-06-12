from __future__ import annotations
from dataclasses import dataclass, field
from enum import Enum, auto
import uuid


class EstadoDescarga(Enum):
    PENDIENTE = auto()
    DESCARGANDO = auto()
    COMPLETADA = auto()
    ERROR = auto()


class FormatoDescarga(Enum):
    MP3 = "mp3"
    MP4 = "mp4"


@dataclass
class Cancion:
    url: str
    titulo: str = ""
    id: str = field(default_factory=lambda: str(uuid.uuid4())[:8])
    estado: EstadoDescarga = EstadoDescarga.PENDIENTE
    numero: int = 0
    formato: FormatoDescarga = FormatoDescarga.MP3

    def marcar_descargando(self) -> None:
        self.estado = EstadoDescarga.DESCARGANDO

    def marcar_completada(self) -> None:
        self.estado = EstadoDescarga.COMPLETADA

    def marcar_error(self) -> None:
        self.estado = EstadoDescarga.ERROR

    @property
    def esta_descargada(self) -> bool:
        return self.estado == EstadoDescarga.COMPLETADA

    @property
    def esta_pendiente(self) -> bool:
        return self.estado == EstadoDescarga.PENDIENTE

    @property
    def etiqueta_formato(self) -> str:
        return "MP3" if self.formato == FormatoDescarga.MP3 else "MP4"
