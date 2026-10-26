"""Publish the current Markdown report plus current figures as a readable PDF.

Offline only. Install optional renderer dependencies with:
  .venv/Scripts/python.exe -m pip install "reportlab>=4,<5" "pypdf>=5,<7"
Existing PDFs are preserved before changed evidence is published. Scientific
source, Markdown, raw decisions and statistical calculations are read-only.
"""
from pathlib import Path
from datetime import datetime, timezone
import hashlib
import html
import json
import re
import shutil

import matplotlib
from PIL import Image as PillowImage
from pypdf import PdfReader
import reportlab
from reportlab.lib import colors
from reportlab.lib.enums import TA_CENTER, TA_LEFT
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.platypus import (
    BaseDocTemplate, Frame, Image, NextPageTemplate, PageBreak,
    PageTemplate, Paragraph, Spacer, Table, TableStyle,
)

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / 'experiments/13_weekly_state_api_20261021'
OUT = EXP / 'reports/agent_collection_v5'
PDF = OUT / 'REPORT.pdf'
RECEIPT = OUT / 'PDF_EXPORT.json'
NAVY = colors.HexColor('#173044')
MUTED = colors.HexColor('#536473')
WIDTH = A4[0] - 80


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def inline(text):
    text = html.escape(text)
    text = re.sub(r'\[([^\]]+)\]\(([^)]+)\)', r'<link href="\2" color="#245B8A">\1</link>', text)
    text = re.sub(r'\*\*(.+?)\*\*', r'<b>\1</b>', text)
    text = re.sub(r'`([^`]+)`', r'<font name="DejaVuMono">\1</font>', text)
    return text


def register_fonts():
    folder = Path(matplotlib.get_data_path()) / 'fonts/ttf'
    for name, file in [('DejaVu', 'DejaVuSans.ttf'), ('DejaVuBold', 'DejaVuSans-Bold.ttf'),
                       ('DejaVuItalic', 'DejaVuSans-Oblique.ttf'), ('DejaVuMono', 'DejaVuSansMono.ttf')]:
        pdfmetrics.registerFont(TTFont(name, str(folder / file)))
    pdfmetrics.registerFontFamily('DejaVu', normal='DejaVu', bold='DejaVuBold',
                                 italic='DejaVuItalic', boldItalic='DejaVuBold')


def styles():
    base = dict(fontName='DejaVu', textColor=NAVY, leading=14, spaceAfter=8)
    return {
        'body': ParagraphStyle('body', fontSize=9.5, **base),
        'small': ParagraphStyle('small', fontSize=8, fontName='DejaVu', leading=11,
                                textColor=MUTED, spaceAfter=7),
        'title': ParagraphStyle('title', fontSize=23, fontName='DejaVuBold', leading=29,
                                textColor=NAVY, spaceAfter=16, keepWithNext=True),
        'heading': ParagraphStyle('heading', fontSize=14, fontName='DejaVuBold', leading=18,
                                  textColor=NAVY, spaceBefore=12, spaceAfter=9, keepWithNext=True),
        'cell': ParagraphStyle('cell', fontSize=8, fontName='DejaVu', leading=11, textColor=NAVY),
        'header': ParagraphStyle('header', fontSize=8, fontName='DejaVuBold', leading=11,
                                 textColor=colors.white),
    }


def table(rows, section, st):
    rows = [list(row) for row in rows]
    columns = len(rows[0])
    if section == 'What each hypothesis measures':
        weights = [38, 267, 210]
        rows[0][0] = 'Test'
    elif section == 'Effect sizes and p-values':
        weights = [30, 67, 40, 63, 100, 35, 45, 90]
        rows[0] = ['Test', 'Model', 'n', 'Mean Δ', '95% bootstrap interval', 'Raw p', 'Holm p (20)', 'Direction']
    elif section == 'Observed H1-H4 differences':
        weights = [65, 41, 60, 42, 60, 44, 56, 147]
        rows[0] = ['Requested model', 'Run', 'H1 Δ sens.', 'H2 Δ cost', 'H3 Δ sens.', 'H4a Δ var.', 'H4b Δ ratio', 'Review']
    elif columns == 2:
        weights = [180, 335]
    else:
        weights = [1] * columns
    widths = [WIDTH * w / sum(weights) for w in weights]
    cells = [[Paragraph(inline(value), st['header'] if i == 0 else st['cell'])
              for value in row] for i, row in enumerate(rows)]
    result = Table(cells, colWidths=widths, repeatRows=1, hAlign='LEFT')
    result.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), NAVY),
        ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.HexColor('#EFF3F6'), colors.HexColor('#FAFBFC')]),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ('LEFTPADDING', (0, 0), (-1, -1), 5), ('RIGHTPADDING', (0, 0), (-1, -1), 5),
        ('TOPPADDING', (0, 0), (-1, -1), 6), ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('LINEBELOW', (0, 0), (-1, -1), .5, colors.white),
    ]))
    return result


