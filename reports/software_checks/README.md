# Free validation

13 offline/mocked tests passed. The complete notebook executed successfully in both calibration and 40-week game modes, with no paid API requests. All generated outcomes here are synthetic software checks, not evidence for H1/H2.

- `calibration_offline_executed.ipynb`: 96 synthetic decisions, 192 cached stages.
- `game_offline_executed.ipynb`: two four-role chains, 40 weeks, including four fixed warmup weeks and 288 agent decisions; 12 automatic continuation weeks.
- `validation.json`: execution and archive-integrity summary.

Both synthetic conditions use the same policy; no treatment effect is built in.
