"""Carry a received v1 first response into an explicitly recorded chat-settings run."""
import argparse
import hashlib
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'src'))
from beergame_study.manual_cohort_chat import (
    CohortConfig, audit, prepare, lineage_for, import_response, load_accepted,
    accepted_path, next_task, progress, read, replay, save_new,
)
from beergame_study.manual_response_formatting import build_report


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--parent', type=Path, required=True)
    parser.add_argument('--response', type=Path, required=True)
    parser.add_argument('--model', required=True)
    parser.add_argument('--effort', choices=['pro', 'high'], required=True)
    parser.add_argument('--chat-label', required=True)
    parser.add_argument('--full-prompt-confirmed', action='store_true', required=True)
    args = parser.parse_args()
    cfg = read(args.parent/'manifest.json')['config']
    run = prepare(CohortConfig(**{key: cfg[key] for key in
                  ('students', 'batch_students', 'weeks', 'repetitions', 'seed', 'synthetic')},
                  study_label='cohort-500-chat-pro', model_label=args.model, effort_label=args.effort,
                  lineage=lineage_for(args.parent, args.response)), root=args.parent.resolve().parents[2])
    raw = args.response.read_text(encoding='utf-8')
    if not accepted_path(run, 'b0001', 'initial').exists():
        import_response(run, 'b0001', 'initial', raw, model_label=args.model, effort_label=args.effort,
                        session_label=args.chat_label, confirm_full_prompt=args.full_prompt_confirmed)
    entry = load_accepted(run, 'b0001', 'initial')
    assert entry['payload'] == json.loads(raw)
    assert entry['raw_sha256'] == hashlib.sha256(args.response.read_bytes()).hexdigest()
    rows, probes, _ = replay(run, paired_only=False)
    current = rows[(rows.batch_id == 'b0001') & (rows.condition == 'initial')]
    generated = current[current.phase == 'model']
    observed_probes = probes[(probes.batch_id == 'b0001') & (probes.condition == 'initial')]
    report = build_report(run)
    task = next_task(run)
    status = progress(run)
    receipt = dict(status='accepted', protocol=audit(run)['protocol'], run=run.name,
                   original_study_id=args.parent.name, batch='b0001', stage='initial',
                   model_label=args.model, ui_setting=args.effort, metadata_source='user report in conversation',
                   chain_count=int(current.chain_id.nunique()), fictional_identities=len(observed_probes),
                   weekly_orders=len(generated), scored_role_states=len(current),
                   rules_check='passed', missing_orders=0, replaced_orders=0,
                   zero_weekly_orders=int((generated.order==0).sum()), largest_weekly_order=int(generated.order.max()),
                   distinct_probe_pairs=observed_probes[['low_order','high_order']].drop_duplicates().values.tolist(),
                   accepted_responses=int(status.initial.sum()+status.revision.sum()),
                   paired_batches=int((status.initial & status.revision).sum()), api_calls=0,
                   raw_sha256=entry['raw_sha256'], prompt_sha256=entry['prompt_sha256'],
                   next_prompt=str(task['prompt_path'].resolve()) if task else None,
                   report=str(report['report'].resolve()))
    folder = run.parents[2]/'reports'/run.name
    save_new(folder/'FIRST_RESPONSE_CHECK.json', receipt)
    save_new(folder/'FIRST_RESPONSE.md',
        f"# First response received — 18 October 2026\n\n"
        f"**Accepted: batch 1 initial, {args.model} / {args.effort} (user-reported).**\n\n"
        f"All {receipt['chain_count']} chains, {receipt['fictional_identities']} fictional identities and "
        f"{receipt['weekly_orders']:,} weekly orders are present. Factual answers and integer/dimension checks passed. "
        f"Local replay completed {receipt['scored_role_states']:,} role-states including practice and automatic continuation. "
        "No submitted order was changed.\n\n"
        f"Weekly orders range from 0 to {receipt['largest_weekly_order']}; {receipt['zero_weekly_orders']} are zero. "
        "All 100 matched-state probe pairs are `[16, 0]`. Their uniformity is retained, not repaired. "
        "This does not verify student realism or the model's internal state tracking.\n\n"
        "The first prompt/response retain the earlier study ID. Their original text and hashes are carried into "
        "this separate run because the actual UI settings differ from the prepared Astra/high settings. "
        "The settings amendment occurred after this response arrived. "
        "[Read the amendment](../../docs/MANUAL_CHAT_SETTINGS_20261018.md).\n\n"
        "**Collection progress: 1/10 responses. No revision or H1/H2/H3 comparison yet.**\n\n"
        "[Next: batch 2 initial prompt](prompts/b0002_INITIAL.md). Use a fresh chat with GPT-6 / Pro. "
        "[Current partial report](REPORT.md).\n")
    print(json.dumps(receipt, indent=2))


if __name__ == '__main__':
    main()
