"""Read-only H1/H2 analysis of saved fixed-high student-protocol evidence.

This module is separate from the five frozen experiment sources. Import and
analysis never construct a client, modify a run, or purchase new observations.
Weekly decisions and interacting roles are not independent participants.
"""
from __future__ import annotations

import ast
import hashlib
import itertools
import json
import math
from pathlib import Path
from typing import Any, Mapping

import numpy as np
import pandas as pd

from .estimation import estimate_beta
from .game import BeerGame, ROLES, demand_path
from .reasoning_protocol import (PROTOCOL, ORDER_SCHEMA, RULES_SCHEMA, ReasoningConfig,
                                 StudyStopped, decide, digest, make_messages, rules_messages, rules_result)
from .student_study import load_calibration


MINIMUM_PAIRS = 8  # inherited software floor; not a power calculation
SIGNFLIP_SEED = 7
HYPOTHESES = (
    ("H1", "group_beta", "Mean of four usable role supply-line coefficients per chain", -1),
    ("H2", "total_scored_cost", "Team holding plus backlog cost across game and automatic scoring weeks", 1),
)
SOURCE_NAMES = ("reasoning_protocol.py", "student_study.py", "student_report.py", "game.py", "estimation.py")
STATE_FIELDS = ("week", "role", "demand", "received", "shipped", "inventory", "backlog",
                "net_inventory", "supply_line", "cost", "shared_inventory")
SHARED_CHECKS = (
    ("api_observations", "Genuine API simulations are required; synthetic checks are software evidence only."),
    ("calibration_passed", "The prospective completion-and-actual-token-usage manipulation screen must pass."),
    ("complete_planned_sample", "Every chain in the frozen pre-outcome plan must finish game and scoring continuation."),
    ("no_replacements", "No chain may be replaced after outcomes; operational cached resume is not replacement."),
    ("no_fallbacks_or_missing", "All planned model decisions must be observed without mechanical fallback orders."),
    ("model_effort_caps_consistent", "The pinned model, high effort, exact prompts, and frozen caps must be consistent."),
    ("rules_checks_passed", "All common factual onboarding checks must pass before gameplay."),
)


class AnalysisError(ValueError):
    """Saved scientific provenance or physical evidence cannot be reconciled."""


def _json(path: Path, default=None):
    if not path.exists():
        return default
    try:
        return json.loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError) as exc:
        raise AnalysisError(f"Cannot read saved JSON: {path.name}") from exc


def _csv(path: Path) -> pd.DataFrame:
    if not path.exists():
        return pd.DataFrame()
    try:
        return pd.read_csv(path)
    except pd.errors.EmptyDataError:
        return pd.DataFrame()


def _true(value) -> bool:
    return value is True or str(value).lower() in ("true", "1", "1.0")


def _finite(value) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def _safe(value: Any):
    if isinstance(value, Mapping):
        return {str(k): _safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple)):
        return [_safe(v) for v in value]
    if isinstance(value, (np.bool_, bool)):
        return bool(value)
    if isinstance(value, (np.integer, int)):
        return int(value)
    if isinstance(value, (float, np.floating)):
        return float(value) if math.isfinite(float(value)) else None
    if value is pd.NA:
        return None
    return value


def signflip(differences, seed: int = SIGNFLIP_SEED) -> float:
    """Legacy two-sided paired sign-flip p-value, with an explicit finite input.

    Exact enumeration through 16 pairs; otherwise 50,000 seeded draws and the
    same +1 Monte Carlo correction as the historical implementation. This is
    an exploratory test requiring exchangeable signs under the null, not a
    design-based guarantee or a human-population test.
    """
    d = np.asarray(differences, dtype=float)
    if d.ndim != 1 or not len(d) or not np.isfinite(d).all():
        raise ValueError("Sign flips require a nonempty finite vector of independent pair contrasts.")
    n = len(d)
    if n <= 16:
        signs = np.asarray(list(itertools.product((-1, 1), repeat=n)), dtype=float)
        values = np.abs(signs @ d / n)
        return float(np.mean(values >= abs(d.mean()) - 1e-12))
    rng = np.random.default_rng(seed)
    values = np.abs(rng.choice([-1, 1], size=(50000, n)) @ d / n)
    return float((1 + np.sum(values >= abs(d.mean()) - 1e-12)) / 50001)


