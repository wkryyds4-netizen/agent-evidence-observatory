"""Check phase-3 references and saved-result consistency, not external event truth."""
import argparse
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]


def verify():
    def read(path):
        return json.loads((ROOT / path).read_text(encoding='utf-8'))
    index = read('evidence/phase3-index.json')
    packs = {key: read('evidence/' + path) for key, path in index['packs'].items()}
    sources = [s for pack in packs.values() for s in pack['sources']]
    ids = [s['id'] for s in sources]
    chains = [c for pack in packs.values() for c in pack.get('chains', [])]
    checks = []
    def check(name, condition):
        checks.append({'name': name, 'passed': bool(condition)})
    check('source_ids_unique_and_indexed', len(ids) == len(set(ids)) and ids == index['source_ids'])
    check('source_denominator', len(sources) == index['source_record_count'] == 32)
    check('source_urls_and_limits', all(s['url'].startswith('https://') and s['limits'] for s in sources))
    check('nine_chains_indexed', [c['id'] for c in chains] == index['chain_ids'] and len(chains) == 9)
    observations = chains + packs['fold']['observations']
    check('all_observation_references_resolve', all(set(c['source_ids']) <= set(ids) for c in observations))
    check('chain_limits_retained', all(c.get('gaps') and c.get('alternative_explanations') for c in chains))
    crypto = read('results/phase3-crypto-checks.json')
    check('crypto_28_saved_checks', len(crypto['checks']) == crypto['check_count'] == index['crypto_check_count'] == 28
          and sum(c['passed'] for c in crypto['checks']) == crypto['passed'] == 28)
    check('crypto_pinned_commit', crypto['commit'] == packs['crypto']['commit'] and bool(re.fullmatch('[a-f0-9]{40}', crypto['commit'])))
    input_hashes = {s['title']: s.get('sha256') for s in packs['crypto']['sources']}
    check('crypto_hashes_match_source_register', all(input_hashes['clients/python/' + filename] == digest
          for filename, digest in crypto['upstream_sha256'].items()))
    check('crypto_guards_and_limits_recorded', crypto['network_or_process_attempts'] == [] and len(crypto['limitations']) >= 4)
    receipt = read('results/phase3-receipt-checks.json')
    api = next(s for s in sources if s['id'] == 'A-S03')
    check('receipt_input_matches_register', receipt['input_sha256'] == api['sha256'])
    check('receipt_hash_and_self_report_boundary', receipt['hash_matches'] and receipt['declared_length_matches']
          and receipt['canonical_byte_length'] == 2040 and receipt['logged_by_agent_claim']
          and receipt['tool_is_journal_log'] and receipt['no_upstream_bytes_claim'])
    check('receipt_clock_discrepancy_retained', receipt['start_minus_created_seconds'] == 71.547
          and receipt['completion_minus_created_seconds'] == 371.547 and receipt['created_precedes_reported_start'])
    check('fold_static_scope', len(packs['fold']['observations']) == index['fold_static_observation_count'] == 5
          and 'not executed' in packs['fold']['mode'])
    check('no_bulk_payload_in_receipt_results', not {'canonical_bytes', 'session_trail', 'result_preview', 'caller'} & set(receipt))
    report = (ROOT / 'reports/phase3-organization-and-artifacts.zh-CN.md').read_text(encoding='utf-8')
    check('report_denominators', all(value in report for value in ['32条来源记录', '9条观察链', '28项', '71.547', '371.547']))
    return {'passed': all(c['passed'] for c in checks), 'check_count': len(checks), 'checks': checks,
            'scope': 'Reference and saved-result consistency only; crypto and external observations are not rerun.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    text = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(text, encoding='utf-8', newline='\n')
    print(text, end='')
    raise SystemExit(0 if result['passed'] else 1)