def image(path, width=WIDTH, max_height=390):
    with PillowImage.open(path) as im:
        w, h = im.size
    scale = min(width / w, max_height / h)
    return Image(str(path), width=w * scale, height=h * scale, hAlign='CENTER')


def markdown_story(text, st):
    lines = text.splitlines()
    story, section = [], ''
    i = 0
    while i < len(lines):
        line = lines[i].strip()
        if not line:
            i += 1
            continue
        if line.startswith('# '):
            story.append(Paragraph(inline(line[2:]), st['title']))
            story.append(Paragraph('Final collection: 25 October 2026 · three complete non-excluded rounds per GPT model', st['small']))
            i += 1
        elif line.startswith('## '):
            section = line[3:]
            story.append(Paragraph(inline(section), st['heading']))
            i += 1
        elif line.startswith('|'):
            rows = []
            while i < len(lines) and lines[i].strip().startswith('|'):
                row = [v.strip() for v in lines[i].strip().strip('|').split('|')]
                if not all(re.fullmatch(r':?-+:?', value) for value in row):
                    rows.append(row)
                i += 1
            assert len({len(row) for row in rows}) == 1
            story.extend([table(rows, section, st), Spacer(1, 9)])
        elif line.startswith('!['):
            match = re.fullmatch(r'!\[([^\]]*)\]\(([^)]+)\)', line)
            assert match, line
            story.append(image(OUT / match[2]))
            story.append(Paragraph(inline(match[1]) + '. Individual complete contexts; review/exclusion status is listed in the preceding tables.', st['small']))
            i += 1
        else:
            group = [line]
            i += 1
            is_list = bool(re.match(r'(?:\d+\.|-) ', line))
            while not is_list and i < len(lines) and lines[i].strip() and not lines[i].lstrip().startswith(('#', '|', '![', '- ')) and not re.match(r'\d+\. ', lines[i].lstrip()):
                group.append(lines[i].strip())
                i += 1
            story.append(Paragraph(inline(' '.join(group)), st['body']))
    return story


def page(canvas, doc):
    canvas.saveState()
    w, h = canvas._pagesize
    canvas.setFont('DejaVu', 8)
    canvas.setFillColor(MUTED)
    canvas.drawString(40, h - 25, 'BEER GAME  |  FINAL AGENT STUDY')
    canvas.drawRightString(w - 40, 23, f'Page {doc.page}')
    canvas.drawString(40, 23, '50 chains per condition · 24 weeks · fresh context is the replication unit')
    canvas.restoreState()


