"""
models/app_state.py
--------------------
Estado compartido entre vistas: qué incidente se está editando o
viendo en detalle, y los filtros activos de la lista. Patrón
singleton simple, igual que en Motor Sizing Pro.
"""


class AppState:
    _instancia = None

    def __new__(cls):
        if cls._instancia is None:
            cls._instancia = super().__new__(cls)
            cls._instancia._inicializar()
        return cls._instancia

    def _inicializar(self):
        self.incidente_editando_id: int | None = None  # None = creando uno nuevo
        self.incidente_detalle_id: int | None = None
        self.filtro_lista: str = "todos"
        self.busqueda_lista: str = ""
