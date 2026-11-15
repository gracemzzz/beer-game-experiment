"""Typeset the human-study design as one standalone PDF; no data collection.

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
    story = []
    expected_titles = []
    equation_map = []

    def p(text, style="body"):
        story.append(Paragraph(text, STYLES[style]))

    def h(text):
        p(text, "h2")

    def page(title):
        if story:
            story.append(PageBreak())
        expected_titles.append(title)
        item = Paragraph(title, STYLES["h1"])
        item.outline = (f"section{len(expected_titles)}", title)
        story.append(item)

    def eq(lines, label=None, size=11.6):
        equation_map.append({"pdf_number": len(equation_map)+1, "companion_source_number": label})
        story.append(Equation(lines, str(len(equation_map)), size))

    def table(headers, rows, widths=None):
        data = [[Paragraph(str(x), STYLES["th"]) for x in headers]]
        data += [[Paragraph(str(x), STYLES["table"]) for x in row] for row in rows]
        item = Table(data, colWidths=widths, repeatRows=1, hAlign="LEFT")
        item.setStyle(TableStyle([
            ("BACKGROUND", (0, 0), (-1, 0), TEAL),
            ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, PALE]),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 8),
            ("RIGHTPADDING", (0, 0), (-1, -1), 8),
            ("TOPPADDING", (0, 0), (-1, -1), 6),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
            ("LINEBELOW", (0, -1), (-1, -1), .5, RULE),
        ]))
        story.append(item)
        story.append(Spacer(1, 9))

    def box(title, text):
        content = [Paragraph(title, STYLES["h2"]), Paragraph(text, STYLES["body"])]
        t = Table([[content]], colWidths=[TEXT_WIDTH])
        t.setStyle(TableStyle([("BACKGROUND", (0,0), (-1,-1), PALE),
                              ("LEFTPADDING", (0,0), (-1,-1), 12),
                              ("RIGHTPADDING", (0,0), (-1,-1), 12),
                              ("TOPPADDING", (0,0), (-1,-1), 5),
                              ("BOTTOMPADDING", (0,0), (-1,-1), 7)]))
        story.extend([t, Spacer(1, 9)])

    # 1 — overview, not an empty title page.
    expected_titles.append("Overview")
    p("STUDY DESIGN AND MEASUREMENT PROTOCOL", "kicker")
    title = Paragraph("Ordering against<br/>the clock", STYLES["title"])
    title.outline = ("overview", "Overview")
    story.append(title)
    p("A human Beer Game experiment on decision time,<br/>pipeline-stock weighting and causal education", "subtitle")
    p("Experiment 15 · Design draft · 14 November 2026", "small")
    p("This report translates the project's AI feasibility work into a proposed human experiment. "
      "Its purpose is to define what will be measured, how observed decisions will estimate the relevant "
      "parameters, and how those estimates determine the recruitment requirement. No human results are reported.")
    h("Four design conclusions")
    for text in [
        "<b>1. Measure two stock responses.</b> Estimate how orders respond to on-hand inventory and to "
        "equally usable outstanding orders. Their difference measures the pipeline-underweighting gap; "
        "the pipeline slope alone cannot separate weighting from adjustment speed.",
        "<b>2. Use a complete four-group design.</b> Cross adequate versus binding decision time with "
        "control versus causal education. This identifies the interaction required by H6.",
        "<b>3. Give H5 a real change in consequences.</b> A separate routine-transfer task establishes an "
        "ordering rule before a shipment becomes too late to meet demand. Correct adaptation and persistence "
        "then have different, explicit numerical benchmarks.",
        "<b>4. Plan recruitment using human variability.</b> AI significance supplies neither a human effect "
        "size nor human statistical power. The sample-size examples are conditional planning scenarios.",
    ]: p(text)
    h("Reading guide")
    table(["Topic", "Pages"], [
        ["Experimental design and actual human timing", "2–3"],
        ["Mathematical model and pipeline-weight estimation", "4–6"],
        ["Explicit H5 and H6 tests", "7–8"],
        ["Performance measures and data requirements", "9"],
        ["Sample-size equations and calculated scenarios", "10–11"],
        ["References and decisions before fieldwork", "12"],
    ], [TEXT_WIDTH-60, 60])

    # 2 — treatment allocation and complete hypothesis family.
    page("1. Experimental design")
    p("Recruit adult undergraduate business students from the intended university population. If the target "
      "is specifically second-year students, make that an eligibility criterion before recruitment. Each "
      "chain contains four different people, one per role; no person switches treatment during the main game.")
    table(["Arm", "Decision time", "Lecture", "(z, e)"], [
        ["A", "Adequate", "Matched control", "(0, 0)"],
        ["B", "Binding", "Matched control", "(1, 0)"],
        ["D", "Adequate", "Causal education", "(0, 1)"],
        ["C", "Binding", "Causal education", "(1, 1)"],
    ], [42, 134, TEXT_WIDTH-240, 64])
    p("Randomize whole chains in blocks of four, assigning one chain to each arm. A block shares one hidden "
      "retail-demand sequence; sequences differ between blocks. Randomize roles within chains and keep "
      "information visibility identical. With <b>k blocks</b>, the study contains <b>k chains per arm, "
      "4k chains and 16k people</b>. Roles and weeks are repeated measurements.")
    h("Hypotheses and outcomes")
    table(["Test", "Outcome and comparison", "Prediction"], [
        ["H1", "Underweighting gap G: pressure versus adequate time, control lecture (B − A)", "Increase"],
        ["H2", "Whole-chain holding + backlog cost C: B − A", "Increase"],
        ["H3", "Underweighting gap G: education versus control under pressure (C − B)", "Decrease"],
        ["H4a", "Mean participant order variance V: C − B", "Decrease"],
        ["H4b", "Bullwhip ratio BW: C − B", "Decrease"],
        ["H5", "Old-rule persistence R: pressure minus adequate time in a separate educated cohort", "Increase"],
        ["H6a", "Education-by-time interaction in G: (C − B) − (D − A)", "Two-sided"],
        ["H6b", "Education-by-time interaction in cost: (C − B) − (D − A)", "Two-sided"],
    ], [44, TEXT_WIDTH-118, 74])
    p("H1–H4 follow the latest presentation; H5/H6 follow the saved project reflection. H4 concerns "
      "order variation and bullwhip, rather than the earlier education-cost wording. The eight tests form "
      "one prespecified Holm-adjusted family. H4a and H4b are related outcomes, not independent replications.", "small")

    # 3 — actual manipulation and protocol.
    page("2. Procedure and human time pressure")
    h("Main-study session")
    for text in [
        "<b>1. Orientation.</b> Consent, eligibility, prior Beer Game/course experience, common instructions, "
        "comprehension correction and four unscored practice weeks.",
        "<b>2. Treatment.</b> Concealed chain allocation, followed by a standardized 20-minute education or "
        "control lecture. Match delivery, instructor attention and engagement. Education explains delays, "
        "accumulation and order propagation without prescribing an ordering policy or inventory target.",
        "<b>3. Game.</b> Forty scored weeks of simultaneous human ordering, followed by server-calculated "
        "shipments, inventory and cost. All scored weeks enter the primary performance measures.",
        "<b>4. Measurement.</b> Thirty-two randomized stock decisions per person, under the assigned time "
        "allowance, estimate inventory and pipeline responses. Administer them after the game, without "
        "correctness feedback, so they cannot train the primary game behavior.",
        "<b>5. Explanation.</b> Collect perceived pressure, lecture comprehension and a short written account "
        "of ordering decisions. Do not exclude randomized participants because the lecture quiz was failed.",
    ]: p(text)
    h("Calibrate deadlines with people")
    p("Use an initial 16-person/four-chain timing pilot, excluded from the main study. Record ordinary "
      "response times and compare candidate allowances near the 25th and 95th percentiles, plus twice "
      "the latter. Check roles, learning, inventory and backlog states separately. The AI's fictional "
      "8- and 120-second allowances are not validated human deadlines.")
    p("Proposed feasibility criteria are at least 90% explicit valid decisions under pressure, at least "
      "95% timely completion under adequate time, greater reported pressure in the short condition, "
      "and little additional benefit from doubling adequate time. These are draft engineering criteria, "
      "not empirical constants. Select deadlines using usability and manipulation checks, not H1–H6 p-values.")
    h("Hold feedback and information constant")
    p("Keep the interval between weekly state releases equal across arms. Hide the current state after "
      "an early lock and reveal no future state. Share own stock, backlog, receipts, incoming demand and "
      "outstanding-order ledger, plus current chain inventories/backlogs and past orders and retail demand. "
      "Never show future realized demand or other players' current uncommitted orders.")
    h("Handle missed deadlines transparently")
    p("A proposed continuation rule executes a standing order that the participant explicitly chose before "
      "the game. Label it as a standing action, retain its actual cost, and do not treat it as a fresh "
      "timed choice in behavioral regressions. An unanswered stock-task item stays missing. This rule "
      "and the missing-data analysis must be finalized in the human pilot.")
    p("Use client render-to-commit time for decision duration; record local and server timestamps separately. "
      "Network delay, time waiting for another person and supply-chain lead time are different quantities.", "small")

    # 4 — full accounting.
    page("3. Physical supply-chain model")
    p("Let g denote chain, r = 1,…,4 denote retailer through factory, and t = 1,…,40 denote scored week. "
      "The model receives stock, observes new demand, fills customer demand, displays the state and then "
      "accepts the new order. Every arm follows this same sequence.")
    table(["Symbol", "Definition at the decision boundary"], [
        ["I, B", "End-of-week on-hand stock and customer backlog"],
        ["A, D, S", "Current physical arrivals, new customer demand and dispatched shipment"],
        ["X = I − B", "Net stock after current receipts and fulfillment"],
        ["P⁻, P⁺", "Own outstanding replenishment before and after the new order"],
        ["q", "New order placed upstream; nonnegative integer"],
    ], [84, TEXT_WIDTH-84])
    eq([r"W_{grt}=I_{gr,t-1}+A_{grt},\qquad L_{grt}=B_{gr,t-1}+D_{grt}",
        r"S_{grt}=\min(W_{grt},L_{grt})",
        r"I_{grt}=W_{grt}-S_{grt},\qquad B_{grt}=L_{grt}-S_{grt}",
        r"X_{grt}=X_{gr,t-1}+A_{grt}-D_{grt}"], "1")
    eq([r"D_{g1t}=d_{gt},\qquad D_{grt}=q_{g,r-1,t-1}\quad(r>1)",
        r"A_{grt}=S_{g,r+1,t-2}\quad(r<4),\qquad A_{g4t}=q_{g4,t-3}"], "2")
    p("Orders take one week to reach suppliers; dispatched goods take two weeks to arrive. The factory "
      "has unlimited production with a three-week delay. A factory order in week 7 arrives in week 10. "
      "Supplier stockouts can lengthen downstream delivery time.")
    eq([r"P^-_{grt}=P^+_{gr,t-1}-A_{grt},\qquad P^+_{grt}=P^-_{grt}+q_{grt}",
        r"IP^-_{grt}=X_{grt}+P^-_{grt}"], "3")
    p("Outstanding stock includes orders awaiting transmission or fulfillment and goods in transit, "
      "once each. It excludes stock already received and the current unplaced order. Do not add supplier "
      "backlog to this ledger a second time, or add current unfilled demand twice to customer backlog.")
    h("Initial conditions and exogenous demand")
    p("Set initial I = 12, B = 0 and P⁺ = 12 per role. For nonfactory roles the initial pipeline is two "
      "dispatched batches of four plus an order of four awaiting processing. Set required pregame shipments "
      "at weeks −1 and 0 to four. Factory orders at weeks −2, −1 and 0 are four; all roles' week-0 orders "
      "are four. Draw customer demand from Uniform{0,…,8}, using one saved sequence per block.")
    p("These delays and initialization are proposed settings for this study. They are not asserted to "
      "reproduce the exact timing convention in Croson and Donohue (2006).", "small")

    # 5 — Donohue and structural distinction.
    page("4. What constitutes underweighting?")
    p("Croson and Donohue (2006), equation (6), p. 329, relate nonnegative orders to inventory, incoming "
      "demand, receipts, outstanding orders and time. Their p. 330 comparison asks whether the "
      "outstanding-stock coefficient is less negative than the inventory coefficient [1]. Using the "
      "explicit ledger defined here, the adapted model is:")
    eq([r"q_{it}=\max\{0,\mu_{it}+\varepsilon_{it}\}",
        r"\mu_{it}=\alpha_{0i}+\alpha_{Ii}X_{i,t-1}+\alpha_{Ri}D_{it}",
        r"\qquad+\alpha_{Si}A_{it}+\alpha_{Ni}P^-_{it}+\alpha_{ti}t"], "4")
    p("An interior constant-target inventory-position rule would choose the target less current net "
      "stock and outstanding stock:")
    eq(r"q^*_{it}=S^*_i-(X_{i,t-1}+A_{it}-D_{it}+P^-_{it})", "5")
    p("This conditional benchmark gives αI = αS = αN = −1 and αR = +1. It is not a proof of global "
      "optimality in a finite-horizon, decentralized chain with uncertain supplier fulfillment.")
    h("Why a pipeline slope alone is insufficient")
    eq(r"q^{latent}_{it}=a_i+\eta_i F_{it}-k_iX_{it}-k_iw_iP^-_{it}+\varepsilon_{it}", "6")
    p("Here F is a specified forecast, k is inventory adjustment gain, and w is the relative pipeline "
      "weight. Inventory responsiveness is κI = k; pipeline responsiveness is κP = kw. A small pipeline "
      "response can therefore reflect slow adjustment, a low pipeline weight, or both. Estimating both "
      "responses separates these explanations when the inventory response is sufficiently identified [2].")
    table(["Quantity", "Calculation", "Interpretation"], [
        ["Inventory response", "κI = −bI", "Order reduction per extra usable unit on hand"],
        ["Pipeline response", "κP = −bP", "Order reduction per extra usable outstanding unit"],
        ["Response gap", "G = κI − κP", "Positive: less response to pipeline than inventory"],
        ["Relative weight", "w = κP / κI", "Ratio separates weighting from common adjustment gain"],
        ["Absolute shortfall", "Uabs = 1 − κP", "Deviation from the diagnostic's one-for-one benchmark"],
    ], [102, 113, TEXT_WIDTH-215])
    p("Report both responses and G. Equal partial responses can produce G = 0 even when both cues are "
      "underused. A change in G need not mean a change in w. Report a ratio of arm-mean slopes with a "
      "Fieller or block-bootstrap interval; if the inventory denominator includes zero, report weak "
      "identification instead of inserting an artificial denominator or clipping the ratio.")
    p("Game histories can contain correlated cues, endogenous states and changing expectations. Their "
      "decision-rule regression is supporting evidence. The randomized stock task on the next page "
      "provides the primary controlled measurement.", "small")

    # 6 — concrete observation-to-estimate bridge.
    page("5. Estimating the two stock responses")
    p("After the game, present 32 one-period allocation decisions. All displayed pipeline stock and the "
      "new order arrive before one known demand/scoring point. There is no earlier demand, spoilage or "
      "holding charge. On-hand and pipeline units are therefore economically interchangeable in this task.")
    eq([r"\ell(q)=0.50\max(I+P+q-D,0)+1.00\max(D-I-P-q,0)",
        r"q^*=\max(0,D-I-P)"], "8")
    p("Use eight frames, each crossing I ∈ {2,6} with P ∈ {2,6}. Demand is 16, 20, 24 or 28, each used "
      "in two frames. Randomize the 32 presentations, show one at a time, and provide no correctness "
      "feedback. Every benchmark order is at least four; observed human zero orders remain valid data.")
    eq(r"q_{ij}=a_{i,frame(j)}+b_{Ii}(I_j-4)+b_{Pi}(P_j-4)+e_{ij}", "9")
    p("With J = 8 and ΔI = ΔP = 4, ordinary least squares yields the same slopes as the balanced "
      "factorial contrasts below. q(j,I,P) denotes the actual observed order in that cell.")
    eq([r"\widehat b_{Ii}=\frac{1}{2J\Delta I}\sum_{j=1}^{J}\{q(j,6,2)-q(j,2,2)",
        r"\qquad+q(j,6,6)-q(j,2,6)\}"], "10")
    eq([r"\widehat b_{Pi}=\frac{1}{2J\Delta P}\sum_{j=1}^{J}\{q(j,2,6)-q(j,2,2)",
        r"\qquad+q(j,6,6)-q(j,6,2)\}"], "11")
    eq(r"\widehat\kappa_{Ii}=-\widehat b_{Ii},\quad\widehat\kappa_{Pi}=-\widehat b_{Pi},\quad\widehat G_i=\widehat b_{Pi}-\widehat b_{Ii}", "12")
    h("Worked example — illustrative, not participant data")
    table(["On-hand I", "Pipeline P", "Observed order"], [
        ["2", "2", "20"], ["6", "2", "17"], ["2", "6", "19"], ["6", "6", "16"],
    ], [TEXT_WIDTH/3]*3)
    p("Four extra on-hand units reduce the order by three; four extra pipeline units reduce it by one. "
      "Thus κI = 0.75, κP = 0.25, G = 0.50 and w = 1/3. Independent cue variation identifies their "
      "separate observed responses. Whether these parameters transfer to the dynamic game remains "
      "an empirical validity question.")
    p("The primary measure includes observed boundary behavior. Retain zero and opposite-direction "
      "responses. Do not impute missing cells as zeros or choose pairs after seeing their effects.", "small")

    # 7 — H5 must not be confused with lower pipeline responsiveness.
    page("6. H5: persistence after conditions change")
    p("H5 predicts greater persistence with an initially adopted replenishment rule under pressure "
      "after changed conditions make that rule less appropriate. It needs evidence of acquisition, "
      "a consequential change and post-change decisions. A static pipeline-response comparison alone "
      "does not test this hypothesis [5].")
    h("Separate educated cohort")
    p("Give new participants the same causal education, then 32 acquisition trials with feedback and "
      "common adequate time. Use demand 48, inventory I ∈ {4,12}, early pipeline PE ∈ {4,12} and labeled "
      "pipeline PL ∈ {8,16}; repeat the eight crossed states four times. Initially both shipments arrive "
      "before the one demand/scoring point.")
    eq(r"q^{old}=48-I-P_E-P_L", "18")
    p("Define adoption before time randomization: at least six of the final eight acquisition orders "
      "are within one unit of the old benchmark. This proposed threshold requires pilot validation. "
      "Record non-adopters; randomize eligible adopters to pressure or adequate time only afterward. "
      "The inference population is educated routine adopters, not all students.")
    h("Change the consequence, then observe transfer")
    p("Explain and check comprehension that PL now arrives after the final scoring point and has no "
      "holding, salvage or demand consequence within the task. New orders and PE still arrive in time. "
      "Give 16 transfer trials without correctness feedback; the first eight form the primary endpoint.")
    eq(r"q^{new}=48-I-P_E,\qquad q^{new}-q^{old}=P_L", "19")
    eq([r"R_{ij}=\frac{q^{new}_j-q_{ij}}{q^{new}_j-q^{old}_j}=\frac{48-I_j-P_{Ej}-q_{ij}}{P_{Lj}}",
        r"\overline{R}_i=\frac{1}{8}\sum_{j=1}^{8}R_{ij}"], "20")
    box("Interpretation", "R = 1 repeats the old benchmark; R = 0 fully adapts. Retain values outside "
        "[0,1]. If I = 4, PE = 4 and PL = 8, the old order is 32 and the new order is 40. Orders of "
        "32, 36 and 40 give persistence scores of 1, 0.5 and 0, respectively.")
    eq(r"q_{ij}=a_i+b_{I,i}I_j+b_{E,i}P_{Ej}+b_{L,i}P_{Lj}+e_{ij}", "21")
    p("As a supporting check, the correct late-pipeline slope changes from −1 to 0; the inventory "
      "and early-pipeline slopes remain −1. <b>Giving a now-useless shipment zero weight is correct "
      "adaptation, not underweighting.</b> Positive R is consistent with persistence, but other errors "
      "can also produce it; inspect acquisition, cue coefficients and explanations together.")
    p("This is a deliberately narrow supply-chain transfer task, not a changed-regime four-person "
      "Beer Game. Excluding people based on their post-randomization transfer performance is not permitted.", "small")

    # 8 — H6 and valid clustering.
    page("7. H6 and the statistical comparisons")
    p("Let μze(Y) denote a mean chain outcome, with z indicating pressure and e indicating education. "
      "For the response gap, first average the four participants' G estimates within each chain.")
    eq([r"\Delta_E^{adequate}(Y)=\mu_{01}(Y)-\mu_{00}(Y)",
        r"\Delta_E^{pressure}(Y)=\mu_{11}(Y)-\mu_{10}(Y)",
        r"\Delta_{int}(Y)=[\mu_{11}(Y)-\mu_{10}(Y)]-[\mu_{01}(Y)-\mu_{00}(Y)]"], "22")
    p("H6a tests the interaction in G; H6b tests the interaction in cost. At the measurement-coefficient "
      "level, the pipeline-underweighting interaction is explicitly:")
    eq([r"\Delta_{int}(G)=[(b_{P,11}-b_{I,11})-(b_{P,10}-b_{I,10})]",
        r"\qquad-[(b_{P,01}-b_{I,01})-(b_{P,00}-b_{I,00})]"], "24")
    p("This directly connects observed stock-task orders to H6. It requires both cue slopes and all "
      "four treatment cells. Significance in one time arm and nonsignificance in another does not "
      "test whether their education effects differ.")
    h("One contrast per randomized block")
    p("For each block b, calculate its arm contrast Lb. Use B − A for H1/H2, C − B for H3/H4, and "
      "(C − B) − (D − A) for H6. With k independent blocks:")
    eq([r"\widehat\Delta=\frac{1}{k}\sum_{b=1}^{k}L_b,\qquad s_L^2=\frac{\sum_b(L_b-\widehat\Delta)^2}{k-1}",
        r"SE(\widehat\Delta)=\frac{s_L}{\sqrt{k}},\qquad t_{obs}=\frac{\widehat\Delta}{SE(\widehat\Delta)}"], "25")
    p("The working t reference has k − 1 degrees of freedom. Report raw-unit mean contrasts and "
      "95% intervals. Resample whole blocks when refitting nonlinear ratios or decision-rule models. "
      "Randomization/sensitivity analyses should assess strongly skewed outcomes. H5 instead compares "
      "independent participants' mean persistence scores in its separate cohort.")
    h("Multiple tests and coefficient uncertainty")
    eq(r"p^{adj}_{(j)}=\min\{1,\max_{\ell\leq j}(8-\ell+1)p_{(\ell)}\}", "26")
    p("Apply Holm to the eight prespecified two-sided p-values. Directional hypotheses additionally "
      "require the predicted estimated sign. Ordinary 95% intervals are estimation intervals, not "
      "simultaneous familywise intervals.")
    eq(r"\mathrm{Var}(\widehat G)=\Sigma_{II}+\Sigma_{PP}-2\Sigma_{IP}", "14")
    p("Σ is the covariance matrix of the two estimated slopes. In the balanced task with independent "
      "equal-variance response error, Var(bI) = Var(bP) = σe²/128 and Cov(bI,bP) = 0, giving Var(G) "
      "= σe²/64. Human power must include this measurement error as well as real person-to-person variation.", "small")

    # 9 — outcomes and concrete data capture.
    page("8. Performance outcomes and data")
    h("Cost: what the chain pays")
    eq(r"C_g=\sum_{r=1}^{4}\sum_{t=1}^{40}(0.50I_{grt}+1.00B_{grt})", "15")
    p("Calculate costs from replayed end-of-week inventory and backlog, in experimental currency. "
      "Also report holding and backlog components separately. Include all forty scored weeks, including "
      "implemented standing actions; exclude practice. Do not append an invented automatic tail. "
      "This follows the accounting structure of Croson and Donohue's equation (4), p. 326 [1].")
    h("Order variation and bullwhip")
    eq([r"v_{gr}=\frac{1}{T-1}\sum_{t=1}^{T}(q_{grt}-\overline{q}_{gr})^2,\qquad V_g=\frac{1}{4}\sum_{r=1}^{4}v_{gr}",
        r"s_{d,g}^2=\frac{1}{T-1}\sum_{t=1}^{T}(d_{gt}-\overline{d}_g)^2,\qquad BW_g=\frac{V_g}{s_{d,g}^2}"], "16–17")
    p("T = 40. Compute each person's variance first, then average across roles. Pooling different "
      "role means creates a different quantity. Use the variance of the actual external-demand path. "
      "A zero denominator makes BW undefined. V and BW share the same numerator and therefore do "
      "not provide independent confirmations of the same mechanism.")
    h("Minimum observation records")
    table(["Record", "Fields that make the calculation auditable"], [
        ["Participant", "Pseudonymous ID, cohort, block, chain, role, treatment, allocation time, eligibility, prior experience"],
        ["Role-week", "Previous stock/backlog, arrivals, new demand, shipments, ending stock/backlog, P⁻/P⁺, fresh and implemented order, source"],
        ["Stock decision", "Person/frame/state IDs, randomized presentation position, I/P/D, literal order and missing reason"],
        ["H5 decision", "Acquisition/transfer phase, I/PE/PL/D, arrival regime, adoption check before allocation, literal order"],
        ["Timing", "Render complete, first entry, final commit, local deadline, server receipt, lock and technical failure"],
    ], [91, TEXT_WIDTH-91])
    p("Save purchase-order and shipment event logs, exact displayed states, demand/allocation seeds and "
      "material versions. Maintain immutable raw records and separate derived tables. Names and student "
      "numbers should not appear in analytical exports.")
    h("Missing data and model checks")
    p("Separate fresh human choices, human-selected standing actions and missing responses. Costs remain "
      "intention-to-treat policy outcomes; a standing action is not a fresh cognitive response. The "
      "reference stock calculator requires all 32 cells. If nonresponse differs by arm, complete-case "
      "estimates can be selected; prespecify an intention-to-treat missing-data sensitivity analysis "
      "before recruitment. Check conservation, duplicate receipts, cue-design rank, boundary choices "
      "and coefficient stability.")

    # 10 — reproducible power model, distinguish levels.
    page("9. Sample-size model")
    p("Choose a smallest meaningful raw-unit effect before setting N. Estimate human endpoint "
      "variability and within-chain correlation in a separate pilot. The AI sample supplies neither. "
      "For G, the SD of estimated participant gaps includes behavioral heterogeneity and measurement error.")
    eq([r"DE=1+(m-1)\rho=1+3\rho,\qquad m=4",
        r"v_G=\mathrm{Var}(\overline{G}_{chain})=\sigma_G^2\frac{DE}{4}"], "P1")
    p("ρ is the within-chain intraclass correlation. For chain-level cost, use v = σC² directly; "
      "do not divide the chain SD by four or add a second participant design effect. Each endpoint "
      "requires its own variance and meaningful difference.")
    eq(r"V_L=a^T\Sigma_{block}a,\qquad\mathrm{Var}(\widehat\Delta)=\frac{V_L}{k}", "P2")
    p("For initial planning, equal cell variance v and zero cross-arm covariance give VL = 2v for "
      "a simple contrast and VL = 4v for an interaction. Common demand may improve precision, but "
      "no benefit is assumed without data. Zero covariance is not a universal conservative bound.")
    eq([r"k_{simple}\simeq\left\lceil\frac{2v(z_{1-\alpha^*/2}+z_{1-\beta})^2}{\Delta^2}\right\rceil",
        r"k_{H6}\simeq\left\lceil\frac{4v(z_{1-\alpha^*/2}+z_{1-\beta})^2}{\Delta_{int}^2}\right\rceil"], "P3")
    p("The tables use the more precise noncentral-t calculation corresponding to the planned "
      "block-contrast test, rather than only this normal approximation:")
    eq([r"\nu=k-1,\qquad\lambda=\Delta\sqrt{k/V_L}",
        r"\mathrm{Power}(k)=\Pr(T_{\nu,\lambda}>t_{1-\alpha^*/2,\nu})",
        r"\qquad+\Pr(T_{\nu,\lambda}<-t_{1-\alpha^*/2,\nu})"], "P4")
    p("Search the integer k for the smallest value reaching the desired power. The calculation is "
      "exact under the stated Gaussian block-contrast model, not an exact prediction for unknown "
      "human cost distributions. Pilot-based simulations must check skew, missingness and unequal variance.")
    h("H5 uses people, not chain blocks")
    eq([r"n\simeq\left\lceil\frac{2\sigma_R^2(z_{1-\alpha^*/2}+z_{1-\beta})^2}{\Delta_R^2}\right\rceil",
        r"\lambda=(\Delta_R/\sigma_R)\sqrt{n/2},\qquad\nu=2n-2"], "P5")
    p("n is randomized adopters per time arm. The calculator uses the corresponding two-sample "
      "noncentral t. Trials within a person do not increase the number of randomized people.")
    p("Planning uses α* = 0.05/8 = 0.00625; final tests use Holm. An 80% target is per endpoint, "
      "not an 80% probability of confirming all eight hypotheses. The interaction's meaningful effect "
      "must be specified independently of either simple education effect.", "small")

    # 11 — source numeric values from the already checked CSV.
    page("10. Calculated recruitment scenarios")
    sizes = pd.read_csv(STUDY / "analysis/sample_sizes.csv")
    core = sizes[(sizes.endpoint_scale == "participant_G") & (sizes.assumed_icc == .1)
                 & (sizes.target_power == .8)]
    rows = []
    for d in [.3, .5, .8]:
        s = core[(core.assumed_standardized_effect == d) & (core.contrast == "simple")].iloc[0]
        t = core[(core.assumed_standardized_effect == d) & (core.contrast == "interaction_H6")].iloc[0]
        rows.append([f"{d:.2f}", int(s.chains_per_cell), f"{int(s.total_people):,}",
                     int(t.chains_per_cell), f"{int(t.total_people):,}"])
    p("Assumptions: four people per chain, ICC = 0.10, 80% power, two-sided α* = 0.00625 and no "
      "cross-arm covariance benefit. dG is a treatment difference divided by the SD of estimated "
      "participant gaps. These are scenarios, not human effect estimates.")
    table(["dG", "Simple: chains / arm", "People, 4 arms", "H6a: chains / arm", "People, 4 arms"],
          rows, [42, 117, 99, 130, TEXT_WIDTH-388])
    story.append(Image(str(STUDY / "analysis/POWER_VS_CHAINS.png"),
                       width=TEXT_WIDTH, height=TEXT_WIDTH*4.4/11.5))
    story.append(Spacer(1, 8))
    p("<b>Ten chains per arm means 160 people.</b> Under dG = 0.50 and ICC = 0.10, this gives "
      "approximately 12.5% power for a simple gap contrast and 5.4% for H6a. For a chain-level "
      "outcome with d = 0.50, the model instead requires 107 chains per arm for a simple contrast "
      "and 209 for an interaction. Raw human cost variability could change these numbers substantially.")
    h("Separate H5 cohort: same α* and 80% target")
    h5 = sizes[(sizes.endpoint_scale == "person_H5_persistence") & (sizes.target_power == .8)]
    table(["Assumed dR", "Adopters / time arm", "Total adopters"], [
        [f"{r.assumed_standardized_effect:.2f}", int(r.randomized_people_per_h5_arm), int(r.total_people)]
        for r in h5.itertuples()], [TEXT_WIDTH/3]*3)
    p("At dR = 0.50, 105 adopters per arm are required. With assumed 80% adoption and 90% retention, "
      "ceil(210 / (0.80 × 0.90)) = 292 invitations gives that expected analyzed count. This is a "
      "separate sample from the main game.")
    p("For complete-block analyses, if each chain is complete with probability rc, block survival "
      "is rc⁴ under independent loss; inflate scheduled blocks accordingly. Do not assume that adding "
      "participants or weeks guarantees significance, and do not use observed p-values as a stopping rule.", "small")

    # 12 — references and scope, concise scholarly prose.
    page("11. Evidence, limits and next steps")
    p("The proposed measurement closes the algebraic gap between order observations and stock-response "
      "parameters. Human validation remains necessary. In particular, the diagnostic's controlled "
      "one-period coefficients may differ from the same person's dynamic game behavior, and the H5 "
      "transfer task addresses a narrower claim than persistence inside an entire four-person chain.")
    h("Before fieldwork")
    p("Finalize and freeze the human deadlines, lecture scripts, compensation, platform, meaningful "
      "effect sizes, missing-data analysis and enrollment target after pilot work and institutional "
      "human-research review. The initial 16-person pilot can assess usability; it cannot precisely "
      "establish all variance and ICC parameters. Use uncertainty ranges and a larger estimation pilot "
      "if needed. Education comprehension is a manipulation measure, not a favorable-outcome filter.")
    h("References and their roles")
    references = [
        ('[1] Croson, R., &amp; Donohue, K. (2006). Behavioral causes of the bullwhip effect and the observed '
         'value of inventory information. <i>Management Science, 52</i>(3), 323–336. '
         '<link href="https://doi.org/10.1287/mnsc.1050.0436" color="#116E79">doi:10.1287/mnsc.1050.0436</link>. '
         'Eq. (4), p. 326: cost; Eq. (6), p. 329 and p. 330: decision rule and stock-weight comparison.'),
        ('[2] Sterman, J. D. (1989). Modeling managerial behavior: Misperceptions of feedback in a dynamic '
         'decision making experiment. <i>Management Science, 35</i>(3), 321–339. '
         '<link href="https://doi.org/10.1287/mnsc.35.3.321" color="#116E79">doi:10.1287/mnsc.35.3.321</link>. '
         'Motivates distinguishing stock adjustment from pipeline weighting.'),
        ('[3] Croson, R., Donohue, K., Katok, E., &amp; Sterman, J. (2014). Order stability in supply chains: '
         'Coordination risk and the role of coordination stock. <i>Production and Operations Management, '
         '23</i>(2), 176–196. <link href="https://doi.org/10.1111/j.1937-5956.2012.01422.x" color="#116E79">'
         'doi:10.1111/j.1937-5956.2012.01422.x</link>. Supports preserving distinct human roles.'),
        ('[4] Oliva, R., Abdulla, H., &amp; Gonçalves, P. (2022). Do managers overreact when in backlog? '
         'Evidence of scope neglect from a supply chain experiment. <i>MSOM, 24</i>(4), 1997–2009. '
         '<link href="https://doi.org/10.1287/msom.2021.1072" color="#116E79">doi:10.1287/msom.2021.1072</link>. '
         'Motivates separate backlog diagnostics and pooled/hierarchical decision models.'),
        ('[5] Betsch, T., Haberstroh, S., Glöckner, A., Haar, T., &amp; Fiedler, K. (2001). The effects of '
         'routine strength on adaptation and information search in recurrent decision making. '
         '<i>OBHDP, 84</i>(1), 23–53. <link href="https://doi.org/10.1006/obhd.2000.2916" color="#116E79">'
         'doi:10.1006/obhd.2000.2916</link>. Motivates acquisition followed by a consequential change.'),
        ('[6] Tian, Z., et al. (2022). Sample size calculation in hierarchical 2 × 2 factorial trials with '
         'unequal cluster sizes. <i>Statistics in Medicine, 41</i>, 645–664. '
         '<link href="https://doi.org/10.1002/sim.9284" color="#116E79">doi:10.1002/sim.9284</link>. '
         'Distinguishes controlled effects from interactions; this report derives its own equal-chain contrast variance.'),
    ]
    for reference in references:
        p(reference, "small")
    h("Reproducibility")
    p("The five numbered Markdown documents hold the full design notes and literature mapping. "
      "The notebook POWER_AND_MEASURES.ipynb reproduces assumptions and examples; sample_sizes.csv "
      "and power_curves.csv hold the plotted numbers. Eight numerical tests and a 30,000-draw Gaussian "
      "power check validate arithmetic, not human behavior. No AI response is treated as a human observation.", "small")

    doc = StudyDocument(str(OUTPUT), pagesize=A4, leftMargin=MARGIN, rightMargin=MARGIN,
                        topMargin=49, bottomMargin=48,
                        title="Human Beer Game Study: Design, Measurement and Sample Size",
                        author="Beer Game Research Project", subject="Proposed human H1–H6 experiment")
    frame = Frame(MARGIN, 48, TEXT_WIDTH, HEIGHT-97, leftPadding=0, rightPadding=0,
                  topPadding=0, bottomPadding=0)
    doc.addPageTemplates(PageTemplate(id="report", frames=frame, onPage=chrome))
    doc.build(story)
    from pypdf import PdfReader
    reader = PdfReader(str(OUTPUT))
    if len(reader.pages) != len(expected_titles):
        raise RuntimeError(f"Expected {len(expected_titles)} pages, produced {len(reader.pages)}; check overflow")
    sources = [*sorted(STUDY.glob("0*.md")), STUDY/"analysis/sample_sizes.csv",
               STUDY/"analysis/POWER_VS_CHAINS.png", Path(__file__)]
    receipt = {"pdf": OUTPUT.name, "pages": len(reader.pages), "date": "2026-11-14",
               "equations": "vector outlines; labels remain searchable text",
               "human_records": 0, "pdf_sha256": hashlib.sha256(OUTPUT.read_bytes()).hexdigest(),
               "sources": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sources},
               "page_titles": expected_titles, "equation_source_map": equation_map}
    (STUDY/"analysis/PDF_VALIDATION.json").write_text(json.dumps(receipt, indent=2), encoding="utf-8")
    print(json.dumps({"pdf": str(OUTPUT), "pages": len(reader.pages), "bytes": OUTPUT.stat().st_size}))


if __name__ == "__main__":
    build()