def paired_contrasts(groups: pd.DataFrame, planned_pairs: int) -> pd.DataFrame:
    """Retain every planned block; never silently select complete-case pairs."""
    if type(planned_pairs) is not int or planned_pairs < 0:
        raise ValueError("The frozen planned pair count must be a nonnegative integer.")
    required = {"block", "condition", "group_beta", "usable_role_betas", "total_scored_cost"}
    if not required.issubset(groups.columns) and not groups.empty:
        raise ValueError("Group outcomes lack required hypothesis fields.")
    if not groups.empty:
        if groups.duplicated(["block", "condition"]).any():
            raise ValueError("More than one chain occupies a planned block/condition; replacements cannot be pooled.")
        if not set(groups.condition).issubset({"short", "adequate"}):
            raise ValueError("Unknown token condition.")
        if not set(groups.block).issubset(set(range(planned_pairs))):
            raise ValueError("Observed blocks differ from the frozen plan.")
    rows = []
    lookup = {(int(row.block), row.condition): row for row in groups.itertuples(index=False)}
    for hypothesis, outcome, _, _ in HYPOTHESES:
        for block in range(planned_pairs):
            values, ids = {}, {}
            reasons = []
            for condition in ("short", "adequate"):
                row = lookup.get((block, condition))
                ids[condition] = getattr(row, "group_id", "") if row is not None else ""
                value = getattr(row, outcome, np.nan) if row is not None else np.nan
                if row is None:
                    reasons.append(f"missing {condition} chain")
                elif hypothesis == "H1" and getattr(row, "usable_role_betas", 0) != len(ROLES):
                    value = np.nan
                    reasons.append(f"{condition} lacks four usable role beta fits")
                elif not _finite(value):
                    reasons.append(f"missing {condition} {outcome}")
                values[condition] = float(value) if _finite(value) else np.nan
            usable = all(_finite(v) for v in values.values())
            rows.append(dict(hypothesis=hypothesis, block=block, outcome=outcome,
                             short_group_id=ids["short"], adequate_group_id=ids["adequate"],
                             short_value=values["short"], adequate_value=values["adequate"],
                             contrast=values["short"]-values["adequate"] if usable else np.nan,
                             usable_pair=usable, pair_reason="; ".join(reasons) or "complete outcome pair"))
    return pd.DataFrame(rows, columns=["hypothesis", "block", "outcome", "short_group_id", "adequate_group_id",
                                      "short_value", "adequate_value", "contrast", "usable_pair", "pair_reason"])


