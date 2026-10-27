# Options for late or missing orders

**Proposal only. No fallback is selected or implemented.** The 16 original development cases and their results remain unchanged.

## First distinguish two situations

- **Near the deadline, but valid and on time:** keep the model's actual order, including zero. Never add random noise to it.
- **Deadline passed without a complete valid submission:** record the model decision as missing. A separately labelled software action can keep a new game moving under a prospectively specified rule. A late model answer stays in the log but cannot replace the action already applied.

## Practical options

| Option | What happens on a true timeout? | Main trade-off |
|---|---|---|
| **1. Repeat the previous order** | Apply the previous order separately for each role. Use the game's initialized quantity of 4 when no previous order exists. | Simple and reproducible; repetition can mechanically reduce order variance. |
| **2. Randomly sample earlier orders** | For each role, draw uniformly from its own earlier on-time model orders in this chain; repeated values retain their frequency. If none exist, apply 4 as an explicit software initialization. | Avoids an arbitrary wide order range, but the sampled action is synthetic and may change costs and bullwhip. |
| **3. Small random change** | Add a draw from {-1, 0, +1}, each with probability 1/3, to the previous applied order, with a floor of zero. Use 4 as the initial reference. | Easy to implement, but the noise size is researcher-chosen without student data. Suitable for a synthetic stress test. |
| **4. Early model commitment** | Ask for a complete current-state order promptly and use it if actually received before the deadline. | Keeps a genuine model choice, but cannot guarantee timely arrival. Allowing later revisions would require a different, explicitly specified protocol. |

These distributions are proposals, not empirically validated models of rushed students. None guarantees significance. The present stop-on-timeout rule remains the baseline until a new protocol is selected.

## Recommendation

If finishing 24 weeks is essential, **option 1 is the simplest primary continuation rule**. If a random option is wanted, **option 2 is preferable to a broad uniform random order range**; use it as a separately declared synthetic sensitivity condition. Option 3 is a further software stress test.

H2/H4 would then measure **the model plus its timeout policy**. More timeouts mean more software intervention. Neither repeated nor random orders should be described as newly observed student/model choices, or used to guarantee the desired hypothesis direction. Do not drop fallback weeks from a trajectory and call the remaining variance a complete-game behavioral result.

**H1/H3 probe answers must remain missing when absent.** A random or repeated answer cannot measure pipeline responsiveness. Game continuation alone does not resolve the failed probe-completion gate; that needs separate prospective development.

## What a new implementation must record

Use the same declared fallback rule in A/B/C. Freeze its first-week rule, random distribution, deadline boundary, four-role packet handling and seed scheme before collection. Random draws must use a separate stream from customer demand, indexed by block, week and role, never redrawn for a preferred result. With the current atomic four-order format, a missing packet means all four current orders are missing.

For each decision save: deadline and receipt time; actual model submission, including rejected late submissions; applied game action; source (`model_on_time`, `carry_forward`, or `random_fallback`); and fallback parameters/seed. Show timeout and synthetic-action shares by condition alongside H1-H4. An analysis of a different fallback that changes the states requires new model decisions for those states; old choices are not validated counterfactual responses.

Computer takeover after a Beer Game timeout has an implementation precedent: [Zensimu's timer documentation](https://docs.zensimu.com/article/22-monitor-the-beer-game) and [its computer-player rule](https://docs.zensimu.com/article/32-computer-player-orders-calculation). That product uses an explicit reorder rule; it does not validate the random distributions proposed here as human behavior. We have not adopted its rule.
