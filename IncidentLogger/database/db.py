"""
database/db.py
--------------
Acceso a SQLite para los incidentes registrados. Funciones simples
(sin ORM) para mantener la app liviana y fácil de seguir.
"""

import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "incident_logger.db"


def _conectar() -> sqlite3.Connection:
    conexion = sqlite3.connect(DB_PATH)
    conexion.row_factory = sqlite3.Row
    return conexion


def inicializar_db():
    """Crea la tabla de incidentes si no existe. Llamar al iniciar la app."""
    with _conectar() as con:
        con.execute("""
            CREATE TABLE IF NOT EXISTS incidentes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                codigo TEXT NOT NULL UNIQUE,
                severidad TEXT NOT NULL,
                linea TEXT NOT NULL,
                estacion TEXT NOT NULL,
                descripcion TEXT NOT NULL,
                causa TEXT NOT NULL,
                acciones TEXT DEFAULT '',
                causa_raiz TEXT DEFAULT '',
                estado TEXT NOT NULL DEFAULT 'Abierto',
                fotos TEXT DEFAULT '',
                fecha_reporte TEXT NOT NULL,
                fecha_resolucion TEXT
            )
        """)
        con.commit()


def _siguiente_codigo() -> str:
    """Genera un código tipo INC-YYYYMMDD-NNN (correlativo por día)."""
    import datetime
    hoy = datetime.datetime.now().strftime("%Y%m%d")
    with _conectar() as con:
        fila = con.execute(
            "SELECT COUNT(*) FROM incidentes WHERE codigo LIKE ?",
            (f"INC-{hoy}-%",),
        ).fetchone()
        correlativo = fila[0] + 1
    return f"INC-{hoy}-{correlativo:03d}"


def crear_incidente(datos: dict) -> str:
    """Inserta un incidente nuevo (estado inicial: Abierto) y devuelve su código."""
    codigo = _siguiente_codigo()
    with _conectar() as con:
        con.execute("""
            INSERT INTO incidentes
                (codigo, severidad, linea, estacion, descripcion, causa,
                 acciones, causa_raiz, estado, fotos, fecha_reporte)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, 'Abierto', ?, datetime('now', 'localtime'))
        """, (
            codigo, datos["severidad"], datos["linea"], datos["estacion"],
            datos["descripcion"], datos["causa"], datos.get("acciones", ""),
            datos.get("causa_raiz", ""), datos.get("fotos", ""),
        ))
        con.commit()
    return codigo


def listar_incidentes(busqueda: str = "", filtro: str = "todos") -> list[dict]:
    """
    Devuelve incidentes, más recientes primero.
    filtro: "todos" | "alta" (Crítico/Alto) | "revision" (En Revisión) | "resueltos"
    """
    condiciones = []
    parametros = []

    if busqueda:
        condiciones.append("(codigo LIKE ? OR descripcion LIKE ? OR estacion LIKE ?)")
        comodin = f"%{busqueda}%"
        parametros.extend([comodin, comodin, comodin])

    if filtro == "alta":
        condiciones.append("severidad IN ('Crítico', 'Alto')")
    elif filtro == "revision":
        condiciones.append("estado = 'En Revisión'")
    elif filtro == "resueltos":
        condiciones.append("estado IN ('Resuelto', 'Cerrado')")

    where = f"WHERE {' AND '.join(condiciones)}" if condiciones else ""

    with _conectar() as con:
        filas = con.execute(
            f"SELECT * FROM incidentes {where} ORDER BY id DESC", parametros
        ).fetchall()
        return [dict(f) for f in filas]


def obtener_incidente(id_incidente: int) -> dict | None:
    with _conectar() as con:
        fila = con.execute(
            "SELECT * FROM incidentes WHERE id = ?", (id_incidente,)
        ).fetchone()
        return dict(fila) if fila else None


