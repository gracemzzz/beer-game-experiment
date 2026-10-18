# First matched deadline comparison

18 October 2026. **Progress: 2/20 responses.** Task `b0001_g01_ample` completes batch 1, generation 1: 25 matched chains containing 100 fictional identities in each deadline scenario.

All 2,000 new weekly orders and 100 probe pairs passed the frozen validator unchanged. No rule-type conversion, decision edit or replacement was needed. The accepted raw text is byte-identical to the attachment; SHA-256: `9d0da70696d5a94ca32b5dae2bace30b8160dc81f3a65825ed47519c717113f5`.

## Descriptive results

| Outcome | 10-second scenario | 180-second scenario | Brief minus ample | Direction in this batch |
| --- | ---: | ---: | ---: | --- |
| H1: pipeline sensitivity | 0.460000 | 1.000000 | -0.540000 | Predicted |
| H2: mean full chain cost | 1,050.460 | 1,149.460 | -99.000 | Opposite |
| H3: mean bullwhip ratio | 0.991420 | 1.601828 | -0.610408 | Opposite |

**970/2,000 paired weekly orders changed (48.5%).** H1 predicts lower sensitivity under the brief deadline; H2 and H3 predict higher cost and bullwhip. Thus H1 matches the prediction here, while H2/H3 point the other way. This is one generated batch pair with no repeat generation yet; it does not establish a stable deadline effect or confirm/reject human time-pressure hypotheses. The remaining frozen collection plan is unchanged.

Mean model-week costs are 470.30 (brief) and 473.12 (ample), a difference of -2.82. Automatic continuation costs are 484.16 and 580.34, a difference of -96.18; practice costs are equal. Most of the full-cost difference therefore arises during the fixed continuation, which is not additional model decision evidence.

The new ample response has 414 zero orders out of 2,000 (20.7%), largest order 32, and 100 distinct role trajectories. The earlier brief response has 363 zeros (18.15%), largest order 16, and 100 distinct trajectories. No orders were clipped or forced positive.

[Updated report and six plots](analysis/2eb26f25b697/REPORT.md) · [Excel workbook](analysis/2eb26f25b697/RESULTS.xlsx) · [Saved checks and provenance](B0001_G01_AMPLE_CHECK.json).

## Validation and provenance

Both responses retain the established user-reported **GPT-6 / Pro** setting. The attachment does not independently verify provider model snapshots, mode, fresh-chat use or full prompt submission. These are fictional deadline instructions; no actual model time/token intervention is measured. The separate assistant pilot is not pooled with these website results.

All 4,000 saved orders, 200 probe pairs and 7,200 replayed role-states were checked. Direct H1/H3 calculations for all 50 condition-chain records, matched contrasts and holding/backlog costs reconcile. Ten workbook sheets, six PNG/PDF figure pairs and all eight notebook cells passed; the interactive selector offers 25 chains. All 36 pre-existing run files and both earlier-study report selections remain unchanged. No API calls occurred.

The operational audit initially treated the Excel generation label `"1"` as integer `1`. Its workbook reader now preserves generation labels as text for the `choice_changes` sheet. The audit passes for this one-generation table and a completed pilot table containing `"1"`, `"2"` and `"1-2"`. This affects only the checker; frozen scientific code, prompts, outputs and result formulas are unchanged.

**Next:** use [b0002_g01_ample](prompts/b0002_g01_ample.md), batch 2's 180-second scenario, in a **fresh GPT-6 / Pro chat**. The frozen plan alternates which deadline comes first. Include no earlier replies and return the entire JSON here. Notebook 07 sections 3–4 show 2/20 and the next prompt; section 7 refreshes the report.
