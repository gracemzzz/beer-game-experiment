"""Experiment 14: fictional student time-pressure framing, unlimited model time.

The unchanged v3 physical engine calculates states, never decisions. Each game
week requests four literal orders; each probe page requests four scalar orders.
All arms commit once. Every applied answer is an actual accepted literal actor
choice. No real deadline, expiry, random action, default or fallback exists.
Wall latency is observational and includes transport/scheduling/output.
"""
from __future__ import annotations

from datetime import datetime, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import time

from . import manual_weekly_v3 as physics


SCHEMA = "exp14-single-chain-fictional-pressure-v1"
MODEL = "gpt-6-astra"
EFFORT = "xhigh"
ROOT = Path(__file__).resolve().parents[2]
TIMING = ("Observational display-open to complete-payload-reception wall latency, including "
          "tool transport, scheduling and output; not verified thinking time or tokens. "
          "No elapsed-time admission restriction exists in any arm.")
FRAMING = ("The stated seconds describe a fictional student's situation only. "
           "Model response time is unlimited; these seconds are not a physical deadline.")


def clone(value):
    return json.loads(json.dumps(value, allow_nan=False))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def source_hashes():
    paths = dict(controller=Path(__file__), transport=ROOT / "scripts/run_exp14_framing.py",
                 physics=Path(physics.__file__))
    return {key: hashlib.sha256(path.read_bytes()).hexdigest() for key, path in paths.items()}


def verify_sources(case):
    actual = source_hashes()
    if case.get("source_hashes") != actual:
        raise ValueError("CASE source_hashes do not match controller, transport and frozen physics")
    return actual


def clock_point():
    return dict(monotonic_ns=time.monotonic_ns(), utc=datetime.now(timezone.utc).isoformat())


def _json(text):
    def pairs(items):
        result = {}
        for key, value in items:
            if key in result:
                raise ValueError("Duplicate JSON key")
            result[key] = value
        return result
    def invalid(value):
        raise ValueError("Nonfinite JSON value")
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid)


def _order(value):
    if type(value) is not int or not 0 <= value <= physics.ORDER_GUARD:
        raise ValueError("Orders must be nonnegative literal integers within the technical validity guard")


