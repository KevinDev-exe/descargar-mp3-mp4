from __future__ import annotations
import tkinter as tk
from tkinter import messagebox
from threading import Thread
import customtkinter as ctk

from domain.entities import Cancion, EstadoDescarga, FormatoDescarga
from use_cases.gestor_canciones import GestionarCanciones


ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

COLOR_FONDO = "#1a1a2e"
COLOR_ACENTO = "#0f3460"
COLOR_VERDE = "#2ecc71"
COLOR_ROJO = "#e74c3c"
COLOR_AMARILLO = "#f39c12"
COLOR_TEXTO = "#e0e0e0"
COLOR_TARJETA = "#1e2a45"
COLOR_MP3 = "#3498db"
COLOR_MP4 = "#e67e22"
FUENTE_TITULO = ("Segoe UI", 22, "bold")
FUENTE_SUBTITULO = ("Segoe UI", 12)
FUENTE_CANCION = ("Segoe UI", 13)
FUENTE_NUMERO = ("Segoe UI", 14, "bold")
FUENTE_PEQUEÑA = ("Segoe UI", 10)
FUENTE_FORMATO = ("Segoe UI", 10, "bold")


class ModalCarga(ctk.CTkToplevel):
    def __init__(self, padre: ctk.CTk):
        super().__init__(padre)
        self.overrideredirect(True)
        self.configure(fg_color=COLOR_TARJETA)
        self.attributes("-topmost", True)

        ancho, alto = 360, 100
        px = padre.winfo_x() + (padre.winfo_width() // 2) - (ancho // 2)
        py = padre.winfo_y() + (padre.winfo_height() // 2) - (alto // 2)
        self.geometry(f"{ancho}x{alto}+{px}+{py}")

        self._label = ctk.CTkLabel(
            self,
            text="",
            font=("Segoe UI", 14),
            text_color=COLOR_TEXTO,
            wraplength=320,
        )
        self._label.pack(expand=True, fill="both", padx=20, pady=20)

    def mostrar_cargando(self, url: str):
        self._label.configure(text="Agregando a la lista de descarga...")
        self.deiconify()
        self.lift()

    def mostrar_exito(self, titulo: str):
        self._label.configure(
            text=f"Agregado con exito!\n{titulo}",
            text_color=COLOR_VERDE,
        )
        self.after(1800, self._cerrar)

    def mostrar_error(self):
        self._label.configure(
            text="Error al obtener la cancion",
            text_color=COLOR_ROJO,
        )
        self.after(2000, self._cerrar)

    def _cerrar(self):
        self.withdraw()


class VentanaPrincipal(ctk.CTk):

    def __init__(self, caso_uso: GestionarCanciones):
        super().__init__()
        self._caso_uso = caso_uso
        self._frames_cancion: dict[str, dict] = {}
        self._monitoreando = True
        self._ultimo_portapapeles = ""

        self._configurar_ventana()
        self._crear_widgets()
        self._modal = ModalCarga(self)
        self._modal.withdraw()
        self._iniciar_monitoreo_portapapeles()
        self._refrescar_lista()

    # ─── Configuración inicial ─────────────────────────────────────

    def _configurar_ventana(self):
        self.title("Melodia — MP3 & MP4 Downloader")
        self.geometry("780x680")
        self.minsize(640, 520)
        self.configure(fg_color=COLOR_FONDO)

    # ─── Creación de widgets ───────────────────────────────────────

    def _crear_widgets(self):
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(2, weight=1)

        encabezado = ctk.CTkFrame(self, fg_color="transparent")
        encabezado.grid(row=0, column=0, sticky="ew", padx=30, pady=(25, 5))
        encabezado.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            encabezado,
            text="Melodia",
            font=FUENTE_TITULO,
            text_color=COLOR_TEXTO,
        ).grid(row=0, column=0, sticky="w")

        ctk.CTkLabel(
            encabezado,
            text="Descarga musica y videos desde YouTube y TikTok.",
            font=FUENTE_SUBTITULO,
            text_color="#8899aa",
        ).grid(row=1, column=0, sticky="w", pady=(0, 5))

        self._crear_barra_entrada()
        self._crear_lista_canciones()
        self._crear_barra_progreso()
        self._crear_pie_pagina()

    def _crear_barra_entrada(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=1, column=0, sticky="ew", padx=30, pady=(5, 10))
        frame.grid_columnconfigure(0, weight=1)

        self._entry_url = ctk.CTkEntry(
            frame,
            placeholder_text="Pega el enlace de YouTube o TikTok aqui...",
            font=("Segoe UI", 13),
            height=42,
            border_width=2,
            corner_radius=12,
            fg_color=COLOR_TARJETA,
            border_color=COLOR_ACENTO,
        )
        self._entry_url.grid(row=0, column=0, sticky="ew", padx=(0, 10))

        self._btn_agregar = ctk.CTkButton(
            frame,
            text="+ Agregar",
            font=("Segoe UI", 13, "bold"),
            height=42,
            corner_radius=12,
            fg_color=COLOR_ACENTO,
            hover_color="#1a4a7a",
            command=self._agregar_desde_entry,
        )
        self._btn_agregar.grid(row=0, column=1)

        self._entry_url.bind("<Return>", lambda e: self._agregar_desde_entry())

    def _crear_lista_canciones(self):
        self._lista_container = ctk.CTkScrollableFrame(
            self,
            fg_color="transparent",
            corner_radius=12,
        )
        self._lista_container.grid(row=2, column=0, sticky="nsew", padx=30, pady=5)
        self._lista_container.grid_columnconfigure(0, weight=1)

    def _crear_barra_progreso(self):
        frame = ctk.CTkFrame(self, fg_color="transparent")
        frame.grid(row=3, column=0, sticky="ew", padx=30, pady=(10, 5))
        frame.grid_columnconfigure(1, weight=1)

        self._progreso_bar = ctk.CTkProgressBar(
            frame,
            height=14,
            corner_radius=7,
            fg_color=COLOR_TARJETA,
            progress_color=COLOR_VERDE,
        )
        self._progreso_bar.grid(row=0, column=0, columnspan=3, sticky="ew", pady=(0, 8))
        self._progreso_bar.set(0.0)

        self._label_progreso = ctk.CTkLabel(
            frame,
            text="0/0",
            font=FUENTE_NUMERO,
            text_color=COLOR_TEXTO,
        )
        self._label_progreso.grid(row=1, column=0, sticky="w")

        self._btn_descargar = ctk.CTkButton(
            frame,
            text="Descargar todo",
            font=("Segoe UI", 13, "bold"),
            height=40,
            corner_radius=12,
            fg_color=COLOR_VERDE,
            hover_color="#27ae60",
            command=self._iniciar_descarga,
        )
        self._btn_descargar.grid(row=1, column=1, padx=(0, 8))

        self._label_pendientes = ctk.CTkLabel(
            frame,
            text="",
            font=FUENTE_PEQUEÑA,
            text_color="#8899aa",
        )
        self._label_pendientes.grid(row=1, column=3, sticky="e")

    def _crear_pie_pagina(self):
        pie = ctk.CTkFrame(self, fg_color="transparent", height=30)
        pie.grid(row=4, column=0, sticky="ew", padx=30, pady=(0, 10))
        pie.grid_columnconfigure(0, weight=1)

        ctk.CTkLabel(
            pie,
            text="Hecho por Kevin Agreda  |  MP3 & MP4 Downloader",
            font=FUENTE_PEQUEÑA,
            text_color="#556677",
        ).grid(row=0, column=0)

    # ─── Lógica de la lista de canciones ──────────────────────────

    def _refrescar_lista(self):
        for info in self._frames_cancion.values():
            info["frame"].destroy()
        self._frames_cancion.clear()

        canciones = self._caso_uso.obtener_lista()
        for cancion in canciones:
            self._crear_fila_cancion(cancion)

        self._actualizar_estadisticas()

    def _crear_fila_cancion(self, cancion: Cancion):
        frame = ctk.CTkFrame(
            self._lista_container,
            fg_color=COLOR_TARJETA,
            corner_radius=10,
            height=48,
        )
        frame.grid(sticky="ew", pady=3)
        frame.grid_columnconfigure(2, weight=1)
        frame.grid_propagate(False)

        es_descargada = cancion.esta_descargada

        lbl_num = ctk.CTkLabel(
            frame,
            text=f"{cancion.numero}.",
            font=FUENTE_NUMERO,
            text_color=COLOR_VERDE if es_descargada else COLOR_ACENTO,
            width=30,
        )
        lbl_num.grid(row=0, column=0, padx=(12, 5), pady=8)

        icono = self._icono_estado(cancion.estado)
        color = self._color_estado(cancion.estado)
        ctk.CTkLabel(
            frame,
            text=icono,
            font=("Segoe UI", 16),
            text_color=color,
        ).grid(row=0, column=1, padx=(0, 5), pady=8, sticky="w")

        ctk.CTkLabel(
            frame,
            text=cancion.titulo or "Cargando titulo...",
            font=FUENTE_CANCION,
            text_color=COLOR_VERDE if es_descargada else COLOR_TEXTO,
            anchor="w",
        ).grid(row=0, column=2, padx=5, pady=8, sticky="ew")

        if es_descargada:
            color_fmt = COLOR_MP3 if cancion.formato == FormatoDescarga.MP3 else COLOR_MP4
            ctk.CTkLabel(
                frame,
                text=f" Descargado [{cancion.etiqueta_formato}] ",
                font=("Segoe UI", 11, "bold"),
                text_color=color_fmt,
                corner_radius=4,
            ).grid(row=0, column=3, padx=5, pady=8)
        else:
            es_mp3 = cancion.formato == FormatoDescarga.MP3
            color_btn = COLOR_MP3 if es_mp3 else COLOR_MP4
            texto_btn = "MP3" if es_mp3 else "MP4"
            hover = "#2980b9" if es_mp3 else "#d35400"

            btn_fmt = ctk.CTkButton(
                frame,
                text=texto_btn,
                font=FUENTE_FORMATO,
                width=48,
                height=28,
                corner_radius=6,
                fg_color=color_btn,
                hover_color=hover,
                command=lambda c=cancion: self._alternar_formato_cancion(c.id),
            )
            btn_fmt.grid(row=0, column=3, padx=5, pady=8)

            ctk.CTkButton(
                frame,
                text="X",
                font=("Segoe UI", 12, "bold"),
                width=28,
                height=28,
                corner_radius=6,
                fg_color="transparent",
                hover_color="#4a1a1a",
                border_width=1,
                border_color="#553333",
                command=lambda c=cancion: self._eliminar_cancion(c.id),
            ).grid(row=0, column=4, padx=(2, 10), pady=8)

        self._frames_cancion[cancion.id] = {"frame": frame}

    def _actualizar_estadisticas(self):
        total = self._caso_uso.contar_pendientes() + self._caso_uso.contar_completadas()
        pendientes = self._caso_uso.contar_pendientes()
        completadas = self._caso_uso.contar_completadas()

        if total == 0:
            self._progreso_bar.set(0.0)
            self._label_progreso.configure(text="0/0")
            self._btn_descargar.configure(state="disabled", fg_color="#444444")
            self._label_pendientes.configure(text="")
        else:
            pct = completadas / total if total > 0 else 0.0
            self._progreso_bar.set(pct)
            self._label_progreso.configure(text=f"{completadas}/{total}")
            if pendientes > 0:
                self._btn_descargar.configure(
                    text=f"Descargar todo ({pendientes} pendiente{'s' if pendientes != 1 else ''})",
                    state="normal",
                    fg_color=COLOR_VERDE,
                )
            else:
                self._btn_descargar.configure(text="Todo descargado", state="disabled", fg_color="#444444")

    # ─── Acciones del usuario ─────────────────────────────────────

    def _alternar_formato_cancion(self, id_cancion: str):
        canciones = self._caso_uso.obtener_lista()
        c = next((c for c in canciones if c.id == id_cancion), None)
        if not c:
            return
        nuevo = FormatoDescarga.MP4 if c.formato == FormatoDescarga.MP3 else FormatoDescarga.MP3
        self._caso_uso.cambiar_formato(id_cancion, nuevo)
        self._refrescar_lista()

    def _agregar_desde_entry(self):
        url = self._entry_url.get().strip()
        if not url:
            return
        if not self._caso_uso.es_url_valida(url):
            messagebox.showwarning(
                "Enlace invalido",
                "Eso no parece un enlace de YouTube o TikTok valido.",
            )
            return
        self._entry_url.delete(0, tk.END)
        Thread(target=self._agregar_con_modal, args=(url,), daemon=True).start()

    def _agregar_con_modal(self, url: str):
        self.after(0, lambda: self._modal.mostrar_cargando(url))
        try:
            cancion = self._caso_uso.agregar_cancion(url, formato=FormatoDescarga.MP3)
            self.after(0, lambda: self._modal.mostrar_exito(cancion.titulo))
            self.after(0, self._refrescar_lista)
        except Exception:
            self.after(0, self._modal.mostrar_error)

    def _eliminar_cancion(self, id_cancion: str):
        self._caso_uso.eliminar_cancion(id_cancion)
        self._refrescar_lista()

    # ─── Descarga ─────────────────────────────────────────────────

    def _iniciar_descarga(self):
        self._btn_descargar.configure(state="disabled", text="Descargando...")
        self._label_progreso.configure(text="Iniciando...")
        Thread(target=self._ejecutar_descarga, daemon=True).start()

    def _ejecutar_descarga(self):
        try:
            self._caso_uso.descargar_todas(
                progreso_global=self._actualizar_progreso_global,
                progreso_individual=self._actualizar_progreso_individual,
                cancion_completada=self._marcar_completada,
            )
        except Exception as e:
            self.after(0, lambda: messagebox.showerror("Error", f"Error en descarga:\n{e}"))
        finally:
            self.after(0, self._refrescar_lista)

    def _actualizar_progreso_global(self, completadas: int, total: int):
        def _actualizar():
            pct = completadas / total if total > 0 else 0.0
            self._progreso_bar.set(pct)
            self._label_progreso.configure(text=f"{completadas}/{total}")
        self.after(0, _actualizar)

    def _actualizar_progreso_individual(self, id_cancion: str, porcentaje: float):
        pass

    def _marcar_completada(self, id_cancion: str):
        self.after(0, self._refrescar_lista)

    # ─── Monitoreo del portapapeles ───────────────────────────────

    def _iniciar_monitoreo_portapapeles(self):
        try:
            self._ultimo_portapapeles = self.clipboard_get()
        except tk.TclError:
            self._ultimo_portapapeles = ""
        self._monitorear_portapapeles()

    def _monitorear_portapapeles(self):
        if not self._monitoreando:
            return
        try:
            contenido = self.clipboard_get()
            if contenido and contenido != self._ultimo_portapapeles:
                self._ultimo_portapapeles = contenido
                if self._caso_uso.es_url_valida(contenido):
                    self._entry_url.delete(0, tk.END)
                    Thread(target=self._agregar_con_modal, args=(contenido,), daemon=True).start()
        except tk.TclError:
            pass
        self.after(1500, self._monitorear_portapapeles)

    # ─── Utilidades ───────────────────────────────────────────────

    @staticmethod
    def _icono_estado(estado: EstadoDescarga) -> str:
        iconos = {
            EstadoDescarga.PENDIENTE: " ",
            EstadoDescarga.DESCARGANDO: " ",
            EstadoDescarga.COMPLETADA: " ",
            EstadoDescarga.ERROR: " ",
        }
        return iconos.get(estado, " ")

    @staticmethod
    def _color_estado(estado: EstadoDescarga) -> str:
        colores = {
            EstadoDescarga.PENDIENTE: "#667788",
            EstadoDescarga.DESCARGANDO: COLOR_AMARILLO,
            EstadoDescarga.COMPLETADA: COLOR_VERDE,
            EstadoDescarga.ERROR: COLOR_ROJO,
        }
        return colores.get(estado, "#667788")

    def cerrar(self):
        self._monitoreando = False
        self.destroy()