def inference_results(groups: pd.DataFrame, planned_pairs: int, gates: Mapping[str, bool],
                      seed: int = SIGNFLIP_SEED) -> dict[str, pd.DataFrame]:
    """Separate H1/H2 eligibility while preserving the preplanned two-test family."""
    contrasts = paired_contrasts(groups, planned_pairs)
    rows, checks = [], []
    for hypothesis, outcome, estimand, predicted_sign in HYPOTHESES:
        own = contrasts[contrasts.hypothesis == hypothesis]
        paired_n = int(own.usable_pair.sum())
        all_outcomes = planned_pairs > 0 and paired_n == planned_pairs
        criteria = [(name, bool(gates.get(name, False)), reason) for name, reason in SHARED_CHECKS]
        criteria += [("minimum_independent_pairs", planned_pairs >= MINIMUM_PAIRS,
                      f"At least {MINIMUM_PAIRS} planned independent complete pairs are required by the inherited software floor; this is not adequate-power evidence."),
                     ("all_planned_outcomes_usable", all_outcomes,
                      "Every planned chain must have four usable role beta fits." if hypothesis == "H1"
                      else "Every planned chain must have its full game-plus-continuation scored cost; H2 does not require beta identification.")]
        checks.extend(dict(hypothesis=hypothesis, check=name, passed=passed, detail=reason)
                      for name, passed, reason in criteria)
        reasons = [reason for _, passed, reason in criteria if not passed]
        eligible = not reasons
        estimate = float(own.contrast.mean()) if all_outcomes else np.nan
        direction = "negative" if _finite(estimate) and estimate < 0 else "positive" if _finite(estimate) and estimate > 0 else "zero" if _finite(estimate) else "missing"
        p = signflip(own.contrast.to_numpy(), seed) if eligible else np.nan
        symbol = "<" if predicted_sign < 0 else ">"
        rows.append(dict(hypothesis=hypothesis, outcome=outcome, estimand=estimand,
                         contrast_definition="short minus adequate", H0="Mean paired contrast = 0",
                         alternative=f"Mean paired contrast {symbol} 0", predicted_direction=f"short minus adequate {symbol} 0",
                         planned_pairs=planned_pairs, complete_pairs=paired_n, estimate=estimate,
                         observed_direction=direction,
                         matches_predicted_direction=bool(_finite(estimate) and predicted_sign*estimate > 0),
                         eligible=eligible, p_raw=p, p_holm=np.nan, family_size=2,
                         ci_lower=np.nan, ci_upper=np.nan,
                         inference_method="Two-sided paired sign flip; Holm family of two",
                         ci_method="No confidence interval was prespecified in the legacy hypothesis procedure; none computed",
                         status="exploratory paired chain test" if eligible else "inference withheld",
                         individual_reasons="; ".join(reasons) if reasons else "All operational gates passed; eight pairs alone do not establish power or human validity."))
    # A missing hypothesis occupies its planned family slot with 1 internally;
    # exported missing p-values remain missing, never a manufactured p=1.
    internal = np.array([r["p_raw"] if _finite(r["p_raw"]) else 1.0 for r in rows])
    order = np.argsort(internal, kind="stable")
    adjusted = np.empty(2)
    adjusted[order[0]] = min(1.0, 2*internal[order[0]])
    adjusted[order[1]] = max(adjusted[order[0]], internal[order[1]])
    for i, row in enumerate(rows):
        if _finite(row["p_raw"]):
            row["p_holm"] = float(adjusted[i])
        row["reject_equal_effect_null_holm_05"] = bool(_finite(row["p_holm"]) and row["p_holm"] < .05)
        row["hypothesis_supported_holm_05"] = bool(row["reject_equal_effect_null_holm_05"] and row["matches_predicted_direction"])
        row["conclusion"] = ("Directional hypothesis supported in exploratory model simulation" if row["hypothesis_supported_holm_05"]
                             else "Equal-effect null rejected in the opposite direction" if row["reject_equal_effect_null_holm_05"]
                             else "Not rejected; does not establish equivalence" if row["eligible"]
                             else "Not tested; descriptive outcomes do not establish a treatment effect or equivalence")
    return {"hypotheses": pd.DataFrame(rows), "block_contrasts": contrasts, "inference_checks": pd.DataFrame(checks)}


def hypothesis_table(groups: pd.DataFrame, planned_pairs: int, gates: Mapping[str, bool],
                     seed: int = SIGNFLIP_SEED) -> pd.DataFrame:
    return inference_results(groups, planned_pairs, gates, seed)["hypotheses"]


def _source_provenance(directory: Path, manifest: Mapping) -> dict:
    hashes = manifest.get("source_hashes", {})
    if set(hashes) != set(SOURCE_NAMES) or manifest.get("protocol") != PROTOCOL:
        raise AnalysisError("This analysis requires the fixed-high student protocol and exact five-source provenance.")
    for name, expected in hashes.items():
        current = Path(__file__).with_name(name)
        saved = directory/"source_implementation"/name
        if not saved.exists() or digest(saved.read_text(encoding="utf-8")) != expected or digest(current.read_text(encoding="utf-8")) != expected:
            raise AnalysisError(f"Scientific implementation differs from the saved run: {name}")
    return dict(hashes)


