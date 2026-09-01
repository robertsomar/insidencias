"""
components/mensajes.py
-------------------------
Helper para mostrar mensajes flotantes (SnackBar). En esta versión de
Flet, SnackBar es un DialogControl -> se muestra con page.show_dialog(),
no con el método show_snack_bar() de versiones anteriores.
"""

import flet as ft


def mostrar_snack(control: ft.Control, texto: str, color: str, texto_color: str = "#FFFFFF"):
    try:
        control.page.show_dialog(
            ft.SnackBar(
                content=ft.Text(texto, color=texto_color, weight=ft.FontWeight.BOLD),
                bgcolor=color,
                duration=2600,
            )
        )
    except Exception:
        pass
