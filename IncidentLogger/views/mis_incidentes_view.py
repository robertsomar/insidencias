"""
views/mis_incidentes_view.py
-------------------------------
Pantalla "Mis Incidentes": lista con buscador por ID, chips de
filtro rápido, y tarjetas con Ver / Editar / Eliminar (con
confirmación antes de borrar).
"""

import flet as ft

import theme
from components.incident_card import crear_incident_card
from components.mensajes import mostrar_snack
from models.app_state import AppState
from services import incidente_service

FILTROS = [
    ("todos", "Todos"),
    ("alta", "Alta Severidad"),
    ("revision", "En Revisión"),
    ("resueltos", "Resueltos"),
]


class MisIncidentesView(ft.Container):
    def __init__(self, on_ver=None, on_editar=None):
        super().__init__(expand=True)
        self.state = AppState()
        self.on_ver = on_ver
        self.on_editar = on_editar

        self.tf_buscar = ft.TextField(
            hint_text="Buscar por ID (INC-2024...)",
            prefix_icon=ft.Icons.SEARCH_ROUNDED,
            bgcolor=theme.INPUT_BG, border_color=theme.BORDER,
            border_radius=theme.RADIUS_INPUT,
            content_padding=ft.Padding.symmetric(horizontal=14, vertical=10),
            on_change=self._al_buscar,
        )
        self.txt_total = ft.Container(
            padding=ft.Padding.symmetric(horizontal=12, vertical=6),
            border_radius=theme.RADIUS_PILL,
            bgcolor=theme.PRIMARY_LIGHT,
            content=ft.Text("", size=11, weight=ft.FontWeight.BOLD, color=theme.PRIMARY_DARK),
        )
        self.fila_filtros = ft.Row(scroll=ft.ScrollMode.AUTO, spacing=8)
        self.lista = ft.Column(spacing=14)
        self.dialogo_confirmar: ft.AlertDialog | None = None

        self.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=14,
            controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Text("Mis Incidentes", size=22, weight=ft.FontWeight.BOLD,
                                color=theme.TEXT_PRIMARY),
                        self.txt_total,
                    ],
                ),
                self.tf_buscar,
                self.fila_filtros,
                self.lista,
                ft.Container(height=10),
            ],
        )

    def refrescar(self):
        self._construir_chips_filtro()
        self._cargar()

    def _construir_chips_filtro(self):
        chips = []
        for clave, etiqueta in FILTROS:
            activo = (clave == self.state.filtro_lista)
            chips.append(
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=9),
                    border_radius=theme.RADIUS_PILL,
                    bgcolor=theme.PRIMARY if activo else "transparent",
                    border=ft.Border.all(1, theme.PRIMARY if activo else theme.BORDER),
                    on_click=lambda e, c=clave: self._al_elegir_filtro(c),
                    content=ft.Row(spacing=4, controls=[
                        ft.Icon(ft.Icons.FILTER_LIST_ROUNDED, size=14,
                                color="#FFFFFF" if activo else theme.TEXT_SECONDARY)
                        if clave == "todos" else ft.Container(width=0),
                        ft.Text(etiqueta, size=12, weight=ft.FontWeight.BOLD,
                                color="#FFFFFF" if activo else theme.TEXT_SECONDARY),
                    ]),
                )
            )
        self.fila_filtros.controls = chips

    def _cargar(self):
        incidentes = incidente_service.obtener_incidentes(
            self.state.busqueda_lista, self.state.filtro_lista
        )
        self.txt_total.content.value = f"TOTAL: {len(incidentes)} incidentes"

        if not incidentes:
            self.lista.controls = [
                ft.Container(
                    padding=ft.Padding.symmetric(vertical=30),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Column(
                        horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                        controls=[
                            ft.Icon(ft.Icons.ASSIGNMENT_OUTLINED, size=36, color=theme.TEXT_MUTED),
                            ft.Container(height=6),
                            ft.Text("No se encontraron incidentes", size=13,
                                    color=theme.TEXT_MUTED),
                        ],
                    ),
                )
            ]
        else:
            self.lista.controls = [
                crear_incident_card(
                    incidente,
                    on_ver=self._al_ver,
                    on_editar=self._al_editar,
                    on_eliminar=self._al_pedir_confirmacion_eliminar,
                )
                for incidente in incidentes
            ]

        try:
            self.content.update()
        except Exception:
            pass

    def _al_elegir_filtro(self, clave: str):
        self.state.filtro_lista = clave
        self._construir_chips_filtro()
        self._cargar()
        try:
            self.fila_filtros.update()
        except Exception:
            pass

    def _al_buscar(self, e):
        self.state.busqueda_lista = self.tf_buscar.value or ""
        self._cargar()

    def _al_ver(self, incidente: dict):
        if self.on_ver:
            self.on_ver(incidente)

    def _al_editar(self, incidente: dict):
        if self.on_editar:
            self.on_editar(incidente)

    def _al_pedir_confirmacion_eliminar(self, incidente: dict):
        def confirmar(e):
            self.page.pop_dialog()
            incidente_service.eliminar_incidente(incidente["id"])
            mostrar_snack(self, "🗑️ Incidente eliminado", theme.PRIMARY)
            self._cargar()

        def cancelar(e):
            self.page.pop_dialog()

        dialogo = ft.AlertDialog(
            modal=True,bgcolor=theme.CARD_BG,
            title=ft.Text("¿Eliminar incidente?", color=theme.PRIMARY_DARK),
            content=ft.Text(f"Se eliminará permanentemente {incidente['codigo']}. "
                            "Esta acción no se puede deshacer.", color=theme.TEXT_PRIMARY),
            actions=[
                ft.TextButton("Cancelar", on_click=cancelar),
                ft.TextButton("Eliminar", on_click=confirmar,
                              style=ft.ButtonStyle(color=theme.PRIMARY)),
            ],
        )
        self.page.show_dialog(dialogo)