def _records(directory: Path, config: ReasoningConfig):
    records, latest = [], {}
    fields = ("protocol", "identity", "messages", "limit", "schema", "requested_model", "reasoning", "mode", "config_fingerprint")
    for path in sorted((directory/"requests").glob("*.json")):
        record = _json(path)
        if not isinstance(record, dict):
            raise AnalysisError("Malformed saved request record.")
        key = digest({name: record.get(name) for name in fields})
        suffixes = (key, key+"_retry_1", key+"_retry_2")
        if (record.get("request_key") != key or path.stem not in suffixes or record.get("protocol") != PROTOCOL
                or record.get("requested_model") != config.model or record.get("reasoning") != {"effort": "high"}
                or record.get("requested_effort") != "high" or record.get("mode") != config.mode
                or record.get("config_fingerprint") != config.fingerprint() or record.get("timeout_s") != config.timeout_s
                or bool(record.get("synthetic")) != (config.mode == "offline")):
            raise AnalysisError(f"Request provenance does not match the fixed scientific configuration: {path.name}")
        stage = record.get("identity", {}).get("stage")
        if stage not in ("calibration", "rules", "decision"):
            raise AnalysisError("Unknown saved request stage.")
        if record.get("schema") != (RULES_SCHEMA if stage == "rules" else ORDER_SCHEMA):
            raise AnalysisError("Saved request schema differs.")
        if config.mode == "api" and record.get("status") == "ok" and record.get("returned_model") != config.model:
            raise AnalysisError("Returned model differs from the pinned model.")
        record = dict(record, _request_file=path.name)
        records.append(record)
        identity_key = digest(record["identity"])
        attempt = suffixes.index(path.stem)
        if identity_key not in latest or attempt > latest[identity_key][0]:
            latest[identity_key] = (attempt, record)
        elif attempt == latest[identity_key][0]:
            # Different messages for one calibrated item are the declared repair;
            # decision/rules duplicates are never extra independent observations.
            if stage != "calibration":
                raise AnalysisError("Multiple scientific requests share a decision identity.")
    return records, {key: record for key, (_, record) in latest.items()}


def _int(value, name):
    if not _finite(value) or float(value) < 0 or not float(value).is_integer():
        raise AnalysisError(f"Saved {name} must be a nonnegative integer.")
    return int(value)


def _state_matches(row, state):
    for name in STATE_FIELDS:
        value = row[name]
        if name == "shared_inventory":
            if isinstance(value, str):
                try:
                    value = ast.literal_eval(value)
                except (ValueError, SyntaxError) as exc:
                    raise AnalysisError("Malformed saved shared inventory.") from exc
            equal = value == state[name]
        elif name == "role":
            equal = value == state[name]
        else:
            equal = _finite(value) and math.isclose(float(value), float(state[name]), rel_tol=0, abs_tol=1e-9)
        if not equal:
            raise AnalysisError(f"Physical state/cost reconstruction disagrees at {row['group_id']}, week {row['week']}, {row['role']}, {name}.")


