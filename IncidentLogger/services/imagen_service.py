
"""
services/imagen_service.py
-----------------------------
Función 6: Exportar a Imagen.
Entrada: ID del incidente. Proceso: obtiene los datos, dibuja una
tarjeta-resumen tipo "compartir en redes" y la guarda como PNG.
Salida: ruta del archivo PNG generado.
"""

import textwrap
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

import theme
from database import db

CARPETA_EXPORTADOS = Path.home() / "IncidentLogger_Exportados"
CARPETA_FUENTES = Path(__file__).parent.parent / "assets" / "fonts"

ANCHO, ALTO = 900, 1100


def _fuente(nombre: str, tamano: int) -> ImageFont.FreeTypeFont:
    try:
        return ImageFont.truetype(str(CARPETA_FUENTES / nombre), tamano)
    except Exception:
        return ImageFont.load_default()


def exportar_incidente_a_imagen(id_incidente: int, carpeta_destino: Path = None) -> tuple[bool, str]:
    incidente = db.obtener_incidente(id_incidente)
    if not incidente:
        return False, "Incidente no encontrado"

    carpeta = carpeta_destino or CARPETA_EXPORTADOS
    carpeta.mkdir(parents=True, exist_ok=True)
    ruta_salida = carpeta / f"{incidente['codigo']}.png"

    color_severidad, fondo_severidad = theme.COLORES_SEVERIDAD.get(
        incidente["severidad"], (theme.PRIMARY, theme.PRIMARY_LIGHT)
    )

    img = Image.new("RGB", (ANCHO, ALTO), theme.BG)
    d = ImageDraw.Draw(img)

    fuente_titulo = _fuente("DejaVuSans-Bold.ttf", 40)
    fuente_subtitulo = _fuente("DejaVuSans-Bold.ttf", 26)
    fuente_label = _fuente("DejaVuSans-Bold.ttf", 18)
    fuente_texto = _fuente("DejaVuSans.ttf", 20)

    margen = 50
    y = 40

    # Encabezado
    d.text((margen, y), "INCIDENT LOGGER", font=fuente_label, fill=theme.PRIMARY)
    y += 40

    # Badge de severidad
    texto_badge = incidente["severidad"].upper()
    caja_badge = d.textbbox((0, 0), texto_badge, font=fuente_label)
    ancho_badge = caja_badge[2] - caja_badge[0] + 30
    d.rounded_rectangle([margen, y, margen + ancho_badge, y + 36], radius=8,
                        fill=fondo_severidad)
    d.text((margen + 15, y + 8), texto_badge, font=fuente_label, fill=color_severidad)
    y += 55

    # Código del incidente
    d.text((margen, y), incidente["codigo"], font=fuente_titulo, fill=theme.PRIMARY)
    y += 70

    def campo(etiqueta: str, valor: str, alto_extra: int = 0):
        nonlocal y
        d.text((margen, y), etiqueta.upper(), font=fuente_label, fill=theme.TEXT_MUTED)
        y += 26
        lineas = textwrap.wrap(valor or "-", width=60)
        for linea in lineas:
            d.text((margen, y), linea, font=fuente_texto, fill=theme.TEXT_PRIMARY)
            y += 28
        y += 20 + alto_extra

    campo("Línea / Planta", incidente["linea"])
    campo("Estación", incidente["estacion"])
    campo("Fecha de reporte", incidente["fecha_reporte"])
    campo("Descripción", incidente["descripcion"])
    campo("Causa preliminar", incidente["causa"])
    if incidente["causa_raiz"]:
        campo("Causa raíz identificada", incidente["causa_raiz"])

    # Pie
    d.rectangle([0, ALTO - 4, ANCHO, ALTO], fill=theme.PRIMARY)

    img.save(ruta_salida)
    return True, str(ruta_salida)