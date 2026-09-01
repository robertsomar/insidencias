"""
components/stat_card.py
--------------------------
Tarjeta de estadística (Total, Críticos, Altos, Resueltos) usada en
la grilla 2x2 del "Resumen General" de Análisis.
"""

import flet as ft

import theme


def crear_stat_card(etiqueta: str, valor: int, color: str) -> ft.Container:
    return ft.Container(
        expand=True,
        bgcolor=theme.CARD_BG,
        border_radius=theme.RADIUS_CARD,
        border=ft.Border(left=ft.BorderSide(4, color)),
        padding=ft.Padding.symmetric(horizontal=14, vertical=14),
        content=ft.Column(spacing=4, controls=[
            ft.Text(etiqueta.upper(), size=10, weight=ft.FontWeight.BOLD,
                    color=theme.TEXT_MUTED),
            ft.Text(str(valor), size=26, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
        ]),
    )
