"""Verify user-obtained local input bytes against the research manifest. No network."""
import argparse
import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def check(data):
    manifest = json.loads((ROOT / 'evidence/inputs.json').read_text(encoding='utf-8'))
    results = []
    for item in manifest['files']:
        file = data / item['filename']
        ok = file.is_file() and file.stat().st_size == item['expanded_bytes']
        if ok:
            ok = hashlib.sha256(file.read_bytes()).hexdigest() == item['expanded_sha256']
        results.append({'filename': item['filename'], 'passed': ok})
    return {'passed': all(r['passed'] for r in results), 'files': results,
            'scope': 'Byte consistency only, not source truth or model attribution.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--data', type=Path, required=True)
    args = parser.parse_args()
    result = check(args.data)
    print(json.dumps(result, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