def _game_outcomes(rounds, tail, config, selection, latest):
    group_rows, fit_rows = [], []
    if rounds.empty:
        return pd.DataFrame(columns=["group_id", "block", "condition", "group_beta", "usable_role_betas", "total_scored_cost"]), pd.DataFrame()
    required = set(STATE_FIELDS) | {"order", "group_id", "block", "condition", "phase", "valid_decision", "fallback", "token_limit"}
    if not required.issubset(rounds.columns):
        raise AnalysisError("Saved rounds lack the physical state and decision provenance fields.")
    if rounds.duplicated(["group_id", "week", "role"]).any() or (not tail.empty and tail.duplicated(["group_id", "week", "role"]).any()):
        raise AnalysisError("Duplicate physical observations are not independent evidence.")
    if not tail.empty and not set(tail.group_id).issubset(set(rounds.group_id)):
        raise AnalysisError("A scoring continuation has no corresponding observed game.")
    for gid, own in rounds.groupby("group_id", sort=True):
        blocks, conditions = own.block.unique(), own.condition.unique()
        if len(blocks) != 1 or len(conditions) != 1:
            raise AnalysisError("Chain metadata changes during a trajectory.")
        block, condition = _int(blocks[0], "block"), conditions[0]
        if condition not in ("short", "adequate") or gid != f"b{block:03d}_{condition}" or block >= selection["groups_per_condition"]:
            raise AnalysisError("Observed chain identity differs from the frozen plan.")
        weeks = sorted(_int(w, "week") for w in own.week.unique())
        if weeks != list(range(1, len(weeks)+1)) or len(weeks) > config.weeks:
            raise AnalysisError("Committed game weeks are not a contiguous prefix of the planned horizon.")
        game, histories, last = BeerGame(), {r: [] for r in ROLES}, {r: 4 for r in ROLES}
        missing, fallback, valid, game_cost = 0, 0, 0, 0.0
        for week in weeks:
            saved = own[own.week == week].set_index("role")
            if set(saved.index) != set(ROLES) or len(saved) != len(ROLES):
                raise AnalysisError("A committed game week lacks exactly four role observations.")
            states = game.observe(demand_path(config.weeks)[week-1])
            orders = []
            for state in states:
                role = state["role"]
                row = saved.loc[role].to_dict() | {"role": role}
                _state_matches(row, state)
                order = _int(row["order"], "order")
                if week <= config.warmup_weeks:
                    if row["phase"] != "warmup" or order != 4 or _true(row["fallback"]) or _true(row["valid_decision"]):
                        raise AnalysisError("Familiarization differs from the prespecified fixed-order rule.")
                else:
                    record = latest.get(digest(dict(stage="decision", group=gid, role=role, week=week)))
                    if record is None or record["messages"] != make_messages(state, histories[role]):
                        raise AnalysisError("Committed decision is missing its exact state/history prompt.")
                    cap = selection[condition+"_tokens"]
                    if record["limit"] != cap or row["token_limit"] != cap or row["phase"] != "agent":
                        raise AnalysisError("A decision used an allowance or phase inconsistent with the frozen plan.")
                    decision = decide(record, last_valid_order=last[role], emergency_order_limit=config.emergency_order_limit)
                    if order != decision.order or _true(row["valid_decision"]) != decision.valid or _true(row["fallback"]) != decision.fallback:
                        raise AnalysisError("Committed action does not match the saved model response or prespecified fallback.")
                    if decision.valid:
                        last[role] = order
                    missing += not decision.valid
                    fallback += decision.fallback
                    valid += decision.valid
                histories[role].append(dict(state, order=order, fallback=_true(row["fallback"])))
                orders.append(order)
                game_cost += .5*state["inventory"]+state["backlog"]
            game.commit(orders)
        full_game = len(weeks) == config.weeks
        own_tail = tail[tail.group_id == gid] if not tail.empty else pd.DataFrame()
        tail_weeks = sorted(_int(w, "week") for w in own_tail.week.unique()) if not own_tail.empty else []
        if tail_weeks and (not full_game or tail_weeks != list(range(config.weeks+1, config.weeks+1+len(tail_weeks))) or len(tail_weeks) > config.continuation_weeks):
            raise AnalysisError("Scoring continuation does not follow the declared full game.")
        tail_cost = 0.0
        for week in tail_weeks:
            saved = own_tail[own_tail.week == week].set_index("role")
            if set(saved.index) != set(ROLES) or len(saved) != len(ROLES):
                raise AnalysisError("A committed continuation week lacks four roles.")
            states = game.observe(demand_path(config.weeks)[-1])
            for state in states:
                row = saved.loc[state["role"]].to_dict() | {"role": state["role"]}
                _state_matches(row, state)
                if row["order"] != state["demand"] or row["phase"] != "automatic" or row["block"] != block or row["condition"] != condition:
                    raise AnalysisError("Scoring continuation differs from the frozen automatic-order rule.")
                tail_cost += .5*state["inventory"]+state["backlog"]
            game.commit([s["demand"] for s in states])
        full_tail = len(tail_weeks) == config.continuation_weeks
        own_fits = []
        for role in ROLES:
            agent = own[(own.role == role) & (own.phase == "agent")]
            fit = dict(beta=np.nan, usable=False, fit_flag="missing_decisions_or_fallback", n=len(agent))
            if len(agent) and not agent.fallback.map(_true).any() and agent.valid_decision.map(_true).all():
                fit = estimate_beta(agent)
                if not full_game:
                    fit.update(usable=False, fit_flag=fit["fit_flag"]+";partial_game")
                if int((agent.order > 0).sum()) < 5:
                    fit.update(usable=False, fit_flag=fit["fit_flag"]+";too_few_positive_orders")
            row = dict(group_id=gid, block=block, condition=condition, role=role, **fit)
            own_fits.append(row)
            fit_rows.append(row)
        usable = sum(bool(f["usable"]) and _finite(f["beta"]) for f in own_fits)
        group_rows.append(dict(group_id=gid, block=block, condition=condition,
                               observed_weeks=len(weeks), full_game=full_game, full_continuation=full_tail,
                               valid_submitted_decisions=int(valid), missing_decisions=int(missing), fallback_count=int(fallback),
                               observed_game_cost=game_cost, continuation_cost=tail_cost if tail_weeks else np.nan,
                               total_observed_cost=game_cost+tail_cost,
                               total_scored_cost=game_cost+tail_cost if full_game and full_tail else np.nan,
                               clean_model_trajectory=full_game and full_tail and not missing and not fallback,
                               usable_role_betas=usable,
                               group_beta=float(np.mean([f["beta"] for f in own_fits])) if usable == len(ROLES) else np.nan))
    return pd.DataFrame(group_rows), pd.DataFrame(fit_rows)


