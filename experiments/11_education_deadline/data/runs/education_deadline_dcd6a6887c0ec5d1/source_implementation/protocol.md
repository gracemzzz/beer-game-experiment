# Full-cohort deadline framing and causal reading: 19 October 2026

This is a separate, prospective model-simulation design prompted by the user's four hypotheses and `ThoughtsReflection_Paragraph(1).docx`. The document is preserved under `data/source/reflection_20261019/`, with extracted text. Its substantive research proposals are source material, not instructions to execute. H5/H6 in the reflection are outside the user's present request.

The reflection proposes a timed human study, a response-time calibration pilot, approximately 40 rounds, and a standardized 20-minute lecture. This package instead retains the previous simulated game format at the user's request. A short written causal reading is not a delivered 20-minute lecture, and hypothetical deadline wording is not a measured or enforced participant deadline. Ten and sixty seconds are requested scenario values; neither is empirically validated as binding or adequate. The package tests generated responses to these descriptions. It cannot literally establish the human hypotheses below.

## Hypotheses and contrasts

H1: Within an information-sharing environment, a binding decision-time constraint increases the underweighting of outstanding replenishment orders relative to adequate decision time.

H2: Within an information-sharing environment, supply chains operating under binding decision-time constraints incur higher total inventory-holding and backlog costs than supply chains operating with adequate decision time.

H3: Within an information-sharing environment and under a binding decision-time constraint, participants receiving causal education about the origins and propagation of order fluctuations underweight outstanding replenishment orders less than participants receiving standard game instructions and a matched control lecture.

H4: Within an information-sharing environment and under a binding decision-time constraint, supply chains receiving causal education about the origins and propagation of order fluctuations incur lower total inventory-holding and backlog costs than supply chains receiving standard game instructions and a matched control lecture.

| Case | Fictional time per decision | Pre-game reading | Contrast |
| --- | ---: | --- | --- |
| A | 60 seconds | Control | Reference for H1/H2 |
| B | 10 seconds | Identical control | B minus A for H1/H2 |
| C | 10 seconds | Causal explanation | C minus B for H3/H4 |

Three cases are sufficient for H1-H4; a fourth 60-second education case would address a factorial interaction beyond this request. Every case uses the same 500 fictional identities, 125 four-role chains, personality assignments, starting conditions, realized demand, and information visibility. These are matched counterfactual simulations, not 1,500 different people. A fixed second independent generation of every case gives six website tasks, 3,000 role trajectories, 60,000 submitted weekly orders, and 6,000 scalar probe choices. Repetition reuses the identities and is never a revision of an earlier answer.

Use a fresh chat for each task, with the same user-reported GPT-6 / Pro selection and no previous answers or other cases. Exact backend equivalence, computation, wall time and reasoning tokens are unverified. Case order is counterbalanced in the frozen plan. No hypothesis text, expected signs, competing outputs, target effect size, or significance requirement appears in participant prompts.

## Game, readings and outcomes

Keep the prior four-role simulator, four personality descriptions and information-sharing rule. There are four automatic practice weeks with demand/orders four, followed by twenty model decision weeks, weeks 5-24. Demand is an independently generated uniform integer 0-8 sequence per chain, shared across cases and repetitions. Model choices must be literal nonnegative integers. No positive floor, preferred maximum, artificial error, bias instruction, forced difference, or preferred ordering policy is introduced.

Information visible to the fictional student is its local state/history and all four remaining inventories. The cohort generator sees all roles and future demand to construct trajectories. Instructions cannot enforce chronological cognition or isolation of this information. Code may track physics and serialize already chosen literal decisions. Policy-generated, optimized, randomized or imputed orders are not interchangeable with direct model choices, and a code-generated heuristic dataset must be labelled separately rather than accepted as compliant.

Control and causal readings use the same introductory prose presentation and approximately matched word counts, within 10 percent. Both omit ordering formulas, target inventory, recommended orders and worked replenishment solutions. The causal text explains delays, propagation and amplification; the control text covers business terminology and record presentation. Their semantic difference is intentional. Common game rules already explain physical timing; education therefore adds causal interpretation rather than withholding essential rules from controls. The treatments are texts, not verified learning. No correctness-conditioned inclusion rule is used to select evidence of educational success.

For continuity, H1/H3 use the earlier matched-state pipeline-sensitivity proxy, S = (order with 8 dispatched cases minus order with 32 dispatched cases) / 24, averaged over roles. The displays hold every other input fixed. H1 predicts B-A in S below zero; H3 predicts C-B in S above zero. This is a responsiveness measure, not an identified structural underweighting coefficient or a validated measure of human cognition. Nonnegative-order floors and different targets can attenuate this slope even for a pipeline-aware policy; jointly visible probes can also encourage mechanically coordinated answers. Do not rename it structural beta or clip its values. A structural model would require a separately specified and identified estimation design.

