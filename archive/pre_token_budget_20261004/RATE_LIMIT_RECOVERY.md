# Conclusions

1. Latest run stopped after 307 valid responses and five HTTP 429 errors in 83.84 seconds. There were no comprehension failures. This is encouraging for the revised prompt, not a completed stability test.
2. Previous logging omitted the API error subtype, so throttling versus quota exhaustion cannot be proven from those records. Buying more credit is not established as the remedy.
3. The updated runner uses four workers, request starts initially at least one second apart, and a shared cooldown. Temporary rate errors follow Retry-After or exponential backoff with jitter, with at most five transport retries per correctness attempt. Pacing slows after temporary errors. Transport retries preserve the exact prompt and do not replace a group.
4. Confirmed billing/quota errors stop immediately. New error records retain safe error codes and Retry-After without storing full exception messages or keys. Unknown new 429 errors are not blindly retried.
5. Resume checkpoint prepared: verify_5nano_api_e9abab153af9ba0c. All 307 valid replies are reused. All request hashes, schemas, experimental settings, and prompt texts were checked. The five old unclassified errors permit one fresh recovery attempt each; subsequent classification controls any further retry. Original files remain unchanged.
6. Carried estimated charges/reservations: $0.060143. These include unknown-usage reservations and are not an invoice. The existing $0.75 allowance includes these amounts; it is not reset.
7. Reopen START_HERE_verify_budget.ipynb from disk, restart the kernel, and run all cells with the prepared settings. Do not change the replicate ID. The progress bar shows cooldown seconds and cached responses. No paid calls were made while preparing this fix.

[Official OpenAI rate-limit guidance](https://developers.openai.com/api/docs/guides/rate-limits) recommends pacing and bounded backoff for temporary limits; quota/billing failures need separate handling.
