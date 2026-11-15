"""Offline human-study planning. No human data, API calls or participant launches.

All generated responses are explicitly synthetic arithmetic checks. See experiment
15's numbered documents for the estimands and the unfinalized design decisions.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd
from scipy import integrate, optimize, stats

ROOT = Path(__file__).resolve().parents[1]
STUDY = ROOT / "experiments" / "15_human_study"
ALPHA = 0.05 / 8


def _two_sided_t_power(df: int, ncp: float, alpha: float) -> float:
    critical = stats.t.isf(alpha / 2, df)
    value = float(stats.nct.sf(critical, df, ncp)
                  + stats.nct.cdf(-critical, df, ncp))
    if np.isfinite(value) and 0 <= value <= 1:
        return value
    # SciPy 1.15 may return NaN for tiny noncentral-t opposite tails. Compute
    # the same probability conditional on V~chi-square(df), T=(Z+ncp)/sqrt(V/df).
    # Integrating over its quantile avoids missing the mass at large df.
    def conditional_probability(u):
        scale = critical * np.sqrt(stats.chi2.ppf(u, df)/df)
        return stats.norm.cdf(ncp-scale) + stats.norm.cdf(-ncp-scale)
    value, error = integrate.quad(conditional_probability, 0, 1,
                                  epsabs=1e-10, epsrel=1e-9, limit=150)
    if not np.isfinite(value) or error > 1e-6:
        raise ArithmeticError("Noncentral-t probability failed numerical check")
    return float(value)


def contrast_power(k: int, effect: float, contrast_variance: float,
                   alpha: float = ALPHA) -> float:
    """One-sample t on k independent Gaussian block contrasts; exact under model."""
    if k < 2 or contrast_variance <= 0 or not 0 < alpha < 1:
        raise ValueError("Need k >= 2, positive variance and 0 < alpha < 1")
    df = k - 1
    ncp = abs(effect) * np.sqrt(k / contrast_variance)
    return _two_sided_t_power(df, ncp, alpha)


def h5_power(n: int, standardized_effect: float, alpha: float = ALPHA) -> float:
    """Two independent equal-size human groups, n per arm; equal normal variance."""
    if n < 2 or not 0 < alpha < 1:
        raise ValueError("Need n >= 2 and 0 < alpha < 1")
    df = 2 * n - 2
    ncp = abs(standardized_effect) * np.sqrt(n / 2)
    return _two_sided_t_power(df, ncp, alpha)


def required_size(power_function, target: float = 0.8) -> int:
    if not 0 < target < 1:
        raise ValueError("Target must be between zero and one")
    low, high = 2, 4
    while power_function(high) < target:
        high *= 2
        if high > 1_000_000:
            raise ValueError("No finite feasible sample in search range; check effect")
    while low < high:
        mid = (low + high) // 2
        if power_function(mid) >= target:
            high = mid
        else:
            low = mid + 1
    return low


def stock_states() -> pd.DataFrame:
    rows = []
    for frame, demand in enumerate([16, 20, 24, 28] * 2, 1):
        for inventory, pipeline in itertools.product([2, 6], repeat=2):
            rows.append(dict(task="stock_weight", frame=frame,
                             inventory=inventory, pipeline=pipeline, demand=demand,
                             state_id=f"s{frame:02d}_i{inventory}_p{pipeline}",
                             benchmark_order=demand-inventory-pipeline))
    return pd.DataFrame(rows)


def estimate_stock_weights(records: pd.DataFrame) -> dict:
    """One person's complete literal 32-response task. No imputation/ratio clipping."""
    expected = stock_states()
    keys = ["frame", "inventory", "pipeline", "demand"]
    required = keys + ["order"]
    if any(c not in records for c in required):
        raise ValueError("Missing required task columns")
    if len(records) != 32 or records.duplicated(keys).any():
        raise ValueError("Exactly 32 unique responses are required")
    x = records[required].merge(expected[keys], on=keys, how="inner",
                                validate="one_to_one")
    if len(x) != 32 or not np.isfinite(x[required].to_numpy()).all():
        raise ValueError("Incomplete/nonfinite/off-design responses")
    y = x["order"].to_numpy(float)
    if (y < 0).any() or not np.equal(y, np.floor(y)).all():
        raise ValueError("Responses must be nonnegative literal integers")
    frame_columns = pd.get_dummies(x["frame"], dtype=float).to_numpy()
    design = np.column_stack([frame_columns,
                              x["inventory"].to_numpy()-4,
                              x["pipeline"].to_numpy()-4])
    beta, _, rank, _ = np.linalg.lstsq(design, y, rcond=None)
    if rank != design.shape[1]:
        raise ValueError("Non-identifiable task design")
    residuals = y-design @ beta
    covariance = (residuals @ residuals / (len(y)-rank)
                  * np.linalg.inv(design.T @ design))[-2:, -2:]
    b_i, b_p = beta[-2:]
    # No denominator substitution. This raw ratio is not an inferential interval.
    ratio = None if abs(b_i) < 1e-12 else float(b_p / b_i)
    return dict(b_inventory=float(b_i), b_pipeline=float(b_p),
                k_inventory=float(-b_i), k_pipeline=float(-b_p),
                gap=float(b_p-b_i), absolute_pipeline_shortfall=float(1+b_p),
                relative_pipeline_weight_descriptive=ratio,
                relative_ratio_warning="Descriptive only; require Fieller/bootstrap interval at arm level",
                covariance_i_p=covariance.tolist(),
                gap_se_iid=float(np.sqrt(max(0, covariance[0, 0]+covariance[1, 1]
                                             -2*covariance[0, 1]))),
                n=32, rank=int(rank))


