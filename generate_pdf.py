"""
generate_pdf.py
---------------
Genera un PDF con diseño para el informe de análisis HMI Analyzer.
Uso: importar generate_hmi_pdf() desde app_light.py
"""

import io
import base64
from datetime import datetime

from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.lib.enums import TA_LEFT, TA_CENTER, TA_RIGHT
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle,
    HRFlowable, Image, KeepTogether, PageBreak
)
from reportlab.pdfgen import canvas as rl_canvas
from reportlab.platypus.flowables import Flowable


# ── Paleta ────────────────────────────────────────────────────────────────────
AZUL          = colors.HexColor("#1e88e5")
AZUL_OSCURO   = colors.HexColor("#1565c0")
GRIS_OSCURO   = colors.HexColor("#212121")
GRIS_MEDIO    = colors.HexColor("#616161")
GRIS_CLARO    = colors.HexColor("#F5F5F5")
VERDE         = colors.HexColor("#2e7d32")
AMARILLO      = colors.HexColor("#f9a825")
ROJO          = colors.HexColor("#c62828")
BLANCO        = colors.white
LINEA         = colors.HexColor("#E0E0E0")

W, H = A4   # 595 x 842 pt


# ── Helpers de color por score ────────────────────────────────────────────────
def score_color(score):
    if score >= 7:
        return VERDE
    elif score >= 5:
        return AMARILLO
    return ROJO


def score_label(score):
    if score >= 7:
        return "Sólida"
    elif score >= 5:
        return "Mejorable"
    return "Crítica"


# ── Barra de progreso como Flowable ──────────────────────────────────────────
class ScoreBar(Flowable):
    def __init__(self, score, width=120*mm, height=6):
        super().__init__()
        self.score = score
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        # fondo
        c.setFillColor(LINEA)
        c.roundRect(0, 0, self.width, self.height, self.height / 2, fill=1, stroke=0)
        # relleno
        filled = self.width * (self.score / 10)
        c.setFillColor(score_color(self.score))
        c.roundRect(0, 0, filled, self.height, self.height / 2, fill=1, stroke=0)

    def wrap(self, availW, availH):
        return self.width, self.height + 2


# ── Cabecera y pie en cada página ─────────────────────────────────────────────
class HeaderFooterCanvas(rl_canvas.Canvas):
    def __init__(self, *args, logo_b64=None, **kwargs):
        super().__init__(*args, **kwargs)
        self._saved_page_states = []
        self.logo_b64 = logo_b64

    def showPage(self):
        self._saved_page_states.append(dict(self.__dict__))
        self._startPage()

    def save(self):
        num_pages = len(self._saved_page_states)
        for state in self._saved_page_states:
            self.__dict__.update(state)
            self.draw_header_footer(num_pages)
            super().showPage()
        super().save()

    def draw_header_footer(self, total):
        page = self._pageNumber

        # ── Header ────────────────────────────────────────────
        self.setFillColor(AZUL)
        self.rect(0, H - 14*mm, W, 14*mm, fill=1, stroke=0)

        # Logo (si existe)
        if self.logo_b64 and page > 1:
            try:
                logo_data = base64.b64decode(self.logo_b64)
                img_buf = io.BytesIO(logo_data)
                self.drawImage(img_buf, 12*mm, H - 12*mm, width=20*mm, height=10*mm,
                               preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(BLANCO)
        self.drawRightString(W - 12*mm, H - 9*mm, "HMI Analyzer · The Cognitive Joint™")

        # ── Footer ────────────────────────────────────────────
        self.setFillColor(GRIS_CLARO)
        self.rect(0, 0, W, 10*mm, fill=1, stroke=0)
        self.setFillColor(GRIS_MEDIO)
        self.setFont("Helvetica", 7)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.drawString(12*mm, 3.5*mm, f"Informe generado el {fecha}")
        self.drawRightString(W - 12*mm, 3.5*mm, f"Página {page} de {total}")


# ── Estilos de texto ──────────────────────────────────────────────────────────
def make_styles():
    base = dict(fontName="Helvetica", fontSize=10, leading=14,
                textColor=GRIS_OSCURO, spaceAfter=4)

    return {
        "titulo_portada": ParagraphStyle("titulo_portada",
            fontName="Helvetica-Bold", fontSize=28, leading=34,
            textColor=BLANCO, alignment=TA_LEFT),
        "sub_portada": ParagraphStyle("sub_portada",
            fontName="Helvetica", fontSize=13, leading=18,
            textColor=colors.HexColor("#BBDEFB"), alignment=TA_LEFT),
        "meta_portada": ParagraphStyle("meta_portada",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=colors.HexColor("#90CAF9"), alignment=TA_LEFT),
        "seccion": ParagraphStyle("seccion",
            fontName="Helvetica-Bold", fontSize=14, leading=18,
            textColor=AZUL, spaceBefore=10, spaceAfter=6),
        "puente_titulo": ParagraphStyle("puente_titulo",
            fontName="Helvetica-Bold", fontSize=11, leading=14,
            textColor=GRIS_OSCURO, spaceBefore=2),
        "puente_num": ParagraphStyle("puente_num",
            fontName="Helvetica", fontSize=8, leading=11,
            textColor=GRIS_MEDIO),
        "score_txt": ParagraphStyle("score_txt",
            fontName="Helvetica-Bold", fontSize=16, leading=20,
            textColor=GRIS_OSCURO),
        "label_txt": ParagraphStyle("label_txt",
            fontName="Helvetica-Bold", fontSize=9, leading=12),
        "body": ParagraphStyle("body", **base),
        "body_small": ParagraphStyle("body_small",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=GRIS_MEDIO, spaceAfter=4),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=9, leading=14,
            textColor=GRIS_OSCURO, leftIndent=10, spaceAfter=3,
            bulletFontName="Helvetica", bulletFontSize=9,
            bulletIndent=0),
        "nota": ParagraphStyle("nota",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=GRIS_MEDIO),
    }


