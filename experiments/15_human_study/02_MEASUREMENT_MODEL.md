# 2. Measurement and mathematical model

**The key distinction:** game costs describe performance; cue-response coefficients describe ordering behavior. A high cost or bullwhip ratio does not itself identify pipeline-stock underweighting.

## A. What we will report

| Quantity | Meaning / reason to calculate it | Unit and level |
|---|---|---|
| κI | Order reduction for one extra usable unit on hand | Order units / stock unit; participant |
| κP | Order reduction for one extra usable outstanding unit | Same; participant |
| G = κI − κP | Pipeline receives less weight than equivalent on-hand stock when G > 0; primary Donohue-style response gap | Same; participant, then chain mean |
| Uabs = 1 − κP | Pipeline response shortfall versus the one-for-one task benchmark | Dimensionless; participant |
| w = κP / κI; Urel = 1 − w | Pipeline weight relative to inventory adjustment; separates cue weighting from adjustment speed when κI is identified | Dimensionless; supporting parameter |
| C | Sum of holding and backlog costs, all four roles, all scored weeks | Experimental currency / chain |
| V | Mean of four participants' within-person weekly order variances | Units² / chain |
| BW | Mean order variance divided by variance of realized external demand | Dimensionless / chain |
| R | How much of the old rule's error remains after the H5 timing change | Dimensionless / participant |
| ΔG, ΔC and interactions | Randomized treatment differences in the above quantities | Same units as endpoint |
| RT, late rate, rushed rating | Whether the human time manipulation actually binds | Seconds, fraction, 1–7 rating |

Report **κI, κP and G together**. G = 0 can mean equal correct weights, equal partial responses, or ignoring both cues. A small G alone does not prove rational behavior. Changes in G need not imply changes in Urel if both adjustment gains change. Do not relabel G as a normalized structural weight.

## B. Physical Beer Game model

Indices: g = chain; r = role (1 retailer, 2 wholesaler, 3 distributor, 4 factory); t = scored week, 1,…,40. The following variables are in cases of product:

| Symbol | Exactly when / what it means |
|---|---|
| I(g,r,t−1), B(g,r,t−1) | Last week's end-of-week on-hand stock and unfilled customer backlog |
| A(g,r,t) | Physical replenishment received at the start of this week |
| D(g,r,t) | New incoming customer order this week; excludes old backlog |
| S(g,r,t) | Shipment dispatched to the downstream customer this week |
| X(g,r,t) | Net stock after receipts and customer fulfillment, before ordering; I − B |
| P⁻(g,r,t) | Own outstanding orders after current receipts, before the new order |
| q(g,r,t) | New order placed upstream this week |
| P⁺(g,r,t) | Outstanding orders after the new order is added |

At the start of a week, receive supply, observe new demand, fill outstanding customer demand, display the resulting state, and then choose q. The event sequence is identical in every arm.

\[
\begin{aligned}
W_{grt}&=I_{gr,t-1}+A_{grt},\\
L_{grt}&=B_{gr,t-1}+D_{grt},\\
S_{grt}&=\min(W_{grt},L_{grt}),\\
I_{grt}&=W_{grt}-S_{grt},\qquad B_{grt}=L_{grt}-S_{grt},\\
X_{grt}&=I_{grt}-B_{grt}=X_{gr,t-1}+A_{grt}-D_{grt}. \tag{1}
\end{aligned}
\]

Backlog already contains current unfilled demand after this update. Never add current demand a second time when computing an inventory position.

With one week of order transmission and two weeks of shipment transit:

\[
D_{g1t}=d_{gt},\quad D_{grt}=q_{g,r-1,t-1}\ (r>1),\quad
A_{grt}=S_{g,r+1,t-2}\ (r<4),\quad A_{g4t}=q_{g4,t-3}. \tag{2}
\]

Factory production is unlimited but delayed three weeks. Thus a factory order in week 7 arrives in week 10. A downstream order placed in week t reaches its supplier in t+1 and, if filled then, arrives in t+3; shortages can extend this lead time.

Maintain a purchase-order ledger, recording each order and each receipt:

\[
P^-_{grt}=P^+_{gr,t-1}-A_{grt},\qquad
P^+_{grt}=P^-_{grt}+q_{grt},\qquad IP^-_{grt}=X_{grt}+P^-_{grt}. \tag{3}
\]