def _verify_derived(directory: Path, groups, fits) -> dict[str, bool]:
    checked = {}
    for filename, actual, keys, numeric, flags in (
        ("group_outcomes.csv", groups, ["group_id"], ["observed_game_cost", "continuation_cost", "total_scored_cost", "group_beta", "usable_role_betas"], ["full_game", "full_continuation", "clean_model_trajectory"]),
        ("beta_fits.csv", fits, ["group_id", "role"], ["beta", "n"], ["usable"]),
    ):
        saved = _csv(directory/filename)
        if saved.empty:
            checked[filename] = False
            continue
        if saved.duplicated(keys).any() or len(saved) != len(actual):
            raise AnalysisError(f"Saved derived table does not match reconstructed observations: {filename}")
        left, right = saved.set_index(keys).sort_index(), actual.set_index(keys).sort_index()
        if not left.index.equals(right.index):
            raise AnalysisError(f"Saved derived table has different chain/role identities: {filename}")
        for name in numeric:
            if name not in left or name not in right or not np.allclose(pd.to_numeric(left[name], errors="coerce"), pd.to_numeric(right[name], errors="coerce"), rtol=1e-5, atol=1e-7, equal_nan=True):
                raise AnalysisError(f"Saved derived {name} differs from raw reconstruction: {filename}")
        for name in flags:
            if name not in left or not np.array_equal(left[name].map(_true), right[name].map(_true)):
                raise AnalysisError(f"Saved derived {name} differs from raw reconstruction: {filename}")
        checked[filename] = True
    return checked


def _token_use(records, groups, selection):
    rows = []
    for condition in ("short", "adequate"):
        gids = set(groups.loc[groups.condition == condition, "group_id"]) if not groups.empty else set()
        decisions = [r for r in records if r["identity"].get("stage") == "decision" and r["identity"].get("group") in gids]
        measured = [r for r in decisions if r.get("usage_observed") and not r.get("synthetic")
                    and _finite((r.get("usage") or {}).get("output_tokens"))]
        outputs = [r["usage"]["output_tokens"] for r in measured]
        reasoning = [r["usage"]["reasoning_tokens"] for r in measured if _finite(r["usage"].get("reasoning_tokens"))]
        cap = selection[condition+"_tokens"]
        rows.append(dict(condition=condition, independent_chains=len(gids), decision_calls=len(decisions),
                         valid_model_decision_calls=sum(decide(r).valid and not r.get("synthetic") for r in decisions),
                         synthetic_decision_calls=sum(bool(r.get("synthetic")) for r in decisions),
                         measured_usage_calls=len(measured), token_limit=cap,
                         median_output_tokens=float(np.median(outputs)) if outputs else np.nan,
                         mean_output_tokens=float(np.mean(outputs)) if outputs else np.nan,
                         median_reasoning_tokens=float(np.median(reasoning)) if reasoning else np.nan,
                         mean_reasoning_tokens=float(np.mean(reasoning)) if reasoning else np.nan,
                         near_cap_fraction=float(np.mean(np.asarray(outputs) >= .9*cap)) if outputs else np.nan,
                         cap_binding_fraction=float(np.mean(np.asarray(outputs) >= cap)) if outputs else np.nan,
                         requested_models="; ".join(sorted({r["requested_model"] for r in decisions})),
                         returned_models="; ".join(sorted({r.get("returned_model", "") for r in measured})),
                         effort="; ".join(sorted({r["requested_effort"] for r in decisions})),
                         observation_unit="Repeated model decisions within interacting four-role chains; calls are not students"))
    return pd.DataFrame(rows)


