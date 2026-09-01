"""
components/incident_card.py
------------------------------
Tarjeta de un incidente en la lista "Mis Incidentes": franja de
color según severidad, badge, título (descripción resumida),
ubicación, fecha, y botones Ver / Editar / Eliminar.
"""

import flet as ft

import theme


def crear_incident_card(incidente: dict, on_ver, on_editar, on_eliminar) -> ft.Container:
    color_severidad, fondo_severidad = theme.COLORES_SEVERIDAD.get(
        incidente["severidad"], (theme.PRIMARY, theme.PRIMARY_LIGHT)
    )

    descripcion_corta = incidente["descripcion"]
    if len(descripcion_corta) > 70:
        descripcion_corta = descripcion_corta[:70].rstrip() + "…"

    fecha_legible = incidente["fecha_reporte"]
    try:
        import datetime
        dt = datetime.datetime.strptime(incidente["fecha_reporte"], "%Y-%m-%d %H:%M:%S")
        fecha_legible = dt.strftime("%d/%m/%y %I:%M %p")
    except (ValueError, TypeError):
        pass

    filas_meta = [
        ft.Row(spacing=4, controls=[
            ft.Icon(ft.Icons.LOCATION_ON_OUTLINED, size=13, color=theme.TEXT_MUTED),
            ft.Text(f"{incidente['linea']} - {incidente['estacion']}", size=12,
                    color=theme.TEXT_SECONDARY),
        ]),
    ]
    if incidente["estado"] in ("Resuelto", "Cerrado"):
        filas_meta.append(ft.Row(spacing=4, controls=[
            ft.Icon(ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, size=13, color=theme.SUCCESS),
            ft.Text(incidente["estado"], size=12, color=theme.SUCCESS),
        ]))
    else:
        filas_meta.append(ft.Row(spacing=4, controls=[
            ft.Icon(ft.Icons.ACCESS_TIME_ROUNDED, size=13, color=theme.TEXT_MUTED),
            ft.Text(fecha_legible, size=12, color=theme.TEXT_SECONDARY),
        ]))

    return ft.Container(
        bgcolor=theme.CARD_BG,
        border_radius=theme.RADIUS_CARD,
        border=ft.Border(left=ft.BorderSide(4, color_severidad)),
        padding=ft.Padding.symmetric(horizontal=16, vertical=14),
        content=ft.Column(spacing=8, controls=[
            ft.Row(
                alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                vertical_alignment=ft.CrossAxisAlignment.START,
                controls=[
                    ft.Text(incidente["codigo"], size=15, weight=ft.FontWeight.BOLD,
                            color=theme.PRIMARY),
                    ft.Container(
                        padding=ft.Padding.symmetric(horizontal=10, vertical=4),
                        border_radius=6,
                        bgcolor=fondo_severidad,
                        content=ft.Text(incidente["severidad"].upper(), size=10,
                                        weight=ft.FontWeight.BOLD, color=color_severidad),
                    ),
                ],
            ),
            ft.Text(descripcion_corta, size=14, weight=ft.FontWeight.W_600,
                    color=theme.TEXT_PRIMARY),
            *filas_meta,
            ft.Divider(height=1, color=theme.BORDER),
            ft.Row(spacing=8, controls=[
                ft.OutlinedButton(
                    content=ft.Row(spacing=4, controls=[
                        ft.Icon(ft.Icons.VISIBILITY_OUTLINED, size=15),
                        ft.Text("Ver", size=12),
                    ]),
                    expand=True,
                    on_click=lambda e: on_ver(incidente),
                ),
                ft.OutlinedButton(
                    content=ft.Row(spacing=4, controls=[
                        ft.Icon(ft.Icons.EDIT_OUTLINED, size=15),
                        ft.Text("Editar", size=12),
                    ]),
                    expand=True,
                    on_click=lambda e: on_editar(incidente),
                ),
                ft.IconButton(
                    icon=ft.Icons.DELETE_OUTLINE_ROUNDED,
                    icon_color=theme.PRIMARY,
                    icon_size=19,
                    on_click=lambda e: on_eliminar(incidente),
                ),
            ]),
        ]),
    )