# ── Función principal ─────────────────────────────────────────────────────────
def generate_hmi_pdf(
    image_bytes: bytes,
    scores: list,          # list of int, len == 8
    bridge_names: list,    # list of str, len == 8
    bridge_summaries: list,# list of str, len == 8
    average_score: float,
    final_summary: str,
    contexto_uso: str,
    impacto_error: str,
    logo_b64: str = None,  # base64 del logo SVG/PNG (opcional)
) -> bytes:
    """Devuelve los bytes del PDF generado."""

    buf = io.BytesIO()
    st = make_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=18*mm, rightMargin=18*mm,
        topMargin=22*mm, bottomMargin=18*mm,
        title="Informe HMI Analyzer",
        author="HMI Analyzer · bigD",
    )

    story = []

    # ══════════════════════════════════════════════════════════
    # PORTADA
    # ══════════════════════════════════════════════════════════
    # Bloque azul de portada (simulado con tabla de fondo)
    fecha = datetime.now().strftime("%d de %B de %Y")

    portada_contenido = [
        Spacer(1, 30*mm),
        Paragraph("HMI Analyzer", st["titulo_portada"]),
        Spacer(1, 4*mm),
        Paragraph("Informe de evaluación cognitiva", st["sub_portada"]),
        Spacer(1, 3*mm),
        Paragraph("Basado en los <b>8 Puentes de The Cognitive Joint™</b>", st["sub_portada"]),
        Spacer(1, 14*mm),
        Paragraph(f"Fecha: {fecha}", st["meta_portada"]),
        Paragraph(f"Uso: {contexto_uso}", st["meta_portada"]),
        Paragraph(f"Impacto: {impacto_error}", st["meta_portada"]),
    ]

    tabla_portada = Table(
        [[portada_contenido]],
        colWidths=[W - 36*mm],
        rowHeights=[120*mm]
    )
    tabla_portada.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING",  (0, 0), (-1, -1), 14*mm),
        ("RIGHTPADDING", (0, 0), (-1, -1), 10*mm),
        ("TOPPADDING",   (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING",(0, 0), (-1, -1), 10*mm),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tabla_portada)
    story.append(Spacer(1, 8*mm))

    # Imagen analizada en portada
    try:
        img_buf = io.BytesIO(image_bytes)
        img = Image(img_buf, width=W - 36*mm, height=60*mm)
        img.hAlign = "CENTER"
        story.append(img)
    except Exception:
        pass

    story.append(Spacer(1, 6*mm))

    # Score global en portada
    color_global = score_color(average_score)
    label_global = score_label(average_score)

    score_row = Table(
        [[
            Paragraph(f"Score global", st["body_small"]),
            Paragraph(f"<font color='#{color_global.hexval()[2:]}' size=26><b>{average_score}/10</b></font>  "
                      f"<font color='#{color_global.hexval()[2:]}' size=11><b>— {label_global}</b></font>",
                      st["body"]),
        ]],
        colWidths=[40*mm, W - 76*mm],
    )
    score_row.setStyle(TableStyle([
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING", (0, 0), (-1, -1), 0),
    ]))
    story.append(score_row)
    story.append(ScoreBar(average_score, width=W - 36*mm, height=8))
    story.append(Spacer(1, 4*mm))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # TABLA RESUMEN DE PUNTUACIONES
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("Resumen por puentes", st["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    tabla_data = [["Puente", "Nombre", "Puntuación", "Valoración"]]
    for i, (name, score) in enumerate(zip(bridge_names, scores)):
        num = name.split("–")[0].strip()
        nom = name.split("–")[1].strip().capitalize() if "–" in name else name
        clr = score_color(score)
        lbl = score_label(score)
        tabla_data.append([
            Paragraph(f"<font size=8 color='#616161'>{num}</font>", st["body"]),
            Paragraph(f"<b>{nom}</b>", st["body"]),
            Paragraph(f"<b>{score}/10</b>", st["body"]),
            Paragraph(f"<font color='#{clr.hexval()[2:]}'><b>{lbl}</b></font>", st["body"]),
        ])

    tabla_scores = Table(
        tabla_data,
        colWidths=[30*mm, 70*mm, 30*mm, 30*mm],
        repeatRows=1,
    )
    tabla_scores.setStyle(TableStyle([
        # Cabecera
        ("BACKGROUND", (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR",  (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",   (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",   (0, 0), (-1, 0), 9),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        # Filas alternas
        *[("BACKGROUND", (0, i), (-1, i), GRIS_CLARO)
          for i in range(2, len(tabla_data), 2)],
        ("ROWBACKGROUNDS", (0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        # General
        ("FONTNAME",   (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",   (0, 1), (-1, -1), 9),
        ("TOPPADDING", (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("GRID", (0, 0), (-1, -1), 0.5, LINEA),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tabla_scores)
    story.append(Spacer(1, 8*mm))

    # ══════════════════════════════════════════════════════════
    # DETALLE POR PUENTE
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("Análisis por puente", st["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    for i, (name, score, summary_text) in enumerate(
            zip(bridge_names, scores, bridge_summaries)):

        num_txt = name.split("–")[0].strip() if "–" in name else f"PUENTE {i+1:02d}"
        nom_txt = name.split("–")[1].strip().capitalize() if "–" in name else name
        clr = score_color(score)
        lbl = score_label(score)

        # Contenido izquierdo
        left = [
            Paragraph(num_txt, st["puente_num"]),
            Paragraph(nom_txt, st["puente_titulo"]),
            Spacer(1, 2),
            Paragraph(
                f"<font color='#{clr.hexval()[2:]}' size=18><b>{score}/10</b></font>"
                f"  <font color='#{clr.hexval()[2:]}' size=9><b>{lbl}</b></font>",
                st["body"]
            ),
            ScoreBar(score, width=42*mm, height=5),
        ]

        # Contenido derecho (resumen)
        right = [Paragraph(summary_text, st["body"])]

        fila = Table(
            [[left, right]],
            colWidths=[52*mm, W - 36*mm - 52*mm - 6*mm],
        )
        fila.setStyle(TableStyle([
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING",  (0, 0), (-1, -1), 0),
            ("RIGHTPADDING", (0, 0), (-1, -1), 0),
            ("TOPPADDING",   (0, 0), (-1, -1), 0),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 0),
            # línea izquierda de color
            ("LINEAFTER", (0, 0), (0, 0), 2, clr),
            ("RIGHTPADDING", (0, 0), (0, 0), 8*mm),
        ]))

        # Contenedor con borde redondeado simulado
        contenedor = Table(
            [[fila]],
            colWidths=[W - 36*mm],
        )
        contenedor.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
            ("LEFTPADDING",  (0, 0), (-1, -1), 8*mm),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8*mm),
            ("TOPPADDING",   (0, 0), (-1, -1), 6*mm),
            ("BOTTOMPADDING",(0, 0), (-1, -1), 6*mm),
            ("LINEABOVE",  (0, 0), (-1, 0), 3, clr),
        ]))

        story.append(KeepTogether([contenedor, Spacer(1, 4*mm)]))

    story.append(Spacer(1, 4*mm))

    # ══════════════════════════════════════════════════════════
    # SÍNTESIS FINAL
    # ══════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Síntesis final", st["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    # Parsear el markdown básico del resumen (bullets y secciones)
    section_colors = {
        "OBSERVACIONES": AZUL,
        "IMPACTO": AMARILLO,
        "OPORTUNIDADES": VERDE,
    }

    current_section = None
    section_items = {}
    for line in final_summary.splitlines():
        line = line.strip()
        if not line:
            continue
        upper = line.upper()
        matched = False
        for key in section_colors:
            if key in upper and "**" in line:
                current_section = key
                section_items[current_section] = []
                matched = True
                break
        if not matched and current_section and line.startswith("-"):
            section_items[current_section].append(line.lstrip("- ").strip())

    if section_items:
        cols = []
        for key, items in section_items.items():
            clr = section_colors.get(key, AZUL)
            titulo_sec = {
                "OBSERVACIONES": "Observaciones clave",
                "IMPACTO": "Impacto operativo",
                "OPORTUNIDADES": "Oportunidades de mejora",
            }.get(key, key.capitalize())

            cell = [
                Paragraph(f"<font color='#{clr.hexval()[2:]}'><b>{titulo_sec}</b></font>",
                          st["body"]),
                Spacer(1, 3),
            ] + [
                Paragraph(f"• {item}", st["bullet"])
                for item in items
            ]
            cols.append(cell)

        if cols:
            n = len(cols)
            col_w = (W - 36*mm - (n - 1) * 4*mm) / n
            tabla_sintesis = Table(
                [cols],
                colWidths=[col_w] * n,
                hAlign="LEFT",
            )
            tabla_sintesis.setStyle(TableStyle([
                ("VALIGN", (0, 0), (-1, -1), "TOP"),
                ("BACKGROUND", (0, 0), (-1, -1), GRIS_CLARO),
                ("LEFTPADDING",  (0, 0), (-1, -1), 6*mm),
                ("RIGHTPADDING", (0, 0), (-1, -1), 6*mm),
                ("TOPPADDING",   (0, 0), (-1, -1), 6*mm),
                ("BOTTOMPADDING",(0, 0), (-1, -1), 6*mm),
                *[("LINEABOVE", (i, 0), (i, 0), 3,
                   list(section_colors.values())[i % len(section_colors)])
                  for i in range(n)],
            ]))
            story.append(tabla_sintesis)
    else:
        # Fallback: texto plano
        for line in final_summary.splitlines():
            line = line.strip().replace("**", "")
            if not line:
                story.append(Spacer(1, 3))
            elif line.startswith("-"):
                story.append(Paragraph(f"• {line.lstrip('- ')}", st["bullet"]))
            else:
                story.append(Paragraph(line, st["body"]))

    story.append(Spacer(1, 10*mm))
    story.append(HRFlowable(width="100%", thickness=0.5, color=LINEA))
    story.append(Spacer(1, 3*mm))
    story.append(Paragraph(
        "Este informe ha sido generado automáticamente por <b>HMI Analyzer</b> · "
        "The Cognitive Joint™ · bigD.es",
        st["nota"]
    ))

    # ── Build ────────────────────────────────────────────────
    def make_canvas(filename, **kwargs):
        return HeaderFooterCanvas(filename, logo_b64=logo_b64, **kwargs)

    doc.build(story, canvasmaker=make_canvas)
    return buf.getvalue()
