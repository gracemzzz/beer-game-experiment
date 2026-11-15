# 5. Literature and source mapping

Sources checked on **14 November 2026**. Equations below distinguish published measurement precedents from our new design choices. This is a focused methods review, not a systematic review. SciSpace was used for discovery; the claims below were checked against primary papers or publisher/institutional records.

## Karen Donohue's relevant work

| Primary source | Verified location / contribution | Use in this design |
|---|---|---|
| Croson, R. & Donohue, K. (2006). *Behavioral Causes of the Bullwhip Effect and the Observed Value of Inventory Information*. Management Science 52(3), 323–336. [DOI](https://doi.org/10.1287/mnsc.1050.0436), [author-hosted full paper](https://faculty.wharton.upenn.edu/wp-content/uploads/2012/04/%5B34%5D.pdf) | Eq. (4), p. 326: chain holding/backlog accounting. Eq. (6), p. 329: nonnegative ordering regression with inventory, orders received, receipts, outstanding orders and time. P. 330: compare outstanding-stock and inventory coefficients. | Our equation (4) adapts the regression to an explicit event-timed ledger. G compares the two negative slopes. Independent cue randomization strengthens measurement identification; it is our addition, not their original instrument. |
| Croson, R., Donohue, K., Katok, E. & Sterman, J. (2014). *Order Stability in Supply Chains: Coordination Risk and the Role of Coordination Stock*. Production and Operations Management 23(2), 176–196. [DOI](https://doi.org/10.1111/j.1937-5956.2012.01422.x), [MIT author-manuscript record](https://dspace.mit.edu/entities/publication/e5e3eb66-6a89-482f-9185-0019da02a003) | Experimental evidence that uncertainty about others' decisions contributes to order instability; coordination stock buffers its consequences. Bibliographic record and abstract verified; no unverified equation attributed to this paper. | Four independent human decision makers per chain. A model selecting all roles cannot establish the same coordination mechanism. |

The 2006 primary PDF is already preserved at `maintenance/shared_inputs/data/references/redesign_20261011/croson_donohue_2006.pdf` (repository root). Its recorded source is the author URL above. Do not rewrite or redistribute altered copies of the paper.

## Other measurement and design evidence

| Primary source | Relevant evidence and limitation |
|---|---|
| Sterman, J. (1989). *Modeling Managerial Behavior: Misperceptions of Feedback in a Dynamic Decision Making Experiment*. Management Science 35(3), 321–339. [Publisher](https://pubsonline.informs.org/doi/abs/10.1287/mnsc.35.3.321?journalCode=mnsc) | Anchoring/adjustment motivates distinguishing adjustment gain from pipeline weight. Our k,w decomposition is an explicit algebraic parameterization; the simple one-period benchmark is our experimental design, not an asserted globally optimal Beer Game policy. |
| Narayanan, A. & Moritz, B. B. (2015). *Decision Making and Cognition in Multi-Echelon Supply Chains*. Production and Operations Management 24(8), 1216–1234. [Publisher](https://journals.sagepub.com/doi/10.1111/poms.12343) | Links cognitive reflection to pipeline underweighting and performance. It does not establish a causal effect of our chosen deadline or lecture. |
| Oliva, R., Abdulla, H. & Gonçalves, P. (2022). *Do Managers Overreact When in Backlog? Evidence of Scope Neglect from a Supply Chain Experiment*. MSOM 24(4), 1997–2009. [Publisher](https://pubsonline.informs.org/doi/abs/10.1287/msom.2021.1072) | Multilevel decision-rule estimates and backlog scope neglect motivate separate inventory/backlog diagnostics and avoiding overfitted individual game regressions. |
| Betsch, T., Haberstroh, S., Glöckner, A., Haar, T. & Fiedler, K. (2001). *The Effects of Routine Strength on Adaptation and Information Search in Recurrent Decision Making*. OBHDP 84(1), 23–53. [Publisher](https://www.sciencedirect.com/science/article/pii/S0749597800929169) | A learning phase establishes a routine; a later change makes it obsolete. Our H5 acquisition/change/transfer sequence follows that experimental logic. Its quantitative stock states and persistence score are new proposals. |
| Katok/Hyndman and Tong/Long, replication report for Croson & Donohue (2006), 2022. [Project](https://msreplication.utdallas.edu/croson-donohue-2006/), [report](https://bpb-us-e2.wpmucdn.com/sites.utdallas.edu/dist/2/1186/files/2022/04/CrosonDonohue2006_PostReplicationReport.pdf) | The report describes partial replication and highly variable order variances. Its target was a different information-sharing contrast. Do not adopt its sample size as power for our time-pressure or interaction hypotheses. It motivates checking skew, outliers and human variance directly. |
| Tian, Z., Esserman, D., Tong, G., Blaha, O., Dziura, J., Peduzzi, P. & Li, F. (2022). *Sample size calculation in hierarchical 2 × 2 factorial trials with unequal cluster sizes*. Statistics in Medicine 41, 645–664. [Full text](https://pmc.ncbi.nlm.nih.gov/articles/PMC8962918/), [DOI](https://doi.org/10.1002/sim.9284) | Separates controlled/marginal effects and interaction power, including finite-sample corrections. Their allocation hierarchy is not identical to ours; our equal-chain, four-cell variance formulas are derived directly from the contrast covariance. |

We do not claim that any paper validates our lecture, numerical deadlines, 32-state diagnostic, H5 threshold or illustrative effect-size assumptions. Those require human piloting and a prospective freeze.

## Which H5 and H6 are intended?

The presentation `INFORMS_2026_Presentation (1).pptx.pdf`, pages 8–9, lists H1–H4 only. Page 9 makes H4 about **order variation and bullwhip**, superseding the earlier reflection's education-cost H4. The human design retains that newer H4.

The existing local source `experiments/11_education_deadline/data/source/reflection_20261019/reflection.txt` contains:

> H5: After education, participants operating under binding decision-time constraints are more likely than those operating under adequate decision time to persist with an initially adopted replenishment rule when changed supply-chain conditions make that rule less appropriate.

> H6: Decision-time availability moderates the effects of causal education on replenishment decisions and supply-chain costs, such that the education effects differ between binding and adequate decision-time conditions.

These are the project's H5/H6, **not hypotheses numbered 5 and 6 in Donohue's paper**. H5 needs rule acquisition and a changed consequence; H6 needs the full time × education design. G quantifies the pipeline-weighting component of H6. For H5, the correct weight itself changes, so a static “lower pipeline weight = more bias” interpretation would be wrong.

## Relationship to the AI evidence

Experiment 14's closed model-roleplay study measured pipeline responsiveness with a different probe structure, 24 weeks and hypothetical student time. It did not establish independently identified human relative weights, human deadlines or human variance estimates. The human study uses real people, calibrated deadlines, four conditions, an explicit counterfactual stock benchmark and a separately randomized H5 task. Compare findings qualitatively only until the tasks/populations and measurement invariance are justified; do not pool the samples or use AI p-values as human power inputs.
