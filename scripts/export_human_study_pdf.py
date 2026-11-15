"""Typeset the concise three-section human-study Markdown as a PDF; no collection.

Equations are drawn as vector glyph paths from matplotlib's math layout, so no
TeX installation, browser or network dependency is needed. Scientific sources
and calculations are the experiment 15 documents and saved planning tables.
"""
from __future__ import annotations

import hashlib
import json
from functools import lru_cache
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
from matplotlib.font_manager import FontProperties
from matplotlib.mathtext import MathTextParser
from matplotlib.path import Path as MPath
from matplotlib.textpath import TextPath
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.enums import TA_LEFT
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    PageBreak, Flowable, Image, KeepTogether,
)

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments/15_human_study"
OUTPUT = STUDY / "HUMAN_STUDY_DESIGN.pdf"
WIDTH, HEIGHT = A4
MARGIN = 46
TEXT_WIDTH = WIDTH - 2*MARGIN
INK = colors.HexColor("#152B3B")
TEAL = colors.HexColor("#116E79")
MUTED = colors.HexColor("#536571")
PALE = colors.HexColor("#EDF4F5")
RULE = colors.HexColor("#D7E1E5")


def register_fonts():
    fontdir = Path(matplotlib.get_data_path()) / "fonts/ttf"
    for name, file in [("Body", "DejaVuSans.ttf"), ("Body-Bold", "DejaVuSans-Bold.ttf"),
                       ("Body-Italic", "DejaVuSans-Oblique.ttf")]:
        pdfmetrics.registerFont(TTFont(name, str(fontdir/file)))
    pdfmetrics.registerFontFamily("Body", normal="Body", bold="Body-Bold", italic="Body-Italic")


register_fonts()
STYLES = {
    "body": ParagraphStyle("body", fontName="Body", fontSize=10, leading=14.8,
                           textColor=INK, spaceAfter=8),
    "small": ParagraphStyle("small", fontName="Body", fontSize=8.4, leading=11.8,
                            textColor=MUTED, spaceAfter=6),
    "table": ParagraphStyle("table", fontName="Body", fontSize=8.8, leading=12.1,
                            textColor=INK),
    "th": ParagraphStyle("th", fontName="Body-Bold", fontSize=8.3, leading=11.3,
                         textColor=colors.white),
    "h1": ParagraphStyle("h1", fontName="Body-Bold", fontSize=20, leading=25,
                         textColor=INK, spaceAfter=13),
    "h2": ParagraphStyle("h2", fontName="Body-Bold", fontSize=11.2, leading=15,
                         textColor=TEAL, spaceBefore=9, spaceAfter=6),
    "title": ParagraphStyle("title", fontName="Body-Bold", fontSize=29, leading=34,
                            textColor=INK, spaceAfter=14),
    "subtitle": ParagraphStyle("subtitle", fontName="Body", fontSize=13.5, leading=20,
                               textColor=TEAL, spaceAfter=15),
    "kicker": ParagraphStyle("kicker", fontName="Body-Bold", fontSize=9, leading=12,
                             textColor=TEAL, spaceAfter=12),
}


@lru_cache(maxsize=2048)
def glyph_segments(font_path, size, character):
    if chr(character).isspace():
        return []
    path = TextPath((0, 0), chr(character), size=size,
                    prop=FontProperties(fname=font_path), usetex=False)
    return list(path.iter_segments(curves=True, simplify=False))


