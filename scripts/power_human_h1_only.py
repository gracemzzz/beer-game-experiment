"""H1-only prospective power scenarios and a worked teaching example.

Preserves the earlier joint H1/H2 analysis. No participant or model calls.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math

from openpyxl import Workbook, load_workbook
from scipy import optimize, stats
from statsmodels.stats.power import TTestIndPower

from power_human_h1_h2 import STUDY, REPORTS, TABLES, excel_sheet, power


def required(d, target):
    initial = TTestIndPower().solve_power(effect_size=d, nobs1=None, alpha=.05,
                                         power=target, ratio=1, alternative='two-sided')
    n = math.ceil(initial)
    # Match the support criterion: a two-sided p < .05 AND the predicted sign.
    while power(d, n, alpha=.05) < target:
        n += 1
    while n > 2 and power(d, n-1, alpha=.05) >= target:
        n -= 1
    assert power(d, n, alpha=.05) >= target
    assert power(d, n-1, alpha=.05) < target
    return n


def main():
    protected = [REPORTS/'POWER_ANALYSIS.xlsx', REPORTS/'POWER_ANALYSIS.pdf',
                 STUDY/'hypotheses/POWER_ASSUMPTIONS.json']
    before = {p: hashlib.sha256(p.read_bytes()).hexdigest() for p in protected}
    rows = []
    for d in [.2, .3, .4, .5, .6, .8, 1., 1.2, 1.5]:
        n80, n90 = required(d, .8), required(d, .9)
        rows.append(dict(H1_chain_effect_d=d, chains_per_condition_80pct=n80,
            completed_people_80pct=8*n80, recruit_with_10pct_chain_loss_80pct=8*math.ceil(n80/.9),
            chains_per_condition_90pct=n90, completed_people_90pct=8*n90,
            recruit_with_10pct_chain_loss_90pct=8*math.ceil(n90/.9),
            achieved_power_at_80pct_target=power(d,n80,alpha=.05),
            power_with_80_people=power(d,10,alpha=.05)))
    path = TABLES/'h1_only_sample_sizes.csv'
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=list(rows[0]))
        writer.writeheader(); writer.writerows(rows)
    mde = optimize.brentq(lambda d: power(d,10,alpha=.05)-.8,.01,5)
    assumptions = dict(status='Conditional H1-only planning scenario; human protocol not frozen',
        primary_hypothesis='H1: Tight deadlines increase pipeline underweighting',
        significance_level=.05, sidedness='Two-sided; predicted sign required for support',
        power_targets=[.8,.9], sole_primary_endpoint='H1; H2 would be secondary/exploratory',
        design='Two independent groups of four-person chains, equal allocation',
        h1_measure='Conditional on paired-probe response aggregated to one score per chain',
        human_effect_and_sd='Unknown; values in tables are scenarios, not GPT-derived predictions',
        distribution='Normally distributed independent chain scores, common SD in both arms',
        example={'adequate_mean':.30,'tight_mean':.25,'common_chain_sd':.10,'d':.5},
        power_with_80_people_d_half=power(.5,10,alpha=.05),
        minimum_effect_d_for_80_people_at_80pct=mde,
        attrition='10% whole-chain loss is illustrative; expected-retention allowance only',
        validation='All integer sample thresholds checked against the immediately smaller n')
    (STUDY/'hypotheses/H1_ONLY_POWER_ASSUMPTIONS.json').write_text(json.dumps(assumptions,indent=2)+'\n')
    guide = [
        dict(item='H1-only scope', explanation='H1 is the only confirmatory primary hypothesis, chosen before human collection. H2 can still be measured as secondary/exploratory; this does not supply a confirmatory H2 test.'),
        dict(item='Conditional counts', explanation='At 80% power: d=.5 requires 512 completed people; d=.8 requires 208; d=1.0 requires 136. These effect sizes are assumptions, not human estimates.'),
        dict(item='What changed?', explanation='One primary test: alpha=.05 instead of .025. For 80% H1 power, target .80 instead of the earlier .90 per endpoint used to plan for detecting BOTH H1 and H2.'),
        dict(item='Independent unit', explanation='A four-person chain. Participants and weeks within a chain are dependent; two conditions with n chains each require 8n people.'),
        dict(item='H1 outcome', explanation='Pipeline response = (order at low outstanding - order at high outstanding) / increase in outstanding cases; average the prespecified pairs to a chain score. Lower response is consistent with greater underweighting; no optimal benchmark has been identified.'),
        dict(item='Effect size d', explanation='Meaningful difference between condition means divided by the common between-chain SD. Use SD, not the standard error. Chain means and SDs must come from a comparable human population or justified scenarios.'),
        dict(item='80% power', explanation='If the specified true effect and model hold, about 80% of repeated studies would detect it with p<.05 and the predicted sign. It is not an 80% probability that H1 is true.'),
        dict(item='80-person cap', explanation=f'80 people = 10 chains per condition. An effect of about d={mde:.2f} is required for 80% power; d=.5 has about 18% power and d=.8 about 40%.'),
        dict(item='Missing inputs', explanation='Primary H1 measure (probe score versus weekly-order regression); smallest meaningful change; human chain-score SD; session/matching structure; deadline calibration; usable-chain retention and recruitment cap.'),
        dict(item='Assumptions', explanation='Independent, approximately normal chain scores with equal between-condition variances. No matching benefit or extra session dependence assumed. A regression endpoint requires model-specific power analysis.'),
        dict(item='Optional attrition allowance', explanation='Recruit 8*ceiling(n/.9) if 10% of whole chains are expected to be unusable. Individual dropout is different; this allowance does not guarantee the final completed count. Pilots are additional.'),
    ]
    normal_n=2*(stats.norm.ppf(.975)+stats.norm.ppf(.8))**2/.5**2
    steps = [
        dict(step='1. Select the sole primary endpoint', calculation='H1 response proxy; lower response under tight deadlines', example_value='One score per chain', explanation='If using regression-estimated weighting instead, change the power model.'),
        dict(step='2. Set false-positive threshold', calculation='alpha = .05, two-sided', example_value=.05, explanation='Under the null, the test has a 5% rejection rate. No adjustment for a second primary hypothesis.'),
        dict(step='3. Set detection probability', calculation='power = .80', example_value=.8, explanation='80% chance to detect the specified true difference under the planning assumptions.'),
        dict(step='4. Specify meaningful difference', calculation='adequate mean .30 minus tight mean .25', example_value=.05, explanation='Hypothetical order cases per outstanding case; not observed human values.'),
        dict(step='5. Specify between-chain variability', calculation='common chain SD = .10', example_value=.10, explanation='Hypothetical SD across chain scores within a condition; NOT SEM and NOT individual-player SD.'),
        dict(step='6. Standardize the difference', calculation='d = .05 / .10', example_value=.5, explanation='The effect is half a between-chain standard deviation.'),
        dict(step='7. Approximate n per condition', calculation='n = 2*(1.95996 + .84162)^2 / d^2', example_value=normal_n, explanation='Normal approximation gives 62.79, rounded up to 63 chains per condition.'),
        dict(step='8. Refine with the t distribution', calculation='df=2n-2; noncentrality=d*sqrt(n/2); critical=t(1-alpha/2,df)', example_value=64, explanation=f'Search smallest integer n with sufficient power: n=63 gives {power(.5,63,alpha=.05):.4f}; n=64 gives {power(.5,64,alpha=.05):.4f}.'),
        dict(step='9. Convert chains into people', calculation='2 conditions * 64 chains * 4 people', example_value=512, explanation='128 completed chains total; 256 people per condition.'),
        dict(step='10. Optional whole-chain loss allowance', calculation='2 * ceiling(64/.9) * 4', example_value=576, explanation='72 recruited chains per condition if allowing an expected 10% whole-chain loss.'),
    ]
    sensitivity=[]
    for delta in [.03,.05,.08,.10]:
        for sd in [.05,.10,.15,.20]:
            d=delta/sd;n=required(d,.8)
            sensitivity.append(dict(assumed_response_decrease=delta,assumed_chain_sd=sd,d=d,
                chains_per_condition=n,completed_people=8*n,status='Hypothetical inputs, 80% power, two-sided alpha .05'))
    wb=Workbook();wb.remove(wb.active)
    wb.properties.title='H1-only human Beer Game power: worked calculation'
    excel_sheet(wb,'00 Read first','H1 alone; conditional planning, not a guarantee of significance.',guide,[32,120])
    excel_sheet(wb,'01 Recruitment','Four people per chain. All counts use two-sided alpha .05; d is a CHAIN-level standardized difference.',rows)
    excel_sheet(wb,'02 Worked example','Example means and SD are hypothetical. Exact sample counts use noncentral-t power; the normal formula is a teaching approximation.',steps,[39,75,28,95])
    excel_sheet(wb,'03 H1 sensitivity','Use human pilot information and a meaningful target difference to choose inputs; no GPT-to-human transfer assumed.',sensitivity,[30,27,20,28,25,75])
    excel_sheet(wb,'04 Method sources','Methodological basis and reproducible code; prior H1/H2 reports remain unchanged.',[
        dict(source='Supplied Hyndman & Embrey chapter', location='Econometrics for Experiments, section 2.2.3 (PDF pp.5-8) and section 2.5 (pp.31-36)', use='Prospective power and dependence among interacting participants.'),
        dict(source='statsmodels TTestIndPower', location='https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestIndPower.solve_power.html', use='Noncentral-t power for two independent groups; nobs1 counts chains in one condition here.'),
        dict(source='Reproduce this workbook', location='python scripts/power_human_h1_only.py', use='Finite-sample calculation, integer-threshold checks, data preservation and output generation.'),
    ],[42,110,75])
    dest=REPORTS/'H1_ONLY_POWER.xlsx';wb.save(dest)
    check=load_workbook(dest,read_only=True)
    assert len(check.sheetnames)==5
    assert check['01 Recruitment'].max_row-4==len(rows)
    check.close()
    assert all(hashlib.sha256(p.read_bytes()).hexdigest()==digest for p,digest in before.items())
    print(json.dumps(dict(workbook=str(dest),normal_approx_chains_per_condition=normal_n,
        minimum_d_with_80_people=mde,rows=[r for r in rows if r['H1_chain_effect_d'] in [.5,.8,1.]],
        prior_joint_analysis_unchanged=True),indent=2))


if __name__=='__main__':
    main()
