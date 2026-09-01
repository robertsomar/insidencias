"""
theme.py
--------
Paleta de colores y constantes visuales de Incident Logger.
Tema rojo/burdeos industrial, igual al diseño original.
"""

# ── Paleta de colores ────────────────────────────────────────────────────
PRIMARY = "#C1272D"           # Rojo/burdeos principal: título, botones, acentos
PRIMARY_DARK = "#8F1D22"      # Rojo oscuro: hover / textos fuertes
PRIMARY_LIGHT = "#F6D9D8"     # Rosa muy claro: bordes de tarjetas, fondos suaves

BG = "#FBF3F2"                 # Fondo general (rosa-crema muy claro)
CARD_BG = "#FFFFFF"            # Fondo de tarjetas
INPUT_BG = "#F2ECEB"           # Fondo de campos de entrada

TEXT_PRIMARY = "#231B1B"       # Texto principal
TEXT_SECONDARY = "#6E6260"     # Texto secundario
TEXT_MUTED = "#9C918F"         # Texto terciario / placeholders
TEXT_ON_PRIMARY = "#FFFFFF"    # Texto sobre fondo rojo

BORDER = "#F0D9D8"             # Bordes sutiles de tarjetas

# ── Severidad / Estado ───────────────────────────────────────────────────
CRITICO = "#C1272D"            # Crítico / Alta
CRITICO_BG = "#FBDADA"
ALTA = "#EA7317"               # Alta severidad (naranja)
ALTA_BG = "#FCE3D0"
MEDIA = "#D18E00"              # Media severidad (ámbar)
MEDIA_BG = "#FBEFC8"
BAJA = "#B8860B"               # Baja severidad (amarillo oscuro)
BAJA_BG = "#F7F0C8"
SUCCESS = "#16A34A"            # Resuelto / éxito
SUCCESS_BG = "#DCFCE7"
INFO = "#2563EB"               # Info / tips
INFO_BG = "#DBEAFE"
WARNING = "#D97706"

# ── Tipografía ─────────────────────────────────────────────────────────
SIZE_TITLE = 19
SIZE_SUBTITLE = 15
SIZE_LABEL = 11
SIZE_VALUE_LG = 24
SIZE_BODY = 13
SIZE_SMALL = 11

# ── Radios y espaciados ───────────────────────────────────────────────────
RADIUS_CARD = 14
RADIUS_INPUT = 10
RADIUS_PILL = 24
PAGE_PADDING = 18

# ── Layout responsivo ──────────────────────────────────────────────────────
MAX_CONTENT_WIDTH = 480

# ── Colores por severidad (para usar dinámicamente) ─────────────────────
COLORES_SEVERIDAD = {
    "Crítico": (CRITICO, CRITICO_BG),
    "Alto": (ALTA, ALTA_BG),
    "Medio": (MEDIA, MEDIA_BG),
    "Bajo": (BAJA, BAJA_BG),
}

COLORES_ESTADO = {
    "Abierto": (PRIMARY, PRIMARY_LIGHT),
    "En Revisión": (MEDIA, MEDIA_BG),
    "Resuelto": (SUCCESS, SUCCESS_BG),
    "Cerrado": (TEXT_MUTED, "#EDEAEA"),
}
