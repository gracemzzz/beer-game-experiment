# Human Beer Game study

## 1. Model and hypotheses

Each student controls one stage of a four-person supply chain. They choose a weekly order after seeing inventory, backlog, incoming demand and outstanding replenishments. The behavioral model, adapted from Croson and Donohue (2006, equation 6), is:

\[
q^*_{it}=a_i+\beta_I X_{i,t-1}+\beta_D D_{it}+\beta_A A_{it}+\beta_P P_{it}+\beta_t t+\varepsilon_{it}
\\
q_{it}=\max(0,q^*_{it})
\]

| Symbol | Meaning |
|---|---|
| q; q* | Observed order; latent desired order before the zero floor |
| X | Previous ending inventory minus customer backlog |
| D; A | New demand; replenishment received this week |
| P | Own orders still outstanding after receipts, before placing q |
| a; t; ε | Participant intercept; week; unexplained variation |

**Interpretation.** Inventory and pipeline coefficients should normally be negative: more stock means less need to order. If the pipeline coefficient is less negative than the inventory coefficient, the participant responds less to outstanding orders. Both coefficients must be estimated; a small pipeline response alone can also reflect generally slow adjustment.

### Hypotheses

All conditions provide the same shared operational information.

- **H1:** Binding decision time increases pipeline-stock underweighting compared with adequate time.
- **H2:** Binding decision time increases total chain holding and backlog costs.
- **H3:** Under binding time, causal education reduces pipeline-stock underweighting compared with a matched control lecture.
- **H4:** Under binding time, education reduces (a) individual order variation and (b) the bullwhip ratio.
- **H5:** After education, binding time increases persistence with an adopted ordering rule when changed conditions make it less appropriate.
- **H6:** Decision time moderates education's effects on replenishment decisions and chain costs.

*Source: Croson & Donohue, Management Science 52(3), 323–336. [doi:10.1287/mnsc.1050.0436](https://doi.org/10.1287/mnsc.1050.0436). H5/H6 follow the project's saved reflection.*

## 2. Measurements and regression

### Estimate stock weighting

**Primary regression:** use 32 randomized stock decisions per person: eight frames crossing I = 2 or 6 and P = 2 or 6. Demand is known; both types of stock arrive before scoring. Fit ordinary least squares with a frame intercept:

\[
q_{ij}=a_{i,frame(j)}+b_{Ii}(I_j-4)+b_{Pi}(P_j-4)+e_{ij}
\\
\kappa_{Ii}=-b_{Ii},\qquad\kappa_{Pi}=-b_{Pi},\qquad G_i=\kappa_{Ii}-\kappa_{Pi}
\]

**G > 0 means less response to pipeline than to equivalent inventory.** Responses of 0.75 and 0.25 give G = 0.50. Also report w = κP/κI when κI is reliably nonzero. G measures a gap; w measures relative weight. Equal responses can still both be too small.

**Game regression:** fit the page-1 model by maximum likelihood for zero-censored, rounded orders, with participant intercepts and treatment-specific slopes. Compare it with the stock-task estimates; changing game states make its coefficients harder to interpret causally.

### Outcomes and hypothesis tests

| Quantity | Calculation and purpose |
|---|---|
| Underweighting G | Inventory response minus pipeline response; H1/H3/H6 |
| Chain cost C | Sum 0.50 × ending inventory + 1.00 × backlog over all four roles and 40 weeks; H2/H6 |
| Order variation V | Calculate each person's sample variance across 40 weekly orders (denominator 39), then average the four variances; H4a |
| Bullwhip BW | V divided by the variance of that chain's actual retail demand; H4b |

For H6, regress each chain outcome Y (mean G or total C) on pressure z, education e, their interaction and randomization-block effects:

\[
Y_g=c+\tau_P z_g+\tau_E e_g+\tau_{PE}z_ge_g+\text{block effects}+u_g
\]

τPE is **(education − control under pressure) − (education − control with adequate time)**. H1/H2 compare B − A; H3/H4 compare C − B. Base uncertainty on independent block contrasts, not weeks or roles. Report estimates, intervals and Holm-adjusted p-values for eight endpoints.

### H5 needs a changed-rule measure

After routine acquisition, change the late shipment PL to arrive after scoring; PE still arrives in time:

\[
q^{old}=D-I-P_E-P_L,\quad q^{new}=D-I-P_E,\quad R=\frac{q^{new}-q^{observed}}{P_L}
\]

R = 1 repeats the old rule; R = 0 adapts. Compare first-eight-trial mean R between time conditions. Correctly ignoring a too-late shipment is adaptation, not underweighting.

## 3. Experiment design

| Decision time | Control lecture | Causal education |
|---|---|---|
| Adequate | A | D |
| Binding | B | C |

1. **Pilot:** use 16 students to calibrate binding and adequate deadlines, check task understanding and obtain preliminary human variability estimates. Keep pilot data separate; enlarge the estimation pilot if variability remains uncertain.
2. **Main game:** assign four-person chains to the four conditions in randomized blocks. Give matched 20-minute lectures, four practice weeks and 40 scored weeks. Hold information, demand sequences within blocks, game delays and state-release intervals constant.
3. **Measurement:** administer the 32 stock decisions after the game under assigned timing. Record every state, order, timestamp and response source. Missing choices remain missing; distinguish any human-selected standing action from a fresh response.
4. **H5 task:** use new educated participants. Give 32 acquisition trials under common adequate time. Require six of the final eight choices within one unit of the old benchmark before time randomization. Then change arrival timing and collect 16 transfer trials; the first eight are primary. This tests routine adopters in a separate task, not the full chain.

### Sample size

Let k be chains per condition: the four-condition game needs **4k chains and 16k people**. For the observed participant gap, let σG be its SD, including measurement error, and ρ the within-chain correlation. Let Δ be the smallest meaningful treatment difference:

\[
v=\frac{\sigma_G^2(1+3\rho)}{4},\qquad
k\approx\frac{V_L(z_{1-\alpha^*/2}+z_{1-\beta})^2}{\Delta^2}
\]

With equal cell variances and no cross-arm covariance, use VL = 2v for a simple contrast and 4v for H6; for chain costs, use the chain-level variance directly. Plan at 80% power and α* = 0.05/8. These examples use the notebook's finite-sample t calculation, ICC = 0.10 and d = Δ/σG:

| Assumed d | Simple: chains/condition | H6: chains/condition |
|---|---|---|
| 0.50 | 38 (608 people total) | 71 (1,136 people total) |
| 0.80 | 17 (272 people total) | 30 (480 people total) |

H5 instead uses individual adopters: n ≈ 2σR² Z²/ΔR² per time arm, using the same sum of z-values Z as above. At dR = 0.50, the t calculation gives 105 per arm, before screening/attrition inflation. These are assumed-effect scenarios, not estimates from AI or human data.

**Before recruitment:** finalize human deadlines, meaningful effects, sample size, lecture scripts and missing-data rules; obtain institutional approval. Freeze the plan before main outcomes are observed. The full calculations and technical notes remain in the accompanying notebook and numbered documents.