P includes untransmitted orders, supplier-unfilled orders and dispatched shipments, once each; it excludes stock already received and the current not-yet-placed order. Do not add supplier backlog on top of this ledger: that counts the same commitment twice. Do not interpret P as merely the trucks currently in transit.

Initialization: I(g,r,0)=12; B(g,r,0)=0; P⁺(g,r,0)=12. For nonfactory roles this comprises two dispatched batches of four plus q(g,r,0)=4 awaiting supplier processing. Set required pregame shipments S(g,r,−1)=S(g,r,0)=4. For factory production set q(g,4,−2)=q(g,4,−1)=q(g,4,0)=4. All other required initial downstream q(g,r,0)=4. Save explicit queues as well as totals. Check nonnegative I/B/P, inventory conservation and exactly-once receipt of every unit in software before collection.

## C. Donohue's equation and the proposed adaptation

Croson and Donohue (2006), **equation (6), p. 329**, model nonnegative orders using previous inventory, received orders, incoming shipments, outstanding orders and time. In aligned notation:

\[
q_{it}=\max\{0,\alpha_{0i}+\alpha_{Ii}X_{i,t-1}
+\alpha_{Ri}D_{it}+\alpha_{Si}A_{it}+\alpha_{Ni}P^-_{it}
+\alpha_{ti}t+\varepsilon_{it}\}. \tag{4}
\]

Their comparison on **p. 330** is αN > αI: a less negative response to outstanding orders than to inventory. [Author-hosted paper](https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/%5B34%5D.pdf).

Equation (4) uses our explicit pre-order ledger and signed net-stock convention. It is an adaptation, not a copy of their pipeline indexing or a claim to reproduce their estimation algorithm. Under an interior, constant-target inventory-position rule:

\[
q^*_{it}=S^*_i-(X_{i,t-1}+A_{it}-D_{it}+P^-_{it}), \tag{5}
\]

so the benchmark coefficients are αI=αS=αN=−1 and αR=+1. This benchmark is conditional on that policy/setting; it is not proof that this rule is globally optimal for a finite-horizon decentralized Beer Game with uncertain supplier fulfillment.

One useful partial-adjustment representation is

\[
q^{latent}_{it}=a_i+\eta_i F_{it}-k_i X_{it}-k_i w_i P^-_{it}+\varepsilon_{it},\tag{6}
\]

where F is a specified demand forecast, k is inventory adjustment gain and w is relative pipeline weight. Then κI=k, κP=kw, G=k(1−w). **A pipeline slope alone identifies the product kw, not w.** If k is near zero, w cannot be reliably recovered. In the known-demand diagnostic below F is held fixed within a scenario; no fitted forecast is needed. In the game, the main descriptive regression uses equation (4); do not combine it with X(t) as an extra regressor because X(t)=X(t−1)+A(t)−D(t) creates exact collinearity.

