"""
views/detalle_view.py
------------------------
Pantalla de Detalle de un incidente: severidad/estado, ubicación,
fecha, descripción, causa raíz, acciones tomadas (como checklist),
fotos de evidencia, y acciones (Editar / Exportar a PDF / Compartir
como imagen).
"""

import datetime
from pathlib import Path

import flet as ft

import theme
from components.mensajes import mostrar_snack
from models.app_state import AppState
from services import imagen_service, incidente_service, pdf_service


class DetalleView(ft.Container):
    def __init__(self, on_editar=None):
        super().__init__(expand=True)
        self.state = AppState()
        self.on_editar = on_editar
        self.content = ft.Container()

    def refrescar(self):
        incidente = None
        if self.state.incidente_detalle_id is not None:
            incidente = incidente_service.obtener_incidente_por_id(self.state.incidente_detalle_id)

        if not incidente:
            self.content.content = ft.Column(
                expand=True,
                horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                alignment=ft.MainAxisAlignment.CENTER,
                controls=[
                    ft.Icon(ft.Icons.SEARCH_OFF_ROUNDED, size=42, color=theme.TEXT_MUTED),
                    ft.Container(height=8),
                    ft.Text("Incidente no encontrado", size=13, color=theme.TEXT_MUTED),
                ],
            )
            try:
                self.content.update()
            except Exception:
                pass
            return

        self._incidente = incidente
        color_sev, fondo_sev = theme.COLORES_SEVERIDAD.get(
            incidente["severidad"], (theme.PRIMARY, theme.PRIMARY_LIGHT)
        )
        color_estado, fondo_estado = theme.COLORES_ESTADO.get(
            incidente["estado"], (theme.PRIMARY, theme.PRIMARY_LIGHT)
        )

        fecha_legible = incidente["fecha_reporte"]
        try:
            dt = datetime.datetime.strptime(incidente["fecha_reporte"], "%Y-%m-%d %H:%M:%S")
            fecha_legible = dt.strftime("%d %b %Y — %H:%M:%S (hora local)")
        except (ValueError, TypeError):
            pass

        self.content.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                self._tarjeta_encabezado(incidente, color_sev, fondo_sev, color_estado, fondo_estado),
                ft.Row(spacing=12, controls=[
                    self._info_box("LÍNEA / PLANTA", incidente["linea"], ft.Icons.APARTMENT_ROUNDED),
                    self._info_box("ESTACIÓN", incidente["estacion"], ft.Icons.LOCATION_ON_OUTLINED),
                ]),
                self._info_box("FECHA Y HORA DE REPORTE", fecha_legible,
                               ft.Icons.CALENDAR_TODAY_OUTLINED, ancho_completo=True),

                self._seccion("DESCRIPCIÓN", ft.Icons.SUBJECT_ROUNDED, incidente["descripcion"]),

                self._seccion("CAUSA RAÍZ IDENTIFICADA", ft.Icons.PSYCHOLOGY_OUTLINED,
                              incidente["causa_raiz"] or "Aún no se ha identificado la causa raíz."),

                self._seccion_acciones(incidente["acciones"]),

                self._seccion_fotos(incidente["fotos"]),

                self._boton_marcar_resuelto(incidente),

                ft.Row(spacing=10, controls=[
                    ft.OutlinedButton(
                        content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.EDIT_OUTLINED, size=16),
                            ft.Text("EDITAR", size=12, weight=ft.FontWeight.BOLD),
                        ]),
                        expand=True,
                        on_click=lambda e: self.on_editar(incidente) if self.on_editar else None,
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.PICTURE_AS_PDF_OUTLINED, size=16),
                            ft.Text("EXPORTAR A PDF", size=12, weight=ft.FontWeight.BOLD),
                        ]),
                        expand=True,
                        on_click=self._al_exportar_pdf,
                    ),
                ]),
                ft.OutlinedButton(
                    content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                        ft.Icon(ft.Icons.IMAGE_OUTLINED, size=16),
                        ft.Text("COMPARTIR COMO IMAGEN", size=12, weight=ft.FontWeight.BOLD),
                    ]),
                    height=46,
                    on_click=self._al_exportar_imagen,
                ),
                ft.Container(height=10),
            ],
        )
        try:
            self.content.update()
        except Exception:
            pass

    # ── Subcomponentes visuales ──────────────────────────────────────────
    def _tarjeta_encabezado(self, incidente, color_sev, fondo_sev, color_estado, fondo_estado):
        return ft.Container(
            bgcolor=theme.CARD_BG,
            border_radius=theme.RADIUS_CARD,
            border=ft.Border(left=ft.BorderSide(5, color_sev)),
            padding=ft.Padding.symmetric(horizontal=16, vertical=14),
            content=ft.Column(spacing=10, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            padding=ft.Padding.symmetric(horizontal=10, vertical=5),
                            border_radius=8, bgcolor=fondo_sev,
                            content=ft.Row(spacing=5, controls=[
                                ft.Container(width=8, height=8, border_radius=4, bgcolor=color_sev),
                                ft.Text(incidente["severidad"].upper(), size=11,
                                        weight=ft.FontWeight.BOLD, color=color_sev),
                            ]),
                        ),
                        ft.Column(spacing=1, horizontal_alignment=ft.CrossAxisAlignment.END, controls=[
                            ft.Text("ESTADO", size=9, color=theme.TEXT_MUTED),
                            ft.Container(
                                padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                                border_radius=8, bgcolor=fondo_estado,
                                content=ft.Text(incidente["estado"].upper(), size=11,
                                                weight=ft.FontWeight.BOLD, color=color_estado),
                            ),
                        ]),
                    ],
                ),
                ft.Text(incidente["codigo"], size=22, weight=ft.FontWeight.BOLD, color=theme.PRIMARY),
            ]),
        )

    def _info_box(self, etiqueta, valor, icono, ancho_completo=False):
        contenido = ft.Container(
            expand=True if not ancho_completo else None,
            bgcolor=theme.CARD_BG,
            border_radius=theme.RADIUS_CARD,
            border=ft.Border.all(1, theme.BORDER),
            padding=ft.Padding.symmetric(horizontal=14, vertical=12),
            content=ft.Column(spacing=4, controls=[
                ft.Row(spacing=5, controls=[
                    ft.Icon(icono, size=14, color=theme.PRIMARY),
                    ft.Text(etiqueta, size=10, weight=ft.FontWeight.BOLD, color=theme.TEXT_MUTED),
                ]),
                ft.Text(valor, size=13, weight=ft.FontWeight.W_600, color=theme.TEXT_PRIMARY),
            ]),
        )
        return contenido

    def _seccion(self, etiqueta, icono, texto):
        return ft.Column(spacing=8, controls=[
            ft.Row(spacing=6, controls=[
                ft.Icon(icono, size=16, color=theme.PRIMARY),
                ft.Text(etiqueta, size=13, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
            ]),
            ft.Container(
                bgcolor=theme.CARD_BG,
                border_radius=theme.RADIUS_CARD,
                border=ft.Border.all(1, theme.BORDER),
                padding=ft.Padding.all(14),
                content=ft.Text(texto, size=13, color=theme.TEXT_SECONDARY),
            ),
        ])

    def _seccion_acciones(self, acciones_texto: str):
        lineas = [linea.strip() for linea in (acciones_texto or "").split("\n") if linea.strip()]
        if not lineas:
            lineas = ["Aún no se registraron acciones de contención."]

        items = []
        for linea in lineas:
            pendiente = "pendiente" in linea.lower()
            items.append(ft.Row(spacing=8, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Icon(
                    ft.Icons.RADIO_BUTTON_UNCHECKED_ROUNDED if pendiente
                    else ft.Icons.CHECK_CIRCLE_ROUNDED,
                    size=17, color=theme.TEXT_MUTED if pendiente else theme.PRIMARY,
                ),
                ft.Text(linea, size=13, color=theme.TEXT_SECONDARY, expand=True),
            ]))

        return ft.Column(spacing=8, controls=[
            ft.Row(spacing=6, controls=[
                ft.Icon(ft.Icons.PLAY_ARROW_ROUNDED, size=16, color=theme.PRIMARY),
                ft.Text("ACCIONES TOMADAS", size=13, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
            ]),
            ft.Container(
                bgcolor=theme.CARD_BG,
                border_radius=theme.RADIUS_CARD,
                border=ft.Border.all(1, theme.BORDER),
                padding=ft.Padding.all(14),
                content=ft.Column(spacing=10, controls=items),
            ),
        ])

    def _seccion_fotos(self, fotos_csv: str):
        rutas = [p for p in (fotos_csv or "").split(",") if p]
        miniaturas = []
        for ruta in rutas[:6]:
            miniaturas.append(
                ft.Container(
                    width=100, height=100,
                    border_radius=10,
                    clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
                    content=ft.Image(src=ruta, fit=ft.BoxFit.COVER,
                                     error_content=ft.Icon(ft.Icons.BROKEN_IMAGE_OUTLINED,
                                                           color=theme.TEXT_MUTED)),
                )
            )
        if not miniaturas:
            miniaturas = [
                ft.Container(
                    padding=ft.Padding.all(20), alignment=ft.Alignment.CENTER,
                    content=ft.Text("Sin fotos de evidencia", size=12, color=theme.TEXT_MUTED),
                )
            ]

        return ft.Column(spacing=8, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    ft.Row(spacing=6, controls=[
                        ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=16, color=theme.PRIMARY),
                        ft.Text("FOTOS DE EVIDENCIA", size=13, weight=ft.FontWeight.BOLD,
                                color=theme.TEXT_PRIMARY),
                    ]),
                    ft.Text(f"{len(rutas)} ARCHIVOS", size=10, color=theme.TEXT_MUTED),
                ],
            ),
            ft.Row(scroll=ft.ScrollMode.AUTO, spacing=10, controls=miniaturas),
        ])

    def _boton_marcar_resuelto(self, incidente: dict):
        if incidente["estado"] in ("Resuelto", "Cerrado"):
            return ft.Container(height=0)  # ya no aplica: no ocupa espacio

        return ft.FilledButton(
            content=ft.Row(
                alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                controls=[
                    ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF", size=18),
                    ft.Text("MARCAR COMO RESUELTO", size=13, weight=ft.FontWeight.BOLD,
                            color="#FFFFFF"),
                ],
            ),
            bgcolor=theme.SUCCESS, height=46,
            on_click=self._al_marcar_resuelto,
        )

    def _al_marcar_resuelto(self, e):
        incidente_service.marcar_resuelto(self._incidente["id"])
        mostrar_snack(self, "✓ Incidente marcado como Resuelto", theme.SUCCESS)
        self.refrescar()

    # ── Acciones ─────────────────────────────────────────────────────────
    async def _obtener_carpeta_temporal(self) -> Path | None:
        """
        En escritorio no hace falta (los servicios usan Path.home() por
        defecto). En móvil, Path.home() no es una carpeta válida/visible
        para la app -> se usa la carpeta temporal de la app, la correcta
        para generar un archivo y pasarlo de inmediato al share nativo.
        """
        try:
            ruta = await ft.StoragePaths().get_temporary_directory()
            return Path(ruta)
        except Exception:
            return None  # cae al valor por defecto (Path.home()) si falla

    async def _compartir_archivo(self, ruta: str, titulo: str):
        """Abre el selector nativo de compartir del sistema operativo
        (WhatsApp, Mensajes, Gmail, Drive, etc.) con el archivo adjunto."""
        try:
            compartir = ft.Share()
            await compartir.share_files([ft.ShareFile(path=ruta)], title=titulo)
        except Exception as ex:
            mostrar_snack(self, f"✗ No se pudo abrir el menú de compartir: {ex}", theme.PRIMARY)

    async def _al_exportar_pdf(self, e):
        nombre_sugerido = f"{self._incidente['codigo']}.pdf"

        try:
            carpeta_defecto = await ft.StoragePaths().get_downloads_directory()
        except Exception:
            carpeta_defecto = None  # el sistema usará su carpeta por defecto

        file_picker = ft.FilePicker()
        try:
            ruta_elegida = await file_picker.save_file(
                dialog_title="Guardar reporte PDF",
                file_name=nombre_sugerido,
                initial_directory=carpeta_defecto,
                file_type=ft.FilePickerFileType.CUSTOM,
                allowed_extensions=["pdf"],
            )
        except Exception:
            ruta_elegida = None

        if not ruta_elegida:
            return  # el usuario canceló el guardado

        if not ruta_elegida.lower().endswith(".pdf"):
            ruta_elegida += ".pdf"

        ok, resultado = pdf_service.exportar_incidente_a_pdf(
            self._incidente["id"], ruta_salida=ruta_elegida,
        )
        if not ok:
            mostrar_snack(self, f"✗ {resultado}", theme.PRIMARY)
            return

        mostrar_snack(self, f"✓ PDF guardado en: {resultado}", theme.SUCCESS)

    async def _al_exportar_imagen(self, e):
        carpeta = await self._obtener_carpeta_temporal()
        ok, resultado = imagen_service.exportar_incidente_a_imagen(self._incidente["id"], carpeta)
        if not ok:
            mostrar_snack(self, f"✗ {resultado}", theme.PRIMARY)
            return
        await self._compartir_archivo(resultado, "Incidente (imagen)")