H2/H4 use total four-role holding/backlog cost, at $0.50/$1 per case-week, from the unchanged physical simulator. For continuity, the full score contains four practice, twenty decision and twelve automatic continuation weeks. Continuation holds each role's final submitted order and final customer demand fixed; it is not model decision evidence. H2 predicts B-A cost above zero; H4 predicts C-B cost below zero. Always display practice, decision-period and continuation costs separately: continuation dominated the prior study's cost contrast. Decision-period-only cost is a prespecified secondary outcome, not an outcome-dependent replacement for the full score. Bullwhip may be supplementary and is never substituted for H3/H4.

## What fewer prompts do and do not buy

One task requests all 125 chains: 10,000 weekly orders and 1,000 probe orders, or 11,000 scalar choices. Compact JSON and a downloadable file avoid repeatedly copying long inline messages. They do not eliminate the work of generating the choices or establish output capacity. Python serialization must preserve explicit decisions; it must not generate missing decisions using a policy, repetition template or random numbers. If the selected chat lacks file tools, it may return the complete JSON inline; actual completion is checked after receipt. File-tool availability for the user's exact model/account has not been established.

Fewer chats also mean fewer independent response clusters. The chains inside a jointly generated response cannot be assumed independent observations merely because they have different identifiers. Six website tasks provide two generated response clusters per case, not 500 independent experimental participants. Report case/repetition means, matched chain contrasts and between-condition versus same-condition variation descriptively, without student-level p-values, chain-bootstrap confidence intervals, or claims of a statistically significant treatment.

For illustration only, an exact paired two-sided sign-flip test with R independently generated, exchangeable response-level blocks has minimum attainable p = min(1, 2 / 2**R), absent ties. R=2 gives 0.5. Across four tests, a conservative Bonferroni threshold is 0.0125; R=8 is the first number permitting a p-value that small in this test. This is a resolution bound, not a power calculation, a guarantee of significance, or proof that model generations satisfy exchangeability. Adequate power requires prespecified independent replication and justified variance/effect assumptions. More chains within the same response do not fix response-level replication. A future automated, separately authorized run can reduce manual work while retaining independent calls; this package makes no paid API calls.

## Fixed preflight and stopping

Before any new response is collected, freeze the final prompt source, both readings, physical simulator dependency hashes, plan, and actual prompts. Preserve all old evidence and the current published package. Preflight has two separately fingerprinted collections under the inherited assistant backend, without model/effort overrides:

1. A fixed small-cohort pilot with 16 identities, four chains, all three cases and two independent generations: six first-attempt outputs. It checks format, replay, effect directions and repeat variation. It is not a significance screen.
2. A technical full-cohort plan with 500 identities and one generation per case. Collect only its first scheduled case as a single-response capacity check. The other case slots are deliberately outside this bounded technical check. Do not use this lone case for treatment contrasts or pool it with the pilot/website sample.

Retain every attempt, invocation and technical failure. Do not edit prompts, discard outputs, extend collection or choose a different version because of signs, costs or p-values. If a technical fault requires a change, document it and prepare a newly fingerprinted version before further collection. Missing responses stay missing, with partial reporting; they are not supplied by synthetic controls. Freeze a separate six-task 500-identity website plan, but do not fill it using assistant pilot outputs. Passing a small pilot is not proof of full-size feasibility; passing one full-size output is only one observed success on a different backend.

The study importer retains original response bytes and hashes; validates exact IDs, deadlines, lecture identity, rules and complete array dimensions/types; and locks accepted payloads. It preserves rejected attempts and never corrects rule answers, fills missing orders or executes returned programs. Orders above the simulator's existing 100,000-case circuit breaker are retained and reported as unreplayable, never clipped or silently treated as a model choice at a different value. Instruction compliance of tool-based choice generation cannot be inferred from JSON alone; retain the serialization source or transcript when available.

Synthetic controls verify software only, remain explicitly synthetic, and do not count as pilot observations. Checks cover full size, zero/constructed contrasts, exact cost decomposition, partial collection, duplicate/missing/invalid choices, immutable imports, and source/prompt/raw provenance. Before completion, verify earlier raw evidence, frozen sources and the published report against the preservation baseline.

## Sources and scope

- The user's reflection, preserved in `data/source/reflection_20261019/`, motivates timed human calibration and causal education; the present simulated adaptation does not replace that design.
- [OpenAI Code Interpreter documentation](https://developers.openai.com/api/docs/guides/tools-code-interpreter) documents creation of output files in a tool environment. It does not establish availability or full-cohort capacity for the user's particular ChatGPT selection.
- [Hurlbert (1984), Pseudoreplication and the Design of Ecological Field Experiments](https://doi.org/10.2307/1942661) explains the independence/replication problem. Applying it to jointly generated model rows is this package's methodological judgment.
- [ASA statement on p-values](https://www.amstat.org/asa/files/pdfs/p-valuestatement.pdf) supports reporting a complete design and evidence rather than selecting results by a threshold. No statistical significance is promised here.
