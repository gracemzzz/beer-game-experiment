"""Build a source-labelled Excel guide from Experiment 14's saved tables only."""
from __future__ import annotations

import csv
import hashlib
import math
from pathlib import Path
from textwrap import wrap

from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter

ROOT = Path(__file__).resolve().parents[1]
EXP = ROOT / "experiments/14_deadline_student_20261026"
TABLES = EXP / "reports/tables"
OUTPUT = TABLES / "RECORDED_VARIABLES_AND_SOURCES.xlsx"
BG = "Beer Game"
PROP = "Your proposal + study implementation"
ADDED = "Added measurement"
ANALYSIS = "Calculated analysis"
TECH = "Software / provenance"
COLORS = {BG: "E2F0D9", PROP: "DDEBF7", ADDED: "FFF2CC", ANALYSIS: "E4DFEC", TECH: "E7E6E6"}


def read_csv(name):
    with (TABLES / name).open(encoding="utf-8-sig", newline="") as stream:
        return list(csv.DictReader(stream))


def source_for(variable, category="", table=""):
    if variable in {"fictional_student_seconds", "assigned_reading", "shared_inventory", "arm", "condition"}:
        return PROP
    if variable in {"pipeline_sensitivity", "backlog_sensitivity", "probe_quantity", "probe_order", "pipeline_arrivals", "recent_demand_history"}:
        return ADDED
    if category in {"Probe diagnostics", "Probe regression diagnostics"}:
        return ANALYSIS
    if category == "Comprehension and recall":
        return ADDED
    if category in {"Observed response timing", "Completeness and procedure"}:
        return TECH
    if category == "Ordering diagnostics":
        return ANALYSIS
    if variable in {
        "chain_total_cost", "complete_holding_cost", "complete_backlog_cost", "order", "demand",
        "received", "shipped", "inventory", "backlog", "net_inventory", "supply_line", "cost",
        "holding_cost", "backlog_cost", "outstanding_after_order", "customer_demand", "role", "week",
        "final_inventory", "final_backlog", "final_outstanding_after_order", "actual_model_orders",
        "final_observed_inventory", "final_observed_backlog", "final_observed_outstanding_after_order",
        "observed_week_cost", "completed_prefix_cost", "observed_holding_cost", "observed_backlog_cost",
    }:
        return ADDED if "probe" in table.lower() and variable == "order" else BG
    if variable.startswith(("pipeline_", "backlog_")):
        return ANALYSIS
    if variable in {
        "mean_role_order_variance", "mean_role_bullwhip", "customer_demand_sample_variance", "bullwhip",
        "weekly_sample_order_variance", "order_min", "order_max", "zero_order_fraction",
        "ci95_high", "ci95_low", "mean_difference", "difference", "control_value", "treated_value",
        "contrast", "direction", "hypothesis", "metric", "units", "predicted_sign", "n_pairs",
        "p_holm_family_5", "p_two_sided", "test", "randomization_draws", "prefix_size", "interpretation",
        "fitted_order", "residual", "response_slope", "mean_response_slope", "min_response_slope",
        "max_response_slope", "sample_sd_response_slope", "zero_slope_fraction",
        "pair_fixed_effect_intercept", "pair_fixed_effect_response_slope",
    }:
        return ANALYSIS
    if variable in {
        "answer", "correct", "correct_answer", "question_id", "reason", "knowledge_items", "quantity",
        "low_quantity", "high_quantity", "delta_quantity", "low_order", "high_order", "pair_id",
        "low_probe_id", "high_probe_id", "probe_id", "assay_dimension", "timing_profile",
    }:
        return ADDED
    return TECH


