"""Demonstrate local packaging and rejection of fictional evidence; no network."""
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]


def run(*arguments, expected=0):
    result = subprocess.run([sys.executable, '-m', 'evidencetrail', *map(str, arguments)],
                            cwd=ROOT, text=True, capture_output=True, check=False)
    print(result.stdout, end='')
    if result.returncode != expected:
        raise RuntimeError(result.stderr or result.stdout)
    return result.stdout


def main():
    with tempfile.TemporaryDirectory(prefix='evidencetrail-demo-') as temporary:
        run('new', 'DEMO_DRAFT', '--tasks-dir', temporary)
        run('form-fields', ROOT / 'examples/fictional-task.json')
        print('Fingerprint of fictional example:')
        run('fingerprint', ROOT / 'examples/fictional-task.json')
        print('Expected rejection of fictional evidence:')
        report = run('check', ROOT / 'examples/fictional-task.json',
                     '--blocklist', ROOT / 'config/demo-blocklist.txt',
                     '--tasks-dir', temporary, expected=1)
        assert 'Fictional example packages cannot be submitted' in report
    print('Offline demonstration complete. No real sources or model runs were claimed.')


if __name__ == '__main__':
    main()
