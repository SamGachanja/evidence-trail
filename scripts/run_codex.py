"""Execute one real research prompt through Codex and record public-facing artifacts.

Requires an authenticated Codex CLI and network access. This command consumes the
configured account's allowance. It does not decide whether the model is correct.
Review generated artifacts before publishing them.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from evidencetrail import resolve_codex_bin


RESEARCH_INSTRUCTIONS = '\n\nUse public web research and cite the official sources you consulted. Do not access local files.'


def public_events(text):
    """Keep event kinds, web actions/source metadata, and usage; omit reasoning/bodies."""
    events = []
    for line in text.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        record = {'event': event.get('type')}
        item = event.get('item') or {}
        if item.get('type'):
            record['item_type'] = item['type']
        if item.get('type') == 'web_search':
            record['query'] = item.get('query')
            action = item.get('action') or {}
            record['action'] = {key: action[key] for key in ('type', 'url', 'query', 'queries') if key in action}
            record['sources'] = [{key: source[key] for key in ('type', 'title', 'domain', 'url') if key in source}
                                 for source in item.get('results', [])]
        if event.get('usage'):
            record['usage'] = event['usage']
        if event.get('type') in ('error', 'turn.failed'):
            record['error'] = event.get('message') or event.get('error')
        events.append(record)
    return events


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n', encoding='utf-8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True, help='fresh directory for artifacts')
    parser.add_argument('--model', help='explicit provider model identifier; omit to use the CLI default')
    parser.add_argument('--codex-bin', default='codex')
    parser.add_argument('--timeout', type=int, default=240)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('--timeout must be positive')
    task = json.loads(args.task.read_text(encoding='utf-8'))
    if not isinstance(task.get('prompt'), str) or not task['prompt'].strip():
        parser.error('task must contain a nonempty prompt')
    binary = resolve_codex_bin(args.codex_bin)
    if not binary:
        parser.error('Codex CLI was not found; install/sign in separately or supply --codex-bin')
    output = args.output.resolve()
    if output.exists():
        parser.error('output exists; use a fresh directory')
    output.mkdir(parents=True)
    prompt = task['prompt'] + RESEARCH_INSTRUCTIONS
    (output / 'prompt.txt').write_text(prompt, encoding='utf-8')
    dump(output / 'task.reference.json', task)
    version = subprocess.run([binary, '--version'], capture_output=True, text=True, timeout=10)
    metadata = {'started_at': datetime.now(timezone.utc).isoformat(),
                'cli_version': version.stdout.strip(), 'requested_model': args.model,
                'resolved_model': None,
                'model_identity_note': 'No resolved model identifier was returned by this event stream; do not infer one from the CLI version.',
                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                'outcome': 'not_assessed', 'evaluation_note': 'Review the actual answer against verified sources; no automatic correctness judgment is made.'}
    with tempfile.TemporaryDirectory(prefix='evidencetrail-model-') as temporary:
        work = Path(temporary)
        command = [binary, '--search', '--ask-for-approval', 'never', 'exec',
                   '--ignore-user-config', '--skip-git-repo-check', '--ephemeral',
                   '--sandbox', 'read-only', '--json', '--output-last-message', str(work / 'answer.md')]
        if args.model:
            command.extend(['--model', args.model])
        command.append('-')
        metadata['cli_command'] = ['codex' if value == binary else value.replace(str(work), '<isolated-workspace>') for value in command]
        metadata['input_transport'] = 'Exact prompt.txt via stdin; golden answer was not passed to the model'
        with (work / 'events.jsonl').open('w') as events, (work / 'stderr.txt').open('w') as errors:
            try:
                result = subprocess.run(command, input=prompt, text=True, stdout=events,
                                        stderr=errors, cwd=work, timeout=args.timeout)
                metadata['exit_code'] = result.returncode
            except subprocess.TimeoutExpired:
                metadata['timed_out'] = True
        raw_events = (work / 'events.jsonl').read_text()
        dump(output / 'tool-events.json', public_events(raw_events))
        stderr = (work / 'stderr.txt').read_text().replace(str(work), '<isolated-workspace>').replace(str(Path.home()), '<user-home>')
        (output / 'stderr.txt').write_text(stderr)
        answer = work / 'answer.md'
        if answer.is_file():
            (output / 'answer.md').write_bytes(answer.read_bytes())
        metadata['finished_at'] = datetime.now(timezone.utc).isoformat()
        metadata['trace_scope'] = 'Event kinds, web queries/actions, source metadata and token usage only; private reasoning, response bodies and thread IDs omitted.'
        dump(output / 'execution.json', metadata)
    files = {str(path.relative_to(output)): hashlib.sha256(path.read_bytes()).hexdigest()
             for path in sorted(output.iterdir()) if path.is_file()}
    dump(output / 'artifact-sha256.json', files)
    print(f'Recorded model run in {output}; outcome remains not_assessed until the answer is reviewed.')
    return 0 if metadata.get('exit_code') == 0 and (output / 'answer.md').is_file() else 1


if __name__ == '__main__':
    raise SystemExit(main())
