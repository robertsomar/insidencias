"""
services/pdf_service.py
--------------------------
Función 5: Exportar a PDF.
Entrada: ID del incidente. Proceso: obtiene los datos, genera un PDF
con formato de reporte. Salida: ruta del archivo PDF generado.
"""

from pathlib import Path

from fpdf import FPDF

import theme
from database import db

CARPETA_EXPORTADOS = Path.home() / "IncidentLogger_Exportados"


def _color_rgb(hex_color: str) -> tuple[int, int, int]:
    hex_color = hex_color.lstrip("#")
    return tuple(int(hex_color[i:i + 2], 16) for i in (0, 2, 4))


def exportar_incidente_a_pdf(id_incidente: int, carpeta_destino: Path = None,
                             ruta_salida: Path = None) -> tuple[bool, str]:
    """
    Genera un PDF con el detalle completo de un incidente.

    carpeta_destino: si se pasa (en móvil, la carpeta temporal de la
    app obtenida con page.storage_paths), se usa esa. Si no, se usa
    la carpeta de escritorio por defecto (CARPETA_EXPORTADOS).

    ruta_salida: si se pasa (ej. la ruta exacta que el usuario eligió
    en un diálogo "Guardar como", con su propio nombre de archivo),
    se usa esa ruta tal cual, ignorando carpeta_destino.
    """
    incidente = db.obtener_incidente(id_incidente)
    if not incidente:
        return False, "Incidente no encontrado"

    if ruta_salida is not None:
        ruta_salida = Path(ruta_salida)
        ruta_salida.parent.mkdir(parents=True, exist_ok=True)
    else:
        carpeta = carpeta_destino or CARPETA_EXPORTADOS
        carpeta.mkdir(parents=True, exist_ok=True)
        ruta_salida = carpeta / f"{incidente['codigo']}.pdf"

    rojo = _color_rgb(theme.PRIMARY)
    gris_texto = _color_rgb(theme.TEXT_SECONDARY)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    # Encabezado
    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*rojo)
    pdf.cell(0, 10, "INCIDENT LOGGER", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 22)
    pdf.cell(0, 12, incidente["codigo"], new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*rojo)
    pdf.cell(0, 8, f"Severidad: {incidente['severidad']}  |  Estado: {incidente['estado']}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    def seccion(titulo: str, contenido: str):
        pdf.set_font("Helvetica", "B", 12)
        pdf.set_text_color(*rojo)
        pdf.cell(0, 8, titulo, new_x="LMARGIN", new_y="NEXT")
        pdf.set_font("Helvetica", "", 11)
        pdf.set_text_color(*gris_texto)
        pdf.multi_cell(0, 6, contenido or "-")
        pdf.ln(3)

    seccion("Línea / Planta", incidente["linea"])
    seccion("Estación / Equipo", incidente["estacion"])
    seccion("Fecha y hora de reporte", incidente["fecha_reporte"])
    seccion("Descripción del incidente", incidente["descripcion"])
    seccion("Causa preliminar", incidente["causa"])
    if incidente["causa_raiz"]:
        seccion("Causa raíz identificada", incidente["causa_raiz"])
    if incidente["acciones"]:
        seccion("Acciones tomadas (contención)", incidente["acciones"])
    if incidente["fecha_resolucion"]:
        seccion("Fecha de resolución", incidente["fecha_resolucion"])

    pdf.set_font("Helvetica", "I", 9)
    pdf.set_text_color(*_color_rgb(theme.TEXT_MUTED))
    pdf.cell(0, 6, "Generado por Incident Logger", new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(ruta_salida))
    return True, str(ruta_salida)


def exportar_reporte_general(carpeta_destino: Path = None) -> tuple[bool, str]:
    """Genera un PDF con el resumen general (totales + lista de incidentes
    del mes actual), para el botón 'Exportar Reporte' del dashboard."""
    import datetime

    carpeta = carpeta_destino or CARPETA_EXPORTADOS
    carpeta.mkdir(parents=True, exist_ok=True)
    marca_tiempo = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    ruta_salida = carpeta / f"Reporte_Incidentes_{marca_tiempo}.pdf"

    resumen = db.resumen_general()
    incidentes = db.listar_incidentes()

    rojo = _color_rgb(theme.PRIMARY)
    gris_texto = _color_rgb(theme.TEXT_SECONDARY)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)

    pdf.set_font("Helvetica", "B", 18)
    pdf.set_text_color(*rojo)
    pdf.cell(0, 10, "INCIDENT LOGGER - Reporte General", new_x="LMARGIN", new_y="NEXT")
    pdf.set_font("Helvetica", "", 10)
    pdf.set_text_color(*gris_texto)
    pdf.cell(0, 6, f"Generado el {datetime.datetime.now().strftime('%d/%m/%Y %H:%M')}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(*rojo)
    pdf.cell(0, 8,
             f"Total: {resumen['total']}   Críticos: {resumen['criticos']}   "
             f"Altos: {resumen['altos']}   Resueltos: {resumen['resueltos']}",
             new_x="LMARGIN", new_y="NEXT")
    pdf.ln(4)

    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(*gris_texto)
    pdf.cell(60, 8, "Código", border="B")
    pdf.cell(30, 8, "Severidad", border="B")
    pdf.cell(35, 8, "Estado", border="B")
    pdf.cell(0, 8, "Línea", border="B", new_x="LMARGIN", new_y="NEXT")

    pdf.set_font("Helvetica", "", 10)
    for inc in incidentes:
        pdf.cell(60, 7, inc["codigo"])
        pdf.cell(30, 7, inc["severidad"])
        pdf.cell(35, 7, inc["estado"])
        pdf.cell(0, 7, inc["linea"][:28], new_x="LMARGIN", new_y="NEXT")

    pdf.output(str(ruta_salida))
    return True, str(ruta_salida)