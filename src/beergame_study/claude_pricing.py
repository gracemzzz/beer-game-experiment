"""Anthropic Haiku 5.5 standard/global prices checked 11 October 2026."""
MODEL = 'claude-haiku-5-5'
RATES = {'input': .10, 'cached': .01, 'cache_write_5m': .125,
         'cache_write_1h': .20, 'output': .50}
PRICING_URL = 'https://platform.claude.com/docs/en/about-claude/pricing'
MAX_INPUT_ALLOWANCE = 32768
CALIBRATION_CAP_USD = .18


def price(usage):
    keys = ('input_tokens', 'cached_input_tokens', 'cache_write_5m_tokens',
            'cache_write_1h_tokens', 'output_tokens')
    incoming, cached, short_write, long_write, outgoing = (usage.get(k, 0) for k in keys)
    if any(type(x) is not int or x < 0 for x in (incoming, cached, short_write, long_write, outgoing)):
        raise ValueError('Invalid measured token usage.')
    ordinary = incoming - cached - short_write - long_write
    if ordinary < 0:
        raise ValueError('Input usage is inconsistent.')
    return (ordinary * RATES['input'] + cached * RATES['cached']
            + short_write * RATES['cache_write_5m'] + long_write * RATES['cache_write_1h']
            + outgoing * RATES['output']) / 1e6 * (5 if incoming > 100000 else 1)


def cost_envelope(config):
    paired_decisions = (config.weeks - 4) * 4 + 8
    initial_calls = 16 + config.groups_per_condition * (2 * paired_decisions + 4)
    revision_calls = 16 + config.groups_per_condition * paired_decisions
    calls = initial_calls + revision_calls
    return dict(maximum_requests=calls, initial_calls=initial_calls, revision_calls=revision_calls,
                input_allowance_per_call=MAX_INPUT_ALLOWANCE,
                conservative_usd=(calls * MAX_INPUT_ALLOWANCE * RATES['cache_write_1h']
                                  + (initial_calls * config.initial_tokens
                                     + revision_calls * config.revision_tokens) * RATES['output']) / 1e6,
                note='Worst-case envelope can exceed campaign budget; request guards stop before overspend. The full sample must pass the measured calibration forecast before games.')
