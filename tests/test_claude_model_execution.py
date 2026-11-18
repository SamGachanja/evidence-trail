"""Test Claude event redaction and failure classification without live inference."""
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('claude_model_run', ROOT / 'scripts/run_haiku.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)


class ClaudeRecorderTests(unittest.TestCase):
    def test_exports_model_and_answer_but_not_private_reasoning_or_tokens(self):
        raw = '\n'.join(json.dumps(x) for x in [
            {'type': 'system', 'subtype': 'init', 'model': 'claude-haiku-test', 'apiKeySource': 'secret', 'session_id': 'private-session'},
            {'type': 'assistant', 'message': {'model': 'claude-haiku-test', 'content': [
                {'type': 'thinking', 'thinking': 'private-reasoning'},
                {'type': 'text', 'text': 'Public answer'},
                {'type': 'tool_use', 'name': 'WebFetch', 'input': {'url': 'private-input'}}]}},
            {'type': 'result', 'is_error': False, 'result': 'Public answer', 'usage': {'output_tokens': 2}},
        ])
        records, models, answer, error = runner.export_stream(raw)
        self.assertEqual(models, ['claude-haiku-test'])
        self.assertEqual(answer, 'Public answer')
        self.assertFalse(error)
        exported = json.dumps(records)
        for value in ('private-session', 'private-reasoning', 'private-input', 'secret'):
            self.assertNotIn(value, exported)

    def test_authentication_failure_is_preserved_as_error(self):
        records, models, answer, error = runner.export_stream(json.dumps({
            'type': 'result', 'is_error': True, 'result': 'Not logged in · Please run /login'}))
        self.assertTrue(error)
        self.assertEqual(models, [])
        self.assertIn('Not logged in', answer)