def main():
    sources = [OUT / 'REPORT.md', OUT / 'RESULTS.json', OUT / 'DESCRIPTIVE_H1_H4.png',
               OUT / 'slides_current/MODEL_COMPARISON_REVIEWED.png',
               OUT / 'size_stability/CHAIN_SIZE.png',
               OUT / 'size_stability/CONTEXT_COUNT.png', Path(__file__)]
    fingerprint = {str(p.relative_to(ROOT)): sha(p) for p in sources}
    if RECEIPT.exists():
        previous = json.loads(RECEIPT.read_text(encoding='utf-8'))
        if previous['sources'] == fingerprint and PDF.exists() and sha(PDF) == previous['pdf_sha256']:
            print(PDF)
            return
    if PDF.exists() or RECEIPT.exists():
        tag = sha(PDF)[:16] if PDF.exists() else sha(RECEIPT)[:16]
        folder = OUT / 'history' / f'pdf_{tag}'
        folder.mkdir(parents=True, exist_ok=True)
        for p in [PDF, RECEIPT]:
            if p.exists():
                target = folder / p.name
                if target.exists():
                    assert target.read_bytes() == p.read_bytes()
                else:
                    shutil.copy2(p, target)
    register_fonts()
    st = styles()
    portrait = Frame(40, 42, WIDTH, A4[1] - 89, id='portrait', leftPadding=0,
                     rightPadding=0, topPadding=0, bottomPadding=0)
    wide_size = landscape(A4)
    wide = Frame(36, 42, wide_size[0] - 72, wide_size[1] - 89, id='wide',
                 leftPadding=0, rightPadding=0, topPadding=0, bottomPadding=0)
    temporary = OUT / '.REPORT.new.pdf'
    doc = BaseDocTemplate(str(temporary), pagesize=A4, title='Beer Game: final H1–H4 report',
                          author='Beer Game research project', pageCompression=1)
    doc.addPageTemplates([PageTemplate('portrait', [portrait], onPage=page, pagesize=A4),
                         PageTemplate('landscape', [wide], onPage=page, pagesize=wide_size)])
    story = markdown_story((OUT / 'REPORT.md').read_text(encoding='utf-8'), st)
    figures = [
        ('Model comparison: reviewed results', sources[3],
         'All five outcomes are shown: H1, H2, H3, H4a and H4b. Dots show model means; labels show signed differences and raw two-sided p-values. H1/H3 use a magnified scale. Reviewed observations: Astra2, Sol2, Luna3. A = control + revision; B = control + one decision; C = education + one decision.'),
        ('H1–H4 metrics versus chain count', sources[4],
         'Each curve averages reviewed contexts using the first 5–50 chains per condition in every included run. Independent n stays2/2/3. All five outcomes are included. H1/H3 use a magnified scale. All 50-chain endpoints match the statistics table.'),
        ('H1–H4 metrics versus context count', sources[5],
         'A context is one fresh model conversation containing the three conditions. Curves average the first k reviewed contexts in chronological order. Astra and Sol stop at two reviewed contexts, Luna at three. No unobserved contexts are plotted. The final means and p-values match the statistics table.'),
    ]
    for title, path, caption in figures:
        story.extend([NextPageTemplate('landscape'), PageBreak(), Paragraph(title, st['heading']),
                      image(path, wide_size[0] - 72, 415), Spacer(1, 7), Paragraph(caption, st['small'])])
    doc.build(story)
    reader = PdfReader(temporary)
    text = '\n'.join(p.extract_text() or '' for p in reader.pages)
    for value in ['What each hypothesis measures', 'H1', 'H2', 'H3', 'H4a', 'H4b',
                  'Raw p', '38.31', '-20.44', 'Collection stopped', 'pipeline sensitivity',
                  'Model comparison: reviewed results', 'metrics versus chain count']:
        assert value in text, f'PDF text missing: {value}'
    assert '\ufffd' not in text, 'Unicode replacement glyph in PDF'
    assert len(reader.pages) >= 3
    temporary.replace(PDF)
    assert fingerprint == {str(p.relative_to(ROOT)): sha(p) for p in sources}, 'A source changed during PDF export'
    receipt = dict(created_utc=datetime.now(timezone.utc).isoformat(), sources=fingerprint,
                   pdf_sha256=sha(PDF), pages=len(reader.pages), reportlab_version=reportlab.Version,
                   figures_embedded=4, scientific_values_recomputed=False, api_calls=0,
                   validation='PDF parses; text includes all five hypotheses, measurement definitions and final statistics; source hashes unchanged.',
                   page_sizes=[list(p.mediabox)[2:] for p in reader.pages])
    RECEIPT.write_text(json.dumps(receipt, indent=2) + '\n', encoding='utf-8')
    print(json.dumps(dict(pdf=str(PDF), pages=len(reader.pages), bytes=PDF.stat().st_size)))


if __name__ == '__main__':
    main()
