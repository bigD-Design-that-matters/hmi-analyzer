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
AZUL          = colors.HexColor("#0050cc")
AZUL_OSCURO   = colors.HexColor("#003d99")
AZUL_CLARO    = colors.HexColor("#e8f0ff")
GRIS_OSCURO   = colors.HexColor("#212121")
GRIS_MEDIO    = colors.HexColor("#616161")
GRIS_CLARO    = colors.HexColor("#F5F5F5")
VERDE         = colors.HexColor("#2e7d32")
AMARILLO      = colors.HexColor("#f9a825")
ROJO          = colors.HexColor("#c62828")
BLANCO        = colors.white
LINEA         = colors.HexColor("#E0E0E0")

W, H = A4
MARGEN_L  = 18 * mm
MARGEN_R  = 18 * mm
CONTENT_W = W - MARGEN_L - MARGEN_R   # ~559 pt


# ── Helpers ───────────────────────────────────────────────────────────────────
def score_color(score):
    if score >= 7:
        return VERDE
    elif score >= 5:
        return AMARILLO
    return ROJO


def score_label(score):
    if score >= 7:
        return "Solida"
    elif score >= 5:
        return "Mejorable"
    return "Critica"


# ── Barra de progreso ─────────────────────────────────────────────────────────
class ScoreBar(Flowable):
    def __init__(self, score, width=120 * mm, height=6):
        super().__init__()
        self.score = score
        self.width = width
        self.height = height

    def draw(self):
        c = self.canv
        c.setFillColor(LINEA)
        c.roundRect(0, 0, self.width, self.height, self.height / 2, fill=1, stroke=0)
        filled = self.width * (self.score / 10)
        c.setFillColor(score_color(self.score))
        c.roundRect(0, 0, filled, self.height, self.height / 2, fill=1, stroke=0)

    def wrap(self, availW, availH):
        return self.width, self.height + 2


# ── Cabecera y pie en cada pagina ─────────────────────────────────────────────
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

        # Header
        self.setFillColor(AZUL)
        self.rect(0, H - 14 * mm, W, 14 * mm, fill=1, stroke=0)

        if self.logo_b64 and page > 1:
            try:
                logo_data = base64.b64decode(self.logo_b64)
                img_buf = io.BytesIO(logo_data)
                self.drawImage(img_buf, 12 * mm, H - 12 * mm,
                               width=20 * mm, height=10 * mm,
                               preserveAspectRatio=True, mask='auto')
            except Exception:
                pass

        self.setFont("Helvetica-Bold", 8)
        self.setFillColor(BLANCO)
        self.drawRightString(W - 12 * mm, H - 9 * mm,
                             "HMI Analyzer - The Cognitive Joint")

        # Footer
        self.setFillColor(GRIS_CLARO)
        self.rect(0, 0, W, 10 * mm, fill=1, stroke=0)
        self.setFillColor(GRIS_MEDIO)
        self.setFont("Helvetica", 7)
        fecha = datetime.now().strftime("%d/%m/%Y")
        self.drawString(12 * mm, 3.5 * mm, f"Informe generado el {fecha}")
        self.drawRightString(W - 12 * mm, 3.5 * mm, f"Pagina {page} de {total}")


# ── Estilos ───────────────────────────────────────────────────────────────────
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
        "puente_num": ParagraphStyle("puente_num",
            fontName="Helvetica", fontSize=8, leading=11,
            textColor=GRIS_MEDIO),
        "body": ParagraphStyle("body", **base),
        "body_small": ParagraphStyle("body_small",
            fontName="Helvetica", fontSize=9, leading=13,
            textColor=GRIS_MEDIO, spaceAfter=4),
        "bullet": ParagraphStyle("bullet",
            fontName="Helvetica", fontSize=9, leading=14,
            textColor=GRIS_OSCURO, leftIndent=8, spaceAfter=3),
        "nota": ParagraphStyle("nota",
            fontName="Helvetica-Oblique", fontSize=8, leading=12,
            textColor=GRIS_MEDIO),
        "disclaimer": ParagraphStyle("disclaimer",
            fontName="Helvetica", fontSize=8, leading=12,
            textColor=GRIS_MEDIO),
        "contacto": ParagraphStyle("contacto",
            fontName="Helvetica-Bold", fontSize=9, leading=13,
            textColor=AZUL),
    }


