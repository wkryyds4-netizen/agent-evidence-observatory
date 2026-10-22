"""Offline reference checks and reproduction of one publicly revealed SHA-256 sample.

No web requests, posting, account access, or model calls. Passing checks establish
file consistency and digest equality, not AI authorship or an earlier commitment.
"""
import argparse
import csv
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check():
    index = json.loads((ROOT / 'evidence/phase2-index.json').read_text(encoding='utf-8'))
    sample = json.loads((ROOT / 'evidence/phase2-public-hash-sample.json').read_text(encoding='utf-8'))
    sources = index['sources']
    candidates = index['candidates']
    source_ids = [s['id'] for s in sources]
    candidate_ids = [c['id'] for c in candidates]
    payload = sample['payload'].encode('utf-8')
    actual = hashlib.sha256(payload).hexdigest()
    checks = {
        'source_ids_unique': len(source_ids) == len(set(source_ids)),
        'candidate_ids_unique': len(candidate_ids) == len(set(candidate_ids)),
        'declared_counts': index['counts'] == {
            'sources': len(sources), 'candidates': len(candidates),
            'query_records': len(index['queries'])},
        'source_access_and_limits': all(s.get('access') and s.get('limits') for s in sources),
        'candidate_source_references': all(c['source_ids'] and set(c['source_ids']) <= set(source_ids)
                                           for c in candidates),
        'candidate_scope_fields': all(c.get('scale') and c.get('model_attribution')
                                      and c.get('judgment') and c.get('gaps') for c in candidates),
        'follow_up_source_references': all(set(f['source_ids']) <= set(source_ids)
                                           for f in index['follow_up_leads']),
        'sample_source_reference': sample['source_id'] in source_ids and any(
            s['id'] == sample['source_id'] and s['url'] == sample['source_url'] for s in sources),
        'sample_byte_count': len(payload) == sample['payload_bytes'],
        'public_sample_digest_matches': actual == sample['expected_sha256'],
    }
    with (ROOT / 'evidence/phase2-candidates.csv').open(encoding='utf-8', newline='') as f:
        rows = list(csv.DictReader(f))
    checks['candidate_csv_matches_json'] = rows == [
        {**row, 'source_ids': '|'.join(row['source_ids'])} for row in candidates]
    return {
        'passed': all(checks.values()), 'checks': checks, 'counts': index['counts'],
        'sample': {'payload_bytes': len(payload), 'actual_sha256': actual,
                   'matches': actual == sample['expected_sha256']},
        'scope': 'Schema/reference consistency and public sample digest only; not source authenticity, prior timestamp, AI identity, independence, or secret-channel evidence.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path, help='Optional result file; default prints only')
    args = parser.parse_args()
    result = check()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.parent.mkdir(parents=True, exist_ok=True)
        args.out.write_text(rendered, encoding='utf-8', newline='\n')
    print(rendered, end='')
    raise SystemExit(0 if result['passed'] else 1)
