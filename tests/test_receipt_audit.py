"""Synthetic evidence-boundary checks, without redistributing any receipt."""
import base64
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

spec = importlib.util.spec_from_file_location('receipt_audit', Path(__file__).resolve().parents[1] / 'code/audit_public_receipt.py')
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def fixture():
    # Whitespace is intentionally noncanonical: hash exact bytes, never reserialize.
    payload = b'{ "tool":{"name":"journal_log"}, "output":{"entry":{"started_at":"2026-01-01T00:01:00Z","completed_at":"2026-01-01T00:02:00Z"},"private_note":"DO_NOT_EXPORT"}}'
    return {'receipt': {'canonical_bytes': base64.b64encode(payload).decode(),
        'output_hash': 'sha256:' + hashlib.sha256(payload).hexdigest(),
        'canonical_byte_length': len(payload), 'created_at': '2026-01-01T00:00:00Z',
        'evidence_status': 'no_upstream_bytes_captured'}}


class ReceiptChecks(unittest.TestCase):
    def test_exact_bytes_and_chronology_without_private_payload(self):
        result = module.audit(json.dumps(fixture()).encode())
        self.assertTrue(result['hash_matches'])
        self.assertTrue(result['tool_is_journal_log'])
        self.assertEqual(result['start_minus_created_seconds'], 60)
        self.assertEqual(result['completion_minus_created_seconds'], 120)
        self.assertNotIn('DO_NOT_EXPORT', json.dumps(result))

    def test_tampered_commitment_is_not_accepted(self):
        data = fixture()
        data['receipt']['output_hash'] = 'sha256:' + '0' * 64
        self.assertFalse(module.audit(json.dumps(data).encode())['hash_matches'])

    def test_invalid_base64_rejected(self):
        data = fixture()
        data['receipt']['canonical_bytes'] += '!'
        with self.assertRaises(ValueError):
            module.audit(json.dumps(data).encode())

    def test_naive_clock_rejected(self):
        data = fixture()
        data['receipt']['created_at'] = '2026-01-01T00:00:00'
        with self.assertRaises(ValueError):
            module.audit(json.dumps(data).encode())


if __name__ == '__main__':
    unittest.main()
