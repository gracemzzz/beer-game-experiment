"""Prospective H1/H2 human-study sensitivity analysis; no participant/model calls.

Run from the repository root with numpy, scipy, statsmodels, matplotlib and
openpyxl installed. Human effects/variances are unknown: all sample-size grids
are conditional scenarios, not forecasts fitted to the GPT results.
"""
from __future__ import annotations

import csv
import hashlib
import json
import math
from pathlib import Path
import textwrap

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import numpy as np
from openpyxl import Workbook, load_workbook
from openpyxl.styles import Alignment, Font, PatternFill
from openpyxl.utils import get_column_letter
from scipy import optimize, stats
import scipy
import statsmodels
from statsmodels.stats.power import TTestIndPower, TTestPower

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments/15_human_time_pressure_planning_20261115"
REPORTS = STUDY / "reports"
TABLES = STUDY / "analysis/tables"
BOOK = Path("/Users/gracezhang/Desktop/The_Handbook_of_Behavioral_Operations_----_(2_Econometrics_for_Experiments).pdf")
GPT = ROOT / "experiments/14_deadline_student_20261026/reports/tables/CHAIN_VALUES.csv"
ALPHA = 0.025  # two co-primary tests; conservative Bonferroni planning for Holm
M = 4
SIM_REPS = 30000
SEED = 20261115


def power(d, n, alpha=ALPHA, one_sided=False):
    """Directional detection with a two-sided critical value by default."""
    df = 2 * n - 2
    critical = stats.t.isf(alpha if one_sided else alpha / 2, df)
    return float(stats.nct.sf(critical, df, abs(d) * math.sqrt(n / 2)))


def required_n(d, target, one_sided=False):
    lo, hi = 2, 4
    while power(d, hi, one_sided=one_sided) < target:
        hi *= 2
    while lo < hi:
        mid = (lo + hi) // 2
        if power(d, mid, one_sided=one_sided) >= target:
            hi = mid
        else:
            lo = mid + 1
    assert power(d, lo, one_sided=one_sided) >= target
    assert lo == 2 or power(d, lo - 1, one_sided=one_sided) < target
    return lo


def people(n):
    return 2 * M * n


def write_csv(name, records):
    with (TABLES / name).open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(records[0]))
        writer.writeheader()
        writer.writerows(records)


def simulate(d1, d2, n, rho, reps, seed):
    """Synthetic bivariate normal CHAIN outcomes, not generated human responses."""
    rng = np.random.default_rng(seed)
    chol = np.linalg.cholesky([[1, rho], [rho, 1]])
    counts = np.zeros(6, dtype=np.int64)
    for start in range(0, reps, 1000):
        size = min(1000, reps - start)
        control = rng.normal(size=(size, n, 2)) @ chol.T
        pressure = rng.normal(size=(size, n, 2)) @ chol.T + [d1, d2]
        pooled = (control.var(axis=1, ddof=1) + pressure.var(axis=1, ddof=1)) / 2
        t = (pressure.mean(axis=1) - control.mean(axis=1)) / np.sqrt(pooled * 2 / n)
        p = 2 * stats.t.sf(np.abs(t), df=2 * n - 2)
        bonf = (p <= ALPHA) & (t > 0)
        holm = np.column_stack([
            (p[:, 0] <= ALPHA) | ((p[:, 0] <= .05) & (p[:, 1] <= ALPHA)),
            (p[:, 1] <= ALPHA) | ((p[:, 1] <= .05) & (p[:, 0] <= ALPHA)),
        ]) & (t > 0)
        counts += [bonf[:, 0].sum(), bonf[:, 1].sum(), bonf.all(axis=1).sum(),
                   holm[:, 0].sum(), holm[:, 1].sum(), holm.all(axis=1).sum()]
    estimates = counts / reps
    return dict(d_H1=d1, d_H2=d2, chains_per_condition=n, participants=people(n),
                oriented_outcome_correlation=rho, repetitions=reps,
                bonf_H1_power=estimates[0], bonf_H2_power=estimates[1],
                bonf_both_power=estimates[2], holm_H1_power=estimates[3],
                holm_H2_power=estimates[4], holm_both_power=estimates[5],
                holm_both_mc_se=math.sqrt(estimates[5] * (1 - estimates[5]) / reps),
                analytic_H1=power(d1, n), analytic_H2=power(d2, n), seed=seed)


