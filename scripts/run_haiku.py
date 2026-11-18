"""Run an isolated task with explicit Claude Haiku selection and capture its identity.

Uses the separately authenticated Claude Code CLI, never reads API keys, and
permits only public web tools. Offline tests do not invoke this script.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import shutil
import subprocess
import tempfile

RESEARCH_INSTRUCTIONS = '\n\nUse public web research and cite the official sources you consulted. Do not access local files.'


def export_stream(raw):
    """Keep public answer, model identity and tool names; omit reasoning/credentials."""
    records, models, fragments = [], set(), []
    result = None
    for line in raw.splitlines():
        try:
            event = json.loads(line)
        except ValueError:
            continue
        kind = event.get('type')
        record = {'event': kind}
        if kind == 'system' and event.get('subtype') == 'init':
            if isinstance(event.get('model'), str):
                models.add(event['model'])
                record['model'] = event['model']
            record['tools'] = event.get('tools', [])
        if kind == 'assistant':
            message = event.get('message', {})
            if isinstance(message.get('model'), str) and message['model'] != '<synthetic>':
                models.add(message['model'])
                record['model'] = message['model']
            for block in message.get('content', []):
                if block.get('type') == 'text':
                    fragments.append(block['text'])
                elif block.get('type') == 'tool_use':
                    record.setdefault('tools_used', []).append(block.get('name'))
        if kind == 'result':
            result = event
            for key in ('subtype', 'is_error', 'duration_ms', 'num_turns', 'usage', 'total_cost_usd'):
                if key in event:
                    record[key] = event[key]
        records.append(record)
    answer = result.get('result', '') if result else ''
    if not answer:
        answer = '\n\n'.join(fragments)
    return records, sorted(models), answer, bool(result and result.get('is_error'))


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, ensure_ascii=False) + '\n')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--task', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    parser.add_argument('--model', default='haiku')
    parser.add_argument('--timeout', type=int, default=360)
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error('timeout must be positive')
    binary = shutil.which('claude')
    if not binary:
        parser.error('Install and sign in to Claude Code separately')
    task = json.loads(args.task.read_text())
    prompt = task['prompt'] + RESEARCH_INSTRUCTIONS
    output = args.output.resolve()
    if output.exists():
        parser.error('Use a fresh output directory')
    output.mkdir(parents=True)
    (output / 'prompt.txt').write_text(prompt)
    dump(output / 'task.reference.json', task)
    version = subprocess.run([binary, '--version'], capture_output=True, text=True, timeout=10)
    command = [binary, '--print', '--model', args.model, '--output-format', 'stream-json', '--verbose',
               '--no-session-persistence', '--setting-sources', 'user', '--settings', '{"disableAllHooks":true}', '--disable-slash-commands',
               '--strict-mcp-config', '--mcp-config', '{"mcpServers":{}}',
               '--tools', 'WebSearch,WebFetch', '--allowedTools', 'WebSearch,WebFetch',
               '--permission-mode', 'dontAsk']
    metadata = {'provider': 'Anthropic via authenticated Claude Code', 'requested_model': args.model,
                'cli_version': version.stdout.strip(), 'started_at': datetime.now(timezone.utc).isoformat(),
                'cli_command': ['claude'] + command[1:], 'outcome': 'not_assessed',
                'prompt_sha256': hashlib.sha256(prompt.encode()).hexdigest(),
                'input_transport': 'Exact prompt.txt via stdin; reference answer not provided',
                'isolation': 'Fresh temporary cwd; only WebSearch/WebFetch tools; no MCP servers; no session persistence. CLI authentication remains external.'}
    with tempfile.TemporaryDirectory(prefix='evidencetrail-haiku-') as temporary:
        work = Path(temporary)
        with (work / 'stream.jsonl').open('w') as stream, (work / 'stderr.txt').open('w') as errors:
            try:
                result = subprocess.run(command, input=prompt, text=True, stdout=stream,
                                        stderr=errors, cwd=work, timeout=args.timeout)
                metadata['exit_code'] = result.returncode
            except subprocess.TimeoutExpired:
                metadata['timed_out'] = True
        records, models, answer, error = export_stream((work / 'stream.jsonl').read_text())
        metadata['reported_models'] = models
        metadata['result_is_error'] = error
        metadata['finished_at'] = datetime.now(timezone.utc).isoformat()
        dump(output / 'tool-events.json', records)
        if answer:
            (output / 'answer.md').write_text(answer)
        stderr = (work / 'stderr.txt').read_text().replace(temporary, '<isolated-workspace>').replace(str(Path.home()), '<user-home>')
        (output / 'stderr.txt').write_text(stderr)
    dump(output / 'execution.json', metadata)
    dump(output / 'artifact-sha256.json', {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()})
    print(json.dumps({'output': str(output), 'reported_models': models, 'exit_code': metadata.get('exit_code'), 'result_is_error': error, 'answer_saved': bool(answer)}))
    return 0 if metadata.get('exit_code') == 0 and answer and not error else 1


if __name__ == '__main__':
    raise SystemExit(main())
