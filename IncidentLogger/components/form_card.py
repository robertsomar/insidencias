"""
components/form_card.py
--------------------------
Tarjeta blanca con borde rosado que envuelve cada campo del
formulario de registro. Soporta un estado de "error" (borde rojo
más grueso + mensaje) para la validación de campos obligatorios.
"""

import flet as ft

import theme


def crear_form_card(etiqueta: str, contenido: ft.Control, ayuda: str = "",
                    contador: str = "") -> ft.Container:
    encabezado_controles = [
        ft.Text(etiqueta, size=theme.SIZE_LABEL, weight=ft.FontWeight.BOLD,
                color=theme.TEXT_SECONDARY),
    ]
    if contador:
        fila_encabezado = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            controls=[
                encabezado_controles[0],
                ft.Text(contador, size=10, color=theme.TEXT_MUTED),
            ],
        )
    else:
        fila_encabezado = encabezado_controles[0]

    hijos = [fila_encabezado, ft.Container(height=8), contenido]
    if ayuda:
        hijos.append(ft.Container(height=4))
        hijos.append(ft.Text(ayuda, size=10, color=theme.TEXT_MUTED))

    contenedor = ft.Container(
        bgcolor=theme.CARD_BG,
        border_radius=theme.RADIUS_CARD,
        border=ft.Border.all(1, theme.BORDER),
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        content=ft.Column(spacing=0, controls=hijos),
    )
    return contenedor


def marcar_error(contenedor: ft.Container, tiene_error: bool):
    """Cambia el borde de la tarjeta a rojo (error) o al color normal."""
    if tiene_error:
        contenedor.border = ft.Border.all(2, theme.PRIMARY)
        contenedor.bgcolor = "#FEF5F5"
    else:
        contenedor.border = ft.Border.all(1, theme.BORDER)
        contenedor.bgcolor = theme.CARD_BG
