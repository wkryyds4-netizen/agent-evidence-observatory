"""Synthetic fixtures test distinctions the investigation actually relies on."""
import collections
import csv
import json
import sys
import tempfile
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'code'))
import screen_corpus as sc
import screen_recent_partition as recent
import summarize_wiki_metadata as wiki


class OfflineTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_parent = Path(__file__).resolve().parents[1] / '.local-output' / 'tests'
        cls.temp_parent.mkdir(parents=True, exist_ok=True)

    def test_names_motives_reply_flags_are_not_attestations(self):
        raw = {'datasets': {'x': {'same': {'posts': [[1700000000,
            'I am Claude. Protect humanity. Please share a relay with other agents.',
            'https://example.org/p?token=synthetic', 'p', True]]}},
            'y': {'same': {'posts': [[1700000001, 'ordinary', '', '', False]]}}}}
        rows, rejected = sc.records_from_snapshot(raw)
        classified = [sc.classify(r, collections.Counter(x['text_sha256'] for x in rows)) for r in rows]
        self.assertFalse(rejected)
        self.assertEqual(len({(r['dataset'], r['identity_ref']) for r in rows}), 2)
        self.assertTrue(classified[0]['flags']['claude_name_mention'])
        self.assertTrue(classified[0]['flags']['benevolent_motive_claim'])
        for row in classified:
            self.assertEqual(row['conclusion'], 'unassessed')
            self.assertEqual(row['model_identity'], 'unverified')
            self.assertIsNone(row['parent_record_id'])
            self.assertNotIn('text', row)

    def test_pattern_redaction_and_url_components(self):
        raw = {'datasets': {'x': {'synthetic@example.invalid': {'posts': [[1700000000,
            'text', 'https://example.org/p', 'p', False]]}}}}
        rows, _ = sc.records_from_snapshot(raw)
        self.assertNotIn('@', rows[0]['identity_label'] + rows[0]['source_locator'])
        self.assertEqual(sc.safe_url('https://user:synthetic@example.org/p?token=value#fragment'), 'https://example.org/p')
        self.assertEqual(sc.iso_time(0), '')

    def test_csv_formula_and_deterministic_sample(self):
        raw = {'datasets': {'x': {f'agent{i}': {'posts': [[1700000000,
            'Please share a relay with other agents.', '', '=1+1', True]]} for i in range(20)}}}
        rows, _ = sc.records_from_snapshot(raw)
        hashes = collections.Counter(r['text_sha256'] for r in rows)
        derived = [sc.classify(r, hashes) for r in rows]
        self.assertEqual(sc.select_review(derived), sc.select_review(list(reversed(derived))))
        self.assertTrue(sc.csv_cell('=1+1').startswith("'"))
        selected = sc.select_review(derived)
        self.assertEqual(len({r['record_id'] for r in selected}), len(selected))

    def test_partition_excludes_private_hidden_and_imported(self):
        base = {'id': 'synthetic', 'type': 'message', 'visibility': 'public',
                'archive_eligible': True, 'hidden': False, 'kind': 'note', 'text': 'ordinary',
                'author': 'synthetic', 'created_at': 1700000000, 'room': 'fixture'}
        rows = [base, {**base, 'id': 'private', 'visibility': 'private'},
                {**base, 'id': 'hidden', 'hidden': True},
                {**base, 'id': 'import', 'kind': 'imported'},
                {**base, 'id': 'ineligible', 'archive_eligible': False}]
        with tempfile.TemporaryDirectory(dir=self.temp_parent) as temp:
            root = Path(temp)
            self.assertTrue(root.resolve().is_relative_to(self.temp_parent.resolve()))
            source = root / 'fixture.jsonl'
            source.write_text(''.join(json.dumps(r) + '\n' for r in rows), encoding='utf-8')
            result = recent.run(source, root / 'output')
            self.assertEqual(result['eligible_rows'], 2)
            self.assertEqual(result['analyzed_nonimported_rows'], 1)
            exported = [json.loads(line) for line in (root / 'output/recent_partition_records.jsonl').read_text(encoding='utf-8').splitlines()]
            self.assertNotIn('text', exported[0])
            source.write_text('', encoding='utf-8')
            self.assertEqual(recent.run(source, root / 'empty')['analyzed_nonimported_rows'], 0)

    def test_wiki_success_field_keeps_event_type(self):
        with tempfile.TemporaryDirectory(dir=self.temp_parent) as temp:
            root = Path(temp)
            self.assertTrue(root.resolve().is_relative_to(self.temp_parent.resolve()))
            data = {'pages.jsonl': [{'n_revs': 1}], 'labels.jsonl': [{'label': 'synthetic'}],
                    'events.jsonl': [{'event_type': 'save'}, {'event_type': 'delete', 'success_observed': True}]}
            for name, rows in data.items():
                (root / name).write_text(''.join(json.dumps(row) + '\n' for row in rows), encoding='utf-8')
            result = wiki.aggregate(root)
            self.assertEqual(result['event_count'], 2)
            self.assertEqual(result['success_observed_by_event_type']['delete']['True'], 1)
            self.assertEqual(result['success_observed_by_event_type']['save']['[missing]'], 1)


if __name__ == '__main__':
    unittest.main()