def analyze_run(directory: str | Path) -> dict[str, Any]:
    """Reconstruct a saved run and return tables plus JSON-safe analysis context.

    No output files are written. Export the returned DataFrames to a separately
    identified derived report. Source/prompt/raw-response or physical conflicts
    raise AnalysisError rather than silently combining incompatible evidence.
    """
    directory = Path(directory).resolve()
    manifest = _json(directory/"manifest.json", {})
    source_hashes = _source_provenance(directory, manifest)
    try:
        config = ReasoningConfig(**manifest["config"])
        config.validate()
    except (KeyError, TypeError, ValueError) as exc:
        raise AnalysisError("Saved configuration is not a valid fixed-high student study.") from exc
    selection = _json(directory/"selection.json")
    if not isinstance(selection, dict) or type(selection.get("groups_per_condition")) is not int:
        raise AnalysisError("A frozen pre-outcome selection.json is required; requested maximum sample is not the plan.")
    planned_pairs = selection["groups_per_condition"]
    if not 0 <= planned_pairs <= config.groups_per_condition:
        raise AnalysisError("Frozen pair count exceeds the configured maximum.")
    records, latest = _records(directory, config)
    rounds, tail = _csv(directory/"rounds.csv"), _csv(directory/"continuation.csv")
    groups, fits = _game_outcomes(rounds, tail, config, selection, latest)
    derived_verified = _verify_derived(directory, groups, fits)
    progress = _json(directory/"progress.json", {})
    calibration_reuse = _json(directory/"calibration_reuse.json", {})
    calibration_source = Path(calibration_reuse["parent"]) if calibration_reuse else directory/"calibration_checkpoint"
    if not calibration_source.exists():
        calibration_source = directory
    calibration_error, calibration_records, calibration_screen = "", [], {}
    try:
        calibration_records, calibration_screen, calibration_provenance = load_calibration(calibration_source, config)
    except StudyStopped as exc:
        calibration_error = str(exc)
        calibration_provenance = {}
    passed = bool(calibration_screen.get("manipulation_screen_passed"))
    if calibration_screen and bool(selection.get("calibration_passed")) != passed:
        raise AnalysisError("Frozen cap plan disagrees with the independently recomputed calibration gate.")
    expected_caps = ({"short": calibration_screen["short_tokens"], "adequate": calibration_screen["adequate_tokens"]}
                     if passed else {"short": max(config.candidate_caps), "adequate": config.reference_tokens})
    if any(selection.get(c+"_tokens") != cap for c, cap in expected_caps.items()):
        raise AnalysisError("Frozen allowances differ from the prospective calibration/diagnostic rule.")
    expected_keys = {(b, c) for b in range(planned_pairs) for c in ("short", "adequate")}
    observed_keys = set(zip(groups.block, groups.condition)) if not groups.empty else set()
    complete = (planned_pairs > 0 and observed_keys == expected_keys and groups.full_game.map(_true).all()
                and groups.full_continuation.map(_true).all() and progress.get("phase") == "complete")
    expected_decisions = 2*planned_pairs*len(ROLES)*(config.weeks-config.warmup_weeks)
    clean = bool(complete and int(groups.valid_submitted_decisions.sum()) == expected_decisions
                 and int(groups.fallback_count.sum()) == 0 and int(groups.missing_decisions.sum()) == 0)
    rules = [r for r in latest.values() if r["identity"].get("stage") == "rules"]
    expected_rules = {(b, c, r) for b in range(planned_pairs) for c in ("short", "adequate") for r in ROLES}
    actual_rules = {(r["identity"].get("block"), r["identity"].get("condition"), r["identity"].get("role")) for r in rules}
    rules_ok = (actual_rules == expected_rules and bool(expected_rules) and all(
        r["limit"] == config.onboarding_tokens and r["messages"] == rules_messages(r["identity"]["role"])
        and rules_result(r)["passed"] for r in rules))
    replaced = any(_true(manifest.get(name, False)) for name in ("replaced", "replacement", "outcome_based_replacement"))
    if "replaced" in rounds:
        replaced = replaced or rounds.replaced.map(_true).any()
    gates = dict(api_observations=config.mode == "api", calibration_passed=passed,
                 complete_planned_sample=complete, no_replacements=not replaced,
                 no_fallbacks_or_missing=clean, model_effort_caps_consistent=True, rules_checks_passed=rules_ok)
    tables = inference_results(groups, planned_pairs, gates)
    tokens = _token_use(records, groups, selection)
    medians = tokens.set_index("condition").median_output_tokens
    usage_contrast = (1-float(medians["short"])/float(medians["adequate"])) if _finite(medians["short"]) and _finite(medians["adequate"]) and medians["adequate"] > 0 else np.nan
    inputs = [directory/n for n in ("manifest.json", "selection.json", "progress.json", "rounds.csv", "continuation.csv", "group_outcomes.csv", "beta_fits.csv", "calibration_recommendation.json", "calibration_reuse.json") if (directory/n).exists()]
    inputs += sorted((directory/"requests").glob("*.json"))
    input_hashes = {str(p.relative_to(directory)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs}
    summary = _safe(dict(protocol=PROTOCOL, analysis_version="student-hypotheses-v1", mode=config.mode,
        requested_model=config.model, effort=config.effort, source_hashes=source_hashes,
        analysis_source_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(), input_sha256=input_hashes,
        hash_definition="Input and analysis hashes are SHA-256 of file bytes; scientific hashes retain the manifest's canonical JSON-string digest.",
        planned_pairs=planned_pairs, requested_max_pairs=config.groups_per_condition,
        independent_chains=len(groups), completed_planned_sample=complete, expected_model_decisions=expected_decisions,
        observed_valid_decisions=int(groups.valid_submitted_decisions.sum()) if not groups.empty else 0,
        fallback_count=int(groups.fallback_count.sum()) if not groups.empty else 0,
        missing_decisions=int(groups.missing_decisions.sum()) if not groups.empty else 0,
        selected_caps=expected_caps, calibration_source=str(calibration_source),
        calibration_screen_passed=passed, calibration_gate_error=calibration_error,
        calibration_screen_observations=len(calibration_records), calibration_provenance=calibration_provenance,
        empirical_main_median_output_contrast=usage_contrast, empirical_contrast_is_descriptive_only=True,
        usable_role_betas=int(fits.usable.map(_true).sum()) if not fits.empty else 0, total_role_beta_fits=len(fits),
        derived_tables_verified=derived_verified, gates=gates, minimum_pairs_software_floor=MINIMUM_PAIRS,
        minimum_pairs_is_power_calculation=False, planned_holm_family_size=2,
        test_method="Legacy two-sided exact sign flips through16pairs;50,000 seeded Monte Carlo signs above16;Holm family2",
        confidence_intervals="Not prespecified by legacy hypothesis procedure; withheld rather than added retrospectively.",
        observation_unit="Independent separately initialized four-role chains, paired by block; calls and roles are dependent repeated observations.",
        claims_scope="Configured LLM simulation only; no real-student validation, human-time conversion, or equivalence inference.",
        new_api_calls=0, additional_spending_usd=0))
    return dict(**tables, token_use=tokens, groups=groups, beta_fits=fits, summary=summary,
                calibration_screen=calibration_screen, provenance=dict(input_sha256=input_hashes, source_hashes=source_hashes))
