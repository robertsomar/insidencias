"""
components/app_header.py
--------------------------
Barra superior de la app. Dos variantes:
  - "principal": logo + "INCIDENT LOGGER" a la izquierda, menú a la derecha.
  - "detalle":   flecha de volver a la izquierda, título centrado,
                 ícono de compartir a la derecha (pantalla de Detalle).
"""

import flet as ft

import theme

def crear_header(on_menu_click=None, on_back_click=None, on_share_click=None,
                 variante: str = "principal") -> ft.Container:
    if variante == "detalle":
        contenido = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.IconButton(
                    icon=ft.Icons.ARROW_BACK_ROUNDED,
                    icon_color=theme.PRIMARY,
                    icon_size=22,
                    on_click=on_back_click,
                ),
                ft.Text("INCIDENT LOGGER", size=16, weight=ft.FontWeight.BOLD,
                        color=theme.PRIMARY),
                ft.IconButton(
                    icon=ft.Icons.SHARE_ROUNDED,
                    icon_color=theme.PRIMARY,
                    icon_size=20,
                    on_click=on_share_click,
                ),
            ],
        )
    else:
        contenido = ft.Row(
            alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
            vertical_alignment=ft.CrossAxisAlignment.CENTER,
            controls=[
                ft.Row(
                    spacing=8,
                    vertical_alignment=ft.CrossAxisAlignment.CENTER,
                    controls=[
                        ft.Container(
                            width=28, height=28,
                            content=ft.Image(src="logo.png", fit=ft.BoxFit.CONTAIN),
                        ),
                        ft.Text("INCIDENT LOGGER", size=17, weight=ft.FontWeight.BOLD,
                                color=theme.PRIMARY),
                    ],
                ),
                ft.IconButton(
                    icon=ft.Icons.MENU_ROUNDED,
                    icon_color=theme.TEXT_PRIMARY,
                    icon_size=22,
                    on_click=on_menu_click,
                ),
            ],
        )

    return ft.Container(
        bgcolor=theme.BG,
        padding=ft.Padding.only(left=8,right=8, bottom=6, top=25),
        border=ft.Border(bottom=ft.BorderSide(1, theme.BORDER)),
        content=contenido,
    )
