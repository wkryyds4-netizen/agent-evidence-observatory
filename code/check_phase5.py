"""Check phase-five evidence structure and denominators, without network access."""
import json
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def verify():
    checks = []

    def check(name, ok):
        checks.append({'name': name, 'passed': bool(ok)})

    def read(path):
        return json.loads((ROOT / path).read_text(encoding='utf-8'))

    index = read('evidence/phase5-index.json')
    all_cases, all_sources = [], []
    dimensions = {'membership', 'roles', 'goal', 'continuity', 'rules', 'artifact'}
    for name, expected in [('claude', 2), ('bilibili', 5), ('international', 5)]:
        pack = read(f'evidence/phase5-{name}.json')
        cases, sources = pack['cases'], pack['sources']
        ids = {s['id'] for s in sources}
        check(name + '_candidate_count', len(cases) == expected)
        check(name + '_unique_source_ids', len(ids) == len(sources))
        check(name + '_six_dimensions_with_resolved_sources', all(
            set(c['dimensions']) == dimensions and all(
                d['judgment'] and d['source_ids'] and set(d['source_ids']) <= ids
                for d in c['dimensions'].values()) for c in cases))
        check(name + '_provenance_fields', all(c['model_attribution'] and c['human_role'] for c in cases))
        check(name + '_index_counts', index['base_packs'][name]['candidates'] == len(cases)
              and index['base_packs'][name]['source_records'] == len(sources))
        all_cases.extend(cases)
        all_sources.extend(sources)
    check('distinct_base_cases', len({c['id'] for c in all_cases}) == len(all_cases) == index['base_candidate_count'] == 12)
    check('source_record_total_not_independent_sources', len(all_sources) == index['base_source_records'] == 36)
    selection = read('evidence/phase5-international-selection.json')
    check('international_frozen_ids', {c['id'] for c in selection['cases']} ==
          {c['id'] for c in all_cases if c['id'].startswith('INT5-')})
    bili = read('evidence/phase5-bilibili.json')
    check('bilibili_no_video_or_comment_claim', all(c['video_watched'] is False and not c['comments_read'] for c in bili['cases']))
    check('protocol_deviation_preserved', bool(bili['protocol_deviations']))

    sample = read('evidence/phase5-content-sample.json')
    records, den = sample['records'], sample['denominators']
    check('snapshot_counts', len(records) == den['selected_posts'] == den['unique_post_ids'] == 18
          and len({r['post_id'] for r in records}) == 18)
    check('preflight_exclusion_and_order', sample['selection']['initial_posts'] == 20
          and sample['selection']['preflight_excluded'] == 2
          and [r['source_position'] for r in records] == list(range(3, 21))
          and not any(r['duplicates_preflight'] for r in records))
    check('readable_content_fields', sum(r['content_text_resolved'] for r in records) == den['readable_bodies'] == 18)
    check('platform_counters_not_reply_observations', sum(r['comment_count_platform_field'] for r in records) == den['platform_comment_counter_sum'] == 39
          and den['observed_reply_records'] == 0 and not any(r['replies_in_this_record'] for r in records))
    check('no_closure_rate_for_zero_denominator', den['action_chains_evaluable'] == 0 and den['action_closure_rate'] is None)
    check('category_counts', dict(Counter(r['semantic_coding']['primary_category'] for r in records)) == sample['category_counts'])
    check('duplicate_body_group_retained', sample['exact_duplicate_content_groups_by_source_position'] == [[4, 19]])
    check('sample_no_raw_body_title_or_author', all(not ({'content', 'body', 'title', 'author', 'author_id'} & set(r)) for r in records))
    check('snapshot_hash_scope', sample['acquisition']['input_sha256'] == '326c16e529afc9c9aa6f8e3a702606bcd97af3096abfce51bd1db41e7ee5610d'
          and sample['acquisition']['input_bytes'] == 211525 and sample['acquisition']['raw_input_published'] is False)

    delegation = read('evidence/phase5-deep-delegation.json')
    assignments = delegation['assignments']
    check('two_nested_assignments', len(assignments) == 2 and all(
        a['agent'].startswith('/root/international_phase2/') for a in assignments)
        and len({a['agent'] for a in assignments}) == 2)
    check('deep_outputs_present', all((ROOT / 'evidence' / a['output']).is_file() for a in assignments))
    check('nested_assignments_completed', all(a['status'] == 'completed' for a in assignments))
    for entry in index['deep_packs']:
        pack = read('evidence/' + entry['file'])
        sources = pack.get('sources', [pack.get('source')])
        source_ids = {s['id'] for s in sources}
        referenced = []

        def collect(value):
            if isinstance(value, dict):
                if 'source_ids' in value:
                    referenced.extend(value['source_ids'])
                for child in value.values():
                    collect(child)
            elif isinstance(value, list):
                for child in value:
                    collect(child)

        collect(pack)
        check(entry['case_id'] + '_deep_source_references', set(referenced) <= source_ids
              and len(source_ids) == len(sources))
    return {'passed': all(c['passed'] for c in checks), 'check_count': len(checks), 'checks': checks,
            'scope': 'Saved evidence consistency only; not independent verification of actors, execution or semantic labels.'}


if __name__ == '__main__':
    result = verify()
    print(json.dumps(result, ensure_ascii=False, indent=2))
    raise SystemExit(0 if result['passed'] else 1)
