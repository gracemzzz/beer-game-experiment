"""Conservative GPT-6 Luna Flex-tier accounting, checked 11 October 2026.

Official Flex rates per million: ordinary input .05, cache reads .005, cache writes
.0625, output .25. Count ALL uncached input at the cache-write rate so the ledger
does not undercount new cache writes. This is an upper estimate, not an invoice.
No tools, premium service tier, regional endpoint or long-context pricing is used.
"""
MODEL = 'gpt-6-luna'
RATES = {'input': 0.0625, 'cached': 0.005, 'output': 0.25}
BASE_INPUT_RATE = 0.05
CALIBRATION_CAP_USD = 0.18
MAX_INPUT_ALLOWANCE = 32768
PRICING_URL = 'https://developers.openai.com/api/docs/models/gpt-6-luna'


def price(usage):
    incoming, cached, outgoing = (usage.get(k, 0) for k in
                                 ('input_tokens', 'cached_input_tokens', 'output_tokens'))
    if any(type(x) is not int or x < 0 for x in (incoming, cached, outgoing)) or cached > incoming:
        raise ValueError('Invalid token usage.')
    return ((incoming-cached)*RATES['input']+cached*RATES['cached']+outgoing*RATES['output'])/1e6


def cost_envelope(config):
    """Conservative no-sharing estimate at every output/input ceiling.

    Eight probes actually share their initial calls, so counting two is generous.
    Clear rejected-call retries have zero charge. Unknown outcomes stop the run.
    This is a software reservation envelope under documented Flex rates, not a claim
    about taxes or unrelated activity on the user's API account.
    """
    paired_decisions = (config.weeks-4)*4 + 8
    initial_calls = 16 + config.groups_per_condition*(2*paired_decisions+4)
    revision_calls = 16 + config.groups_per_condition*paired_decisions
    total = initial_calls+revision_calls
    return dict(maximum_requests=total, initial_calls=initial_calls, revision_calls=revision_calls,
                input_allowance_per_call=MAX_INPUT_ALLOWANCE,
                conservative_usd=(total*MAX_INPUT_ALLOWANCE*RATES['input']
                                 +(initial_calls*config.initial_tokens+revision_calls*config.revision_tokens)*RATES['output'])/1e6)
