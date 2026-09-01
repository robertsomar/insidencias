"""
models/constantes.py
-----------------------
Listas de opciones fijas usadas en toda la app (formulario de
registro, filtros, badges). Centralizadas aquí para que un cambio
(agregar una línea de producción nueva, por ejemplo) se haga en un
solo lugar.
"""

SEVERIDADES = ["Bajo", "Medio", "Alto", "Crítico"]

LINEAS_PRODUCCION = ["Línea A", "Línea B", "Línea C", "Línea D", "Línea de Ensamble B-04"]

CAUSAS = ["Eléctrica", "Mecánica", "Operativa", "Seguridad", "Otros"]

# Ciclo de vida de un incidente (en orden). "Abierto" es el estado
# inicial al crear; el resto se recorre con Editar/Actualizar/Resolver/Cerrar.
ESTADOS = ["Abierto", "En Revisión", "Resuelto", "Cerrado"]
