"""
services/incidente_service.py
--------------------------------
Lógica de negocio de incidentes: validación de formulario y las
funciones principales (Registrar, Obtener, Actualizar, Eliminar),
todas apoyadas en database/db.py.

Módulo separado de la UI a propósito -> se puede testear sin Flet.
"""

from database import db


def validar_formulario(severidad: str, linea: str, estacion: str,
                       descripcion: str, causa: str) -> tuple[bool, set[str]]:
    """
    Valida los 5 campos obligatorios del formulario de incidente:
        1) Severidad seleccionada
        2) Línea seleccionada
        3) Estación con texto
        4) Descripción con texto
        5) Causa seleccionada

    Devuelve (es_valido, campos_invalidos) donde campos_invalidos es
    el conjunto de claves a resaltar en rojo en el formulario.
    """
    campos_invalidos = set()

    if not severidad:
        campos_invalidos.add("severidad")
    if not linea:
        campos_invalidos.add("linea")
    if not (estacion or "").strip():
        campos_invalidos.add("estacion")
    if not (descripcion or "").strip():
        campos_invalidos.add("descripcion")
    if not causa:
        campos_invalidos.add("causa")

    return (len(campos_invalidos) == 0), campos_invalidos


# ── Función 1: Registrar Incidente ──────────────────────────────────────
def registrar_incidente(datos: dict) -> tuple[bool, str, str]:
    """
    Entrada: datos del formulario (dict).
    Proceso: valida, genera ID (lo hace db.crear_incidente), guarda en SQLite.
    Salida: (ok, mensaje, codigo_generado)
    """
    es_valido, _ = validar_formulario(
        datos.get("severidad", ""), datos.get("linea", ""),
        datos.get("estacion", ""), datos.get("descripcion", ""),
        datos.get("causa", ""),
    )
    if not es_valido:
        return False, "⚠️ Por favor completa todos los campos obligatorios", ""

    codigo = db.crear_incidente(datos)
    return True, "✓ Incidente guardado correctamente", codigo


# ── Función 2: Obtener Incidentes ───────────────────────────────────────
def obtener_incidentes(busqueda: str = "", filtro: str = "todos") -> list[dict]:
    """Entrada: filtros. Proceso: consulta SQLite. Salida: lista de incidentes."""
    return db.listar_incidentes(busqueda, filtro)


def obtener_incidente_por_id(id_incidente: int) -> dict | None:
    return db.obtener_incidente(id_incidente)


# ── Función 3: Actualizar Incidente ─────────────────────────────────────
def actualizar_incidente(id_incidente: int, datos: dict) -> tuple[bool, str]:
    """Entrada: ID + datos nuevos. Proceso: valida y actualiza. Salida: (ok, mensaje)."""
    es_valido, _ = validar_formulario(
        datos.get("severidad", ""), datos.get("linea", ""),
        datos.get("estacion", ""), datos.get("descripcion", ""),
        datos.get("causa", ""),
    )
    if not es_valido:
        return False, "⚠️ Por favor completa todos los campos obligatorios"

    db.actualizar_incidente(id_incidente, datos)
    return True, "✓ Incidente actualizado correctamente"


def marcar_resuelto(id_incidente: int):
    """Función 4 del ciclo de vida: Resolver."""
    db.cambiar_estado(id_incidente, "Resuelto")


def cerrar_incidente(id_incidente: int):
    """Función 5 del ciclo de vida: Cerrar."""
    db.cambiar_estado(id_incidente, "Cerrado")


# ── Función 4: Eliminar Incidente ───────────────────────────────────────
def eliminar_incidente(id_incidente: int) -> tuple[bool, str]:
    """Entrada: ID. Proceso: elimina de SQLite (la confirmación la hace la UI)."""
    db.eliminar_incidente(id_incidente)
    return True, "Incidente eliminado"
