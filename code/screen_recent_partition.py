"""Screen a user-supplied static public archive partition, entirely offline."""
import argparse
import collections
import hashlib
import json
from pathlib import Path
import screen_corpus as sc


def run(file, output):
    raw = file.read_bytes()
    if len(raw) > 16 * 1024 * 1024:
        raise ValueError('Partition exceeds the reviewed 16 MiB local bound')
    allrows = [json.loads(x) for x in raw.decode('utf-8-sig').splitlines() if x.strip()]
    eligible = [r for r in allrows if isinstance(r, dict)
                and r.get('type') in ('event', 'message') and not r.get('hidden')
                and r.get('visibility') == 'public' and r.get('archive_eligible') is True]
    parent_ids = {r.get('id') for r in eligible}
    rows = []
    for index, r in enumerate(allrows, 1):
        if r not in eligible or r.get('kind') == 'imported' or not isinstance(r.get('text'), str):
            continue
        author = str(r.get('author') or '')
        rows.append({
            'record_id': hashlib.sha256(('hf:' + str(r.get('id'))).encode()).hexdigest()[:20],
            'dataset': 'swarmmemo_2026-10-13',
            'identity_label': sc.redact(str(r.get('handle') or '[unsigned]')),
            'identity_ref': hashlib.sha256(author.encode()).hexdigest()[:20],
            'source_locator': f'messages-2026-10-13.jsonl:line:{index}',
            'timestamp_utc': sc.iso_time(r.get('created_at')), 'text': r['text'],
            'source_url_sanitized': '', 'place_label': sc.redact(str(r.get('room'))),
            'publisher_reply_flag': r.get('reply_to') is not None,
            'text_sha256': sc.normalized_hash(r['text']), 'post_index': index - 1,
            'publisher_parent_present_in_partition': bool(r.get('reply_to') and r['reply_to'] in parent_ids),
            'text_type': r.get('kind'),
        })
    counts = collections.Counter(r['text_sha256'] for r in rows)
    classified = [sc.classify(r, counts) for r in rows]
    dates = [r['timestamp_utc'] for r in rows if r['timestamp_utc']]
    summary = {
        'input_sha256': hashlib.sha256(raw).hexdigest(), 'archive_rows': len(allrows),
        'eligible_rows': len(eligible), 'analyzed_nonimported_rows': len(rows),
        'identity_reference_count': len({r['identity_ref'] for r in rows}),
        'kind_counts': dict(collections.Counter(r['text_type'] for r in rows)),
        'created_min_utc': min(dates) if dates else None, 'created_max_utc': max(dates) if dates else None,
        'publisher_reply_to_present': sum(r['publisher_reply_flag'] for r in rows),
        'parent_present_in_this_partition': sum(r['publisher_parent_present_in_partition'] for r in rows),
        'feature_counts': {k: sum(r['flags'][k] for r in classified) for k in sc.FEATURES},
        'limits': [
            'Partial-day partition at a fixed revision, not a complete day or current feed.',
            'Full texts and historical short excerpts are not directly comparable.',
            'Reply IDs are publisher-declared, not authenticated by this script.',
            'All conclusions remain unassessed; names and keys do not authenticate models.',
            'Per-record local outputs remain linkable, are not anonymous, and should not be published in bulk.',
        ],
    }
    output.mkdir(parents=True, exist_ok=True)
    (output / 'recent_partition_screening.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    with (output / 'recent_partition_records.jsonl').open('w', encoding='utf-8') as f:
        for row in classified:
            f.write(json.dumps(row, ensure_ascii=False) + '\n')
    return summary


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    print(json.dumps(run(args.input, args.out), ensure_ascii=False, indent=2))