def sheet(wb, name, subtitle, headers, rows, widths, source_col=None):
    ws = wb.create_sheet(name)
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.cell(1, 1, name.split(" ", 1)[1]).font = Font(name="Calibri", size=20, bold=True, color="FFFFFF")
    ws.cell(1, 1).fill = PatternFill("solid", fgColor="17324D")
    ws.row_dimensions[1].height = 36
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    ws.cell(2, 1, subtitle).font = Font(name="Calibri", size=11, color="455A64")
    ws.cell(2, 1).alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[2].height = 34
    for col, header in enumerate(headers, 1):
        cell = ws.cell(4, col, header)
        cell.font = Font(name="Calibri", size=11, bold=True, color="FFFFFF")
        cell.fill = PatternFill("solid", fgColor="284D6D")
        cell.alignment = Alignment(wrap_text=True, vertical="center")
    ws.row_dimensions[4].height = 34
    for row_index, values in enumerate(rows, 5):
        height = 34
        for col, value in enumerate(values, 1):
            cell = ws.cell(row_index, col, value)
            cell.font = Font(name="Calibri", size=11, color="203442", bold=(col == 1))
            cell.alignment = Alignment(vertical="top", wrap_text=True)
            if row_index % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="F2F6FA")
            if source_col == col:
                cell.fill = PatternFill("solid", fgColor=COLORS.get(value, "FFFFFF"))
            if isinstance(value, (int, float)):
                cell.number_format = "0.####"
            line_count = sum(max(1, len(wrap(part, max(8, int(widths[col - 1]) - 3)))) for part in str(value or "").split("\n"))
            height = max(height, 15 * line_count + 10)
        ws.row_dimensions[row_index].height = height
    for col, width in enumerate(widths, 1):
        ws.column_dimensions[get_column_letter(col)].width = width
    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:{get_column_letter(len(headers))}{ws.max_row}"
    ws.print_title_rows = "1:4"
    ws.print_options.horizontalCentered = True
    ws.page_setup.orientation = "landscape"
    ws.page_setup.paperSize = ws.PAPERSIZE_A3 if len(headers) > 7 else ws.PAPERSIZE_A4
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.sheet_properties.tabColor = "284D6D"
    ws.print_area = ws.dimensions
    return ws


def numeric(text):
    if text == "":
        return "Undefined (no enforced timer)"
    value = float(text)
    if not math.isfinite(value):
        raise ValueError(f"Nonfinite saved value: {text}")
    return int(value) if value.is_integer() else value


