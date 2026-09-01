"""
views/registrar_view.py
--------------------------
Pantalla "Registrar Incidente". Sirve tanto para CREAR uno nuevo como
para EDITAR uno existente (según models.AppState.incidente_editando_id).

Validaciones obligatorias antes de guardar:
    1) Severidad seleccionada
    2) Línea seleccionada
    3) Estación con texto
    4) Descripción con texto
    5) Causa seleccionada
Si falta algo: mensaje de advertencia + bordes en rojo + no guarda.
Si todo está bien: guarda en SQLite, mensaje de éxito, limpia el formulario.
"""

import flet as ft

import theme
from components.form_card import crear_form_card, marcar_error
from components.mensajes import mostrar_snack
from models import constantes
from models.app_state import AppState
from services import incidente_service


class RegistrarView(ft.Container):
    def __init__(self, on_guardado=None):
        super().__init__(expand=True)
        self.state = AppState()
        self.on_guardado = on_guardado
        self.fotos_seleccionadas: list[str] = []

        # ── Campos del formulario ────────────────────────────────────────
        self.dd_severidad = ft.Dropdown(
            hint_text="Seleccione...",
            options=[ft.DropdownOption(v, style=ft.ButtonStyle(color=theme.TEXT_PRIMARY)) for v in constantes.SEVERIDADES],
            bgcolor=theme.INPUT_BG, border_color="transparent",
            hint_style = ft.TextStyle(color=theme.TEXT_PRIMARY),
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )
        self.dd_linea = ft.Dropdown(
            hint_text="Seleccione...",
            options=[ft.DropdownOption(v, style=ft.ButtonStyle(color=theme.TEXT_PRIMARY)) for v in constantes.LINEAS_PRODUCCION],
            bgcolor=theme.INPUT_BG, border_color="transparent",
            hint_style = ft.TextStyle(color=theme.TEXT_PRIMARY),
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )
        self.tf_estacion = ft.TextField(
            hint_text="Ej: Brazo Robótico K-450",
            bgcolor=theme.INPUT_BG, border_color="transparent",
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )
        self.tf_descripcion = ft.TextField(
            hint_text="Describa lo sucedido de forma detallada...",
            multiline=True, min_lines=4, max_lines=6, max_length=500,
            bgcolor=theme.INPUT_BG, border_color="transparent",
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_change=self._al_escribir_descripcion,
        )
        self.dd_causa = ft.Dropdown(
            hint_text="Seleccione una causa...",
            options=[ft.DropdownOption(v, style=ft.ButtonStyle(color=theme.TEXT_PRIMARY)) for v in constantes.CAUSAS],
            bgcolor=theme.INPUT_BG, border_color="transparent",
            hint_style = ft.TextStyle(color=theme.TEXT_PRIMARY),
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )
        self.tf_acciones = ft.TextField(
            hint_text="¿Qué medidas se aplicaron inmediatamente?",
            multiline=True, min_lines=3, max_lines=5,
            bgcolor=theme.INPUT_BG, border_color="transparent",
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )
        # Solo visible al editar un incidente ya existente (ciclo de vida:
        # Editar -> Actualizar estado)
        self.dd_estado = ft.Dropdown(
            options=[ft.DropdownOption(v, style=ft.ButtonStyle(color=theme.TEXT_PRIMARY)) for v in constantes.ESTADOS],
            bgcolor=theme.INPUT_BG, border_color="transparent",
            hint_style = ft.TextStyle(color=theme.TEXT_PRIMARY),
            border_radius=theme.RADIUS_INPUT, text_size=14,color=theme.TEXT_PRIMARY,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
        )

        self.txt_contador_desc = ft.Text("0/500", size=10, color=theme.TEXT_MUTED)
        self.txt_fotos_info = ft.Text("", size=11, color=theme.TEXT_SECONDARY)

        # ── Tarjetas (para poder resaltarlas en rojo si hay error) ───────
        self.card_severidad = crear_form_card("SEVERIDAD", self.dd_severidad)
        self.card_linea = crear_form_card("LÍNEA DE PRODUCCIÓN", self.dd_linea)
        self.card_estacion = crear_form_card("ESTACIÓN / EQUIPO", self.tf_estacion)
        self.card_descripcion = crear_form_card(
            "DESCRIPCIÓN DEL INCIDENTE", self.tf_descripcion, contador="0/500",
        )
        self.card_causa = crear_form_card("CAUSA PRELIMINAR", self.dd_causa)
        self.card_acciones = crear_form_card("ACCIONES TOMADAS (CONTENCIÓN)", self.tf_acciones)
        self.card_estado = crear_form_card("ESTADO DEL INCIDENTE", self.dd_estado)
        self.card_estado.visible = False  # se muestra solo en modo edición

        self.titulo_form = ft.Text("Registrar Incidente", size=20, weight=ft.FontWeight.BOLD,
                                   color="#FFFFFF")

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                self._crear_banner(),
                ft.Text(
                    "Complete los detalles del evento con precisión para garantizar "
                    "un seguimiento adecuado.",
                    size=13, color=theme.TEXT_SECONDARY,
                ),
                self.card_severidad,
                self.card_linea,
                self.card_estacion,
                self.card_descripcion,
                self.card_causa,
                self.card_acciones,
                self.card_estado,
                ft.Row(spacing=10, controls=[
                    ft.OutlinedButton(
                        content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.CAMERA_ALT_OUTLINED, size=17, color=theme.PRIMARY),
                            ft.Text("Tomar Foto", size=13, color=theme.PRIMARY),
                        ]),
                        expand=True,
                        on_click=self._al_tomar_foto,
                    ),
                    ft.OutlinedButton(
                        content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.PERM_MEDIA_OUTLINED, size=17, color=theme.PRIMARY),
                            ft.Text("Galería", size=13, color=theme.PRIMARY),
                        ]),
                        expand=True,
                        on_click=self._al_abrir_galeria,
                    ),
                ]),
                self.txt_fotos_info,
                ft.FilledButton(
                    content=ft.Row(
                        alignment=ft.MainAxisAlignment.CENTER, spacing=8,
                        controls=[
                            ft.Icon(ft.Icons.CHECK_CIRCLE_ROUNDED, color="#FFFFFF", size=19),
                            ft.Text("GUARDAR INCIDENTE", size=14, weight=ft.FontWeight.BOLD,
                                    color="#FFFFFF"),
                        ],
                    ),
                    bgcolor=theme.PRIMARY,
                    height=50,
                    on_click=self._al_guardar,
                ),
                ft.OutlinedButton(
                    content=ft.Text("LIMPIAR FORMULARIO", size=13, weight=ft.FontWeight.BOLD,
                                    color=theme.PRIMARY),
                    height=46,
                    on_click=lambda e: self.limpiar_formulario(),
                ),
                ft.Container(height=10),
            ],
        )

    # ── Banner superior con imagen de fondo ─────────────────────────────
    def _crear_banner(self) -> ft.Container:
        return ft.Container(
            height=150,
            border_radius=theme.RADIUS_CARD,
            clip_behavior=ft.ClipBehavior.ANTI_ALIAS,
            image=ft.DecorationImage(src="hero_fabrica.png", fit=ft.BoxFit.COVER),
            gradient=ft.LinearGradient(
                begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                colors=[ft.Colors.with_opacity(0.15, "#000000"),
                        ft.Colors.with_opacity(0.75, "#000000")],
            ),
            padding=ft.Padding.all(16),
            alignment=ft.Alignment.BOTTOM_LEFT,
            content=self.titulo_form,
        )

    # ── Eventos ──────────────────────────────────────────────────────────
    def _al_escribir_descripcion(self, e):
        largo = len(self.tf_descripcion.value or "")
        self.txt_contador_desc.value = f"{largo}/500"
        # El contador vive dentro del encabezado de card_descripcion:
        # lo actualizamos accediendo a esa fila (Column -> Row -> Text).
        fila_encabezado = self.card_descripcion.content.controls[0]
        fila_encabezado.controls[1].value = f"{largo}/500"
        fila_encabezado.update()

    async def _al_tomar_foto(self, e):
        await self._seleccionar_imagenes(multiple=False)

    async def _al_abrir_galeria(self, e):
        await self._seleccionar_imagenes(multiple=True)

    async def _seleccionar_imagenes(self, multiple: bool):
        fp = ft.FilePicker()
        archivos = await fp.pick_files(
            dialog_title="Seleccionar foto de evidencia",
            file_type=ft.FilePickerFileType.IMAGE,
            allow_multiple=multiple,
        )
        if not archivos:
            return
        for archivo in archivos:
            self.fotos_seleccionadas.append(archivo.path)
        self.txt_fotos_info.value = f"📎 {len(self.fotos_seleccionadas)} foto(s) agregada(s)"
        self.txt_fotos_info.update()

    def _al_guardar(self, e):
        datos = {
            "severidad": self.dd_severidad.value or "",
            "linea": self.dd_linea.value or "",
            "estacion": self.tf_estacion.value or "",
            "descripcion": self.tf_descripcion.value or "",
            "causa": self.dd_causa.value or "",
            "acciones": self.tf_acciones.value or "",
            "fotos": ",".join(self.fotos_seleccionadas),
        }

        es_valido, campos_invalidos = incidente_service.validar_formulario(
            datos["severidad"], datos["linea"], datos["estacion"],
            datos["descripcion"], datos["causa"],
        )

        self._resaltar_errores(campos_invalidos)

        if not es_valido:
            mostrar_snack(self, "⚠️ Por favor completa todos los campos obligatorios",
                         theme.PRIMARY)
            return

        if self.state.incidente_editando_id is not None:
            if self.dd_estado.value:
                datos["estado"] = self.dd_estado.value
            incidente_service.actualizar_incidente(self.state.incidente_editando_id, datos)
            mostrar_snack(self, "✓ Incidente actualizado correctamente", theme.SUCCESS)
        else:
            incidente_service.registrar_incidente(datos)
            mostrar_snack(self, "✓ Incidente guardado correctamente", theme.SUCCESS)

        self.limpiar_formulario()
        if self.on_guardado:
            self.on_guardado()

    def _resaltar_errores(self, campos_invalidos: set[str]):
        mapa = {
            "severidad": self.card_severidad,
            "linea": self.card_linea,
            "estacion": self.card_estacion,
            "descripcion": self.card_descripcion,
            "causa": self.card_causa,
        }
        for clave, card in mapa.items():
            marcar_error(card, clave in campos_invalidos)
            card.update()

    # ── Modo edición / limpieza ──────────────────────────────────────────
    def cargar_para_editar(self, incidente: dict):
        self.state.incidente_editando_id = incidente["id"]
        self.dd_severidad.value = incidente["severidad"]
        self.dd_linea.value = incidente["linea"]
        self.tf_estacion.value = incidente["estacion"]
        self.tf_descripcion.value = incidente["descripcion"]
        self.dd_causa.value = incidente["causa"]
        self.tf_acciones.value = incidente["acciones"]
        self.dd_estado.value = incidente["estado"]
        self.fotos_seleccionadas = [p for p in (incidente["fotos"] or "").split(",") if p]

        self.titulo_form.value = "Editar Incidente"
        self.card_estado.visible = True
        self._resaltar_errores(set())
        self._al_escribir_descripcion(None)
        try:
            self.content.update()
        except Exception:
            pass

    def limpiar_formulario(self):
        self.state.incidente_editando_id = None
        self.dd_severidad.value = None
        self.dd_linea.value = None
        self.tf_estacion.value = ""
        self.tf_descripcion.value = ""
        self.dd_causa.value = None
        self.tf_acciones.value = ""
        self.dd_estado.value = None
        self.fotos_seleccionadas = []
        self.txt_fotos_info.value = ""
        self.titulo_form.value = "Registrar Incidente"
        self.card_estado.visible = False
        self._resaltar_errores(set())
        try:
            self.content.update()
        except Exception:
            pass

    def refrescar(self):
        """Si venimos de 'Editar' en la lista, carga esos datos; si no, no hace nada."""
        if self.state.incidente_editando_id is not None:
            incidente = incidente_service.obtener_incidente_por_id(self.state.incidente_editando_id)
            if incidente:
                self.cargar_para_editar(incidente)
