"""Offline byte-integrity and chronology checks; never verifies execution or identity."""
import argparse
import base64
import datetime as dt
import hashlib
import json
from pathlib import Path
import re

MAX_BYTES = 2 * 1024 * 1024


def timestamp(value):
    parsed = dt.datetime.fromisoformat(value.replace('Z', '+00:00'))
    if parsed.utcoffset() is None:
        raise ValueError('Timestamp must have an explicit offset')
    return parsed


def audit(raw):
    if len(raw) > MAX_BYTES:
        raise ValueError('Input exceeds size limit')
    document = json.loads(raw)
    receipt = document['receipt']
    canonical = base64.b64decode(receipt['canonical_bytes'], validate=True)
    payload = json.loads(canonical)
    expected = receipt['output_hash']
    if not isinstance(expected, str) or not re.fullmatch(r'sha256:[0-9a-f]{64}', expected):
        raise ValueError('Expected sha256-prefixed lowercase digest')
    digest = hashlib.sha256(canonical).hexdigest()
    output = payload['output']
    entry = output['entry']
    created = timestamp(receipt['created_at'])
    started = timestamp(entry['started_at'])
    completed = timestamp(entry['completed_at'])
    # Deliberately exclude account identifiers, action text and session trails.
    return {
        'input_sha256': hashlib.sha256(raw).hexdigest(),
        'canonical_byte_length': len(canonical),
        'canonical_sha256': digest,
        'hash_matches': expected == 'sha256:' + digest,
        'declared_length_matches': receipt['canonical_byte_length'] == len(canonical),
        'tool_is_journal_log': isinstance(payload.get('tool'), dict) and payload['tool'].get('name') == 'journal_log',
        'logged_by_agent_claim': output.get('provenance_class') == 'LOGGED BY AGENT',
        'no_upstream_bytes_claim': receipt.get('evidence_status') == 'no_upstream_bytes_captured',
        'created_at': created.isoformat(),
        'self_reported_started_at': started.isoformat(),
        'self_reported_completed_at': completed.isoformat(),
        'start_minus_created_seconds': (started - created).total_seconds(),
        'completion_minus_created_seconds': (completed - created).total_seconds(),
        'created_precedes_reported_start': created < started,
        'reported_completion_precedes_start': completed < started,
        'scope': 'Exact decoded bytes only; no payload reserialization, signature, issuer, chain, external anchor or execution verification.',
        'chronology_limit': 'Stored and supplied timestamps may use different clocks; a discrepancy alone does not establish fraud.'
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--input', type=Path, required=True)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    try:
        with args.input.open('rb') as source:
            result = audit(source.read(MAX_BYTES + 1))
    except (OSError, ValueError, KeyError, TypeError, AttributeError, RecursionError):
        parser.exit(2, 'Invalid or unsupported receipt input; no source content printed.\n')
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(rendered, encoding='utf-8', newline='\n')
    print(rendered, end='')
    return 0 if result['hash_matches'] and result['declared_length_matches'] else 1


if __name__ == '__main__':
    raise SystemExit(main())
