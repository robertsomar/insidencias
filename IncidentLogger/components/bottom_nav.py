"""
components/bottom_nav.py
--------------------------
Barra de navegación inferior: Registrar, Mis Incidentes, Análisis.
La pestaña activa se resalta con una "pill" roja de fondo, igual que
en el diseño original.
"""

import flet as ft

import theme

DESTINOS = [
    ("registrar", ft.Icons.EDIT_NOTE_ROUNDED, "Registrar"),
    ("mis_incidentes", ft.Icons.ASSIGNMENT_OUTLINED, "Mis Incidentes"),
    ("analisis", ft.Icons.BAR_CHART_ROUNDED, "Análisis"),
]


def crear_bottom_nav(vista_activa: str, on_tab_click) -> ft.Container:
    items = []
    for clave, icono, etiqueta in DESTINOS:
        activo = (clave == vista_activa)
        items.append(
            ft.Container(
                expand=True,
                padding=ft.Padding.symmetric(vertical=8, horizontal=4),
                border_radius=theme.RADIUS_PILL,
                bgcolor=theme.PRIMARY if activo else "transparent",
                on_click=lambda e, c=clave: on_tab_click(c),
                content=ft.Column(
                    spacing=2,
                    horizontal_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Icon(icono, size=20,
                                color="#FFFFFF" if activo else theme.TEXT_MUTED),
                        ft.Text(etiqueta, size=10,
                                weight=ft.FontWeight.BOLD if activo else ft.FontWeight.NORMAL,
                                color="#FFFFFF" if activo else theme.TEXT_MUTED),
                    ],
                ),
            )
        )

    return ft.Container(
        bgcolor=theme.CARD_BG,
        border=ft.Border(top=ft.BorderSide(1, theme.BORDER)),
        padding=ft.Padding.symmetric(horizontal=6, vertical=6),
        content=ft.Row(controls=items, spacing=6),
    )
