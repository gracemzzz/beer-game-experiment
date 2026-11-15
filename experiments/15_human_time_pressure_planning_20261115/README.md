# Human H1/H2 study — prospective power planning

1. **A final human recruitment target cannot yet be identified:** human outcome variability, meaningful effects and the H1 measurement choice are missing. The saved calculations are conditional scenarios, not predictions fitted to GPT responses.
2. **Four people form one chain.** Under the independent-chain planning model, 80 people give only 10 chains per condition.
3. **For at least 80% power to detect both endpoints under the model:** a weaker chain-level effect of d = 0.8 requires 328 completed people; d = 0.5 requires 808. These correspond to 90% power per endpoint using conservative two-sided alpha .025. Holm controls the two-test family at .05.
4. The human study is **not collected or frozen**. No participant/model/API calls were made; Experiment 14's records remain unchanged.

| Open | Contents |
|---|---|
| [H1-only workbook and worked example](reports/H1_ONLY_POWER.xlsx) | Sole-primary H1 scenario: two-sided alpha .05, 80%/90% power, recruitment counts and step-by-step calculation; human effects/variances still unknown |
| [Power report](reports/POWER_ANALYSIS.pdf) | Conclusions, power curves, outcome definitions, methods, missing inputs and chapter references |
| [Power workbook](reports/POWER_ANALYSIS.xlsx) | Recruitment scenarios, the original 80-person plan, H1/H2 sensitivity grids, matching/ICC alternatives, simulations and missing inputs |
| [Power curves](reports/figures/POWER_CURVES.png) | Power for one endpoint versus completed participants, with chain counts and explicit effect-size assumptions |
| [Planning assumptions](hypotheses/POWER_ASSUMPTIONS.json) | Two independent conditions, four-person chains, conditional 24-week game; H1 method and human deadlines pending |
| [Numerical tables](analysis/tables/) | Exact CSV outputs, including synthetic simulation results explicitly separated from observations |
| [Validation](analysis/VALIDATION.json) | Integer sample-size checks, statsmodels comparison and Monte Carlo checks |
| [Source receipt](data/SOURCE_MANIFEST.json) | User-supplied chapter location/hash and the separately labelled GPT reference |

H1 is **Tight deadlines increase pipeline underweighting**. The default illustration uses the previous paired-probe response proxy, which is not a normative underweighting score. If the human endpoint instead estimates a weighting coefficient from weekly orders, specify the model and rerun a model-specific power simulation.

H2 is **Tight deadlines increase total holding and backlog costs**. The conditional example sums 0.5 × inventory + 1 × backlog over four roles and 24 weeks. No education treatment is included; information sharing and reading are held fixed.

The supplied Hyndman and Embrey chapter informs prospective power and dependence assumptions (PDF pages 5–8 and 31–36). It supplies no human effect size for these particular treatments. Actual human deadlines need calibration; 8/120-second fictional LLM framing is not evidence of binding/adequate human time.

## Reproduce offline

For the additional H1-only scenario, run `python scripts/power_human_h1_only.py`. It preserves the previous joint analysis, checks each minimum integer chain count and saves separate assumptions in `hypotheses/H1_ONLY_POWER_ASSUMPTIONS.json`. At 80% H1 power, d=.5 requires 512 completed people and d=.8 requires 208; these are conditional examples, not selected human effect estimates. The worked example explains why 64 chains per condition means 512 people.

From the repository root:

```bash
python scripts/power_human_h1_h2.py
```

Requires NumPy, SciPy, statsmodels, matplotlib and openpyxl. The script reads the supplied chapter for its source hash and the existing chain CSV only for a clearly labelled GPT reference. Human scenarios use specified effect sizes, not the GPT estimates. It generates 21 synthetic normal-chain scenarios with 30,000 repetitions each, checks them against analytical power, checks minimum integer sample sizes, and confirms the original GPT CSV is unchanged.

All participant counts exclude pilot participants and are conditional on completed usable chains. The optional 10% whole-chain loss allowance targets the expected retained count; it is neither an individual-dropout correction nor a guarantee of reaching the target.

[Experiment index](../README.md)