def excel_sheet(wb, name, note, rows, widths=None):
    ws = wb.create_sheet(name)
    headers = list(rows[0])
    ws.sheet_view.showGridLines = False
    ws.sheet_view.zoomScale = 85
    ws.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(headers))
    ws.cell(1, 1, name).font = Font(name="Calibri", size=19, bold=True, color="FFFFFF")
    ws.cell(1, 1).fill = PatternFill("solid", fgColor="18374F")
    ws.row_dimensions[1].height = 34
    ws.merge_cells(start_row=2, start_column=1, end_row=2, end_column=len(headers))
    ws.cell(2, 1, note).alignment = Alignment(wrap_text=True, vertical="center")
    ws.cell(2, 1).font = Font(name="Calibri", size=11, color="455A64")
    ws.row_dimensions[2].height = 46
    for j, key in enumerate(headers, 1):
        ws.cell(4, j, key.replace("_", " ")).font = Font(name="Calibri", bold=True, color="FFFFFF")
        ws.cell(4, j).fill = PatternFill("solid", fgColor="284F6B")
        ws.cell(4, j).alignment = Alignment(wrap_text=True, vertical="center")
        ws.column_dimensions[get_column_letter(j)].width = widths[j - 1] if widths else (32 if j == 1 else 24)
    ws.row_dimensions[4].height = 45
    for i, record in enumerate(rows, 5):
        height = 28
        for j, key in enumerate(headers, 1):
            value = record[key]
            if isinstance(value, np.generic):
                value = value.item()
            cell = ws.cell(i, j, value)
            cell.font = Font(name="Calibri", size=11, color="203442", bold=(j == 1))
            cell.alignment = Alignment(wrap_text=True, vertical="top")
            if i % 2 == 0:
                cell.fill = PatternFill("solid", fgColor="EFF4F8")
            if isinstance(value, float):
                cell.number_format = "0.0000"
            width = ws.column_dimensions[get_column_letter(j)].width
            lines = sum(max(1, len(textwrap.wrap(part, width=max(8, int(width) - 3)))) for part in str(value).split("\n"))
            height = max(height, 15 * lines + 8)
        ws.row_dimensions[i].height = height
    ws.freeze_panes = "B5"
    ws.auto_filter.ref = f"A4:{get_column_letter(len(headers))}{ws.max_row}"
    ws.sheet_properties.tabColor = "284F6B"
    ws.page_setup.orientation = "landscape"
    ws.page_setup.fitToWidth = 1
    ws.page_setup.fitToHeight = 0
    ws.sheet_properties.pageSetUpPr.fitToPage = True
    ws.print_title_rows = "1:4"
    return ws


def pdf_text_page(pdf, title, blocks, footer):
    fig = plt.figure(figsize=(8.27, 11.69), facecolor="white")
    fig.text(.08, .95, title, fontsize=20, color="#18374F", weight="bold", va="top")
    y = .895
    for heading, body in blocks:
        fig.text(.08, y, heading, fontsize=12, color="#18374F", weight="bold", va="top")
        y -= .026
        wrapped = "\n".join(textwrap.fill(p, 91) for p in body.split("\n"))
        fig.text(.08, y, wrapped, fontsize=10.3, color="#253746", va="top", linespacing=1.45)
        y -= .0185 * (wrapped.count("\n") + 1) + .026
    assert y > .045, f"PDF text overflow: {title} / {y}"
    fig.text(.08, .035, footer, fontsize=8, color="#607D8B")
    pdf.savefig(fig)
    plt.close(fig)


