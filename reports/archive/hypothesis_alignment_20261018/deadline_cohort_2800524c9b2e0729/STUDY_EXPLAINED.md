# The Beer Game study, simply explained

## 1. Which model are we using?

**GPT-6 / Pro**, as selected in your ChatGPT website and reported by you. You copy and paste prompts; no API key is needed.

## 2. How do we mimic students?

The prompt describes **hypothetical second-year University at Buffalo business students**, with no Beer Game experience. Each gets one of four fictional personalities: **organized/calm, organized/concerned, flexible/calm, or flexible/concerned**. We have no real student data to validate these portrayals.

## 3. What does the model actually do?

One reply supplies **20 weeks of beer orders for 100 fictional students**, grouped into 25 teams. Each team has a **retailer, wholesaler, distributor and factory**. We supply the rules, personalities and demand paths; students aim to minimize inventory and shortage costs.

Two prompts describe students having **10 seconds or 180 seconds** to decide. Model settings and matched inputs stay the same. This changes the imagined situation, **not the model's actual thinking-time limit**.

## 4. How is data collected?

1. Copy each prompt into a **fresh GPT-6 / Pro chat** without earlier replies.
2. Return the complete JSON here or paste it into notebook 07.
3. Python saves and checks it, then calculates inventories, shortages, costs and plots.

**500 fictional identities = five batches of 100.** We collect **5 batches × 2 deadlines × 2 repeats = 20 replies**. Repeats reuse identities to check ordinary output variation. Exact prompts and responses are retained.

## 5. What does the JSON mean?

JSON is a **results sheet Python can read**.

| Field | Meaning |
| --- | --- |
| `schema_version`, `study_id` | Format and experiment identifiers. |
| `task_id` | Batch, repeat and scenario: `b0003_g01_ample` = batch 3, repeat 1, 180 seconds. |
| `deadline_seconds` | Fictional deadline: 10 or 180. |
| `rules` | Three game-rule comprehension answers. |
| `chains` / `chain_id` | The teams and their identifiers. |
| `orders` | Weekly rows for weeks 5–24, in retailer/wholesaler/distributor/factory order. `[2,4,4,4]` means they order 2, 4, 4 and 4 cases. |
| `probes` | One pair per role: orders chosen with 8 versus 32 cases already on the way. Used for H1. |
| `complete` | Claimed completeness; Python checks it. |

## 6. What are H1, H2 and H3?

Under the shorter deadline, we predict:

- **H1:** orders respond less to beer already on the way.
- **H2:** total inventory and shortage costs increase.
- **H3:** orders fluctuate more relative to customer demand—the **bullwhip effect (牛鞭效应)**.

Costs include **4 practice + 20 model-decision + 12 automatic continuation weeks**, calculated by Python.

The model sees entire demand paths and generates students together. These are **simulated decisions, not 500 independent human observations**.

[Collection steps and next prompt](START_HERE.md) · [Results and plots](REPORT.md)