# ── Funcion principal ─────────────────────────────────────────────────────────
def generate_hmi_pdf(
    image_bytes: bytes,
    scores: list,
    bridge_names: list,
    bridge_summaries: list,
    average_score: float,
    final_summary: str,
    contexto_uso: str,
    impacto_error: str,
    logo_b64: str = None,
) -> bytes:

    buf = io.BytesIO()
    s = make_styles()

    doc = SimpleDocTemplate(
        buf,
        pagesize=A4,
        leftMargin=MARGEN_L, rightMargin=MARGEN_R,
        topMargin=22 * mm, bottomMargin=18 * mm,
        title="Informe HMI Analyzer",
        author="HMI Analyzer - bigD",
    )

    story = []

    # ══════════════════════════════════════════════════════════
    # PORTADA
    # ══════════════════════════════════════════════════════════
    fecha = datetime.now().strftime("%d de %B de %Y")

    portada_contenido = [
        Spacer(1, 28 * mm),
        Paragraph("HMI Analyzer", s["titulo_portada"]),
        Spacer(1, 4 * mm),
        Paragraph("Informe de evaluacion cognitiva", s["sub_portada"]),
        Spacer(1, 3 * mm),
        Paragraph("Basado en los <b>8 Puentes de The Cognitive Joint</b>", s["sub_portada"]),
        Spacer(1, 12 * mm),
        Paragraph(f"Fecha: {fecha}", s["meta_portada"]),
        Paragraph(f"Uso: {contexto_uso}", s["meta_portada"]),
        Paragraph(f"Impacto: {impacto_error}", s["meta_portada"]),
    ]

    tabla_portada = Table(
        [[portada_contenido]],
        colWidths=[CONTENT_W],
        rowHeights=[105 * mm],
    )
    tabla_portada.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL),
        ("LEFTPADDING",   (0, 0), (-1, -1), 14 * mm),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 10 * mm),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 10 * mm),
        ("VALIGN",        (0, 0), (-1, -1), "TOP"),
    ]))
    story.append(tabla_portada)
    story.append(Spacer(1, 6 * mm))

    # ── Imagen analizada (ratio correcto) ─────────────────────
    try:
        from PIL import Image as PILImage
        pil = PILImage.open(io.BytesIO(image_bytes))
        img_w_px, img_h_px = pil.size
    except Exception:
        img_w_px, img_h_px = 16, 9

    max_w = CONTENT_W
    max_h = 65 * mm
    ratio = img_w_px / img_h_px
    img_w = min(max_w, max_h * ratio)
    img_h = img_w / ratio
    if img_h > max_h:
        img_h = max_h
        img_w = img_h * ratio

    try:
        img = Image(io.BytesIO(image_bytes), width=img_w, height=img_h)
        img.hAlign = "LEFT"
        story.append(img)
    except Exception:
        pass

    story.append(Spacer(1, 5 * mm))

    # ── Score global ──────────────────────────────────────────
    color_g = score_color(average_score)
    label_g = score_label(average_score)
    hex_g = color_g.hexval()[2:]

    fila_score = Table(
        [[
            Paragraph("<font size=28><b>Score global</b></font>", s["body"]),
            Paragraph(f"<font color='#{hex_g}' size=28><b>{average_score}/10</b></font>", s["body"]),
        ]],
        colWidths=[CONTENT_W * 0.55, CONTENT_W * 0.45],
    )
    fila_score.setStyle(TableStyle([
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
        ("LEFTPADDING",   (0, 0), (-1, -1), 0),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 0),
        ("TOPPADDING",    (0, 0), (-1, -1), 0),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 0),
        ("ALIGN",         (1, 0), (1, 0), "RIGHT"),
    ]))
    story.append(fila_score)
    story.append(Spacer(1, 8 * mm))
    story.append(ScoreBar(average_score, width=CONTENT_W, height=8))
    story.append(Spacer(1, 4 * mm))

    story.append(PageBreak())

    # ══════════════════════════════════════════════════════════
    # TABLA RESUMEN
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("Resumen por puentes", s["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    tabla_data = [["Puente", "Nombre", "Puntuacion", "Valoracion"]]
    for name, score in zip(bridge_names, scores):
        num = name.split("-")[0].strip() if "-" in name else name.split("–")[0].strip()
        nom_raw = name.split("–")[1].strip() if "–" in name else (
            name.split("-")[1].strip() if "-" in name else name)
        nom = nom_raw.capitalize()
        clr = score_color(score)
        lbl = score_label(score)
        tabla_data.append([
            Paragraph(f"<font size=8 color='#616161'>{num}</font>", s["body"]),
            Paragraph(f"<b>{nom}</b>", s["body"]),
            Paragraph(f"<b>{score}/10</b>", s["body"]),
            Paragraph(f"<font color='#{clr.hexval()[2:]}'><b>{lbl}</b></font>", s["body"]),
        ])

    tabla_scores = Table(
        tabla_data,
        colWidths=[30 * mm, 72 * mm, 30 * mm, 28 * mm],
        repeatRows=1,
    )
    tabla_scores.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, 0), AZUL),
        ("TEXTCOLOR",     (0, 0), (-1, 0), BLANCO),
        ("FONTNAME",      (0, 0), (-1, 0), "Helvetica-Bold"),
        ("FONTSIZE",      (0, 0), (-1, 0), 9),
        ("TOPPADDING",    (0, 0), (-1, 0), 6),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("ROWBACKGROUNDS",(0, 1), (-1, -1), [BLANCO, GRIS_CLARO]),
        ("FONTNAME",      (0, 1), (-1, -1), "Helvetica"),
        ("FONTSIZE",      (0, 1), (-1, -1), 9),
        ("TOPPADDING",    (0, 1), (-1, -1), 5),
        ("BOTTOMPADDING", (0, 1), (-1, -1), 5),
        ("GRID",          (0, 0), (-1, -1), 0.5, LINEA),
        ("VALIGN",        (0, 0), (-1, -1), "MIDDLE"),
    ]))
    story.append(tabla_scores)
    story.append(Spacer(1, 8 * mm))

    # ══════════════════════════════════════════════════════════
    # DETALLE POR PUENTE  (sin barra vertical lateral)
    # ══════════════════════════════════════════════════════════
    story.append(Paragraph("Analisis por puente", s["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    for i, (name, score, summary_text) in enumerate(
            zip(bridge_names, scores, bridge_summaries)):

        sep = "–" if "–" in name else "-"
        parts = name.split(sep, 1)
        num_txt = parts[0].strip()
        nom_txt = parts[1].strip().capitalize() if len(parts) > 1 else name

        clr = score_color(score)
        lbl = score_label(score)
        hex_clr = clr.hexval()[2:]

        cabecera = Paragraph(
            f"<font size=8 color='#616161'>{num_txt}</font>  "
            f"<b>{nom_txt}</b>  "
            f"<font color='#{hex_clr}' size=14><b>{score}/10</b></font>  "
            f"<font color='#{hex_clr}' size=9><b>{lbl}</b></font>",
            s["body"],
        )
        barra = ScoreBar(score, width=CONTENT_W - 16 * mm, height=5)
        resumen = Paragraph(summary_text, s["body"])

        bloque = [cabecera, Spacer(1, 3), barra, Spacer(1, 5), resumen]

        contenedor = Table([[bloque]], colWidths=[CONTENT_W])
        contenedor.setStyle(TableStyle([
            ("BACKGROUND",    (0, 0), (-1, -1), GRIS_CLARO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 8 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 8 * mm),
            ("TOPPADDING",    (0, 0), (-1, -1), 5 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
            ("LINEABOVE",     (0, 0), (-1, 0), 3, clr),
        ]))

        story.append(KeepTogether([contenedor, Spacer(1, 4 * mm)]))

    story.append(Spacer(1, 4 * mm))

    # ══════════════════════════════════════════════════════════
    # SINTESIS FINAL
    # ══════════════════════════════════════════════════════════
    story.append(PageBreak())
    story.append(Paragraph("Sintesis final", s["seccion"]))
    story.append(HRFlowable(width="100%", thickness=1, color=LINEA, spaceAfter=6))

    section_colors = {
        "OBSERVACIONES": AZUL,
        "IMPACTO": AMARILLO,
        "OPORTUNIDADES": VERDE,
    }
    section_titles = {
        "OBSERVACIONES": "Observaciones clave",
        "IMPACTO": "Impacto operativo",
        "OPORTUNIDADES": "Oportunidades de mejora",
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
            if key in upper and ("**" in line or ":" in line):
                current_section = key
                section_items[current_section] = []
                matched = True
                break
        if not matched and current_section and line.startswith("-"):
            section_items[current_section].append(line.lstrip("- ").strip())

    if section_items:
        cols, clr_list = [], []
        for key, items in section_items.items():
            clr = section_colors.get(key, AZUL)
            clr_list.append(clr)
            titulo_sec = section_titles.get(key, key.capitalize())
            cell = [
                Paragraph(
                    f"<font color='#{clr.hexval()[2:]}'><b>{titulo_sec}</b></font>",
                    s["body"],
                ),
                Spacer(1, 4),
            ] + [Paragraph(f"- {item}", s["bullet"]) for item in items]
            cols.append(cell)

        n = len(cols)
        gap = 4 * mm
        col_w = (CONTENT_W - (n - 1) * gap) / n

        tabla_s = Table([cols], colWidths=[col_w] * n, hAlign="LEFT")
        cmds = [
            ("VALIGN",        (0, 0), (-1, -1), "TOP"),
            ("BACKGROUND",    (0, 0), (-1, -1), GRIS_CLARO),
            ("LEFTPADDING",   (0, 0), (-1, -1), 6 * mm),
            ("RIGHTPADDING",  (0, 0), (-1, -1), 5 * mm),
            ("TOPPADDING",    (0, 0), (-1, -1), 6 * mm),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6 * mm),
        ]
        for idx, clr in enumerate(clr_list):
            cmds.append(("LINEABOVE", (idx, 0), (idx, 0), 3, clr))
        tabla_s.setStyle(TableStyle(cmds))
        story.append(tabla_s)
    else:
        for line in final_summary.splitlines():
            line = line.strip().replace("**", "")
            if not line:
                story.append(Spacer(1, 3))
            elif line.startswith("-"):
                story.append(Paragraph(f"- {line.lstrip('- ')}", s["bullet"]))
            else:
                story.append(Paragraph(line, s["body"]))

    story.append(Spacer(1, 8 * mm))

    # ══════════════════════════════════════════════════════════
    # DISCLAIMER
    # ══════════════════════════════════════════════════════════
    bloque_disclaimer = Table(
        [[
            [
                Paragraph("<b>Privacidad de los datos.</b>", s["disclaimer"]),
                Spacer(1, 3),
                Paragraph("Las imagenes analizadas no son almacenadas por bigD.", s["disclaimer"]),
                Spacer(1, 3),
                Paragraph("Los resultados del analisis no se vinculan con el usuario registrado.", s["disclaimer"]),
            ]
        ]],
        colWidths=[CONTENT_W],
    )
    bloque_disclaimer.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), GRIS_CLARO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8 * mm),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING",    (0, 0), (-1, -1), 5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
        ("LINEABOVE",     (0, 0), (-1, 0), 1, LINEA),
    ]))
    story.append(bloque_disclaimer)

    story.append(Spacer(1, 3 * mm))

    # ══════════════════════════════════════════════════════════
    # CONTACTO
    # ══════════════════════════════════════════════════════════
    bloque_contacto = Table(
        [[
            [
                Paragraph("<b>Necesitas un diagnostico mas profundo?</b>", s["contacto"]),
                Spacer(1, 3),
                Paragraph("info@bigd.es  -  bigd.es/contacto", s["contacto"]),
            ]
        ]],
        colWidths=[CONTENT_W],
    )
    bloque_contacto.setStyle(TableStyle([
        ("BACKGROUND",    (0, 0), (-1, -1), AZUL_CLARO),
        ("LEFTPADDING",   (0, 0), (-1, -1), 8 * mm),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 8 * mm),
        ("TOPPADDING",    (0, 0), (-1, -1), 5 * mm),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 5 * mm),
        ("LINEABOVE",     (0, 0), (-1, 0), 2, AZUL),
    ]))
    story.append(bloque_contacto)

    story.append(Spacer(1, 4 * mm))
    story.append(Paragraph(
        "Este informe ha sido generado automaticamente por <b>HMI Analyzer</b> - "
        "The Cognitive Joint - bigD.es",
        s["nota"],
    ))

    # ── Build ────────────────────────────────────────────────
    def make_canvas(filename, **kwargs):
        return HeaderFooterCanvas(filename, logo_b64=logo_b64, **kwargs)

    doc.build(story, canvasmaker=make_canvas)
    return buf.getvalue()
