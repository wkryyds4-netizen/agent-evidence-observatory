"""Reproduce a pinned CLI contract with synthetic files, never governance content."""
import argparse
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

COMMIT = '467a8cdab13869dc24091edf71502d7c4ed5d0a4'
EXPECTED = {
    'fold_check.py': 'ddb3174849cca5c1a0d534191e79a9318acd12b7ad2f3d5897dd022543e87b8c',
    'META.json': '83d1e57dd7a0cc6b81970587480010d0eb6557736d143984abf9dc1f9b3b18ab',
}
NAMES = {'page1_v11': 'page1_v11_served.md', 'page3_v3': 'page3_v3.md',
         'page3_v4': 'page3_v4_draft.md', 'page1_repoint_to_v3': 'page1_repoint_to_v3.md',
         'page1_repoint_to_v4': 'page1_repoint_to_v4.md'}
RUNNER = '''import sys, runpy
def guard(event, args):
    if event in {'socket.connect','socket.getaddrinfo','socket.bind','subprocess.Popen','os.system'}:
        raise RuntimeError('Blocked network/process event')
sys.addaudithook(guard)
sys.argv = sys.argv[1:]
runpy.run_path(sys.argv[0], run_name='__main__')
'''


def roots(data, recipe):
    size = len(data)
    header = bytes.fromhex(recipe['magic_descriptor_hex']) + size.to_bytes(4, 'little') + (size * 8 + 1).to_bytes(3, 'little')
    framed = header + data
    pieces = [framed[i:i + recipe['chunk_bytes']] for i in range(0, len(framed), recipe['chunk_bytes'])]
    values = []
    for ordered in (pieces[::-1], pieces):
        link = bytes.fromhex(recipe['link_seed_hex'])
        for piece in ordered:
            link = hashlib.sha256(piece + link).digest()
        values.append(link.hex())
    return values


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--source-dir', type=Path, required=True)
    parser.add_argument('--out', type=Path, required=True)
    args = parser.parse_args()
    for name, digest in EXPECTED.items():
        if hashlib.sha256((args.source_dir / name).read_bytes()).hexdigest() != digest:
            parser.error('Unreviewed input: ' + name)
    original = json.loads((args.source_dir / 'META.json').read_bytes())['frame_recipe']
    fields = ('header_bytes','chunk_bytes','link','fold_direction','link_seed_hex','magic_descriptor_hex')
    recipe = {key: original[key] for key in fields}
    recipe.update(backward_fold_gives={}, forward_fold_counterfactual_not_a_root={}, header_hex={})
    results = []
    # Keep generated files below the user's explicit output directory.
    output_parent = args.out.resolve().parent
    with tempfile.TemporaryDirectory(prefix='qz-fold-synthetic-', dir=output_parent) as folder:
        directory = Path(folder)
        if not directory.resolve().is_relative_to(output_parent):
            raise RuntimeError('Temporary directory escaped the output directory')
        target = directory / 'fold_check.py'
        target.write_bytes((args.source_dir / 'fold_check.py').read_bytes())
        for number, (key, filename) in enumerate(NAMES.items()):
            body = ((str(number) + ':synthetic calibration only\n') * 240).encode()
            (directory / filename).write_bytes(body)
            backward, forward = roots(body, recipe)
            recipe['backward_fold_gives'][key] = backward
            recipe['forward_fold_counterfactual_not_a_root'][key] = forward
        # Replace upstream governance fixture contents with generated non-governance data.
        (directory / 'META.json').write_text(json.dumps({'frame_recipe': recipe}), encoding='utf-8')
        lf = b'alpha\nbeta\n'
        crlf = lf.replace(b'\n', b'\r\n')
        (directory / 'lf.txt').write_bytes(lf)
        (directory / 'crlf.txt').write_bytes(crlf)
        expected_root = roots(lf, recipe)[0]

        def run(name, arguments, expected_exit, marker):
            process = subprocess.run([sys.executable, '-I', '-B', '-X', 'utf8', '-c', RUNNER, str(target), *arguments],
                cwd=directory, capture_output=True, timeout=10)
            combined = (process.stdout + process.stderr).decode('utf-8', errors='replace')
            result = {'name': name, 'exit_code': process.returncode, 'expected_observation_exit': expected_exit,
                'expected_marker_found': marker in combined,
                'observation_reproduced': process.returncode == expected_exit and marker in combined,
                'stdout_sha256': hashlib.sha256(process.stdout).hexdigest(),
                'stderr_sha256': hashlib.sha256(process.stderr).hexdigest()}
            results.append(result)
        run('default_calibration_with_synthetic_fixture', [], 0, 'ALL MATCH')
        run('documented_json_only_is_rejected', ['--json'], 2, 'usage error:')
        run('explicit_flags_matching_root', ['--text','lf.txt','--expect',expected_root], 0, 'MATCH')
        run('explicit_flags_wrong_root', ['--text','lf.txt','--expect','0' * 64], 1, 'MISMATCH')
        run('positional_arguments_rejected', ['lf.txt',expected_root], 2, 'usage error:')
        run('missing_expect_rejected', ['--text','lf.txt'], 2, 'usage error:')
        run('crlf_does_not_match_lf_root', ['--text','crlf.txt','--expect',expected_root], 1, '2 CR bytes')
        produced_json = bool(list(directory.glob('fold_calibration_*.json')))
    result = {'commit': COMMIT, 'input_sha256': EXPECTED, 'recipe_constants': {k: recipe[k] for k in fields},
        'python': sys.version.split()[0], 'cases': results, 'case_count': len(results),
        'observations_reproduced': sum(r['observation_reproduced'] for r in results),
        'json_calibration_file_created': produced_json,
        'documented_json_mode_contract_satisfied': False,
        'scope': 'Pinned CLI with generated fixture content. Reproducing a documented-mode failure is not a product pass.',
        'limits': ['No real proposal text, chain transaction or governance outcome tested.',
                   'No model identity, operator independence or autonomous organization established.',
                   'Two fixture roots use a separately written implementation of the same recipe, not an external protocol oracle.',
                   'Output hashes record this local run; CLI help contains whitespace and may vary with line-ending conversion.']}
    args.out.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8', newline='\n')
    print(json.dumps({'cases': len(results), 'observations_reproduced': result['observations_reproduced'],
                      'documented_json_mode_contract_satisfied': False}))
    return 0 if all(r['observation_reproduced'] for r in results) and not produced_json else 1


if __name__ == '__main__':
    raise SystemExit(main())