def actualizar_incidente(id_incidente: int, datos: dict):
    """Actualiza los datos de un incidente. Si no se pasa estado nuevo,
    y el incidente estaba 'Abierto', pasa automáticamente a 'En Revisión'
    (según el ciclo de vida: Editar -> Actualizar = En Revisión)."""
    actual = obtener_incidente(id_incidente)
    if actual is None:
        return

    nuevo_estado = datos.get("estado")
    if not nuevo_estado:
        nuevo_estado = "En Revisión" if actual["estado"] == "Abierto" else actual["estado"]

    with _conectar() as con:
        con.execute("""
            UPDATE incidentes SET
                severidad = ?, linea = ?, estacion = ?, descripcion = ?,
                causa = ?, acciones = ?, causa_raiz = ?, estado = ?, fotos = ?
            WHERE id = ?
        """, (
            datos["severidad"], datos["linea"], datos["estacion"],
            datos["descripcion"], datos["causa"], datos.get("acciones", ""),
            datos.get("causa_raiz", actual["causa_raiz"]), nuevo_estado,
            datos.get("fotos", actual["fotos"]), id_incidente,
        ))
        con.commit()


def cambiar_estado(id_incidente: int, nuevo_estado: str):
    with _conectar() as con:
        if nuevo_estado == "Resuelto":
            con.execute(
                "UPDATE incidentes SET estado = ?, fecha_resolucion = datetime('now', 'localtime') "
                "WHERE id = ?", (nuevo_estado, id_incidente),
            )
        else:
            con.execute("UPDATE incidentes SET estado = ? WHERE id = ?",
                        (nuevo_estado, id_incidente))
        con.commit()


def eliminar_incidente(id_incidente: int):
    with _conectar() as con:
        con.execute("DELETE FROM incidentes WHERE id = ?", (id_incidente,))
        con.commit()


def contar_incidentes() -> int:
    with _conectar() as con:
        return con.execute("SELECT COUNT(*) FROM incidentes").fetchone()[0]


def resumen_general() -> dict:
    """Totales para el dashboard de Análisis."""
    with _conectar() as con:
        total = con.execute("SELECT COUNT(*) FROM incidentes").fetchone()[0]
        criticos = con.execute(
            "SELECT COUNT(*) FROM incidentes WHERE severidad = 'Crítico'"
        ).fetchone()[0]
        altos = con.execute(
            "SELECT COUNT(*) FROM incidentes WHERE severidad = 'Alto'"
        ).fetchone()[0]
        resueltos = con.execute(
            "SELECT COUNT(*) FROM incidentes WHERE estado IN ('Resuelto', 'Cerrado')"
        ).fetchone()[0]
        return {"total": total, "criticos": criticos, "altos": altos, "resueltos": resueltos}


def conteo_por_causa() -> list[tuple[str, int]]:
    with _conectar() as con:
        filas = con.execute("""
            SELECT causa, COUNT(*) as cantidad FROM incidentes
            GROUP BY causa ORDER BY cantidad DESC
        """).fetchall()
        return [(f["causa"], f["cantidad"]) for f in filas]


def conteo_por_linea() -> list[tuple[str, int]]:
    with _conectar() as con:
        filas = con.execute("""
            SELECT linea, COUNT(*) as cantidad FROM incidentes
            GROUP BY linea ORDER BY linea
        """).fetchall()
        return [(f["linea"], f["cantidad"]) for f in filas]


def tiempo_promedio_resolucion_minutos() -> float | None:
    """Promedio de minutos entre fecha_reporte y fecha_resolucion de los
    incidentes ya resueltos. None si todavía no hay ninguno resuelto."""
    with _conectar() as con:
        filas = con.execute("""
            SELECT fecha_reporte, fecha_resolucion FROM incidentes
            WHERE fecha_resolucion IS NOT NULL
        """).fetchall()
    if not filas:
        return None

    import datetime
    total_minutos = 0.0
    for fila in filas:
        try:
            inicio = datetime.datetime.strptime(fila["fecha_reporte"], "%Y-%m-%d %H:%M:%S")
            fin = datetime.datetime.strptime(fila["fecha_resolucion"], "%Y-%m-%d %H:%M:%S")
            total_minutos += (fin - inicio).total_seconds() / 60
        except (ValueError, TypeError):
            continue
    return round(total_minutos / len(filas), 0) if filas else None


def linea_con_mas_incidentes_recientes() -> tuple[str, int] | None:
    """Línea con más incidentes registrados (para el insight de 'punto crítico')."""
    conteo = conteo_por_linea()
    if not conteo:
        return None
    return max(conteo, key=lambda par: par[1])
