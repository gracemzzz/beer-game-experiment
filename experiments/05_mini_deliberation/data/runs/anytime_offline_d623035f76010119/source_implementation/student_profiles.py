"""Explicit fictional heterogeneity; profile frequencies are design weights."""
import json
from pathlib import Path
import numpy as np

PROFILE_DIR = Path(__file__).resolve().parents[2]/'config/student_profiles'
PROFILE_IDS = ('methodical_calm', 'methodical_concerned', 'flexible_calm', 'flexible_concerned')


def profiles():
    result = {key: json.loads((PROFILE_DIR/(key+'.json')).read_text(encoding='utf-8')) for key in PROFILE_IDS}
    if any(value['id'] != key or not value['description'] for key, value in result.items()):
        raise ValueError('Invalid student profile file.')
    return result


def assignment(seed, block):
    """Each profile occupies every role in four pairs; treatments are matched."""
    base = list(np.random.default_rng(seed+37000+block//4).permutation(PROFILE_IDS))
    offset = block % 4
    return base[offset:]+base[:offset]
