# Start the website version here

**A/B/C pilot files have now been received and replayed.** [Review and plots](../reports/manual_pilot_review_20261025/REPORT.md). Full-context provenance remains incomplete; C's recorded source-exposure deviation is preserved. The main numbered prompts are still a separate, uncollected sample.

**Use these three pilots first. No API calls or keys.** Each chat runs ten chains, with the website's Python tool calculating the physical game.

1. Download [beergame_controller.py](manual_v3_3e5479b5ae2ffc96/beergame_controller.py).
2. In a **fresh chat with Python/code execution**, upload that file and paste the entire [PILOT A prompt](manual_v3_3e5479b5ae2ffc96/00_PILOT_A.md).
3. Repeat in two other fresh chats using [PILOT B](manual_v3_3e5479b5ae2ffc96/00_PILOT_B.md) and [PILOT C](manual_v3_3e5479b5ae2ffc96/00_PILOT_C.md). Use the same selected model and reasoning mode.
4. Let each chat finish. Return its downloaded JSON **and saved full chat/tool transcript** in this conversation. Tell me the exact displayed website model and selected reasoning mode.

You do not run Python yourself. The website model does that. If it lacks code execution or cannot finish, return the failure/partial response rather than asking for invented decisions.

[All main prompts, grouped into waves of ten tabs](manual_v3_3e5479b5ae2ffc96/README.md) · [Five simple steps](../reports/review_20261025/WEBSITE_STEPS.md) · [Import/analysis notebook](../notebooks/MANUAL_WEBSITE.ipynb)

The main prompts are prepared; wait for the three pilots' technical review before collecting them. Ten chains in one chat are dependent. A uses an additional reconsideration opportunity; this is not a calibrated human deadline and does not guarantee significance. Fixed 10/20/40 independent matched blocks require 30/60/120 chats per model.
