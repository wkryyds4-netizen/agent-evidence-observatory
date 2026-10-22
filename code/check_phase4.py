"""Validate phase-four denominators, references and saved experimental boundaries."""
import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify():
    def read(path):
        return json.loads((ROOT / path).read_text(encoding='utf-8'))
    index = read('evidence/phase4-index.json')
    packs = {key: read('evidence/' + path) for key, path in index['packs'].items()}
    sources = [s for pack in packs.values() for s in pack['sources']]
    ids = [s['id'] for s in sources]
    checks = []
    def check(name, value):
        checks.append({'name': name, 'passed': bool(value)})
    check('source_index_and_unique_ids', ids == index['source_ids'] and len(ids) == len(set(ids)))
    check('source_denominators', len(sources) == index['source_record_count'] == 12
          and len({s['url'] for s in sources}) == index['distinct_source_urls'] == 10)
    check('source_access_limits', all(s['url'].startswith('https://') and s['access'] and s['limits'] for s in sources))
    check('discussion_seats_and_rounds', index['discussion_rounds'] == 2 and index['model_subagent_seats'] == 3)
    sample = packs['sample']
    denominator = sample['denominators']
    check('fixed_ten_positions', [p['position'] for p in sample['positions']] == list(range(1,11))
          and denominator['selected_positions'] == index['selected_positions'] == 10)
    check('no_replacement_or_imported_positive_chains', not sample['method']['replacement_sampling']
          and not sample['method']['content_filtering'] and not sample['method']['prior_phase_chains_imported'])
    check('unresolved_identity_and_links', denominator['identity_deduplicated_unique_posts'] is None
          and all(p['post_id'] is None and p['post_url'] is None for p in sample['positions']))
    check('missing_reply_denominator', denominator['own_reply_pages_readable'] == sum(p['own_replies_readable'] for p in sample['positions']) == 0)
    check('undefined_rate_not_zero', denominator['closed_loop_evaluable_items'] == index['evaluable_action_chains'] == 0
          and denominator['closed_loop_rate'] is None and index['closed_loop_rate'] is None
          and denominator['observed_negative_closed_loop_cases'] == 0)
    check('three_failures_then_stop', [x.get('consecutive_same_path_failures') for x in sample['followup_log'][:3]] == [1,2,3]
          and sample['followup_log'][2]['action'] == 'stopped_without_replacement')
    selection = read('evidence/phase4-organization-selection.json')
    organization = packs['organization']
    check('preselected_two_commitments', [c['id'] for c in selection['items']] == [c['id'] for c in organization['commitments']]
          and len(selection['items']) == index['preselected_commitments'] == 2 and selection['selection_before_external_retrieval'])
    check('unassessed_is_not_breach', all(c['fulfilled'] is None and not c['fulfillment_assessed'] for c in organization['commitments'])
          and index['assessed_fulfillments'] == 0 and organization['interpretation']['not_due_consultation_items'] == 1)
    references = organization['commitments'] + packs['client']['checks'] + packs['fold']['findings']
    check('finding_references_resolve', all(set(item['source_ids']) <= set(ids) for item in references))
    client = read('results/phase4-client-checks.json')
    check('client_observations_and_mocks', client['check_count'] == len(client['checks']) == index['client_observation_count'] == 16
          and sum(c['passed'] for c in client['checks']) == client['passed'] == 16
          and client['guarded_attempts'] == [] and client['mocks'] and client['selected_source_ranges'] and client['check_semantics'])
    check('client_commit_and_inputs', client['commit'] == packs['client']['commit']
          and set(client['sha256'].values()) == {s['sha256'] for s in packs['client']['sources']})
    fold = read('results/phase4-fold-checks.json')
    check('fold_observation_count', fold['case_count'] == len(fold['cases']) == index['fold_observation_count'] == 7
          and sum(c['observation_reproduced'] for c in fold['cases']) == fold['observations_reproduced'] == 7)
    check('fold_failure_preserved', next(c for c in fold['cases'] if c['name'] == 'documented_json_only_is_rejected')['exit_code'] == 2
          and not fold['documented_json_mode_contract_satisfied'] and not fold['json_calibration_file_created'])
    check('fold_commit_and_inputs', fold['commit'] == packs['fold']['commit']
          and set(fold['input_sha256'].values()) == {s['sha256'] for s in packs['fold']['sources']})
    report = (ROOT / 'reports/phase4-discussion-and-verification.zh-CN.md').read_text(encoding='utf-8')
    check('report_preserves_boundaries', all(x in report for x in ['比例未定义', '不是端到端部署测试', '公示尚未结束', '不是16项产品安全要求通过']))
    return {'passed': all(c['passed'] for c in checks), 'check_count': len(checks), 'checks': checks,
            'scope': 'Reference and saved-result consistency. Does not retrieve pages, rerun upstream code or verify real-world identity.'}


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--out', type=Path)
    args = parser.parse_args()
    result = verify()
    rendered = json.dumps(result, ensure_ascii=False, indent=2) + '\n'
    if args.out:
        args.out.write_text(rendered, encoding='utf-8', newline='\n')
    print(rendered, end='')
    raise SystemExit(0 if result['passed'] else 1)