class Equation(Flowable):
    parser = MathTextParser("path")

    def __init__(self, lines, label=None, font_size=11.6):
        super().__init__()
        self.lines = [lines] if isinstance(lines, str) else lines
        self.lines = [line.replace(r"\frac", r"\dfrac") for line in self.lines]
        self.label = label
        self.parses = [self.parser.parse("$"+line+"$", dpi=72,
                         prop=FontProperties(size=font_size, math_fontfamily="stix"))
                       for line in self.lines]
        self.scale = min(1., (TEXT_WIDTH-48)/max(p.width for p in self.parses))
        if self.scale < .76:
            raise ValueError(f"Equation too wide; split it: {label}")
        self.line_heights = [max(19., p.height+8)*self.scale for p in self.parses]
        self.width = TEXT_WIDTH
        self.height = sum(self.line_heights)+7

    def draw(self):
        canvas = self.canv
        top = self.height-4
        canvas.setFillColor(INK)
        for parsed, height in zip(self.parses, self.line_heights):
            baseline = top-height+4+parsed.depth*self.scale
            canvas.saveState()
            canvas.translate(9, baseline)
            canvas.scale(self.scale, self.scale)
            for font, fontsize, number, ox, oy in parsed.glyphs:
                path = canvas.beginPath()
                current = (0., 0.)
                for vertices, code in glyph_segments(font.fname, fontsize, number):
                    if code == MPath.MOVETO:
                        current = (vertices[0]+ox, vertices[1]+oy)
                        path.moveTo(*current)
                    elif code == MPath.LINETO:
                        current = (vertices[0]+ox, vertices[1]+oy)
                        path.lineTo(*current)
                    elif code == MPath.CURVE3:
                        ctrl = (vertices[0]+ox, vertices[1]+oy)
                        end = (vertices[2]+ox, vertices[3]+oy)
                        c1 = tuple(current[j]+2/3*(ctrl[j]-current[j]) for j in (0, 1))
                        c2 = tuple(end[j]+2/3*(ctrl[j]-end[j]) for j in (0, 1))
                        path.curveTo(*c1, *c2, *end)
                        current = end
                    elif code == MPath.CURVE4:
                        shifted = [v+(ox if j%2 == 0 else oy) for j, v in enumerate(vertices)]
                        path.curveTo(*shifted)
                        current = tuple(shifted[-2:])
                    elif code == MPath.CLOSEPOLY:
                        path.close()
                canvas.drawPath(path, fill=1, stroke=0)
            for x, y, w, h in parsed.rects:
                canvas.rect(x, y, w, h, stroke=0, fill=1)
            canvas.restoreState()
            top -= height
        if self.label:
            canvas.setFillColor(MUTED)
            canvas.setFont("Body", 8.2)
            canvas.drawRightString(self.width, self.height/2-2, f"({self.label})")


class StudyDocument(BaseDocTemplate):
    def afterFlowable(self, flowable):
        if getattr(flowable, "outline", None):
            key, title = flowable.outline
            self.canv.bookmarkPage(key)
            self.canv.addOutlineEntry(title, key, level=0, closed=False)


def chrome(canvas, doc):
    canvas.saveState()
    canvas.setStrokeColor(RULE)
    canvas.setLineWidth(.5)
    canvas.line(MARGIN, HEIGHT-32, WIDTH-MARGIN, HEIGHT-32)
    canvas.setFont("Body", 7.5)
    canvas.setFillColor(MUTED)
    canvas.drawString(MARGIN, HEIGHT-24, "HUMAN BEER GAME  /  EXPERIMENT 15")
    canvas.drawRightString(WIDTH-MARGIN, HEIGHT-24, "RESEARCH DESIGN")
    canvas.line(MARGIN, 33, WIDTH-MARGIN, 33)
    canvas.drawString(MARGIN, 20, "Design draft • 14 November 2026")
    canvas.drawRightString(WIDTH-MARGIN, 20, f"{doc.page}")
    canvas.restoreState()