def main():
    input_names = ("VARIABLE_DICTIONARY.csv", "SOURCE_FIELD_DICTIONARY.csv", "ALL_MEASURED_VALUES.csv")
    protected = [TABLES / name for name in input_names] + [TABLES / "ALL_VALUES.xlsx", EXP / "reports/REPORT.md", EXP / "reports/REPORT.pdf"]
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    definitions = read_csv(input_names[0])
    fields = read_csv(input_names[1])
    values = {r["variable"]: r for r in read_csv(input_names[2])}
    origins = {r["variable"]: source_for(r["variable"], r["category"]) for r in definitions}
    wb = Workbook()
    wb.remove(wb.active)
    wb.properties.title = "Experiment 14: Recorded variables and their sources"
    wb.properties.subject = "student_framing_v3 variable inventory; saved data only"
    wb.properties.creator = "Beer Game study"

    guide_rows = [
        ("Scope", "Experiment 14 / student_framing_v3. Ten matched blocks, three conditions, 30 main chain contexts. Four roles and 24 weeks per chain. Development excluded."),
        ("Conditions", "120 s + control reading; 8 s + control reading; 8 s + causal education. These are three conditions in one study."),
        ("Independent variables", "Two between-condition factors: fictional student time allowance and assigned reading. The probe quantity is a separate within-pair assay manipulation."),
        ("H1", "Tight deadlines increase pipeline underweighting. Measured proxy: order reduction per additional outstanding case. Lower response is consistent with more underweighting; no optimal benchmark was estimated."),
        ("H2", "Tight deadlines increase total holding and backlog costs. Measure: cumulative holding plus backlog cost across four roles and 24 weeks."),
        ("Timing", "8 and 120 seconds describe a fictional student scenario. Actual model runtime is unrestricted. Recorded elapsed time includes service, transport and scheduling."),
        ("Units", "A case is the game's inventory unit. The dataset does not define bottles per case. Cost is expressed in game cost units, not actual business expenditure."),
        (BG, "Standard game quantities/mechanics; this does not claim that every current setting exactly reproduces the earliest Beer Game version."),
        (PROP, "Ideas present in the saved ThoughtsReflection proposal; exact 8/120-second values, text delivery and LLM portrayal are current implementation choices."),
        (ADDED, "Custom probes, comprehension questions and recall checks. These are additions to the core game."),
        (ANALYSIS, "Statistics derived from recorded choices or states. Exact aggregations and diagnostics belong to this implementation."),
        (TECH, "Timing, completeness, identifiers, validation and provenance. These are not extra behavioral dependent variables."),
        ("01 Settings", "Experimental factors and fixed settings, with values and origin labels."),
        ("02 Game records", "Weekly game decisions, states and costs."),
        ("03 Outcomes", "Measured outcomes, definitions, units and sources."),
        ("04 Additional records", "Probes, quizzes, timing, statistical outputs and technical records."),
        ("05 All measurements", f"All {len(definitions)} dictionary entries, with source classifications and the {len(values)} saved summary rows. Use the aggregation column: entries can be means, counts, extrema or rates."),
        ("06 Export fields", f"All {len(fields)} entries in SOURCE_FIELD_DICTIONARY.csv ({len({r['field'] for r in fields})} distinct field names). Repeated names across tables are not separate independent variables."),
        ("07 Sources", "Primary description, preserved proposal, frozen protocol, source code and saved tables."),
        ("Detailed observations", "ALL_VALUES.xlsx, in this same folder, contains the full existing raw-value exports. This workbook is an explanatory inventory, not a new experiment or statistical reanalysis."),
    ]
    guide = sheet(wb, "00 Start here", "Read the first five tabs for the plain-language inventory; the last three provide full definitions and traceability.", ["Item", "Explanation"], guide_rows, [31, 118])

    settings = [
        ("Time-pressure framing", "Independent variable", "120 s or 8 s per fictional student decision", "seconds", PROP, "Proposal specifies decision-time constraints; these exact values and fictional implementation are study choices. No model timer."),
        ("Education / assigned reading", "Independent variable", "170-word control reading or 170-word causal supply-chain education", "category", PROP, "Education idea comes from the proposal; here it is a reading, not an actual 20-minute lecture."),
        ("Information sharing", "Fixed environment", "All four roles' physical inventories displayed", "cases by role", PROP, "Information-sharing extension; not a manipulated factor in this sample."),
        ("Supply-chain role", "Repeated role", "Retailer; wholesaler; distributor; factory", "role", BG, "Four roles per chain; roles are not four independent chain observations."),
        ("Game duration", "Fixed setting", "24 weeks", "weeks", BG, "Weekly structure comes from the game; 24 weeks is this experiment's selected horizon."),
        ("Holding-cost rate", "Fixed parameter", 0.5, "game cost units / case / week", BG, "Applied to end-of-week physical inventory."),
        ("Backlog-cost rate", "Fixed parameter", 1, "game cost unit / unfilled case / week", BG, "Applied to end-of-week unfilled demand."),
        ("Matched sampling", "Study design", "10 matched blocks; one context for each of three conditions per block", "30 main chain contexts", TECH, "Inference uses 10 matched block differences; roles and weeks are repeated observations."),
        ("Requested model / effort", "Fixed requested setting", "gpt-6-astra / xhigh", "model / effort", TECH, "Recorded actual_model and actual_effort are UNVERIFIED; requested labels are not provider authentication."),
        ("Actual response deadline", "Fixed runtime setting", "None / unrestricted", "seconds", TECH, "deadline_seconds and model_runtime_limit_seconds are null."),
    ]
    sheet(wb, "01 Settings", "Two manipulated independent variables; all other rows are fixed settings or identifiers.", ["Factor", "Role in study", "Setting / value", "Unit", "Source", "Clarification"], settings, [28, 24, 50, 27, 30, 62], 5)

    game = [
        ("New replenishment order", "order", "Actual nonnegative integer chosen for one role in one week", "cases", BG),
        ("Final-consumer demand", "customer_demand", "External demand at the retailer; count once per chain/week", "cases", BG),
        ("Incoming role demand", "demand", "Order received from the role's downstream customer", "cases", BG),
        ("Replenishment received", "received", "Cases arriving from upstream", "cases", BG),
        ("Shipment quantity", "shipped", "Cases delivered to the downstream customer", "cases", BG),
        ("Physical inventory", "inventory", "Cases left after this week's receipts and shipments", "cases", BG),
        ("Unfilled demand", "backlog", "Demand remaining unfilled after shipments", "cases", BG),
        ("Outstanding before new order", "supply_line", "Previously ordered replenishment not yet received", "cases", BG),
        ("Outstanding after new order", "outstanding_after_order", "Outstanding replenishment including this week's new order", "cases", BG),
        ("Net inventory", "net_inventory", "Physical inventory minus backlog", "cases", BG),
        ("Holding cost", "holding_cost", "0.5 × end-of-week inventory", "game cost units / role-week", BG),
        ("Backlog cost", "backlog_cost", "1 × end-of-week backlog", "game cost units / role-week", BG),
        ("Weekly combined cost", "cost", "Holding cost + backlog cost", "game cost units / role-week", BG),
        ("Shared inventory display", "shared_inventory", "The four roles' inventories shown together; an information display, not a separate outcome", "cases by role", PROP),
    ]
    sheet(wb, "02 Game records", "2,880 role-week rows in WEEKLY_ROLE_VALUES.csv. Game quantities are observed or calculated by the engine; orders are literal model choices.", ["Quantity", "Saved field", "Meaning / calculation", "Unit", "Source"], game, [32, 32, 70, 32, 30], 5)

    outcomes = [
        ("Pipeline underweighting (H1 construct)", "Not directly observed", "Assessed using the pipeline-response proxy below; no normative optimal benchmark estimated", "No direct underweighting score", PROP),
        ("Pipeline response (H1 proxy; also H3)", "pipeline_sensitivity", "For each pair: (order at low outstanding − order at high outstanding) / (high outstanding − low outstanding). Average 8 pairs equally per chain.", "order cases / outstanding case", ADDED),
        ("Total holding and backlog cost (H2)", "chain_total_cost", "Sum (0.5 × inventory + 1 × backlog) across 4 roles and 24 weeks", "game cost units / chain", BG),
        ("Total holding cost", "complete_holding_cost", "Sum 0.5 × inventory across 4 roles and 24 weeks", "game cost units / chain", BG),
        ("Total backlog cost", "complete_backlog_cost", "Sum 1 × backlog across 4 roles and 24 weeks", "game cost units / chain", BG),
        ("Weekly order variance", "mean_role_order_variance", "For each role, sample variance of 24 weekly orders (denominator 23); average the 4 role variances", "cases squared", ANALYSIS),
        ("Bullwhip ratio", "mean_role_bullwhip", "Each role's order variance / final-consumer demand variance; average the 4 role ratios within a chain", "unitless ratio", ANALYSIS),
        ("Final-consumer demand variance", "customer_demand_sample_variance", "Sample variance of 24 external demand values (denominator 23); bullwhip denominator", "cases squared", ANALYSIS),
        ("Response to backlog", "backlog_sensitivity", "For each pair: (order at high backlog − order at low backlog) / (high backlog − low backlog). Average 8 pairs per chain.", "order cases / backlog case", ADDED),
        ("Final inventory", "final_inventory", "Physical inventory after week 24, for each role", "cases", BG),
        ("Final backlog", "final_backlog", "Unfilled demand after week 24, for each role", "cases", BG),
        ("Final outstanding replenishment", "final_outstanding_after_order", "Outstanding replenishment including the final new order, for each role", "cases", BG),
    ]
    sheet(wb, "03 Outcomes", "H1: Tight deadlines increase pipeline underweighting. H2: Tight deadlines increase total holding and backlog costs.", ["Outcome", "Field / status", "Calculation / interpretation", "Unit", "Source"], outcomes, [40, 35, 83, 34, 30], 5)

    checks = [
        ("Probe states and answers", "Inventory, backlog, outstanding replenishment, 3-arrival schedule, demand/history, shared inventories, role and submitted order", ADDED, "32 hypothetical scenario answers per chain: 8 pipeline pairs and 8 backlog pairs. Uses Beer Game quantities in a separate assay."),
        ("Probe pairing", "Pair/scenario identifiers, dimension varied, low/high quantities, quantity difference, low/high orders and completeness", ADDED, "Manipulates outstanding quantity or backlog within a matched pair."),
        ("Order diagnostics", "Minimum order; maximum order; zero-order fraction; all probe answers identical", ANALYSIS, "Calculated from literal game/probe orders; not manipulated factors."),
        ("Probe slope diagnostics", "Mean, minimum, maximum and sample SD of pair slopes; fraction of zero slopes", ANALYSIS, "The equal-weight mean of 8 pipeline slopes is the primary proxy; other summaries are diagnostics."),
        ("Probe regression diagnostics", "Pair fixed-effect slope and intercepts; fitted orders; residuals", ANALYSIS, "Regression slope uses quantity-change-squared weighting; it is not the primary equal-pair mean."),
        ("Comprehension", "Question, choices, submitted answer, answer key, correctness, number answered/correct and accuracy", ADDED, "Four questions per context. The 'reason' field is the scoring-key explanation, not the model's reasoning."),
        ("Time-allowance recall", "Assigned seconds, recalled seconds, correct/incorrect", ADDED, "Checks recall of the fictional allowance; does not establish actual pressure or stress."),
        ("Observed packet timing", "Elapsed seconds; phase; decision ID; median, 90th percentile and maximum latency", TECH, "Game and probe packets each contain 4 choices; the quiz packet contains 4 answers. Includes service/transport/scheduling."),
        ("Completeness", "Weeks completed, probe answers observed, complete/missing pairs, quiz items answered, missing data, endpoint availability", TECH, "Tracks whether required observations exist."),
        ("Submission checks", "Displays opened, packets accepted, acceptance rates, rejected/late events, deadline and on-time fields", TECH, "Actual deadlines are null; deadline compliance is undefined, not evidence of meeting 8/120 seconds."),
        ("Validation", "Replay valid, analysis/replay errors, primary endpoints complete, literal-model-choice verification, review status", TECH, "Checks recorded procedure and physical game consistency."),
        ("Statistical summaries", "Condition means, SDs, minima/maxima, counts, paired differences, 95% intervals, raw and Holm-adjusted p-values", ANALYSIS, "Intervals/tests are calculated outputs; they are not extra observations or independent variables."),
        ("Sample-prefix summaries", "Prefix size, complete-prefix flag, sample counts, effects, intervals, p-values and adjustment", ANALYSIS, "Descriptive summaries of already collected data; not a new stopping rule."),
        ("Identifiers and provenance", "Case/block/role/condition IDs, stage, profiles, seeds, prompts/versions, requested and recorded model/effort, paths and hashes", TECH, "Requested model settings and provider-authenticated settings must remain distinct."),
        ("Event / status history", "Timestamps, literal submission text, displays, acceptance/rejection reasons, completion/stopping status, terminal reason", TECH, "Preserved controller records allow reconstruction of the sequence of events."),
        ("Not measured as behavioral variables", "Hidden thinking time; human stress; bottle count per case; normative optimal pipeline weight", TECH, "These cannot be inferred as observed variables. Temperature and reasoning-token limits are not exposed by the local launcher."),
    ]
    sheet(wb, "04 Additional records", "Supporting measurements, calculated summaries and technical records; these are not all independent experimental factors.", ["Record group", "Recorded fields / quantities", "Source", "Interpretation"], checks, [33, 78, 30, 82], 3)

    definition_rows = []
    for r in definitions:
        variable = r["variable"]
        value_row = values.get(variable)
        vals = [numeric(value_row[f"{arm}_value"]) for arm in "ABC"] if value_row else ["See row-level data"] * 3
        if variable == "fictional_student_seconds":
            vals = [120, 8, 8]
        elif variable == "assigned_reading":
            vals = ["Control reading", "Control reading", "Causal education"]
        label = "Pipeline response (proxy for underweighting)" if variable == "pipeline_sensitivity" else r["definition"]
        definition_rows.append((variable, label, r["category"], origins[variable], r["units"], r["calculation"], r["aggregation"], *vals, r["values_file"]))
    measurement_sheet = sheet(wb, "05 All measurements", "All 88 existing dictionary entries. Values are copied from saved summaries; read the aggregation column before interpreting a value as a mean.", ["Saved variable", "Meaning", "Category", "Source", "Units", "Calculation", "Aggregation", "120 s + control", "8 s + control", "8 s + education", "Values file"], definition_rows, [38, 47, 29, 30, 28, 80, 42, 24, 24, 24, 34], 4)
    for row in range(5, measurement_sheet.max_row + 1):
        filename = measurement_sheet.cell(row, 11).value
        path = TABLES / filename
        if path.is_file():
            measurement_sheet.cell(row, 11).hyperlink = filename
            measurement_sheet.cell(row, 11).font = Font(name="Calibri", size=11, color="0563C1", underline="single")

    field_rows = [(r["source_table"], r["field"], source_for(r["field"], table=r["source_table"]) if r["field"] not in origins else (ADDED if r["field"] == "order" and "probe" in r["source_table"].lower() else origins[r["field"]]), r["definition"], r["exact_values_path"]) for r in fields]
    sheet(wb, "06 Export fields", "Original export dictionary: 248 table/field entries, 155 distinct field names. Source labels are editorial classifications; existing definitions are preserved.", ["Source table", "Field", "Source", "Definition", "Exact values path"], field_rows, [43, 42, 30, 100, 70], 3)

    source_rows = [
        ("Classic Beer Game", "John Sterman, MIT: Teaching Takes Off / The Beer Game", "https://web.mit.edu/jsterman/www/SDG/beergame.html", "Supports roles, weekly orders/states, shipping delays, cost objective and 0.5/1 holding/backlog rates; does not supply this study's custom probes."),
        ("Your proposal", "Saved ThoughtsReflection text", "../../../11_education_deadline/data/source/reflection_20261019/reflection.txt", "Supports time constraints, information sharing and causal education. Exact 8/120-second LLM framing is an implementation choice."),
        ("Current protocol", "Frozen student_framing_v3 protocol", "../../hypotheses/STUDENT_FRAMING_V3.md", "Defines this completed experiment; distinct from earlier experiments and deadline pilots."),
        ("Current prompts", "Exact student framing and reading materials", "../../prompts/student_framing_v3/README.md", "Source for delivered instructions and readings."),
        ("Measurement dictionary", "VARIABLE_DICTIONARY.csv", "VARIABLE_DICTIONARY.csv", "88 existing entries; definitions, units, calculations and aggregation."),
        ("Saved summary values", "ALL_MEASURED_VALUES.csv", "ALL_MEASURED_VALUES.csv", "81 existing summary rows; numerical values copied without reanalysis."),
        ("Original export fields", "SOURCE_FIELD_DICTIONARY.csv", "SOURCE_FIELD_DICTIONARY.csv", "248 table/field entries, including repeated names across source tables."),
        ("All observation values", "ALL_VALUES.xlsx", "ALL_VALUES.xlsx", "Existing workbook with full current tables and raw-value exports."),
        ("Controller", "exp14_framing.py", "../../../../src/beergame_study/exp14_framing.py", "Literal choices, timing, status, validation and provenance records."),
        ("Presentation calculations", "exp14_publication.py", "../../../../src/beergame_study/exp14_publication.py", "Code that defines current published measurements and summaries."),
        ("Workbook generator", "export_exp14_variable_inventory.py", "../../../../scripts/export_exp14_variable_inventory.py", "Rebuild offline; reads saved records and makes no model/API calls."),
    ]
    source_sheet = sheet(wb, "07 Sources", "Origin labels distinguish standard game mechanics, proposal concepts, implementation choices and derived analysis.", ["Source type", "Document / file", "Location / link", "What it supports"], source_rows, [30, 50, 88, 85])
    for row in range(5, source_sheet.max_row + 1):
        cell = source_sheet.cell(row, 3)
        if not cell.value.startswith("https://") and not (TABLES / cell.value).is_file():
            raise FileNotFoundError(cell.value)
        cell.hyperlink = cell.value
        cell.font = Font(name="Calibri", size=11, color="0563C1", underline="single")
    for row in range(5, guide.max_row + 1):
        key = guide.cell(row, 1).value
        if key in wb.sheetnames:
            guide.cell(row, 1).hyperlink = f"#'{key}'!A1"
            guide.cell(row, 1).font = Font(name="Calibri", size=11, bold=True, color="0563C1", underline="single")
        if key in COLORS:
            guide.cell(row, 1).fill = PatternFill("solid", fgColor=COLORS[key])
    wb.active = 0
    wb.save(OUTPUT)

    check = load_workbook(OUTPUT, data_only=False)
    assert check["05 All measurements"].max_row - 4 == len(definitions)
    assert check["06 Export fields"].max_row - 4 == len(fields)
    for row in check["05 All measurements"].iter_rows(min_row=5, values_only=True):
        if row[0] in values:
            expected = [numeric(values[row[0]][f"{arm}_value"]) for arm in "ABC"]
            for actual, original in zip(row[7:10], expected):
                assert actual == original if isinstance(original, str) else math.isclose(actual, original, rel_tol=1e-14, abs_tol=1e-14)
    assert not any(c.data_type == "f" for ws in check for row in ws for c in row), "Unexpected Excel formula"
    check.close()
    assert all(hashlib.sha256(p.read_bytes()).hexdigest() == digest for p, digest in before.items()), "Source artifact changed"
    print(f"Created {OUTPUT}")
    print(f"Verified: {len(wb.sheetnames)} sheets; {len(definitions)} measurement definitions; {len(fields)} original field entries; {len(values) * 3} saved condition values; input files unchanged.")


if __name__ == "__main__":
    main()
