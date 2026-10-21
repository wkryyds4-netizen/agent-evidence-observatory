"""Check the public edition's manifest, scope, references and aggregate consistency."""
import argparse
import csv
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
IGNORED = {'.git', '.local-data', '.local-output', '__pycache__'}
DIRS = {'code', 'docs', 'evidence', 'reports', 'results', 'tests'}
TOP = {'README.md', 'AUTHORS.md', 'LICENSE', 'THIRD_PARTY_NOTICES.md',
       'CONTRIBUTING.md', 'CHANGELOG.md', '.gitignore', '.gitattributes'}


def files():
    return sorted(p for p in ROOT.rglob('*') if p.is_file()
                  and not any(part in IGNORED for part in p.relative_to(ROOT).parts)
                  and p.name != 'SHA256SUMS.txt')


def write_manifest():
    (ROOT / 'SHA256SUMS.txt').write_text(''.join(
        hashlib.sha256(p.read_bytes()).hexdigest() + '  ' + p.relative_to(ROOT).as_posix() + '\n'
        for p in files()), encoding='utf-8')


def verify():
    checks = []

    def check(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})

    paths = files()
    names = {p.relative_to(ROOT).as_posix() for p in paths}
    allowed = all((p.relative_to(ROOT).parts[0] in DIRS
                   or p.relative_to(ROOT).as_posix() in TOP) for p in paths)
    check('allowlisted_directories', allowed)
    check('no_raw_archives_or_bulk_record_files', not any(
        p.suffix in {'.jsonl', '.gz', '.zip', '.html', '.pem', '.key'} or
        p.name in {'agents.json', 'ranked_index.csv', 'manual_review_sample.json', 'manual_review_sample.csv'}
        for p in paths))
    manifest_path = ROOT / 'SHA256SUMS.txt'
    manifest = {}
    if manifest_path.is_file():
        for line in manifest_path.read_text(encoding='utf-8').splitlines():
            digest, name = line.split('  ', 1)
            manifest[name] = digest
    check('manifest_exact_file_set', set(manifest) == names)
    check('manifest_hashes', bool(manifest) and all(
        manifest.get(p.relative_to(ROOT).as_posix()) == hashlib.sha256(p.read_bytes()).hexdigest()
        for p in paths))
    text = '\n'.join(p.read_text(encoding='utf-8-sig') for p in paths)
    check('no_local_user_directory', not re.search(r'(?i)[a-z]:[/\\]+Users[/\\]+[\w.-]+', text))
    check('no_known_credential_prefix', not re.search(r'(?i)\b(?:gh[pousr]_|github_pat_|sk-(?:ant-)?|AKIA)[A-Za-z0-9_-]{10,}', text))
    # Synthetic fixtures use reserved domains, never real addresses.
    emails = re.findall(r'[\w.+-]+@[\w.-]+\.[A-Za-z]{2,}', text)
    check('no_nonfixture_email', all(e.endswith(('@example.invalid', '@example.org')) for e in emails))
    broken = []
    for p in paths:
        if p.suffix != '.md':
            continue
        for target in re.findall(r'\]\(([^\s)]+)\)', p.read_text(encoding='utf-8')):
            if urlsplit(target).scheme or target.startswith('#'):
                continue
            relative = unquote(target.split('#', 1)[0])
            if relative and not (p.parent / relative).resolve().is_file():
                broken.append(p.relative_to(ROOT).as_posix() + ':' + target)
    check('local_markdown_links', not broken)
    docs = json.loads((ROOT / 'evidence/index.json').read_text(encoding='utf-8'))
    check('source_and_candidate_counts', len(docs['sources']) == 38 and len(docs['candidate_rows']) == 21)
    source_ids = [s['id'] for s in docs['sources']]
    check('source_ids_unique', len(source_ids) == len(set(source_ids)))
    known_ids = set(source_ids) | {'D-D01', 'D-D02', 'D-D03'}
    check('candidate_source_references', all(set(r['source_ids']) <= known_ids for r in docs['candidate_rows']))
    check('nine_hypotheses_marked', len([r for r in docs['candidate_rows']
        if r['id'].startswith('A-A') and r['name'].startswith('待检：')]) == 9)
    with (ROOT / 'evidence/candidates.csv').open(encoding='utf-8-sig', newline='') as f:
        check('candidate_csv_count', len(list(csv.DictReader(f))) == 21)
    historical = json.loads((ROOT / 'results/screening_summary.json').read_text(encoding='utf-8'))
    wiki = json.loads((ROOT / 'results/wiki_metadata_summary.json').read_text(encoding='utf-8'))
    recent = json.loads((ROOT / 'results/recent_partition_screening.json').read_text(encoding='utf-8'))
    signature = json.loads((ROOT / 'results/recent_partition_verification.json').read_text(encoding='utf-8'))
    check('historical_denominators', historical['record_count'] == 5808 and historical['dataset_count'] == 8
          and historical['snapshot_dataset_count'] == 9 and historical['identity_labels_by_dataset'] == 1676)
    check('wiki_event_types_sum', sum(wiki['event_type_counts'].values()) == wiki['event_count'] == 19913)
    check('true_success_field_only_delete_revert', {k for k, v in wiki['success_observed_by_event_type'].items()
          if 'True' in v} == {'delete', 'revert'})
    check('recent_partial_day_count', recent['analyzed_nonimported_rows'] == 58
          and recent['created_min_utc'].startswith('2026-10-13') and recent['created_max_utc'].startswith('2026-10-13'))
    check('signature_aggregates_only', 'records' not in signature
          and signature['signature_status_counts'] == {'valid': 51, 'unsigned': 7}
          and signature['signed_core_fields_match'] == 24)
    check('signature_input_hash', signature['input_sha256'] == recent['input_sha256'])
    reviews = json.loads((ROOT / 'results/semantic_reviews.json').read_text(encoding='utf-8'))
    check('model_review_counts', len(reviews['historical']['reviews']) == 32 and len(reviews['recent']['reviews']) == 9)
    check('review_identifier_maps_removed', all('record_id' not in r and 'line_number' not in r
          for section in ('historical', 'recent') for r in reviews[section]['reviews']))
    audit = json.loads((ROOT / 'evidence/attribution_audit.json').read_text(encoding='utf-8'))
    check('hypothesis_field_semantics', all('hypothesis_under_review' in a and 'claim' not in a
          and 'falsifiable_by' not in a and 'evidence_needed_for_reassessment' in a for a in audit['assessments']))
    readme = (ROOT / 'README.md').read_text(encoding='utf-8')
    check('authorship_and_evidence_limits', '求证（QiuZheng）' in readme and '不证明此类组织不存在' in readme)
    return {'passed': all(c['passed'] for c in checks), 'check_count': len(checks),
            'file_count': len(paths) + 1, 'checks': checks, 'broken_links': broken,
            'scope': 'Public-edition file integrity and bounded schema checks, not event verification.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--write-manifest', action='store_true')
    args = parser.parse_args()
    if args.write_manifest:
        write_manifest()
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