def main():
    for folder in [REPORTS / "figures", TABLES, STUDY / "hypotheses", STUDY / "data"]:
        folder.mkdir(parents=True, exist_ok=True)
    source_hash = hashlib.sha256(GPT.read_bytes()).hexdigest()
    assumptions = dict(status="Prospective sensitivity analysis, not a frozen human protocol",
        human_data_available=False, hypothesis_1="Tight deadlines increase pipeline underweighting",
        hypothesis_2="Tight deadlines increase total holding and backlog costs",
        h1_measure="Conditional: same matched pipeline-response probes; not a directly estimated normative weight",
        h2_measure="Sum of 0.5 * end-week inventory + 1 * end-week backlog over 4 roles and 24 weeks",
        independent_unit="Four-person chain, conditional on no residual cross-chain/session dependence",
        allocation="1:1 randomization of distinct chains; no assumed matching gain",
        hypothetical_weeks=24, roles_per_chain=4, family_alpha=.05, planning_alpha_per_test=ALPHA,
        primary_tests=2, alternative="Two-sided; support also requires the predicted direction",
        family_procedure="Holm across H1 and H2; conservative sample planning at .025 for each",
        joint_target=.80, marginal_target_for_joint=.90,
        joint_bound="P(both) >= 1 - (1-power_H1) - (1-power_H2); no endpoint-correlation assumption",
        model_assumptions="Independent normally distributed chain summaries with equal between-condition variances",
        attrition_sensitivity="10% whole-chain loss; expected-retention allowance, not an assurance guarantee",
        exact_deadlines="Not selected. Human feasibility calibration required; do not inherit 8/120 seconds automatically",
        human_h1_choice="Pending user choice: probes versus weekly-order regression",
        human_effects_and_variances="Unknown; no GPT-to-human transfer assumed", planned_date="2026-11-15")
    (STUDY / "hypotheses/POWER_ASSUMPTIONS.json").write_text(json.dumps(assumptions, indent=2) + "\n")
    manifest = dict(chapter_path=str(BOOK), sha256=hashlib.sha256(BOOK.read_bytes()).hexdigest(),
        authors="Kyle Hyndman and Matthew Embrey", year=2018, chapter="Econometrics for Experiments",
        relevant_pdf_pages=[5,6,7,8,31,32,33,34,35,36],
        note="User-supplied source; full chapter text/PDF not copied into repository",
        gpt_reference_path=str(GPT.relative_to(ROOT)), gpt_reference_sha256=source_hash)
    (STUDY / "data/SOURCE_MANIFEST.json").write_text(json.dumps(manifest, indent=2) + "\n")

    sample_rows, budget_rows = [], []
    for d in [.2, .3, .4, .5, .6, .8, 1., 1.2, 1.5]:
        n80, n90 = required_n(d, .8), required_n(d, .9)
        sample_rows.append(dict(weaker_effect_d=d, chains_per_condition_80_each=n80,
            completed_people_80_each=people(n80), chains_per_condition_90_each=n90,
            total_chains_joint80=2*n90, completed_people_joint80=people(n90),
            recruit_people_10pct_chain_loss=people(math.ceil(n90 / .9)),
            achieved_per_endpoint_power=power(d, n90), joint_power_lower_bound=2*power(d,n90)-1))
        p = power(d, 10)
        budget_rows.append(dict(effect_d=d, completed_people=80, chains_per_condition=10,
            per_endpoint_power=p, both_power_bonf_if_independent=p*p,
            both_power_bonf_lower_bound=max(0, 2*p-1), both_power_bonf_upper_bound=p))
    h1_rows=[]
    for delta in [.03, .05, .10]:
        for sd in [.05, .10, .15, .20]:
            d=delta/sd; n=required_n(d,.9)
            h1_rows.append(dict(response_decrease=delta, chain_score_sd=sd, effect_d=d,
                chains_per_condition=n, completed_people=people(n),
                recruit_people_10pct_chain_loss=people(math.ceil(n/.9)), assumption="Hypothetical; 90% H1 power only. H2 may require more."))
    h2_rows=[]
    for pct in [.10,.20,.30]:
        for cv in [.25,.50,.75,1.]:
            d=pct/cv; n=required_n(d,.9)
            h2_rows.append(dict(cost_increase_fraction=pct, common_chain_sd_over_control_mean=cv,
                effect_d=d, chains_per_condition=n, completed_people=people(n),
                recruit_people_10pct_chain_loss=people(math.ceil(n/.9)), assumption="Hypothetical equal absolute SD in both arms; 90% H2 power only."))
    alternatives=[]
    for d in [.5,.8,1.]:
        for rho in [0,.25,.5,.75]:
            dz=d/math.sqrt(2*(1-rho))
            n=math.ceil(TTestPower().solve_power(effect_size=dz,nobs=None,alpha=ALPHA,power=.9))
            alternatives.append(dict(design="Matched distinct chains, two-sided", marginal_chain_effect_d=d,
                assumed_pair_correlation=rho, pairs_or_chains_per_condition=n, completed_people=people(n),
                limitation="One pair = two separate 4-person chains. Correlation must be justified by human data."))
        n=required_n(d,.9,True)
        alternatives.append(dict(design="Independent chains, one-sided", marginal_chain_effect_d=d,
            assumed_pair_correlation="Not applicable", pairs_or_chains_per_condition=n, completed_people=people(n),
            limitation="Only if justified and preregistered before data; cannot switch after seeing results."))
    icc_rows=[]
    for individual_d in [.3,.5,.8]:
        for rho in [0,.1,.3,.5,.8,1.]:
            de=1+3*rho
            chain_d=individual_d*math.sqrt(4/de)
            n=required_n(chain_d,.9)
            icc_rows.append(dict(individual_score_effect_d=individual_d, assumed_within_chain_ICC=rho,
                design_effect=de, implied_chain_mean_effect_d=chain_d, chains_per_condition=n,
                completed_people=people(n), limitation="Exchangeable individual H1 scores with equal variances. Not for chain-total H2; do not apply twice."))
    simulations=[]
    scenarios=[(.5,.5,10),(.5,.5,78),(.5,.5,101),(.8,.8,10),(.8,.8,31),(.8,.8,41),(.5,.8,101)]
    for d1,d2,n in scenarios:
        for rho in [0,.5,.8]:
            simulations.append(simulate(d1,d2,n,rho,SIM_REPS,SEED+len(simulations)))
    validation=[]
    for d in [.2,.5,.8,1.2]:
        for target in [.8,.9]:
            n=required_n(d,target)
            other=TTestIndPower().power(d,n,alpha=ALPHA,ratio=1)
            our=power(d,n)
            # statsmodels adds the very small opposite-direction rejection tail.
            assert abs(other-our)<1e-4
            validation.append(dict(effect=d,target=target,n=n,analytic_directional=our,
                statsmodels_two_sided=other,absolute_difference=abs(other-our)))
    for s in simulations:
        for endpoint in ['H1','H2']:
            analytic=s[f'analytic_{endpoint}']; observed=s[f'bonf_{endpoint}_power']
            se=math.sqrt(analytic*(1-analytic)/SIM_REPS)
            assert abs(analytic-observed)<5*se, (s,endpoint)

    with GPT.open(newline="") as f: raw=list(csv.DictReader(f))
    gpt_rows=[]
    for hypothesis,field in [('H1','pipeline_sensitivity'),('H2','chain_total_cost')]:
        a=np.array([float(r[field]) for r in raw if r['arm']=='A'])
        b=np.array([float(r[field]) for r in raw if r['arm']=='B'])
        sd=math.sqrt((a.var(ddof=1)+b.var(ddof=1))/2)
        gpt_rows.append(dict(hypothesis=hypothesis,metric=field,
            no_pressure_mean=a.mean(),pressure_mean=b.mean(),no_pressure_sd=a.std(ddof=1),
            pressure_sd=b.std(ddof=1),pooled_sd=sd,absolute_standardized_effect=abs(b.mean()-a.mean())/sd,
            status="LLM portrayal only. NOT used as the human effect/variance in recruitment targets."))
    missing = [
        dict(input="H1 operational measure", why="Probe-response score and weekly-order regression coefficient are different estimands and need different power models.", current="Probes used only as a conditional illustration; user choice pending", needed="Specify the primary H1 outcome, probe count/timing or exact regression model."),
        dict(input="Meaningful H1 difference", why="Power depends on the smallest response decrease or weighting change worth detecting.", current="Unknown; hypothetical decreases .03, .05, .10", needed="Choose an effect in order cases per outstanding case, or coefficient units if regression."),
        dict(input="Meaningful H2 difference", why="A 10% cost increase and a 30% increase require very different samples.", current="Unknown; hypothetical 10%, 20%, 30%", needed="Choose percentage or absolute increase in cumulative holding/backlog costs."),
        dict(input="Human chain-score variability", why="The denominator of d is between-chain SD, including measurement noise.", current="No human pilot dataset provided", needed="Per-chain H1 scores and 24-week cumulative costs, condition and session; raw roles/probes preferred."),
        dict(input="H1/H2 correlation", why="Needed for less conservative joint-power simulation with Holm.", current="Unknown; simulations use oriented correlations 0, .5, .8", needed="Both outcomes from the same human chains. Conservative joint bound does not need this correlation."),
        dict(input="Sessions and allocation", why="Shared facilitators, demand paths or interactions can make different chains dependent.", current="Assumes independent chains, balanced random allocation", needed="Number of sessions, chains per session, treatment mixing, facilitators, demand-path blocking and cross-chain contact."),
        dict(input="Human deadline calibration", why="The LLM fictional 8/120-second framing does not establish binding/adequate human deadlines.", current="Actual human allowances not selected", needed="Human response times, completion rates and pressure/adequacy ratings under the intended interface."),
        dict(input="Game length / parameters", why="Changing weeks, costs, demand or initial stocks changes the outcome distribution.", current="Conditional on 24 weeks, four roles and 0.5/1 cost rates", needed="Confirm final human protocol; original reflection pilot mentioned about 40 rounds."),
        dict(input="Attrition / missing orders", why="A lost member can invalidate an entire chain; misses may be treatment related.", current="Illustrative 10% whole-chain loss", needed="Whole-chain usable-data rate, no-show rate, fixed timeout/missing-data policy and final recruitment cap."),
        dict(input="Target and multiplicity", why="80% for each hypothesis is not 80% for both; more endpoints need revised adjustment.", current="Two-sided Holm family .05; 90% each for conservative joint target .80", needed="Confirm H1/H2 only and whether success requires both; approve any directional test prospectively."),
    ]
    source_rows=[
        dict(source="Hyndman & Embrey (2018), Econometrics for Experiments", location=str(BOOK), pages="PDF 5-8; 31-36", use="Prospective power, interacting clusters, repeated observations, session dependence and few-cluster inference."),
        dict(source="List, Sadoff & Wagner (2011)", location="https://rady.ucsd.edu/_files/faculty-research/sadoff/List_Sadoff_Wagner_Optimal_Sample_Design_Experimental_Economics_2011.pdf", pages="Experimental Economics 14:439-457", use="Effect/variance/sample-size relationships, allocation and cluster-design principles."),
        dict(source="Cameron & Miller (2015)", location="https://cameron.econ.ucdavis.edu/research/Cameron_Miller_JHR_2015.pdf", pages="Journal of Human Resources 50:317-372", use="Dependence within groups and limits of large-sample cluster inference."),
        dict(source="statsmodels TTestIndPower", location="https://www.statsmodels.org/stable/generated/statsmodels.stats.power.TTestIndPower.solve_power.html", pages="API reference", use="Independent calculation check for equal-variance two-sample t power."),
        dict(source="Saved ThoughtsReflection", location=str(ROOT/'experiments/11_education_deadline/data/source/reflection_20261019/reflection.txt'), pages="Time constraint experiment", use="Original 80-person / 20-chain proposal and human timing-calibration concept."),
    ]
    datasets={'required_sample_sizes.csv':sample_rows,'power_with_80_people.csv':budget_rows,
        'h1_sensitivity.csv':h1_rows,'h2_sensitivity.csv':h2_rows,'design_alternatives.csv':alternatives,
        'h1_icc_sensitivity.csv':icc_rows,'synthetic_joint_power_checks.csv':simulations,
        'analytic_validation.csv':validation,'gpt_reference_not_human.csv':gpt_rows,'missing_inputs.csv':missing}
    for name,records in datasets.items():write_csv(name,records)
    mde80=optimize.brentq(lambda d:power(d,10)-.8,.01,5)
    mde90=optimize.brentq(lambda d:power(d,10)-.9,.01,5)
    results=dict(mde_80_people_80_each=mde80,mde_80_people_joint80_conservative=mde90,
        scipy_version=scipy.__version__,statsmodels_version=statsmodels.__version__,
        monte_carlo_repetitions_per_scenario=SIM_REPS,monte_carlo_scenarios=len(simulations),
        checked_minimal_integer_sample_sizes=True,compared_with_statsmodels=True,
        simulation_agreement_within_5_mc_se=True,gpt_not_used_to_predict_human_effects=True)
    (STUDY/'analysis/VALIDATION.json').write_text(json.dumps(results,indent=2)+'\n')

    wb=Workbook();wb.remove(wb.active)
    wb.properties.title="Human Beer Game H1/H2: prospective power analysis"
    summary=[
        dict(item="Status",finding="Conditional planning scenarios; human effect sizes and variances are unknown. No sample size guarantees significance."),
        dict(item="Design",finding="Two conditions; equal random allocation; 4 people per chain; 24 weeks assumed; independent chains, no matching gain assumed."),
        dict(item="Two hypotheses",finding="Family false-positive level .05. Plan conservatively at two-sided .025 per test; final Holm adjustment across H1/H2."),
        dict(item="Detecting both",finding="Target 90% for each endpoint gives at least 80% for detecting both, under the planning model, without assuming endpoint independence."),
        dict(item="If weaker effect d = 0.5",finding="101 completed chains per condition = 808 people. With 10% whole-chain loss allowance: recruit 904 people."),
        dict(item="If weaker effect d = 0.8",finding="41 completed chains per condition = 328 people. With 10% whole-chain loss allowance: recruit 368 people."),
        dict(item="If weaker effect d = 1.0",finding="27 completed chains per condition = 216 people. With 10% whole-chain loss allowance: recruit 240 people."),
        dict(item="Original 80-person plan",finding=f"10 chains per condition. Minimum d approximately {mde80:.2f} for 80% per endpoint; {mde90:.2f} for the conservative joint target. These are very large standardized differences."),
        dict(item="What is d?",finding="Absolute meaningful difference / common between-chain standard deviation. It is not a percentage change. Use the weaker (smaller d) of H1 and H2."),
        dict(item="Human pilot needed",finding="Estimate chain-score variability, session effects, deadline feasibility and missing-data rates. The GPT study cannot establish human effect sizes."),
        dict(item="Attrition allowance",finding="10% is illustrative loss of whole usable chains, not individuals. Inflating by 1/0.9 targets expected retained count; it does not guarantee that many completed chains."),
        dict(item="Regressions / skew",finding="If H1 uses a weekly-order interaction model, or costs are strongly skewed/heteroskedastic, simulate the exact prespecified analysis using human pilot information."),
    ]
    excel_sheet(wb,'00 Start here','Conclusions first. All recruitment counts are conditional; the weaker endpoint determines the common sample.',summary,[32,115])
    excel_sheet(wb,'01 Recruitment scenarios','d is a CHAIN-level standardized effect. 80% each does not mean 80% both. Joint80 columns use 90% each and two-sided alpha .025.',sample_rows)
    excel_sheet(wb,'02 Original 80 people','10 independent chains per condition. Joint columns here refer to the conservative Bonferroni rule; Holm joint power is simulated separately.',budget_rows)
    excel_sheet(wb,'03 H1 sensitivity','Hypothetical response decreases and human chain-score SDs; not estimates. These rows power H1 at 90%; the shared study must also meet H2.',h1_rows)
    excel_sheet(wb,'04 H2 sensitivity','Hypothetical percent increases; common absolute SD / control mean. d = increase fraction / this ratio. If variances differ, recalculate.',h2_rows)
    excel_sheet(wb,'05 Missing inputs','Inputs needed to turn scenarios into a defensible final human recruitment target.',missing,[32,68,63,90])
    excel_sheet(wb,'06 Design alternatives','90% per endpoint. Matched designs pair TWO distinct chains; no crossover assumed. Correlation and test direction must be justified before data.',alternatives,[43,24,25,28,24,85])
    excel_sheet(wb,'07 H1 ICC sensitivity','Only needed when starting from INDIVIDUAL H1 score variability. Primary tables already use chain SD; never add this design effect again.',icc_rows,[25,27,24,28,26,24,85])
    excel_sheet(wb,'08 Joint simulations','Synthetic normal chain outcomes, not human data. Correlation is between oriented outcomes: lower H1 response and higher H2 cost. MC SE measures simulation error.',simulations)
    excel_sheet(wb,'09 GPT reference only','These are existing LLM summaries. They were NOT used as human effect-size or variance estimates.',gpt_rows,[22,35,24,24,24,24,24,28,85])
    excel_sheet(wb,'10 Sources','User-supplied chapter plus primary methodological sources; PDF page numbers refer to the uploaded 64-page export.',source_rows,[53,115,35,95])
    wb.save(REPORTS/'POWER_ANALYSIS.xlsx')

    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':12,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(11.7,6.9),layout='constrained')
    n_grid=np.arange(4,126)
    for d,color in zip([.4,.5,.6,.8,1.],['#7570B3','#1B9E77','#377EB8','#D95F02','#B05C91']):
        ax.plot(n_grid*8,[power(d,int(n)) for n in n_grid],label=f'd = {d:.1f}',color=color,lw=2.6)
    ax.axhline(.8,color='#61727E',ls=':',lw=1.3)
    ax.axhline(.9,color='#18374F',ls='--',lw=1.3)
    ax.axvline(80,color='#AE5252',ls='--',lw=1.3)
    ax.text(91,.035,'Original plan: 80 people',fontsize=10,color='#8E3939')
    ax.text(1000,.905,'90% each: conservative 80% both',ha='right',va='bottom',fontsize=10,color='#18374F')
    ax.text(1000,.805,'80% each',ha='right',va='bottom',fontsize=10,color='#61727E')
    ax.set(xlim=(32,1000),ylim=(0,1.02),xlabel='Completed participants (4 per chain; equal allocation)',ylabel='Power for one hypothesis',title='Human-study planning: sample size depends on effect size')
    ax.yaxis.set_major_formatter(matplotlib.ticker.PercentFormatter(1))
    ax.grid(axis='y',alpha=.16)
    ax.legend(title='Difference / chain SD',loc='lower right',frameon=False)
    sec=ax.secondary_xaxis('top',functions=(lambda p:p/4,lambda c:c*4))
    sec.set_xlabel('Total completed chains')
    fig.savefig(REPORTS/'figures/POWER_CURVES.png',dpi=180)
    fig.savefig(REPORTS/'figures/POWER_CURVES.pdf')

    with PdfPages(REPORTS/'POWER_ANALYSIS.pdf') as pdf:
        pdf_text_page(pdf,'Human Beer Game: H1/H2 power',[
            ('1. A final recruitment number needs human information.', 'The GPT results do not establish human effect sizes or human variability. The calculations below are prospective sensitivity scenarios, not a guarantee of significance.'),
            ('2. The four-person chain is the planning unit.', 'Assume two randomized conditions, four distinct people per chain and 24 weeks. The original 80 people give 20 chains, or 10 per condition. Repeated roles, weeks and probes do not create additional independent chains.'),
            ('3. Conditional completed-participant targets for BOTH hypotheses.', 'If the weaker standardized chain effect is d = 0.5: 101 chains per condition, 808 completed people; 904 recruits with a 10% whole-chain loss allowance.\nIf d = 0.8: 41 chains per condition, 328 completed people; 368 recruits with the same allowance.\nIf d = 1.0: 27 chains per condition, 216 completed people; 240 recruits with the same allowance.'),
            ('4. What the target means.', 'Use two-sided tests and family alpha .05 across H1/H2. Conservative planning uses alpha .025 per endpoint and 90% power for each, giving at least 80% power for detecting both under the assumed model. Final Holm adjustment can be more powerful. This is not an unconditional claim about human behavior.'),
            ('5. The original 80-person plan detects only very large effects.', f'At 10 chains per condition, 80% power for one endpoint requires d about {mde80:.2f}; the conservative joint target requires each effect to be at least about {mde90:.2f}. At d = 0.5, per-endpoint power is about 12%; at d = 0.8, about 28%.'),
            ('6. Next step.', 'Specify the primary H1 measure and meaningful differences; use a separate human pilot to estimate variability and validate actual deadlines. Preserve a fixed prospective sampling/analysis plan. An underpowered null result would not establish that the hypothesis is false.'),
        ],'Planning analysis | 15 November 2026 | No human observations generated; no model calls')
        pdf.savefig(fig)
        pdf_text_page(pdf,'What is being tested?',[
            ('H1: Tight deadlines increase pipeline underweighting.', 'Conditional probe definition: for a matched pair, response = (order at low outstanding - order at high outstanding) / increase in outstanding cases. Average the prespecified pairs to form a chain score. Reusing Experiment 14 means eight pipeline pairs per chain (two per role). Expected direction: lower response under tight deadlines. This is a responsiveness proxy, not a normative underweighting score.'),
            ('Alternative H1: weighting inferred from weekly game orders.', 'If the human study estimates a pipeline coefficient or time-pressure-by-pipeline interaction from repeated orders, the present probe-score calculation is not a model-specific answer. Power then depends on pipeline variation, covariates, role heterogeneity, serial/within-chain correlation, coefficient uncertainty and the exact estimator. Gameplay states are endogenous; a structural weighting interpretation needs a specified behavioral model.'),
            ('H2: Tight deadlines increase total holding and backlog costs.', 'For each chain, sum [0.5 x end-of-week inventory + 1 x end-of-week backlog] across four roles and 24 weeks. Expected direction: higher total cost under tight deadlines. Units are game cost units per chain. A percent effect also requires the human control mean and chain SD.'),
            ('Independent variable and comparison.', 'Compare actual tight versus adequate human decision deadlines in an information-sharing environment. Keep education/reading and the game environment identical. Do not inherit the LLM fictional 8/120-second settings as validated human constraints. Calibrate deadline feasibility, pressure and adequacy in humans.'),
            ('Dependence and sessions.', 'Chain-level planning already includes dependence among its four members through the chain-score variance. No additional within-chain inflation is applied. Residual common-session effects, shared demand paths or cross-chain contact can invalidate independence; block/randomize within sessions where feasible and revisit power for the intended analysis.'),
        ],'Measurement choice remains provisional pending the human protocol; no existing experiment altered')
        pdf_text_page(pdf,'Calculation and assumptions',[
            ('Standardized effect.', 'd = absolute meaningful difference / common between-chain SD. It is not a percent. H1 example: a 0.05 response decrease with chain SD 0.10 gives d = 0.5. H2 example: a 20% cost increase with common SD equal to 50% of the control mean gives d = 0.4. These are illustrations, not human estimates. Select the larger required sample across H1 and H2.'),
            ('Exact planning model.', 'For n independent chains per condition: degrees of freedom = 2n - 2; noncentrality = d x sqrt(n/2); critical value = t quantile at 1 - .025/2. Compute the upper rejection probability in the predicted direction and search the smallest integer n meeting .80 or .90. Participants = 8n. A normal approximation is n approximately 2(z[1-alpha/2] + z[power])^2 / d^2.'),
            ('Joint success and multiplicity.', 'For two endpoint detection events with powers p1 and p2, P(both) is at least p1 + p2 - 1. Thus .90 for each gives at least .80 for both; .80 for each gives only a .60 lower bound (.64 if independent). We use Bonferroni thresholds for conservative planning and Holm for the planned two-test family. A pure conjunction-only claim could use a different multiplicity strategy, which must be chosen prospectively.'),
            ('Attrition.', 'The illustrative recruitment allowance is 8 x ceiling(n / .90), assuming loss of whole usable chains. Individual loss is different: if every member must complete and individual completion is independent with probability p, chain retention is p^4. Expected-retention inflation does not guarantee a completed count and does not resolve treatment-related missingness.'),
            ('Limits and verification.', f'Normal, equal-variance chain summaries are a planning assumption. Skewed costs, heteroskedasticity, a regression endpoint or extra session clustering require a model-specific simulation. Integer thresholds were checked against n-1 and statsmodels. {len(simulations)} synthetic bivariate-normal scenarios, {SIM_REPS:,} trials each, checked individual and joint power; no simulated choices were treated as human data.'),
        ],'Numerical details and full sensitivity grids: POWER_ANALYSIS.xlsx and analysis/tables/')
        pdf_text_page(pdf,'Missing inputs and next steps',[
            ('Needed to finalize recruitment.', '1. H1 measurement: paired probes or a specified weekly-order weighting model.\n2. Smallest meaningful H1 decrease and H2 cost increase.\n3. Human chain-level SDs, cost baseline and distributions.\n4. Recruitment cap, whole-chain loss and no-show rates.\n5. Sessions, demand-path matching, randomization and any cross-chain interactions.\n6. Human deadline calibration, final weeks, incentives and missing-order rules.'),
            ('What to retain from a human pilot.', 'Record chain/participant/role/session IDs, assigned condition, all weekly orders and states/costs, every probe state and literal answer, per-decision response time, missing submissions and completion. Obtain both H1 and H2 from each chain. This permits chain variance, endpoint correlation, and (if needed) within-chain or matched-pair correlations to be estimated. A small calibration pilot can test the interface, but its variance estimates will remain uncertain.'),
            ('Efficiency options to evaluate prospectively.', 'Match distinct chains on prespecified demand paths/session characteristics if human evidence supports useful correlation. Use validated baseline covariates and reliable measurements. One-sided testing is an option only if justified before seeing outcomes. Reusing the same participants under both deadlines introduces learning/carryover and is a new crossover design, not a free sample-size reduction. More weeks are not more independent participants.'),
            ('How the supplied chapter informed this analysis.', 'Hyndman and Embrey (2018), section 2.2.3, PDF pages 5-8: plan power before collection and account for interacting clusters. Section 2.5, PDF pages 31-36: repeated observations, session effects, aggregation and few-cluster inference. The chapter provides methods, not human effect/variance estimates for these particular H1/H2 treatments.'),
            ('Supporting sources.', 'List, Sadoff and Wagner (2011), Experimental Economics, DOI 10.1007/s10683-011-9275-7. Cameron and Miller (2015), Journal of Human Resources, DOI 10.3368/jhr.50.2.317. statsmodels TTestIndPower documentation. Direct links and the uploaded chapter path are in the workbook Sources tab.'),
        ],'Status: conditional planning only. Final human sample and protocol have not been frozen.')
    plt.close(fig)
    check = load_workbook(REPORTS/'POWER_ANALYSIS.xlsx', read_only=True)
    assert len(check.sheetnames) == 11
    assert check['01 Recruitment scenarios'].max_row - 4 == len(sample_rows)
    check.close()
    assert hashlib.sha256(GPT.read_bytes()).hexdigest()==source_hash
    print(json.dumps(dict(output=str(REPORTS),summary=results,sample_rows=[r for r in sample_rows if r['weaker_effect_d'] in [.5,.8,1.]]),indent=2))


if __name__ == '__main__':
    main()
