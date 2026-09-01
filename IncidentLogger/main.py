# main.py
import asyncio

import flet as ft

import theme
from components.app_header import crear_header
from components.bottom_nav import crear_bottom_nav
from database import db
from models.app_state import AppState
from views.registrar_view import RegistrarView
from views.mis_incidentes_view import MisIncidentesView
from views.detalle_view import DetalleView
from views.analisis_view import AnalisisView


class IncidentLoggerApp:
    """Orquesta la navegación entre pantallas y el layout responsivo."""

    CONFIG_HEADER = {
        "registrar": "principal",
        "mis_incidentes": "principal",
        "analisis": "principal",
        "detalle": "detalle",
    }
    # A qué pestaña de la barra inferior corresponde resaltar cada vista
    TAB_POR_VISTA = {
        "registrar": "registrar",
        "mis_incidentes": "mis_incidentes",
        "detalle": "mis_incidentes",
        "analisis": "analisis",
    }

    def __init__(self, page: ft.Page):
        self.page = page
        self.state = AppState()

        self._setup_page()

        self.registrar_view = RegistrarView(on_guardado=self._al_guardar_incidente)
        self.mis_incidentes_view = MisIncidentesView(
            on_ver=self._al_ver_incidente, on_editar=self._al_editar_incidente,
        )
        self.detalle_view = DetalleView(on_editar=self._al_editar_incidente)
        self.analisis_view = AnalisisView()

        self.vistas = {
            "registrar": self.registrar_view,
            "mis_incidentes": self.mis_incidentes_view,
            "detalle": self.detalle_view,
            "analisis": self.analisis_view,
        }

        self.pila_navegacion: list[str] = []
        self.vista_actual = "registrar"

        self.contenedor_header = ft.Container()
        self.contenedor_cuerpo = ft.Container(
            expand=True,
            padding=ft.Padding.all(theme.PAGE_PADDING),
            content=self.registrar_view,
        )
        self.contenedor_bottom_nav = ft.Container()

        self.columna_centrada = ft.Container(
            expand=True,
            width=theme.MAX_CONTENT_WIDTH,
            bgcolor=theme.BG,
            content=ft.Column(
                expand=True, spacing=0,
                controls=[self.contenedor_header, self.contenedor_cuerpo, self.contenedor_bottom_nav],
            ),
        )

        self.fila_raiz = ft.Row(
            expand=True, alignment=ft.MainAxisAlignment.CENTER, spacing=0,
            controls=[self.columna_centrada],
        )

        self.page.add(self.fila_raiz)
        self.page.on_resize = self._al_cambiar_tamano
        self._ajustar_ancho_responsivo()

        self._construir_drawer()
        self.ir_a("registrar")

    # ── Configuración de la página / ventana ────────────────────────────
    def _setup_page(self):
        p = self.page
        p.title = "Incident Logger"
        p.bgcolor = theme.BG
        p.padding = 0
        p.spacing = 0
        p.theme = ft.Theme(color_scheme=ft.ColorScheme(primary=theme.PRIMARY))
        p.window.width = 400
        p.window.height = 860
        p.window.min_width = 320
        p.window.min_height = 560

    def _ajustar_ancho_responsivo(self):
        ancho_disponible = self.page.width or theme.MAX_CONTENT_WIDTH
        self.columna_centrada.width = min(ancho_disponible, theme.MAX_CONTENT_WIDTH)

    def _al_cambiar_tamano(self, e):
        self._ajustar_ancho_responsivo()
        self.columna_centrada.update()

    # ── Menú lateral (hamburguesa) ──────────────────────────────────────
    def _construir_drawer(self):
        self._destinos_drawer = [
            ("registrar", ft.Icons.EDIT_NOTE_ROUNDED, "Registrar Incidente"),
            ("mis_incidentes", ft.Icons.ASSIGNMENT_OUTLINED, "Mis Incidentes"),
            ("analisis", ft.Icons.BAR_CHART_ROUNDED, "Análisis"),
        ]
        self.drawer = ft.NavigationDrawer(
            bgcolor=theme.CARD_BG,
            indicator_color=theme.PRIMARY,
            controls=[
                ft.Container(height=12),
                ft.Container(
                    padding=ft.Padding.symmetric(horizontal=16, vertical=8),
                    content=ft.Row(spacing=8, controls=[
                        ft.Container(width=26, height=26,
                                    content=ft.Image(src="logo.png", fit=ft.BoxFit.CONTAIN)),
                        ft.Text("Incident Logger", size=16, weight=ft.FontWeight.BOLD,
                                color=theme.PRIMARY),
                    ]),
                ),
                ft.Divider(height=1, color=theme.BORDER),
                *[
                    ft.NavigationDrawerDestination(label=etiqueta, icon=icono)
                    for _, icono, etiqueta in self._destinos_drawer
                ],
            ],
            on_change=self._al_elegir_drawer,
            on_dismiss=self._al_cerrar_drawer,
        )
        self.page.drawer = self.drawer

    async def _al_elegir_drawer(self, e):
        await self._cerrar_drawer_con_reintento()
        indice = e.control.selected_index
        self.ir_a(self._destinos_drawer[indice][0])

    def _al_cerrar_drawer(self, e):
        pass  # el drawer ya maneja su propio cierre; no se necesita lógica extra

    async def _abrir_menu(self, e):
        await self._abrir_drawer_con_reintento()

    async def _abrir_drawer_con_reintento(self):
        """
        A veces, justo después de recargar la app, el cliente todavía no
        terminó de registrar el listener de 'show_drawer' para la vista
        actual y la llamada expira (TimeoutException). Se reintenta una
        vez tras una breve pausa; si vuelve a fallar, se ignora en
        silencio (el usuario puede simplemente volver a tocar el botón)
        en vez de romper la app con un error sin manejar.
        """
        try:
            await self.page.show_drawer()
        except Exception:
            await asyncio.sleep(0.3)
            try:
                await self.page.show_drawer()
            except Exception:
                pass

    async def _cerrar_drawer_con_reintento(self):
        try:
            await self.page.close_drawer()
        except Exception:
            await asyncio.sleep(0.3)
            try:
                await self.page.close_drawer()
            except Exception:
                pass

    # ── Navegación entre vistas ──────────────────────────────────────────
    def ir_a(self, nombre_vista: str, apilar: bool = False):
        if apilar and self.vista_actual != nombre_vista:
            self.pila_navegacion.append(self.vista_actual)

        self.vista_actual = nombre_vista
        vista = self.vistas[nombre_vista]

        if hasattr(vista, "refrescar"):
            vista.refrescar()

        self.contenedor_cuerpo.content = vista

        variante_header = self.CONFIG_HEADER[nombre_vista]
        self.contenedor_header.content = crear_header(
            on_menu_click=self._abrir_menu,
            on_back_click=lambda e: self._volver(),
            on_share_click=self._al_compartir_desde_header,
            variante=variante_header,
        )

        tab_activa = self.TAB_POR_VISTA[nombre_vista]
        self.contenedor_bottom_nav.content = crear_bottom_nav(tab_activa, self._al_tocar_tab)

        self.page.update()

    def _volver(self):
        if self.pila_navegacion:
            anterior = self.pila_navegacion.pop()
            self.ir_a(anterior)
        else:
            self.ir_a("mis_incidentes")

    def _al_tocar_tab(self, clave: str):
        self.pila_navegacion.clear()
        if clave == "registrar":
            self.registrar_view.limpiar_formulario()
        self.ir_a(clave)

    # ── Callbacks de las vistas ──────────────────────────────────────────
    def _al_guardar_incidente(self):
        # Tras guardar/actualizar, refresca la lista para que se vea el cambio
        if hasattr(self.mis_incidentes_view, "refrescar"):
            self.mis_incidentes_view.refrescar()

    def _al_ver_incidente(self, incidente: dict):
        self.state.incidente_detalle_id = incidente["id"]
        self.ir_a("detalle", apilar=True)

    def _al_editar_incidente(self, incidente: dict):
        self.registrar_view.cargar_para_editar(incidente)
        self.pila_navegacion.clear()
        self.ir_a("registrar")

    async def _al_compartir_desde_header(self, e):
        if self.vista_actual == "detalle" and self.state.incidente_detalle_id:
            await self.detalle_view._al_exportar_imagen(e)


def main(page: ft.Page):
    db.inicializar_db()
    IncidentLoggerApp(page)


if __name__ == "__main__":
    ft.run(main=main)