def week_end(inventory: int, backlog: int, arrivals: int, new_demand: int) -> dict:
    values = [inventory, backlog, arrivals, new_demand]
    if any(v < 0 or int(v) != v for v in values):
        raise ValueError("Stock flows must be nonnegative integers")
    ship = min(inventory+arrivals, backlog+new_demand)
    return dict(shipped=ship, inventory=inventory+arrivals-ship,
                backlog=backlog+new_demand-ship)


def chain_metrics(orders, inventory, backlog, external_demand) -> dict:
    q, inv, back, d = (np.asarray(x, dtype=float)
                       for x in (orders, inventory, backlog, external_demand))
    if q.ndim != 2 or q.shape[1] != 4 or q.shape[0] < 2:
        raise ValueError("Need T x 4 role arrays")
    if inv.shape != q.shape or back.shape != q.shape or d.shape != (len(q),):
        raise ValueError("Orders/states/demand dimensions do not match")
    if not all(np.isfinite(a).all() and (a >= 0).all() for a in (q, inv, back, d)):
        raise ValueError("Missing, negative or nonfinite game values")
    if ((inv > 0) & (back > 0)).any():
        raise ValueError("Positive ending stock and backlog cannot coexist")
    role_var = q.var(axis=0, ddof=1)
    demand_var = float(d.var(ddof=1))
    variance = float(role_var.mean())
    return dict(holding_cost=float(.5*inv.sum()), backlog_cost=float(back.sum()),
                total_cost=float(.5*inv.sum()+back.sum()),
                role_order_variances=role_var.tolist(), mean_order_variance=variance,
                demand_variance=demand_var,
                bullwhip_ratio=None if demand_var == 0 else variance/demand_var)


