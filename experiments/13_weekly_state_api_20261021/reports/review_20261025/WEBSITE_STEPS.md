# Website version: what you do

**No new API spending. One chat handles ten chains—40 fictional students—through the game.** The website must support Python/code execution. The model makes decisions; the supplied Python helper handles inventory and costs.

1. Open the prompt index linked below. Download **beergame_controller.py**.
2. Start a **fresh chat**, select the model/reasoning mode you want, and upload that helper. Keep that same selection for all three pilots.
3. Copy the **entire PILOT A prompt** into that chat. Let it work until it returns a downloadable JSON file. Repeat PILOT B and C in two other fresh chats.
4. Download each JSON. Also save/export the **full chat with its Python/tool messages**. Send both back in this conversation, with the exact displayed model name and selected reasoning mode. You do not have to calculate anything yourself.
5. I check the three pilots first. If the website followed the procedure and the results replay correctly, use the prepared numbered main prompts. They are organized into groups of ten for ten tabs. Use a fresh chat for each prompt.

**Important:** Python must not generate the orders with an algorithm. The transcript must show the model choosing orders after each displayed state. If the website cannot execute Python or stops early, send that failure/partial file; do not ask it to invent the missing game.

The active helper and exact prompt links are in [WEBSITE_START_HERE.md](../../prompts/WEBSITE_START_HERE.md). The [new notebook](../../notebooks/MANUAL_WEBSITE.ipynb) imports the files, shows progress and analyzes the results. It needs no API keys.

What the cases mean:

- **A:** standard/control reading; an initial decision plus one separate reconsideration opportunity.
- **B:** the same reading; first decision committed.
- **C:** causal supply-chain reading; first decision committed.

This tests an AI reconsideration-opportunity difference, not a measured human deadline. It does not guarantee significant results or validated student behavior. Ten chains in one chat are dependent; three fresh chats make one matched block. The fixed 10/20/40 independent-block prefixes need 30/60/120 chats **per model**. Start with the three pilots on your best available model; do not collect hundreds of chats before checking feasibility.