def build():
    import re
    from html import escape
    source = STUDY / "HUMAN_STUDY_DESIGN.md"
    lines = source.read_text(encoding="utf-8").splitlines()
    STYLES["body"].fontSize = 10
    STYLES["body"].leading = 14
    STYLES["body"].spaceAfter = 6
    STYLES["h1"].fontSize = 18
    STYLES["h1"].leading = 23
    STYLES["h1"].spaceAfter = 10
    STYLES["h2"].spaceBefore = 5
    STYLES["h2"].spaceAfter = 4
    STYLES["table"].fontSize = 8.9
    STYLES["table"].leading = 11.8
    story, titles, equation_count = [], [], 0

    def inline(text):
        text = escape(text)
        text = re.sub(r"\[([^\]]+)\]\((https?://[^)]+)\)",
                      r'<link href="\2" color="#116E79">\1</link>', text)
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)
        if text.startswith('*') and text.endswith('*'):
            text = '<i>'+text[1:-1]+'</i>'
        return text

    index = 0
    while index < len(lines):
        line = lines[index].strip()
        if not line or line.startswith('# '):
            index += 1
            continue
        if line.startswith('## '):
            if titles:
                story.append(PageBreak())
            title = line[3:]
            item = Paragraph(inline(title), STYLES['h1'])
            item.outline = (f'section{len(titles)+1}', title)
            story.append(item)
            titles.append(title)
            index += 1
        elif line.startswith('### '):
            story.append(Paragraph(inline(line[4:]), STYLES['h2']))
            index += 1
        elif line == r'\[':
            index += 1
            latex = []
            while lines[index].strip() != r'\]':
                latex.append(lines[index].strip())
                index += 1
            equation_count += 1
            parts = [part.strip() for part in ' '.join(latex).split(r'\\')]
            story.append(Equation(parts, str(equation_count), font_size=11.2))
            index += 1
        elif line.startswith('|'):
            rows = []
            while index < len(lines) and lines[index].strip().startswith('|'):
                values = [v.strip() for v in lines[index].strip().strip('|').split('|')]
                if not all(re.fullmatch(r'[-: ]+',v) for v in values):
                    rows.append(values)
                index += 1
            columns = len(rows[0])
            widths = [92, TEXT_WIDTH-92] if columns == 2 else [120,(TEXT_WIDTH-120)/2,(TEXT_WIDTH-120)/2]
            if rows[0][0] == 'Decision time':
                widths = [TEXT_WIDTH/3]*3
            table_rows = [[Paragraph(inline(v), STYLES['th' if i == 0 else 'table'])
                           for v in row] for i,row in enumerate(rows)]
            table = Table(table_rows, colWidths=widths, repeatRows=1, hAlign='LEFT')
            table.setStyle(TableStyle([
                ('BACKGROUND',(0,0),(-1,0),TEAL),
                ('ROWBACKGROUNDS',(0,1),(-1,-1),[colors.white,PALE]),
                ('VALIGN',(0,0),(-1,-1),'TOP'),
                ('LEFTPADDING',(0,0),(-1,-1),7),
                ('RIGHTPADDING',(0,0),(-1,-1),7),
                ('TOPPADDING',(0,0),(-1,-1),5),
                ('BOTTOMPADDING',(0,0),(-1,-1),5),
                ('LINEBELOW',(0,-1),(-1,-1),.5,RULE),
            ]))
            story.extend([table, Spacer(1,7)])
        else:
            paragraph = [line]
            index += 1
            while index < len(lines) and lines[index].strip() and not lines[index].startswith(('#','|','- ')) and lines[index].strip() != r'\[' and not re.match(r'\d+\. ',lines[index]):
                paragraph.append(lines[index].strip())
                index += 1
            content = ' '.join(paragraph)
            if content.startswith('- '):
                content = content[2:]
            style = 'small' if content.startswith('*Source:') else 'body'
            story.append(Paragraph(inline(content),STYLES[style]))

    doc = StudyDocument(str(OUTPUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=49, bottomMargin=48,
                        title="Human Beer Game: Model, Measurement and Experiment Design",
                        author="Beer Game Research Project")
    frame = Frame(MARGIN,48,TEXT_WIDTH,HEIGHT-97,leftPadding=0,rightPadding=0,
                  topPadding=0,bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id='report',frames=frame,onPage=chrome))
    doc.build(story)
    from pypdf import PdfReader
    reader = PdfReader(str(OUTPUT))
    if len(reader.pages) != 3:
        raise RuntimeError(f'Expected three pages, produced {len(reader.pages)}; shorten the prose rather than reducing type size.')
    receipt = {
        'pdf': OUTPUT.name, 'pages':len(reader.pages), 'sections': titles,
        'source':source.name, 'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),
        'pdf_sha256':hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
        'exporter_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'equation_count':equation_count, 'human_records':0,
        'source_words':len(source.read_text(encoding='utf-8').split()),
        'equations':'vector outlines; no raw LaTeX printed'
    }
    (STUDY/'analysis/PDF_VALIDATION.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
    print(json.dumps(receipt,indent=2))


if __name__ == '__main__':
    build()
