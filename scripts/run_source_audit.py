"""Run a real public-HTML audit and record CLI outputs, with no mocked retrieval.

Use a fresh output directory for each execution; existing records are never replaced.
This is a source-audit demonstration, not model screening or independent approval.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import platform
import shutil
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parents[1]


def now():
    return datetime.now(timezone.utc).isoformat()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def build_task():
    releases = [
        ('S1', 'Python 3.12.0', 'Oct. 2, 2023', 'python.org',
         'https://www.python.org/downloads/release/python-3120/',
         'This is the stable release of Python 3.12.0',
         'Release date: Oct. 2, 2023', 'Page heading and release-date field'),
        ('S2', 'PostgreSQL 16', 'September 14, 2023', 'postgresql.org',
         'https://www.postgresql.org/about/news/postgresql-16-released-2715/',
         'PostgreSQL 16 Released!', 'September 14, 2023',
         'Announcement heading and dated opening paragraph'),
    ]
    task = {
        'id': 'PUBLIC_RELEASE_DATES',
        'owner': 'EvidenceTrail public execution example',
        'topic': 'Initial stable release dates for two named software releases',
        'break_pattern': 'Baseline source-audit demonstration, not a model-breaking benchmark',
        'modality_decision': 'Public HTML only; raw retrieval is performed by this execution. No official browser or screening harness is claimed.',
        'prompt': 'For the initial stable releases Python 3.12.0 and PostgreSQL 16, list the release name and release date recorded on the respective official release page or announcement. Retain each page\'s human-readable date spelling.',
        'answer_template': '[release] | [release date]',
        'example_answer': 'ImaginaryDB 99 | January 1, 1900',
        'scope': {
            'inclusion_rule': 'Exactly the two named initial stable releases; exclude release candidates, later patches, and site-wide news banners.',
            'start_boundary': 'The initial stable Python 3.12.0 and PostgreSQL 16 release records.',
            'end_boundary': 'The same two historical records; later page notices do not change the release dates.',
        },
        'golden_answer': [], 'sources': [], 'evidence': [],
        'research': {
            'search_trial': [{'query': 'Direct lookup of the official Python 3.12.0 release page and PostgreSQL 16 release announcement',
                              'observation': 'The two official records were opened during preparation; the runner separately retrieves and audits their HTML. No search-engine or model trajectory is claimed.'}],
            'completeness_proof': 'The question explicitly names two releases; there is one answer row for each, supported by its own official project record.',
            'completeness_source_ids': ['S1', 'S2'],
            'domain_dependency': 'Python supplies the Python date; PostgreSQL supplies the PostgreSQL date. These are separate project-maintained records.',
            'single_domain_shortcut_test': 'The selected evidence set requires both project records; no claim is made that these facts cannot be found together elsewhere.',
            'prompt_to_source_connection': 'Each named software release identifies its official project release record.',
            'output_normalization': 'Keep the source date spelling; do not substitute an ISO date or a later site-wide banner date.',
            'pretest': {'method': '', 'observation': '', 'not_run_reason': 'No model pretest or external screening was performed; this example exercises live source auditing.'},
            'realistic_reason': 'An engineer can reconstruct release-date provenance for a compatibility or dependency report.',
            'timeless_reason': 'Both named initial releases occurred in 2023; this is not a latest-version question.',
            'constraint_evidence': [{'constraint': 'Initial stable release identity and original release date, excluding later patches and banners',
                                     'source_ids': ['S1', 'S2'],
                                     'evidence': 'Use the named release heading and its own dated release metadata or announcement opening.'}],
        },
        'screening': [],
    }
    for sid, release, date, domain, url, fact, date_quote, locator in releases:
        answer = f'{release} | {date}'
        task['golden_answer'].append(answer)
        task['sources'].append({
            'id': sid, 'url': url, 'domain': domain, 'title': fact,
            'language': 'English', 'credibility_reason': 'Official software-project release record, authoritative for its own release.',
            'retrieved_at': datetime.now(timezone.utc).date().isoformat(),
            'quote_locator': locator, 'source_format': 'html', 'source_fact': fact,
            'public': False, 'non_social': True, 'raw_html_checked': False,
            'necessary_for': [release + ' release identity and initial stable release date'],
        })
        task['evidence'].append({
            'answer_item': answer, 'source_ids': [sid],
            'qualification': 'This is one of the two exact releases named by the question; use its release-specific date.',
            'field_support': [
                {'field': 'release', 'value': release, 'source_id': sid, 'exact_quote': release},
                {'field': 'release date', 'value': date, 'source_id': sid, 'exact_quote': date_quote},
            ],
        })
    return task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True, help='fresh directory for recorded execution artifacts')
    args = parser.parse_args()
    output = args.output.resolve()
    if output.exists():
        parser.error('output already exists; select a fresh directory to preserve previous executions')
    output.mkdir(parents=True)
    package = output / 'package'
    package.mkdir()
    logs = output / 'logs'
    logs.mkdir()
    task_path = package / 'task.json'
    dump(task_path, build_task())
    shutil.copyfile(task_path, output / 'task.before.json')
    shutil.copyfile(ROOT / 'evidencetrail/templates/review.json', package / 'review.json')
    dump(package / 'creation-report.json', {
        'generator': 'Manually authored public reference example; no model generation executed',
        'phase': 'source_audit_pending', 'blockers': ['External screening and independent review have not been performed'],
        'source_audit': [],
    })
    records = []
    version = subprocess.run(['git', 'rev-parse', 'HEAD'], cwd=ROOT, text=True, capture_output=True)
    summary = {'started_at': now(), 'python': platform.python_version(),
               'platform': platform.system(), 'source_commit': version.stdout.strip() or None,
               'implementation_sha256': hashlib.sha256((ROOT / 'evidencetrail/__init__.py').read_bytes()).hexdigest(),
               'network': 'Real public HTML requests through EvidenceTrail/curl; no mocks',
               'path_redaction': 'Checkout and execution directory paths in logs/argv replaced with <checkout> and <run>; all other command output retained',
               'external_model_screening_performed': False, 'independent_review_performed': False,
               'commands': records}

    def clean(text):
        return text.replace(str(output), '<run>').replace(str(ROOT), '<checkout>')

    def run(label, arguments, expected):
        started = now()
        clock = time.monotonic()
        result = subprocess.run([sys.executable, '-m', 'evidencetrail', *map(str, arguments)],
                                cwd=ROOT, capture_output=True, text=True, timeout=100)
        (logs / (label + '.stdout.txt')).write_text(clean(result.stdout), encoding='utf-8')
        (logs / (label + '.stderr.txt')).write_text(clean(result.stderr), encoding='utf-8')
        records.append({'label': label, 'argv': ['python3', '-m', 'evidencetrail', *[clean(str(x)) for x in arguments]],
                        'started_at': started, 'finished_at': now(), 'duration_seconds': round(time.monotonic() - clock, 3),
                        'exit_code': result.returncode, 'expected_exit_code': expected})
        dump(output / 'execution.json', summary)
        if result.returncode != expected:
            raise RuntimeError(f'{label}: expected exit {expected}, got {result.returncode}; inspect recorded logs')
        print(f'{label}: exit {result.returncode} (expected {expected})')
        return result.stdout

    common = ['--blocklist', ROOT / 'config/demo-blocklist.txt', '--tasks-dir', output / 'batch']
    run('01-before-check', ['check', task_path, *common], 1)
    run('02-live-source-audit', ['verify-sources', package, '--source-timeout', '20', *common], 0)
    report = json.loads((package / 'creation-report.json').read_text())
    if len(report['source_audit']) != 2 or not all(x['verified'] for x in report['source_audit']):
        raise RuntimeError('live source audit did not verify both public pages')
    run('03-after-check', ['check', task_path, *common], 1)
    run('04-form-fields', ['form-fields', task_path, '--output', package / 'form-fields.md'], 0)
    digest = run('05-fingerprint', ['fingerprint', task_path], 0).strip()
    run('06-render-blocked', ['render', task_path, '--output', package / 'submission.md', *common], 1)
    run('07-review-blocked', ['review', package, *common], 1)
    if (package / 'submission.md').exists():
        raise RuntimeError('an unscreened submission should not have been rendered')
    # This copy intentionally contains a wrong quote. It is never the canonical answer.
    probe = output / 'negative-probe'
    shutil.copytree(package, probe)
    changed = json.loads((probe / 'task.json').read_text())
    changed['evidence'][0]['field_support'][1]['exact_quote'] = 'This date quotation deliberately does not exist on the release page.'
    dump(probe / 'task.json', changed)
    run('08-negative-live-source-audit', ['verify-sources', probe, '--source-timeout', '20', *common], 1)
    negative = json.loads((probe / 'creation-report.json').read_text())['source_audit']
    if negative[0]['verified'] or 'Could not locate exact_quote' not in negative[0]['reason']:
        raise RuntimeError('negative quotation probe was not rejected for the intended reason')
    summary.update({'finished_at': now(), 'source_audit_verified': 2, 'negative_quote_rejected': True,
                    'task_sha256': digest, 'status': 'live_sources_verified_screening_and_independent_review_pending'})
    dump(output / 'execution.json', summary)
    files = {str(p.relative_to(output)): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(output.rglob('*')) if p.is_file()}
    dump(output / 'artifact-sha256.json', files)
    print('Recorded real source retrieval and blocked handoff; no external model screening or independent approval claimed.')


if __name__ == '__main__':
    main()
