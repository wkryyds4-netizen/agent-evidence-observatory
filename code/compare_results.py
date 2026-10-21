"""Compare recomputed local aggregates to the published computational fields."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXCLUDED = {'limits', 'limitations', 'publication_note', 'records', 'self_test', 'verifier'}


def compare(actual):
    checks = []
    for name in ['screening_summary.json', 'wiki_metadata_summary.json',
                 'recent_partition_screening.json', 'recent_partition_verification.json']:
        expected = json.loads((ROOT / 'results' / name).read_text(encoding='utf-8'))
        current = json.loads((actual / name).read_text(encoding='utf-8'))
        for key, value in expected.items():
            if key not in EXCLUDED:
                checks.append({'field': name + ':' + key, 'passed': current.get(key) == value})
    return {'passed': all(c['passed'] for c in checks), 'check_count': len(checks),
            'failed': [c['field'] for c in checks if not c['passed']],
            'scope': 'Computational fields only; no semantic accuracy or external truth claim.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--actual', type=Path, required=True)
    args = parser.parse_args()
    result = compare(args.actual)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