def routine_states() -> pd.DataFrame:
    rows = []
    for phase, repeats in [("acquisition", 4), ("transfer", 2)]:
        for block in range(1, repeats+1):
            for i, early, late in itertools.product([4, 12], [4, 12], [8, 16]):
                old, new = 48-i-early-late, 48-i-early
                rows.append(dict(task="h5_routine", phase=phase, block=block,
                                 inventory=i, early_pipeline=early, late_pipeline=late,
                                 demand=48, old_benchmark=old, new_benchmark=new,
                                 correct_benchmark=old if phase == "acquisition" else new,
                                 primary_transfer=phase == "transfer" and block == 1))
    return pd.DataFrame(rows)


def routine_persistence(order, inventory, early_pipeline, late_pipeline, demand=48):
    if late_pipeline <= 0 or order < 0:
        raise ValueError("Need a positive late shipment and nonnegative order")
    return (demand-inventory-early_pipeline-order)/late_pipeline


def write_outputs(study: Path = STUDY) -> None:
    analysis, materials = study / "analysis", study / "materials"
    analysis.mkdir(parents=True, exist_ok=True)
    materials.mkdir(parents=True, exist_ok=True)
    stock_states().to_csv(materials / "stock_task_states.csv", index=False)
    routine_states().to_csv(materials / "h5_task_states.csv", index=False)

    sample_rows = []
    for target in [.8, .9]:
        for level, icc in [("participant_G", r) for r in [0, .1, .3]] + [("chain_outcome", None)]:
            cluster_factor = (1+3*icc)/4 if icc is not None else 1.
            for d in [.3, .5, .8]:
                for contrast, w2 in [("simple", 2), ("interaction_H6", 4)]:
                    v = w2*cluster_factor
                    n = required_size(lambda k: contrast_power(k, d, v), target)
                    sample_rows.append(dict(endpoint_scale=level, assumed_icc=icc,
                                            assumed_standardized_effect=d, target_power=target,
                                            contrast=contrast, alpha=ALPHA,
                                            chains_per_cell=n, total_chains=4*n,
                                            total_people=16*n, achieved_power=contrast_power(n, d, v),
                                            randomized_people_per_h5_arm=None))
        for d in [.3, .5, .8]:
            n = required_size(lambda n: h5_power(n, d), target)
            sample_rows.append(dict(endpoint_scale="person_H5_persistence", assumed_icc=None,
                                    assumed_standardized_effect=d, target_power=target,
                                    contrast="H5", alpha=ALPHA, chains_per_cell=None,
                                    total_chains=None, total_people=2*n,
                                    achieved_power=h5_power(n, d), randomized_people_per_h5_arm=n))
    pd.DataFrame(sample_rows).to_csv(analysis / "sample_sizes.csv", index=False)

    curves = []
    for kind, cluster_factor in [("participant_G", 1.3/4), ("chain_outcome", 1.)]:
        for d in [.3, .5, .8]:
            for k in range(2, 241):
                for contrast, w2 in [("simple", 2), ("interaction_H6", 4)]:
                    curves.append(dict(endpoint_scale=kind, assumed_standardized_effect=d,
                                       contrast=contrast, chains_per_cell=k, total_people=16*k,
                                       alpha=ALPHA, power=contrast_power(k, d, w2*cluster_factor)))
    curve_df = pd.DataFrame(curves)
    curve_df.to_csv(analysis / "power_curves.csv", index=False)

    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    plt.rcParams.update({"font.size": 11, "axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(1, 2, figsize=(11.5, 4.4), sharey=True)
    for ax, kind, title in zip(axes, ["participant_G", "chain_outcome"],
                              ["Underweighting gap\nIndividual d = 0.5; ICC = 0.10",
                               "Chain performance\nChain-level d = 0.5"]):
        subset = curve_df[(curve_df.endpoint_scale == kind)
                          & (curve_df.assumed_standardized_effect == .5)]
        for contrast, label, color in [("simple", "Simple contrast", "#1f77b4"),
                                       ("interaction_H6", "H6 interaction", "#d46219")]:
            s = subset[subset.contrast == contrast]
            ax.plot(s.chains_per_cell, s.power, color=color, label=label, lw=2.2)
        ax.axhline(.8, color="#777777", ls="--", lw=1)
        ax.axvline(10, color="#aaaaaa", ls=":", lw=1)
        ax.set(title=title, xlabel="Chains per condition (4 conditions)", ylim=(0, 1.03), xlim=(2, 240))
        ax.set_yticks([0, .2, .4, .6, .8, 1.])
        ax.grid(axis="y", alpha=.15)
    axes[0].set_ylabel("Power")
    axes[0].legend(frameon=False, loc="lower right")
    fig.suptitle("Human-study planning — illustrative assumptions", fontsize=15)
    fig.text(.5, .01, "80% target; two-sided α = 0.05/8. Assumed variance, no human data. Total people = 16 × x.",
             ha="center", fontsize=9)
    fig.tight_layout(rect=(0, .04, 1, .94))
    for ext in ["png", "pdf", "svg"]:
        fig.savefig(analysis / f"POWER_VS_CHAINS.{ext}", dpi=200)
    plt.close(fig)

    examples = {}
    for name, func in [
        ("fully_counts_both", lambda df: df.demand-df.inventory-df.pipeline),
        ("ignores_pipeline", lambda df: df.demand-df.inventory),
        ("partial_both_equal", lambda df: (df.demand-df.inventory-df.pipeline)/2),
        ("worked_gap_050", lambda df: 22-.75*df.inventory-.25*df.pipeline),
    ]:
        frame = stock_states()
        frame["order"] = func(frame)
        examples[name] = estimate_stock_weights(frame)
    h5 = routine_states().query("phase == 'transfer' and block == 1")
    examples["h5_old_rule_mean_persistence"] = float(np.mean([
        routine_persistence(row.old_benchmark, row.inventory, row.early_pipeline, row.late_pipeline)
        for row in h5.itertuples()]))
    examples["h5_adapted_mean_persistence"] = float(np.mean([
        routine_persistence(row.new_benchmark, row.inventory, row.early_pipeline, row.late_pipeline)
        for row in h5.itertuples()]))
    examples["data_kind"] = "synthetic arithmetic only; zero human participants"
    (analysis / "measurement_examples.json").write_text(json.dumps(examples, indent=2), encoding="utf-8")

    # Independent Monte Carlo check of the t-power calculation; no behavioral simulation.
    rng = np.random.default_rng(20261114)
    simulations, k, d, v = 30000, 38, .5, .65
    contrast = rng.normal(d, np.sqrt(v), size=(simulations, k))
    t_stats = contrast.mean(axis=1) / (contrast.std(axis=1, ddof=1)/np.sqrt(k))
    rejected = np.abs(t_stats) > stats.t.isf(ALPHA/2, k-1)
    mc_power = float(rejected.mean())
    analytic = contrast_power(k, d, v)
    validation = dict(data_kind="Gaussian power verification, not participant data",
                      simulations=simulations, seed=20261114, k=k, assumed_d=d,
                      assumed_contrast_variance=v, analytic_power=analytic,
                      monte_carlo_power=mc_power,
                      monte_carlo_se=float(np.sqrt(mc_power*(1-mc_power)/simulations)),
                      agreement_within_4_mc_se=bool(abs(mc_power-analytic)
                          < 4*np.sqrt(analytic*(1-analytic)/simulations)),
                      code_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
                      human_records=0)
    (analysis / "CALCULATION_VALIDATION.json").write_text(json.dumps(validation, indent=2), encoding="utf-8")
    chosen = pd.DataFrame(sample_rows)
    print(chosen[(chosen.endpoint_scale == "participant_G") & (chosen.assumed_icc == .1)
                 & (chosen.target_power == .8)][["assumed_standardized_effect", "contrast",
                                                 "chains_per_cell", "total_people"]].to_string(index=False))
    print(json.dumps(validation, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=STUDY)
    args = parser.parse_args()
    write_outputs(args.output)
