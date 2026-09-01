"""
views/analisis_view.py
-------------------------
Pantalla de Análisis: resumen general (4 tarjetas), gráfico de
barras "Incidentes por Causa", botón "Exportar Reporte", gráfico de
línea "Incidentes por Línea de Producción", e insights dinámicos
calculados a partir de los datos reales.
"""

import flet as ft
import flet_charts as fch
from pathlib import Path

import theme
from components.mensajes import mostrar_snack
from components.stat_card import crear_stat_card
from services import analisis_service, pdf_service


class AnalisisView(ft.Container):
    def __init__(self):
        super().__init__(expand=True)
        self.content = ft.Container()

    def refrescar(self):
        resumen = analisis_service.generar_resumen()

        self.content.content = ft.Column(
            expand=True,
            scroll=ft.ScrollMode.AUTO,
            spacing=16,
            controls=[
                ft.Text("Resumen General", size=20, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),

                ft.Row(spacing=12, controls=[
                    crear_stat_card("Total", resumen["total"], theme.TEXT_PRIMARY),
                    crear_stat_card("Críticos", resumen["criticos"], theme.PRIMARY),
                ]),
                ft.Row(spacing=12, controls=[
                    crear_stat_card("Altos", resumen["altos"], theme.ALTA),
                    crear_stat_card("Resueltos", resumen["resueltos"], theme.SUCCESS),
                ]),

                self._grafico_por_causa(resumen["por_causa"]),

                self._tarjeta_exportar_reporte(),

                self._grafico_por_linea(resumen["por_linea"]),

                self._insight(
                    ft.Icons.LIGHTBULB_OUTLINE_ROUNDED, theme.INFO,
                    "Punto Crítico Detectado", self._texto_insight_linea(resumen),
                ),
                self._insight(
                    ft.Icons.CHECK_CIRCLE_OUTLINE_ROUNDED, theme.SUCCESS,
                    "Mejora en Resolución", self._texto_insight_tiempo(resumen),
                ),

                ft.Container(height=10),
            ],
        )
        try:
            self.content.update()
        except Exception:
            pass

    # ── Gráficos ─────────────────────────────────────────────────────────
    def _grafico_por_causa(self, por_causa: list[tuple[str, int]]) -> ft.Container:
        if not por_causa:
            contenido = ft.Container(
                height=140, alignment=ft.Alignment.CENTER,
                content=ft.Text("Aún no hay incidentes registrados", size=12,
                                color=theme.TEXT_MUTED),
            )
        else:
            maximo = max(cantidad for _, cantidad in por_causa) or 1
            grupos = [
                fch.BarChartGroup(
                    x=i,
                    rods=[fch.BarChartRod(
                        from_y=0, to_y=cantidad, width=30, color=theme.PRIMARY,
                        border_radius=ft.BorderRadius(4, 4, 0, 0),
                        bgcolor=ft.Colors.with_opacity(0.08, theme.PRIMARY), bg_to_y=maximo,
                    )],
                )
                for i, (_, cantidad) in enumerate(por_causa)
            ]
            grafico = fch.BarChart(
                groups=grupos,
                expand=True,
                max_y=maximo * 1.2,
                bgcolor=ft.Colors.TRANSPARENT,
                border=ft.Border.all(0, ft.Colors.TRANSPARENT),
                left_axis=fch.ChartAxis(label_size=26),
                bottom_axis=fch.ChartAxis(
                    label_size=22,
                    labels=[
                        fch.ChartAxisLabel(value=i, label=ft.Text(causa, size=9,
                                                                  color=theme.TEXT_MUTED))
                        for i, (causa, _) in enumerate(por_causa)
                    ],
                ),
            )
            contenido = ft.Container(height=180, content=grafico)

        return ft.Container(
            bgcolor=theme.CARD_BG, border_radius=theme.RADIUS_CARD,
            border=ft.Border.all(1, theme.BORDER), padding=ft.Padding.all(16),
            content=ft.Column(spacing=10, controls=[
                ft.Row(
                    alignment=ft.MainAxisAlignment.SPACE_BETWEEN,
                    controls=[
                        ft.Text("Incidentes por Causa", size=14, weight=ft.FontWeight.BOLD,
                                color=theme.TEXT_PRIMARY),
                        ft.Icon(ft.Icons.FILTER_ALT_OUTLINED, size=16, color=theme.TEXT_MUTED),
                    ],
                ),
                contenido,
            ]),
        )

    def _grafico_por_linea(self, por_linea: list[tuple[str, int]]) -> ft.Container:
        if not por_linea:
            contenido = ft.Container(
                height=140, alignment=ft.Alignment.CENTER,
                content=ft.Text("Aún no hay incidentes registrados", size=12,
                                color=theme.TEXT_MUTED),
            )
        else:
            valores = [cantidad for _, cantidad in por_linea]
            serie = fch.LineChartData(
                points=[fch.LineChartDataPoint(x=i, y=v) for i, v in enumerate(valores)],
                stroke_width=3, color=theme.PRIMARY, curved=True,
                below_line_gradient=ft.LinearGradient(
                    begin=ft.Alignment.TOP_CENTER, end=ft.Alignment.BOTTOM_CENTER,
                    colors=[ft.Colors.with_opacity(0.25, theme.PRIMARY),
                            ft.Colors.with_opacity(0.0, theme.PRIMARY)],
                ),
            )
            grafico = fch.LineChart(
                data_series=[serie], expand=True,
                min_x=0, max_x=max(len(valores) - 1, 1),
                min_y=0, max_y=max(valores) * 1.2 if valores else 1,
                bgcolor=ft.Colors.TRANSPARENT,
                border=ft.Border.all(0, ft.Colors.TRANSPARENT),
                left_axis=fch.ChartAxis(label_size=24),
                bottom_axis=fch.ChartAxis(
                    label_size=20,
                    labels=[
                        fch.ChartAxisLabel(value=i, label=ft.Text(linea.replace("Línea ", ""),
                                                                  size=9, color=theme.TEXT_MUTED))
                        for i, (linea, _) in enumerate(por_linea)
                    ],
                ),
            )
            contenido = ft.Container(height=180, content=grafico)

        return ft.Container(
            bgcolor=theme.CARD_BG, border_radius=theme.RADIUS_CARD,
            border=ft.Border.all(1, theme.BORDER), padding=ft.Padding.all(16),
            content=ft.Column(spacing=10, controls=[
                ft.Text("Incidentes por Línea de Producción", size=14, weight=ft.FontWeight.BOLD,
                        color=theme.TEXT_PRIMARY),
                contenido,
            ]),
        )

    def _tarjeta_exportar_reporte(self) -> ft.Container:
        return ft.Container(
            bgcolor=ft.Colors.with_opacity(0.8, theme.PRIMARY), border_radius=theme.RADIUS_CARD,
            padding=ft.Padding.all(20),
            content=ft.Column(
                horizontal_alignment=ft.CrossAxisAlignment.CENTER, spacing=12,
                controls=[
                    ft.Icon(ft.Icons.BAR_CHART_ROUNDED, color="#FFFFFF", size=30),
                    ft.Text(
                        "Genera un informe detallado con el histórico de incidentes "
                        "del mes actual.",
                        size=13, color="#FFFFFF", text_align=ft.TextAlign.CENTER,
                    ),
                    ft.FilledButton(
                        content=ft.Row(spacing=6, alignment=ft.MainAxisAlignment.CENTER, controls=[
                            ft.Icon(ft.Icons.BAR_CHART_ROUNDED, size=16, color=theme.PRIMARY),
                            ft.Text("COMPARTIR REPORTE EN PDF", size=12, weight=ft.FontWeight.BOLD,
                                    color=theme.PRIMARY),
                        ]),
                        bgcolor="#FFFFFF",
                        on_click=self._al_exportar_reporte,
                    ),
                ],
            ),
        )

    def _insight(self, icono, color, titulo, texto) -> ft.Container:
        return ft.Container(
            bgcolor=theme.PRIMARY_LIGHT, border_radius=theme.RADIUS_CARD,
            padding=ft.Padding.all(14),
            content=ft.Row(spacing=12, vertical_alignment=ft.CrossAxisAlignment.START, controls=[
                ft.Container(
                    width=34, height=34, border_radius=17,
                    bgcolor=ft.Colors.with_opacity(0.15, color),
                    alignment=ft.Alignment.CENTER,
                    content=ft.Icon(icono, size=18, color=color),
                ),
                ft.Column(spacing=2, expand=True, controls=[
                    ft.Text(titulo, size=13, weight=ft.FontWeight.BOLD, color=theme.TEXT_PRIMARY),
                    ft.Text(texto, size=12, color=theme.TEXT_SECONDARY),
                ]),
            ]),
        )

    # ── Texto de insights (calculado con datos reales) ──────────────────
    def _texto_insight_linea(self, resumen: dict) -> str:
        linea_top = resumen.get("linea_con_mas_incidentes")
        if not linea_top or linea_top[1] == 0:
            return "Aún no hay suficientes datos para detectar puntos críticos."
        linea, cantidad = linea_top
        return f"{linea} concentra la mayor cantidad de incidentes registrados ({cantidad})."

    def _texto_insight_tiempo(self, resumen: dict) -> str:
        minutos = resumen.get("tiempo_promedio_minutos")
        if minutos is None:
            return "Aún no hay incidentes resueltos para calcular el tiempo promedio."
        return f"El tiempo promedio de respuesta hasta resolución es de {int(minutos)} minutos."

    # ── Acciones ─────────────────────────────────────────────────────────
    async def _al_exportar_reporte(self, e):
        try:
            carpeta = Path(await ft.StoragePaths().get_temporary_directory())
        except Exception:
            carpeta = None  # cae al valor por defecto (Path.home()) si falla

        ok, resultado = pdf_service.exportar_reporte_general(carpeta)
        if not ok:
            mostrar_snack(self, f"✗ {resultado}", theme.PRIMARY)
            return

        try:
            compartir = ft.Share()
            await compartir.share_files([ft.ShareFile(path=resultado)],
                                        title="Reporte de incidentes")
        except Exception as ex:
            mostrar_snack(self, f"✗ No se pudo abrir el menú de compartir: {ex}", theme.PRIMARY)