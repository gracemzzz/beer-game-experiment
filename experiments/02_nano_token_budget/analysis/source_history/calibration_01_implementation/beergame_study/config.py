from dataclasses import dataclass, asdict

MODEL = 'gpt-5.4-nano-2026-03-17'
PROTOCOL = 'information-sharing-token-budget-v1'
RATES = {'input': .20, 'cached': .02, 'output': 1.25}  # USD per million; checked 2026-10-04

@dataclass(frozen=True)
class Config:
    mode: str = 'offline'
    stage: str = 'calibration'  # calibration or game
    replicate_id: str = 'token-pilot-01'
    model: str = MODEL
    groups_per_condition: int = 1  # 2 conditions, 4 roles each -> 8 agents
    weeks: int = 40
    warmup_weeks: int = 4
    continuation_weeks: int = 12
    short_tokens: int = 64
    adequate_tokens: int = 256
    final_tokens: int = 192
    calibration_reference_tokens: int = 1024
    calibration_run: str = ''
    budget_usd: float = 1.05
    concurrency: int = 4
    request_interval_s: float = 1.0
    timeout_s: float = 90.
    transport_retries: int = 4
    group_replacements: int = 1
    collect_debriefs: bool = False  # optional 384-token self-report after completed games
    seed: int = 20261004
    emergency_order_limit: int = 100000  # circuit breaker; NOT shown as an allowed maximum

    def validate(self):
        assert self.mode in ('offline', 'api') and self.stage in ('calibration', 'game')
        assert self.model == MODEL, 'Model/rates are pinned. A model change requires a new protocol.'
        assert self.groups_per_condition >= 1 and self.weeks >= 20
        assert self.warmup_weeks == 4 and self.continuation_weeks == 12
        assert 16 <= self.short_tokens < self.adequate_tokens <= 2048
        assert self.final_tokens == 192 and self.calibration_reference_tokens == 1024
        assert 0 < self.budget_usd and 1 <= self.concurrency <= 8
        assert self.request_interval_s >= 0 and 0 <= self.transport_retries <= 6
        assert 0 <= self.group_replacements <= 2
        assert self.emergency_order_limit == 100000
        return self

    def scientific(self):
        # These operational changes can safely resume a checkpoint.
        return {k:v for k,v in asdict(self).items() if k not in
                ('budget_usd','concurrency','request_interval_s','timeout_s')}
