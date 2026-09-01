"""
services/analisis_service.py
-------------------------------
Función 7: Generar Análisis.
Entrada: todos los incidentes (vía SQLite). Proceso: contar por
severidad, causa y línea. Salida: contadores y datos listos para
graficar en la pantalla de Análisis.
"""

from database import db


def generar_resumen() -> dict:
    """Contadores generales + series para los gráficos + insights."""
    resumen = db.resumen_general()
    por_causa = db.conteo_por_causa()
    por_linea = db.conteo_por_linea()
    tiempo_promedio = db.tiempo_promedio_resolucion_minutos()
    linea_critica = db.linea_con_mas_incidentes_recientes()

    return {
        "total": resumen["total"],
        "criticos": resumen["criticos"],
        "altos": resumen["altos"],
        "resueltos": resumen["resueltos"],
        "por_causa": por_causa,
        "por_linea": por_linea,
        "tiempo_promedio_minutos": tiempo_promedio,
        "linea_con_mas_incidentes": linea_critica,
    }