class FramingCase:
    """Mutable private state. Public results never contain unobserved demands.

    CASE requires case_id, block_id, arm, stage, prompt_version, seed, weeks,
    fictional_student_seconds, explicitly null model_runtime_limit_seconds and
    deadline_seconds, and source_hashes. Actual phase limits must also be null.
    probes uses probe_id (id is accepted),
    in groups of four. comprehension uses question_id and options/choices dict.
    Caller supplies trusted clock points; CLI users cannot provide timestamps.
    """

    def __init__(self, case, *, clock=None):
        self.case = clone(case)
        if case.get("schema_version") != SCHEMA:
            raise ValueError("CASE must bind the fictional-pressure schema")
        expected_seconds = 120 if case.get("arm") == "A" else 8
        if type(case.get("fictional_student_seconds")) is not int or case["fictional_student_seconds"] != expected_seconds:
            raise ValueError("Fictional student seconds must be A=120 and B/C=8")
        if "model_runtime_limit_seconds" not in case or case["model_runtime_limit_seconds"] is not None:
            raise ValueError("Actual model runtime must be explicitly unlimited")
        if "deadline_seconds" not in case or case["deadline_seconds"] is not None:
            raise ValueError("Actual deadline_seconds must be explicitly null")
        overrides = case.get("phase_deadline_seconds", {})
        if not isinstance(overrides, dict) or any(value is not None for value in overrides.values()):
            raise ValueError("Every phase has unlimited actual model response time")
        for key in ("case_id", "block_id", "stage", "prompt_version"):
            if not isinstance(case.get(key), str) or not case[key]:
                raise ValueError("Missing nonempty CASE field: " + key)
        if case.get("arm") not in "ABC" or len(case["arm"]) != 1:
            raise ValueError("Arm must be A, B or C")
        if type(case.get("seed")) is not int or case["seed"] < 0:
            raise ValueError("Seed must be a nonnegative integer")
        if type(case.get("weeks")) is not int or not 1 <= case["weeks"] <= 24:
            raise ValueError("Weeks must be 1 through 24 (development or main protocol)")
        limit = case.get("deadline_seconds")
        if limit is not None and (isinstance(limit, bool) or not isinstance(limit, (int, float))
                                  or not math.isfinite(limit) or limit <= 0):
            raise ValueError("Deadline must be positive finite seconds or null for calibration")
        overrides = case.get("phase_deadline_seconds", {})
        if not isinstance(overrides, dict) or not set(overrides) <= {"game", "probes"}:
            raise ValueError("phase_deadline_seconds may override game and probes only")
        for value in overrides.values():
            if value is not None and (isinstance(value, bool) or not isinstance(value, (int, float))
                                      or not math.isfinite(value) or value <= 0):
                raise ValueError("Phase deadline must be positive finite seconds or null")
        for key, expected in (("requested_model", MODEL), ("requested_effort", EFFORT)):
            if case.get(key, expected) != expected:
                raise ValueError("Experiment 14 keeps " + key + " fixed")
        self.hashes = verify_sources(case)
        self.case_hash = digest(self.case)
        self.game = physics._PhysicalGame()
        self.rng = random.Random(case["seed"])
        self.profiles = clone(case.get("profiles", list(physics.PROFILES)))
        if not isinstance(self.profiles, list) or len(self.profiles) != 4:
            raise ValueError("Exactly four profiles are required")
        ids = list(range(4))
        random.Random(case["seed"] + 7331).shuffle(ids)
        self.profile_ids = clone(case.get("profile_ids", ids))
        if sorted(self.profile_ids) != list(range(4)):
            raise ValueError("profile_ids must permute 0, 1, 2, 3")
        self.probes = clone(case.get("probes", []))
        if not isinstance(self.probes, list) or len(self.probes) % 4:
            raise ValueError("Probes must be a list in complete pages of four")
        seen = set()
        for probe in self.probes:
            if not isinstance(probe, dict):
                raise ValueError("Probe must be an object")
            ident = probe.get("probe_id", probe.get("id"))
            if not isinstance(ident, str) or not ident or ident in seen:
                raise ValueError("Each probe requires a unique probe_id")
            probe["probe_id"] = ident
            probe.pop("id", None)
            seen.add(ident)
        self.questions = clone(case.get("comprehension", []))
        seen = set()
        for question in self.questions:
            ident = question.get("question_id", question.get("id"))
            options = question.get("options", question.get("choices"))
            if not isinstance(ident, str) or not ident or ident in seen or not isinstance(options, dict) or not options:
                raise ValueError("Each comprehension question needs a unique question_id and options")
            if not all(isinstance(key, str) and len(key) == 1 and key.isalpha() for key in options):
                raise ValueError("Comprehension option keys must be choice letters")
            question["question_id"], question["options"] = ident, options
            question.pop("id", None)
            question.pop("choices", None)
            seen.add(ident)
        self.events = []
        self.decisions = []
        self.weeks = []
        self.probe_answers = {}
        self.comprehension_answers = None
        self.pending = None
        self.terminal_reason = None
        self.terminal_at = None
        self._event("initialized", clock or clock_point(), case_sha256=self.case_hash)

    def _event(self, kind, clock, **fields):
        event = dict(index=len(self.events), kind=kind, clock=clone(clock),
                     previous_event_sha256=self.events[-1]["event_sha256"] if self.events else None,
                     **clone(fields))
        event["event_sha256"] = digest(event)
        self.events.append(event)

    def phase(self):
        if self.terminal_reason:
            return "stopped"
        if len(self.weeks) < self.case["weeks"]:
            return "game"
        if len(self.probe_answers) < len(self.probes):
            return "probes"
        if self.questions and self.comprehension_answers is None:
            return "comprehension"
        return "complete"

    def _stop(self, reason, clock):
        if self.terminal_reason is None:
            self.terminal_reason, self.terminal_at = reason, clone(clock)
            self._event("stopped", clock, reason=reason,
                        decision_id=self.pending["display"]["decision_id"] if self.pending else None)

    def _body(self):
        phase = self.phase()
        body = dict(case_id=self.case["case_id"], phase=phase, role_order=list(physics.ROLES),
                    profiles=self.profiles, profile_ids=self.profile_ids,
                    fictional_student_seconds=self.case["fictional_student_seconds"],
                    model_runtime_limit_seconds=None, framing_interpretation=FRAMING)
        if phase == "game":
            demand = self.rng.randrange(9)
            rows = self.game.observe(demand)
            body.update(week=len(self.weeks) + 1, roles=rows, customer_demand=demand,
                        recent_history=[dict(week=w["week"], orders=w["orders"],
                                             customer_demand=w["customer_demand"])
                                        for w in self.weeks[-4:]],
                        response_format="JSON list of four literal integer orders in role_order")
        elif phase == "probes":
            offset = len(self.probe_answers)
            body.update(page_index=offset // 4 + 1, pages=len(self.probes) // 4,
                        probes=self.probes[offset:offset + 4],
                        response_format="JSON object mapping exactly these four probe_id values to integer orders")
        elif phase == "comprehension":
            body.update(questions=self.questions,
                        response_format="JSON object mapping each question_id to one choice letter")
        return clone(body)

    def show(self, clock=None):
        clock = clock or clock_point()
        if self.phase() in ("stopped", "complete"):
            return self.status()
        if self.pending is None:
            body = self._body()
            ident = digest([self.case_hash, len(self.decisions), body["phase"], digest(body)])[:24]
            display = dict(body, decision_id=ident, deadline_clock=dict(
                opened_monotonic_ns=clock["monotonic_ns"], opened_utc=clock["utc"],
                deadline_seconds=None, deadline_monotonic_ns=None, deadline_utc=None,
                admissible_boundary="No actual response deadline; elapsed wall time never limits admission",
                measurement=TIMING))
            display["display_sha256"] = digest(display)
            self.pending = dict(display=display)
            self._event("display_opened", clock, display=display)
        return clone(self.pending["display"])

    def _validate(self, choices):
        display = self.pending["display"]
        if display["phase"] == "game":
            if not isinstance(choices, list) or len(choices) != 4:
                raise ValueError("Supply exactly four literal integer orders")
            for value in choices:
                _order(value)
        else:
            is_probe = display["phase"] == "probes"
            rows, key = (display["probes"], "probe_id") if is_probe else (display["questions"], "question_id")
            if not isinstance(choices, dict) or set(choices) != {row[key] for row in rows}:
                raise ValueError("Supply every current requested ID exactly once")
            for row in rows:
                value = choices[row[key]]
                if is_probe:
                    _order(value)
                elif not isinstance(value, str) or value not in row["options"]:
                    raise ValueError("Comprehension answer must be one displayed choice letter")

    def submit(self, raw_text, decision_id, *, received=None):
        received = received or clock_point()
        reason = None
        choices = None
        if self.terminal_reason:
            reason = "case_stopped:" + self.terminal_reason
        elif self.pending is None:
            reason = "no_open_decision"
        elif decision_id != self.pending["display"]["decision_id"]:
            reason = "stale_or_duplicate_decision_id"
        else:
            try:
                choices = _json(raw_text)
                self._validate(choices)
            except (ValueError, TypeError) as error:
                reason = "invalid_payload:" + str(error)
        elapsed = None
        if self.pending:
            elapsed = (received["monotonic_ns"] - self.pending["display"]["deadline_clock"]["opened_monotonic_ns"]) / 1e9
        event_fields = dict(decision_id=decision_id, literal_input_text=raw_text,
                            accepted=reason is None, rejection_reason=reason,
                            elapsed_seconds=elapsed)
        if reason is not None:
            self._event("submission_rejected", received, **event_fields)
            if reason.startswith("invalid_payload:"):
                self._stop("invalid_payload", received)
            return dict(accepted=False, reason=reason, **self.status())
        display = self.pending["display"]
        self._event("submission_accepted", received, choices=choices,
                    display_sha256=display["display_sha256"], **event_fields)
        decision = dict(decision_id=decision_id, phase=display["phase"], choices=clone(choices),
                        display_sha256=display["display_sha256"], received=clone(received),
                        deadline_clock=clone(display["deadline_clock"]), elapsed_seconds=elapsed)
        if display["phase"] == "game":
            self.game.commit(choices)
            self.weeks.append(dict(week=display["week"], customer_demand=display["customer_demand"],
                                   roles=clone(display["roles"]), orders=clone(choices),
                                   cost=sum(row["cost"] for row in display["roles"])))
        elif display["phase"] == "probes":
            self.probe_answers.update(choices)
        else:
            self.comprehension_answers = clone(choices)
        self.decisions.append(decision)
        self.pending = None
        return dict(accepted=True, decision_id=decision_id, **self.status())

    def status(self):
        phase = self.phase()
        return dict(case_id=self.case["case_id"], phase=phase, complete=phase == "complete",
                    stopped=phase == "stopped", terminal_reason=self.terminal_reason,
                    completed_weeks=len(self.weeks), planned_weeks=self.case["weeks"],
                    completed_probe_pages=len(self.probe_answers) // 4,
                    planned_probe_pages=len(self.probes) // 4,
                    comprehension_complete=self.comprehension_answers is not None,
                    open_decision_id=self.pending["display"]["decision_id"] if self.pending else None,
                    next_action="none" if phase in ("stopped", "complete") else "submit" if self.pending else "show")

    def export(self):
        missing = dict(weeks=list(range(len(self.weeks) + 1, self.case["weeks"] + 1)),
                       probe_ids=[p["probe_id"] for p in self.probes if p["probe_id"] not in self.probe_answers],
                       question_ids=[q["question_id"] for q in self.questions] if self.comprehension_answers is None else [])
        return clone(dict(schema_version=SCHEMA, **self.status(),
                          fictional_student_seconds=self.case["fictional_student_seconds"],
                          model_runtime_limit_seconds=None, framing_interpretation=FRAMING,
                          block_id=self.case["block_id"], arm=self.case["arm"], stage=self.case["stage"],
                          prompt_version=self.case["prompt_version"], case_sha256=self.case_hash,
                          source_hashes=self.hashes, independent_generation_clusters=1, chains=1,
                          requested_model=MODEL, requested_effort=EFFORT,
                          actual_model=self.case.get("actual_model", "UNVERIFIED"),
                          actual_effort=self.case.get("actual_effort", "UNVERIFIED"),
                          temperature="not exposed by local agent launcher",
                          reasoning_token_limit="not exposed by local agent launcher",
                          deadline_seconds=self.case["deadline_seconds"],
                          phase_deadline_seconds=self.case.get("phase_deadline_seconds", {}),
                          timing_interpretation=TIMING,
                          profile_ids=self.profile_ids, decisions=self.decisions, weeks=self.weeks,
                          probe_answers=self.probe_answers, comprehension_answers=self.comprehension_answers,
                          pending_display=self.pending["display"] if self.pending else None,
                          missing=missing, terminal_at=self.terminal_at, events=self.events,
                          completed_prefix_cost=sum(w["cost"] for w in self.weeks),
                          full_game_cost=sum(w["cost"] for w in self.weeks) if len(self.weeks) == self.case["weeks"] else None,
                          provenance_interpretation="Local execution receipts; external transcript required. Not tamper-proof."))


def audit_result(payload, case):
    """Replay accepted literal decisions, timing admission and every physical state."""
    replay = FramingCase(case, clock=payload["events"][0]["clock"])
    previous = None
    for index, event in enumerate(payload["events"]):
        saved = dict(event)
        claimed = saved.pop("event_sha256")
        if event["index"] != index or event["previous_event_sha256"] != previous or digest(saved) != claimed:
            raise ValueError("Event chain differs")
        previous = claimed
        if event["kind"] == "initialized":
            continue
        if event["kind"] == "display_opened":
            if replay.show(event["clock"]) != event["display"]:
                raise ValueError("Display replay differs")
        elif event["kind"] == "stopped":
            if replay.terminal_reason != event["reason"]:
                raise ValueError("Termination replay differs")
        elif event["kind"].startswith("submission_"):
            answer = replay.submit(event["literal_input_text"], event["decision_id"], received=event["clock"])
            if answer["accepted"] != event["accepted"]:
                raise ValueError("Admission replay differs")
        else:
            raise ValueError("Unknown event")
    rebuilt = replay.export()
    if rebuilt != payload:
        raise ValueError("Result replay differs")
    return dict(valid=True, **replay.status(), full_game_cost=rebuilt["full_game_cost"])