For dynamic supporting estimates, pool subjects with participant intercepts and arm-specific cue coefficients, plus prespecified role and linear-time adjustments. If participant intercepts absorb fixed role differences, omit redundant role intercepts. A hierarchical random-slope version is a sensitivity model, not four dozen independent per-person regressions selected by fit. Allow on-hand and backlog response slopes to differ in a sensitivity specification. [Oliva, Abdulla and Gonçalves (2022)](https://pubsonline.informs.org/doi/abs/10.1287/msom.2021.1072) motivates checking backlog separately.

### Estimation at the nonnegative boundary

Integer orders can be modeled as a rounded latent normal, lower-censored at zero. For latent mean μ and error SD σ:

\[
\Pr(q=0)=\Phi((0.5-\mu)/\sigma),\quad
\Pr(q=k)=\Phi((k+0.5-\mu)/\sigma)-\Phi((k-0.5-\mu)/\sigma),\ k\ge1. \tag{7}
\]

Maximize the sum of log probabilities; estimate σ>0, but do not force slopes into a preferred sign or force w into [0,1]. If a real upper cap is imposed, replace its top-cell probability with the corresponding upper tail. A quasi-likelihood/fixed-effects fit with chain-level resampling remains descriptive unless conditional-error assumptions hold. Lagged state variables are endogenous to previous decisions, cue values can be highly collinear, and targets/expectations may change. Check rank, condition number, fitted zeros, residual serial correlation and held-out-week prediction. Cluster uncertainty at the randomized chain/block level. Forty observations per participant do not justify an unconstrained individual seven-parameter model with reliable individual ratios.

## D. Identify inventory and pipeline responses with controlled data

**Primary measurement task: 32 decisions per participant after the game.** Each is a one-period stock-allocation problem, with a known demand D, no order charge, holding charge h=0.50 and shortage charge b=1.00 at one scoring point. New orders and the displayed outstanding replenishment both arrive before that point with certainty. No intervening demand, spoilage or extra holding charge occurs before the scoring point. Therefore on-hand and pipeline stock are economically interchangeable here.

\[
\ell(q;I,P,D)=h\max(I+P+q-D,0)+b\max(D-I-P-q,0),
\quad q^*=\max(0,D-I-P). \tag{8}
\]

Use eight scenario frames j, each containing the independently crossed four cells I∈{2,6}, P∈{2,6}. D is 16,20,24 or28, each in two frames. That is 8×4=32 decisions, randomized separately for each participant. Present only one state at a time; do not announce which observations are paired. The optimal order is at least four in every cell, reducing benchmark floor confounding. This does not force human choices to be positive.

Fit the prespecified additive model per person:

\[
q_{ij}=a_{i,frame(j)}+b_{Ii}(I_j-4)+b_{Pi}(P_j-4)+e_{ij}. \tag{9}
\]

Both cues are randomized independently within frames, which prevents the pipeline/inventory collinearity of ordinary game histories. The coefficients describe responses in this diagnostic task. They are not automatically the person's parameters during the dynamic game. Verify convergence with the game regression rather than assuming transfer.

For a complete balanced task the slopes are also exact factorial contrasts. Write q(j,I,P) for a literal observed order, J=8 and ΔI=ΔP=4:

\[
\hat b_{Ii}=\frac{1}{2J\Delta I}\sum_{j=1}^J
\{q(j,6,2)-q(j,2,2)+q(j,6,6)-q(j,2,6)\}, \tag{10}
\]

\[
\hat b_{Pi}=\frac{1}{2J\Delta P}\sum_{j=1}^J
\{q(j,2,6)-q(j,2,2)+q(j,6,6)-q(j,6,2)\}. \tag{11}
\]

Then calculate

\[
\hat\kappa_{Ii}=-\hat b_{Ii},\quad
\hat\kappa_{Pi}=-\hat b_{Pi},\quad
\hat G_i=\hat b_{Pi}-\hat b_{Ii},\quad
\hat U^{abs}_i=1+\hat b_{Pi}. \tag{12}
\]

G>0 means the participant's order responds less to pipeline than to equivalent inventory. Report the two slopes even if unexpected. Zero orders are retained. The primary OLS/factorial quantity is an **observed response gap**, including actual boundary behavior. Equation (7) gives a secondary latent-slope sensitivity analysis; do not select the model yielding the desired sign.

For normalized relative weighting,

\[
\hat w_i=\hat b_{Pi}/\hat b_{Ii},\qquad \hat U^{rel}_i=1-\hat w_i. \tag{13}
\]

Do not divide by a replacement epsilon, clip weights, or silently discard inconvenient ratios. Report normalized weights at the arm level as a ratio of estimated mean slopes, with a Fieller or chain-bootstrap interval. If the inventory-response denominator interval includes zero, label the ratio weakly identified/unbounded. A ratio of means and the mean of individual ratios are different estimands; the former is the planned supporting summary. G stays defined even if the ratio does not.

With slope covariance matrix Σ for (bI,bP), uncertainty propagates as

\[
\operatorname{Var}(\hat G)=\Sigma_{II}+\Sigma_{PP}-2\Sigma_{IP},\quad
\nabla w=(-b_P/b_I^2,\ 1/b_I),\quad
\operatorname{Var}(\hat w)\approx\nabla w^T\Sigma\nabla w. \tag{14}
\]

The last approximation is unsuitable near a zero denominator. In the balanced independent-error diagnostic, X′X gives Var(bI)=Var(bP)=σe²/128 and Cov(bI,bP)=0, so measurement-error Var(G)=σe²/64. Serial dependence or heterogeneous errors require the full covariance. Estimate reliability in the human pilot: the power SD of observed G includes **true between-person heterogeneity plus estimation error**, not just a regression residual SD.

### Worked example

Within a frame, observed orders at (I,P)=(2,2),(6,2),(2,6),(6,6) are 20,17,19,16. Equations (10)–(12) give bI=−0.75, bP=−0.25, G=0.50. Relative weight w=1/3; Urel=2/3. This is illustrative arithmetic, **not an AI or human finding**.

Two necessary checks: q=D−I−P gives κI=κP=1 and G=0; q=(D−I−P)/2 gives κI=κP=0.5 and G=0 despite incomplete adjustment. This is why G, absolute response and the ratio must be distinguished.

### Missingness and measurement validity

The reference calculator requires all 32 valid human responses. It deliberately does not fill missing cells or estimate G from arbitrarily selected pairs. Record missingness by treatment. A final human protocol must prespecify bounds/model-based sensitivity for differential nonresponse; otherwise report the complete-task estimand and its selection limitation. If zero choices, misunderstood rules or failed timing manipulation dominate the pilot, revise the instrument before the main sample. Do not repair main responses or select a different endpoint afterward.

## E. Performance outcomes from the game

From end-of-week states, with T=40:

\[
C_g=\sum_{r=1}^4\sum_{t=1}^{T}(0.50 I_{grt}+1.00 B_{grt}),\quad
C^H_g=0.50\sum I_{grt},\quad C^B_g=\sum B_{grt}. \tag{15}
\]

This is a direct stock/backlog accounting adaptation of Croson and Donohue's **equation (4), p. 326**, not inferred from the order vector alone. Include costs caused by explicitly elected standing orders; tag their source. Exclude unscored practice and do not append an invented automatic tail. Save terminal inventory, backlog and outstanding orders to expose horizon effects.

For each role, calculate variance across that same participant's forty implemented orders:

\[
\bar q_{gr}=T^{-1}\sum_tq_{grt},\quad
v_{gr}=\frac{\sum_t(q_{grt}-\bar q_{gr})^2}{T-1},\quad
V_g=\tfrac14\sum_r v_{gr}. \tag{16}
\]

Do not compute variance after pooling different roles' levels. For realized external demand:

\[
s^2_{d,g}=\frac{\sum_t(d_{gt}-\bar d_g)^2}{T-1},\quad
BW_{gr}=v_{gr}/s^2_{d,g},\quad BW_g=\tfrac14\sum_r BW_{gr}=V_g/s^2_{d,g}. \tag{17}
\]

Use the empirical variance of the actual demand path, not the theoretical Uniform{0,…,8} variance 20/3. If the empirical denominator is zero, BW is undefined; retain that record and report why. Because the denominator is common within a chain, V and BW are closely related. Report role profiles and upstream/downstream adjacent ratios as secondary plots, with any zero denominator explicit. Do not call those alternative ratios the primary BW.

## F. H5: persistence after a rule becomes inappropriate

This is a **separate educated human cohort**, randomized to time pressure only after common-time routine acquisition. Let I be on-hand stock, PE an early pipeline shipment, PL a labeled shipment, and D=48. In acquisition, both shipments arrive before the task's one demand/scoring point:

\[
q^{old}=48-I-P_E-P_L. \tag{18}
\]

Use I∈{4,12}, PE∈{4,12}, PL∈{8,16}; cross all eight cells four times for 32 acquisition trials. In transfer the labeled PL shipment arrives after the final scoring point; it has no salvage, holding or demand consequence inside that task. New orders still arrive before scoring. Thus

\[
q^{new}=48-I-P_E,\qquad q^{new}-q^{old}=P_L>0. \tag{19}
\]

The measured persistence on a transfer trial is

\[
R_{ij}=\frac{q^{new}_j-q^{observed}_{ij}}{q^{new}_j-q^{old}_j}
=\frac{48-I_j-P_{Ej}-q_{ij}}{P_{Lj}},\qquad
\bar R_i=\tfrac18\sum_{j=1}^{8}R_{ij}. \tag{20}
\]

R=1 means the old benchmark is repeated; R=0 means complete adjustment to the new benchmark. Values outside [0,1] are retained. Example: I=4, PE=8, PL=8; old order=28, new order=36. An observed 28 gives R=1; 32 gives R=0.5; 36 gives R=0. This off-grid example only explains the arithmetic; actual task states are in `materials/`.

The primary H5 contrast is E(R̄ | pressure) − E(R̄ | adequate) among the prospectively defined routine adopters. Report the fraction of transfer decisions closer to qold than qnew as a secondary descriptive quantity, with midpoint ties separate. A positive R is **consistent with** persistence; a wrong demand calculation can also create it. Establish acquisition first and inspect cue coefficients and post-task explanations instead of claiming direct access to a cognitive routine.

Fit the following supporting model before and after the change:

\[
q_{ij}=a_i+b_{I,i}I_j+b_{E,i}P_{Ej}+b_{L,i}P_{Lj}+e_{ij}. \tag{21}
\]

Old benchmark bI=bE=bL=−1; new benchmark bI=bE=−1, bL=0. Continuing to give PL weight −1 after the change is obsolete-rule persistence. **Correctly setting its weight to zero is not pipeline underweighting.** H5 must distinguish the applicable normative weight from the observed weight. Pre/post changes in the ordinary Beer Game's total-pipeline coefficient cannot make this distinction on their own.

Routine adopters are identified before time randomization, using the criterion in document 1. Do not exclude transfer failures or reclassify adopters using post-randomization performance. This design tests persistence in trained adopters, not an education-versus-control effect; H6 supplies that separate comparison.

## G. H6: direct moderation equations

Let μze(Y) be the mean chain outcome with z=pressure and e=education; for the response gap use the chain average of the four G estimates. Define

\[
\Delta_E^{adequate}(Y)=\mu_{01}(Y)-\mu_{00}(Y),\quad
\Delta_E^{pressure}(Y)=\mu_{11}(Y)-\mu_{10}(Y),\\
\Delta_{int}(Y)=[\mu_{11}(Y)-\mu_{10}(Y)]-[\mu_{01}(Y)-\mu_{00}(Y)]. \tag{22}
\]

H6a tests Δint(G)=0; H6b tests Δint(C)=0. Equivalently, the interaction is τPE in

\[
Y_g=\beta_0+\tau_P z_g+\tau_E e_g+\tau_{PE}z_ge_g+\text{block effects}+u_g. \tag{23}
\]

At the cue-coefficient level,

\[
\Delta_{int}(G)=
[(b_{P,11}-b_{I,11})-(b_{P,10}-b_{I,10})]
-[(b_{P,01}-b_{I,01})-(b_{P,00}-b_{I,00})]. \tag{24}
\]

This is the explicit link from experimental order data to the pipeline-underweighting moderation test. It requires both manipulated inventory cues and all four time/education cells. A significant education effect in one time arm and a nonsignificant effect in the other **does not test their difference**.

## H. From people to statistical units

In block b, calculate Gbg = (G1+G2+G3+G4)/4 for each chain, and C,V,BW from its full game. Then calculate one contrast Lb per hypothesis, using the coefficients in document 1:

\[
\hat\Delta=k^{-1}\sum_bL_b,\quad
s_L^2=\frac{\sum_b(L_b-\hat\Delta)^2}{k-1},\quad
SE(\hat\Delta)=s_L/\sqrt{k}. \tag{25}
\]

The working t statistic has k−1 degrees of freedom; confidence intervals use the same independent block unit. If re-estimating ratios or dynamic models, resample whole blocks and refit, retaining all roles/weeks together. Individual G values can be plotted, but 40 people in ten chains do not equal forty independent randomized treatment assignments.

The eight-test Holm algorithm orders raw p-values p(1)≤…≤p(8) and sets

\[
p^{adj}_{(j)}=\min\{1,\max_{\ell\le j}(8-\ell+1)p_{(\ell)}\}. \tag{26}
\]

Report unadjusted 95% estimation intervals as such; they are not simultaneous familywise intervals. Use α/8 intervals if simultaneous conservative intervals are desired. Do not interpret unavailable coefficients or missing task responses as zero effects.
