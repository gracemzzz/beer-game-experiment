"""Read-only checks of values, comparisons, links and preserved experiment-14 data."""
from pathlib import Path
from itertools import product
import argparse
import csv
import json
import math
import re
import statistics as st
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))
from beergame_study.exp14_publication import EXPERIMENT, ARMS, sha, read, verify_preservation
from verify_exp14_framing_results import metrics, exact_p


def csv_rows(path):
    with path.open(encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def near(a, b):
    if not math.isclose(float(a), float(b), rel_tol=1e-10, abs_tol=1e-10):
        raise AssertionError((a, b))


def verify():
    exp = EXPERIMENT; reports = exp / "reports"; tables = reports / "tables"
    preservation = verify_preservation(exp)
    publication = read(reports / "PUBLICATION.json")
    for name, expected in publication["artifacts"].items():
        assert sha(reports / name) == expected, name
    assert sorted(str(p.relative_to(reports)) for p in reports.rglob("REPORT.*")) == ["REPORT.md", "REPORT.pdf"]
    raw = {}; independent = {}
    for p in sorted((exp / "data/student_framing_v3/main").glob("*/RESULT.json")):
        r, c = read(p), read(p.parent / "CASE.json"); ident = (r["block_id"], r["arm"])
        raw[ident] = r; independent[ident] = metrics(r, c)
        independent[ident].update(holding=sum(.5*s["inventory"] for w in r["weeks"] for s in w["roles"]),
                                 backlog=sum(s["backlog"] for w in r["weeks"] for s in w["roles"]))
    primary = csv_rows(tables / "CONDITION_OUTCOMES.csv")
    assert len(primary) == 12 and len(independent) == 30
    for row in primary:
        values = [v[row["variable"]] for (block, arm), v in independent.items() if arm == row["arm"]]
        for key, expected in (("mean", st.mean(values)), ("sd_across_chains", st.stdev(values)), ("minimum", min(values)), ("maximum", max(values))):
            near(row[key], expected)
        assert row["condition"] == ARMS[row["arm"]]
    comparisons = csv_rows(tables / "HYPOTHESIS_COMPARISONS.csv")
    p_values = []
    for row in comparisons:
        first, second = row["contrast"].split("-")
        assert row["first_condition"] == ARMS[first] and row["second_condition"] == ARMS[second]
        assert row["comparison"] == ARMS[first] + " minus " + ARMS[second]
        values = [independent[(b, first)][row["metric"]] - independent[(b, second)][row["metric"]] for b in sorted({b for b, a in raw})]
        near(st.mean(values), row["mean_difference"])
        near(float(row["first_condition_mean"]) - float(row["second_condition_mean"]), row["mean_difference"])
        p = exact_p(values); near(p, row["p_two_sided"]); p_values.append(p)
    bound = 0.
    for rank, i in enumerate(sorted(range(5), key=lambda i: p_values[i])):
        bound = max(bound, min(1., (5-rank)*p_values[i])); near(bound, comparisons[i]["p_holm_family_5"])
    summary = {r["variable"]: r for r in csv_rows(tables / "ALL_MEASURED_VALUES.csv")}
    weekly = csv_rows(tables / "WEEKLY_ROLE_VALUES.csv")
    assert len(weekly) == 2880
    raw_checks = 0
    for row in weekly:
        record = raw[(row["block_id"], row["arm"])]
        week = record["weeks"][int(row["week"])-1]
        index = [s["role"] for s in week["roles"]].index(row["role"]); state = week["roles"][index]
        for field in ("inventory", "backlog", "net_inventory", "supply_line", "received", "shipped", "demand", "cost"):
            near(row[field], state[field]); raw_checks += 1
        near(row["order"], week["orders"][index]); near(row["outstanding_after_order"], state["supply_line"]+week["orders"][index]); raw_checks += 2
    for arm in ARMS:
        selected = [r for (b, a), r in raw.items() if a == arm]
        orders = [q for r in selected for w in r["weeks"] for q in w["orders"]]
        near(summary["game_order_min"][arm+"_value"], min(orders)); near(summary["game_order_max"][arm+"_value"], max(orders))
        near(summary["game_zero_order_fraction"][arm+"_value"], sum(q == 0 for q in orders) / len(orders))
        for key, independent_key in (("complete_holding_cost", "holding"), ("complete_backlog_cost", "backlog")):
            near(summary[key][arm+"_value"], st.mean(v[independent_key] for (b, a), v in independent.items() if a == arm))
        for field in ("inventory", "backlog", "outstanding_after_order"):
            actual = st.mean(sum(s[field] if field != "outstanding_after_order" else s["supply_line"]+r["weeks"][-1]["orders"][i]
                                 for i, s in enumerate(r["weeks"][-1]["roles"])) for r in selected)
            near(summary["final_"+field][arm+"_value"], actual)
    probes = csv_rows(tables / "PROBE_ANSWERS.csv"); assert len(probes) == 960
    for row in probes:
        assert int(row["order"]) == raw[(row["block_id"], row["arm"])]["probe_answers"][row["probe_id"]]
    quiz = csv_rows(tables / "QUIZ_ANSWERS.csv"); assert len(quiz) == 120
    for row in quiz:
        assert row["answer"] == raw[(row["block_id"], row["arm"])]["comprehension_answers"][row["question_id"]]
    assert len(csv_rows(tables / "RESPONSE_TIMES.csv")) == 990
    source_dictionary = csv_rows(tables / "SOURCE_FIELD_DICTIONARY.csv")
    for path in (exp / "analysis/student_framing_v3/tables").glob("*.csv"):
        rows = csv_rows(path)
        if rows:
            covered = {r["field"] for r in source_dictionary if r["source_table"] == path.name}
            assert covered == set(rows[0]), path.name
    for item in read(reports / "figures/FIGURE_DEFINITIONS.json"):
        assert item["calculation"] and item["caption"] and item["axes"]
        for ax in item["axes"]:
            assert ax["x_label"] and ax["y_label"], (item["file"], ax)
    roots = [ROOT / "README.md", ROOT / "experiments/README.md", exp / "README.md", exp / "archive/README.md", *reports.rglob("*.md")]
    broken = []
    for path in roots:
        for dest in re.findall(r"!?\[[^]]*\]\(([^)]+)\)", path.read_text(encoding="utf-8")):
            if "://" in dest or dest.startswith("#"):
                continue
            target = (path.parent / dest.split("#", 1)[0]).resolve()
            if not target.exists(): broken.append((str(path), dest))
    assert not broken, broken
    from pypdf import PdfReader
    pdf = PdfReader(reports / "REPORT.pdf"); text = "\n".join(p.extract_text() for p in pdf.pages)
    for phrase in ("Independent variables", "Dependent variables", "574.45", "642.95", "538.45", "Calculation and aggregation", "Backlog", "seconds", "0.009766"):
        assert phrase in text, phrase
    result = dict(passed=True, **preservation, published_primary_condition_values=12,
                  independently_checked_comparisons=5, independently_checked_weekly_state_fields=raw_checks,
                  actual_probe_answers_checked=960, actual_quiz_answers_checked=120,
                  summary_variables=len(summary), original_export_fields_documented=len(source_dictionary),
                  report_pdf_pages=len(pdf.pages), broken_current_links=broken, new_model_calls=0,
                  publication_sha256=sha(reports / "PUBLICATION.json"), verifier_sha256=sha(Path(__file__)))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipt", type=Path)
    args = parser.parse_args(); result = verify()
    if args.receipt:
        args.receipt.parent.mkdir(parents=True, exist_ok=True)
        args.receipt.write_text(json.dumps(result, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(result, indent=2))
