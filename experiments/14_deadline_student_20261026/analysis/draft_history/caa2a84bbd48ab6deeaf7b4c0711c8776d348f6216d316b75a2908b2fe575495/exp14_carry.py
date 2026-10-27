"""Experiment 14 carry-forward amendment; separate from frozen strict stopping.

The unchanged v3 physical engine calculates states, never decisions. Each game
week requests four literal orders; each probe page requests four scalar orders.
On true game expiry the previous APPLIED packet continues physical play, with
all actor choices missing. The initial packet is [4, 4, 4, 4]. Each expired
probe receives that role's last applied GAME order, labelled carry_forward;
actor probe responses remain missing. No expiry/submit/status opens a new clock.
Elapsed time includes transport/scheduling/output and is not thinking-token time.
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone
import hashlib
import json
import math
from pathlib import Path
import random
import time

from . import manual_weekly_v3 as physics


SCHEMA = "exp14-single-chain-wall-deadline-carry-v2"
POLICY = "previous_applied_orders"
PROBE_POLICY = "last_applied_game_order_by_role"
INITIAL_ORDERS = [4, 4, 4, 4]
MODEL = "gpt-6-astra"
EFFORT = "xhigh"
ROOT = Path(__file__).resolve().parents[2]
TIMING = ("Local display-open to complete-payload-reception elapsed time, including "
          "tool transport, scheduling and output; not verified thinking time or tokens. "
          "Expiry is persisted on next access; late admission is always forbidden.")


def clone(value):
    return json.loads(json.dumps(value, allow_nan=False))


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"),
                                     ensure_ascii=False, allow_nan=False).encode()).hexdigest()


def source_hashes():
    paths = dict(controller=Path(__file__), transport=ROOT / "scripts/run_exp14_carry.py",
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
    def finite_float(value):
        number = float(value)
        if not math.isfinite(number):
            raise ValueError("Nonfinite JSON number")
        return number
    return json.loads(text, object_pairs_hook=pairs, parse_constant=invalid, parse_float=finite_float)


def _order(value):
    if type(value) is not int or not 0 <= value <= physics.ORDER_GUARD:
        raise ValueError("Orders must be nonnegative literal integers within the technical validity guard")


class CarryCase:
    """Mutable private state. Public results never contain unobserved demands.

    CASE requires case_id, block_id, arm, stage, prompt_version, seed, weeks,
    deadline_seconds and source_hashes. Optional phase_deadline_seconds maps game
    and/or probes to overriding positive seconds or null. probes uses probe_id (id is accepted),
    in groups of four. comprehension uses question_id and options/choices dict.
    Caller supplies trusted clock points; CLI users cannot provide timestamps.
    """

    def __init__(self, case, *, clock=None):
        self.case = clone(case)
        if (case.get("schema_version") != SCHEMA or case.get("timeout_policy") != POLICY
                or case.get("probe_timeout_policy") != PROBE_POLICY):
            raise ValueError("CASE must explicitly bind the carry schema, timeout_policy and probe_timeout_policy")
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
            if probe.get("role") not in physics.ROLES:
                raise ValueError("Each probe requires one valid displayed role")
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
        self.opportunities = []
        self.applied_actions = []
        self.weeks = []
        self.probe_answers = {}
        self.actor_probe_answers = {}
        self.probe_answer_sources = {}
        self.probe_actor_missing_mask = {}
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

    def check_expiry(self, clock=None):
        """Resolve at most one open opportunity; never open another clock."""
        clock = clock or clock_point()
        if self.pending and not self.terminal_reason:
            opened = self.pending["display"]["deadline_clock"]
            now = clock["monotonic_ns"]
            if now < opened["opened_monotonic_ns"]:
                self._stop("clock_discontinuity", clock)
            elif opened["deadline_monotonic_ns"] is not None and now > opened["deadline_monotonic_ns"]:
                display = self.pending["display"]
                source = "carry_forward"
                orders = (clone(self.applied_actions[-1]["orders"] if self.applied_actions else INITIAL_ORDERS)
                          if display["phase"] == "game" else None)
                self._event("deadline_expired", clock, decision_id=display["decision_id"],
                            display_sha256=display["display_sha256"], phase=display["phase"],
                            action_source=source, applied_orders=orders,
                            applied_choices=({p["probe_id"]: display["timeout_fallback"]["orders_by_role"][p["role"]]
                                              for p in display["probes"]}
                                             if display["phase"] == "probes" else orders),
                            missing_mask=[True] * 4, deadline_clock=opened)
                self._resolve(display, None, source, clock, orders=orders)
                return True
        return bool(self.terminal_reason)

    def _body(self):
        phase = self.phase()
        body = dict(case_id=self.case["case_id"], phase=phase, role_order=list(physics.ROLES),
                    profiles=self.profiles, profile_ids=self.profile_ids)
        if phase == "game":
            demand = self.rng.randrange(9)
            rows = self.game.observe(demand)
            body.update(week=len(self.weeks) + 1, roles=rows, customer_demand=demand,
                        recent_history=[dict(week=w["week"], orders=w["orders"],
                                             action_source=w["action_source"],
                                             actor_missing_mask=w["actor_missing_mask"],
                                             customer_demand=w["customer_demand"])
                                        for w in self.weeks[-4:]],
                        response_format="JSON list of four literal integer orders in role_order")
        elif phase == "probes":
            offset = len(self.probe_answers)
            last_orders = self.applied_actions[-1]["orders"] if self.applied_actions else INITIAL_ORDERS
            body.update(page_index=offset // 4 + 1, pages=len(self.probes) // 4,
                        probes=self.probes[offset:offset + 4],
                        timeout_fallback=dict(policy=PROBE_POLICY,
                                              orders_by_role=dict(zip(physics.ROLES, last_orders)),
                                              source_game_decision_id=(self.applied_actions[-1]["decision_id"]
                                                                       if self.applied_actions else None),
                                              initial_orders_used=not self.applied_actions),
                        response_format="JSON object mapping exactly these four probe_id values to integer orders")
        elif phase == "comprehension":
            body.update(questions=self.questions,
                        response_format="JSON object mapping each question_id to one choice letter")
        return clone(body)

    def show(self, clock=None):
        clock = clock or clock_point()
        self.check_expiry(clock)
        if self.phase() in ("stopped", "complete"):
            return self.status()
        if self.pending is None:
            body = self._body()
            limit = None if body["phase"] == "comprehension" else self.case.get(
                "phase_deadline_seconds", {}).get(body["phase"], self.case["deadline_seconds"])
            duration_ns = None if limit is None else round(limit * 1_000_000_000)
            deadline_ns = None if duration_ns is None else clock["monotonic_ns"] + duration_ns
            deadline_utc = None if limit is None else (
                datetime.fromisoformat(clock["utc"]) + timedelta(seconds=limit)).isoformat()
            ident = digest([self.case_hash, len(self.opportunities), body["phase"], digest(body)])[:24]
            display = dict(body, decision_id=ident, deadline_clock=dict(
                opened_monotonic_ns=clock["monotonic_ns"], opened_utc=clock["utc"],
                deadline_seconds=limit, deadline_monotonic_ns=deadline_ns, deadline_utc=deadline_utc,
                admissible_boundary="complete payload received at or before deadline",
                measurement=TIMING))
            display["display_sha256"] = digest(display)
            self.pending = dict(display=display)
            self._event("display_opened", clock, display=display)
        return clone(self.pending["display"])

    def _validate(self, choices, display):
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

    def _resolve(self, display, choices, source, clock, *, orders=None):
        """Keep observed actor decisions distinct from all physically applied actions."""
        missing = choices is None
        mask = [missing] * (len(display["questions"]) if display["phase"] == "comprehension" else 4)
        elapsed = (clock["monotonic_ns"] - display["deadline_clock"]["opened_monotonic_ns"]) / 1e9
        opportunity = dict(decision_id=display["decision_id"], phase=display["phase"],
                           choices=clone(choices), action_source=source, actor_missing_mask=mask,
                           display_sha256=display["display_sha256"], resolved_at=clone(clock),
                           deadline_clock=clone(display["deadline_clock"]), elapsed_seconds=elapsed)
        if not missing:
            self.decisions.append(dict(decision_id=display["decision_id"], phase=display["phase"],
                                       choices=clone(choices), display_sha256=display["display_sha256"],
                                       received=clone(clock), deadline_clock=clone(display["deadline_clock"]),
                                       elapsed_seconds=elapsed))
        if display["phase"] == "game":
            applied = clone(choices if source == "actor" else orders)
            self.game.commit(applied)
            action = dict(decision_id=display["decision_id"], week=display["week"], orders=applied,
                          action_source=source, actor_orders=[None] * 4 if missing else clone(choices),
                          actor_missing_mask=mask, applied_at=clone(clock),
                          deadline_clock=clone(display["deadline_clock"]),
                          carried_from_decision_id=(self.applied_actions[-1]["decision_id"]
                                                    if missing and self.applied_actions else None),
                          initial_orders_used=missing and not self.applied_actions)
            self.applied_actions.append(action)
            self.weeks.append(dict(**clone(action), customer_demand=display["customer_demand"],
                                   roles=clone(display["roles"]),
                                   cost=sum(row["cost"] for row in display["roles"])))
            opportunity["week"] = display["week"]
            opportunity["applied_orders"] = applied
            opportunity["applied_choices"] = applied
        elif display["phase"] == "probes":
            answers = ({p["probe_id"]: display["timeout_fallback"]["orders_by_role"][p["role"]]
                        for p in display["probes"]} if missing else choices)
            self.probe_answers.update(answers)
            if not missing:
                self.actor_probe_answers.update(choices)
            self.probe_answer_sources.update({key: source for key in answers})
            self.probe_actor_missing_mask.update({key: missing for key in answers})
            opportunity.update(page_index=display["page_index"], probe_ids=list(answers),
                               answers=clone(answers), applied_choices=clone(answers),
                               timeout_fallback=clone(display["timeout_fallback"]))
        else:
            if missing:
                raise ValueError("Comprehension can never receive fallback answers")
            self.comprehension_answers = clone(choices)
        self.opportunities.append(opportunity)
        self.pending = None

    def submit(self, raw_text, decision_id, *, received=None):
        received = received or clock_point()
        # Diagnose against the submitted ID's original display, never the next display.
        display = next((event["display"] for event in reversed(self.events)
                        if event["kind"] == "display_opened"
                        and event["display"]["decision_id"] == decision_id), None)
        elapsed = lateness = None
        receipt_status = "unknown_decision"
        if display:
            opened = display["deadline_clock"]
            elapsed = (received["monotonic_ns"] - opened["opened_monotonic_ns"]) / 1e9
            due = opened["deadline_monotonic_ns"]
            lateness = None if due is None else max(0, received["monotonic_ns"] - due) / 1e9
            receipt_status = ("clock_before_open" if elapsed < 0 else "late" if lateness else "on_time")
        choices = None
        payload_error = None
        try:
            choices = _json(raw_text)
            if display:
                self._validate(choices, display)
        except (ValueError, TypeError) as error:
            payload_error = "invalid_payload:" + str(error)
        payload_status = payload_error or ("valid" if display else "unknown_decision")
        before = len(self.opportunities)
        self.check_expiry(received)
        expired = self.opportunities[-1] if len(self.opportunities) > before else None
        if self.terminal_reason:
            reason = "case_stopped:" + self.terminal_reason
        elif not isinstance(decision_id, str) or not decision_id:
            reason = "missing_decision_id"
        elif receipt_status == "late" and any(o["decision_id"] == decision_id and
                                               o["action_source"] != "actor" for o in self.opportunities):
            reason = "deadline_expired"
        elif self.pending is None:
            reason = "no_open_decision"
        elif decision_id != self.pending["display"]["decision_id"]:
            reason = "stale_or_duplicate_decision_id"
        else:
            reason = payload_error
        event_fields = dict(decision_id=decision_id, literal_input_text=raw_text,
                            accepted=reason is None, rejection_reason=reason,
                            elapsed_seconds=elapsed, lateness_seconds=lateness,
                            receipt_status=receipt_status, payload_status=payload_status,
                            attempted_choices=clone(choices) if not payload_error else None)
        if reason is not None:
            self._event("submission_rejected", received, **event_fields)
            handled = expired is not None and expired["decision_id"] == decision_id
            return dict(**self.status(), accepted=False, reason=reason, receipt_status=receipt_status,
                        payload_status=payload_status, continue_allowed=handled,
                        transition_kind=self._transition_kind(expired) if handled else None)
        self._event("submission_accepted", received, choices=choices,
                    display_sha256=display["display_sha256"], **event_fields)
        self._resolve(display, choices, "actor", received)
        return dict(accepted=True, decision_id=decision_id, **self.status())

    @staticmethod
    def _transition_kind(opportunity):
        return "game_carry_forward" if opportunity["phase"] == "game" else "probe_carry_forward"

    def status(self, clock=None):
        # Internal/export calls are pure; an explicit external clock can process expiry.
        before = len(self.opportunities)
        if clock is not None:
            self.check_expiry(clock)
        expired = self.opportunities[-1] if len(self.opportunities) > before else None
        phase = self.phase()
        probes_complete = (len(self.probe_answers) == len(self.probes)
                           and all(value is not None for value in self.probe_answers.values()))
        actor_probes_complete = len(self.actor_probe_answers) == len(self.probes)
        result = dict(case_id=self.case["case_id"], phase=phase, complete=phase == "complete",
                    protocol_complete=phase == "complete", game_complete=len(self.weeks) == self.case["weeks"],
                    probes_complete=probes_complete,
                    actor_probes_complete=actor_probes_complete,
                    all_actor_responses_complete=(phase == "complete" and actor_probes_complete
                                                 and all(w["action_source"] == "actor" for w in self.weeks)),
                    stopped=phase == "stopped", terminal_reason=self.terminal_reason,
                    completed_weeks=len(self.weeks), planned_weeks=self.case["weeks"],
                    actor_completed_weeks=sum(w["action_source"] == "actor" for w in self.weeks),
                    fallback_weeks=sum(w["action_source"] == "carry_forward" for w in self.weeks),
                    processed_probe_pages=len(self.probe_answers) // 4,
                    completed_probe_pages=sum(o["phase"] == "probes" and o["action_source"] == "actor"
                                              for o in self.opportunities),
                    planned_probe_pages=len(self.probes) // 4,
                    comprehension_complete=not self.questions or self.comprehension_answers is not None,
                    open_decision_id=self.pending["display"]["decision_id"] if self.pending else None,
                    next_action="none" if phase in ("stopped", "complete") else "submit" if self.pending else "show")
        if clock is not None:
            result.update(continue_allowed=expired is not None,
                          transition_kind=self._transition_kind(expired) if expired else None)
        return result

    def export(self):
        missing = dict(weeks=[w["week"] for w in self.weeks if w["action_source"] != "actor"]
                             + list(range(len(self.weeks) + 1, self.case["weeks"] + 1)),
                       physical_weeks=list(range(len(self.weeks) + 1, self.case["weeks"] + 1)),
                       probe_ids=[p["probe_id"] for p in self.probes if p["probe_id"] not in self.actor_probe_answers],
                       applied_probe_ids=[p["probe_id"] for p in self.probes if p["probe_id"] not in self.probe_answers],
                       question_ids=[q["question_id"] for q in self.questions] if self.comprehension_answers is None else [])
        return clone(dict(schema_version=SCHEMA, timeout_policy=POLICY, probe_timeout_policy=PROBE_POLICY,
                          initial_orders=INITIAL_ORDERS,
                          **self.status(),
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
                          opportunities=self.opportunities, applied_actions=self.applied_actions,
                          probe_answers=self.probe_answers, applied_probe_answers=self.probe_answers,
                          actor_probe_answers=self.actor_probe_answers,
                          probe_answer_sources=self.probe_answer_sources,
                          probe_actor_missing_mask=self.probe_actor_missing_mask,
                          comprehension_answers=self.comprehension_answers,
                          pending_display=self.pending["display"] if self.pending else None,
                          missing=missing, terminal_at=self.terminal_at, events=self.events,
                          completed_prefix_cost=sum(w["cost"] for w in self.weeks),
                          full_game_cost=sum(w["cost"] for w in self.weeks) if len(self.weeks) == self.case["weeks"] else None,
                          provenance_interpretation="Local execution receipts; external transcript required. Not tamper-proof."))


def audit_result(payload, case):
    """Replay accepted literal decisions, timing admission and every physical state."""
    replay = CarryCase(case, clock=payload["events"][0]["clock"])
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
        elif event["kind"] == "deadline_expired":
            if not replay.check_expiry(event["clock"]):
                raise ValueError("Deadline expiry replay differs")
        elif event["kind"] == "stopped":
            replay.check_expiry(event["clock"])
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
