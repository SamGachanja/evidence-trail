"""Validate the saved real model run offline; never call a live model in CI."""
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'examples/release-dates/model-run'


class ModelExecutionRecordTests(unittest.TestCase):
    def test_saved_actual_execution_manifest_is_complete(self):
        expected = json.loads((RUN / 'artifact-sha256.json').read_text())
        actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in RUN.iterdir() if p.is_file() and p.name != 'artifact-sha256.json'}
        self.assertEqual(actual, expected)

    def test_actual_baseline_is_recorded_as_correct_not_a_break(self):
        evaluation = json.loads((RUN / 'evaluation.json').read_text())
        metadata = json.loads((RUN / 'execution.json').read_text())
        answer = (RUN / 'answer.md').read_text()
        self.assertEqual(metadata['exit_code'], 0)
        self.assertEqual(evaluation['verdict'], 'correct')
        self.assertFalse(evaluation['model_break_observed'])
        for check in evaluation['checks']:
            self.assertIn(check['returned_release_date'], answer)
            self.assertIn(check['official_source'], answer)
        prompt = (RUN / 'prompt.txt').read_bytes()
        self.assertEqual(hashlib.sha256(prompt).hexdigest(), metadata['prompt_sha256'])

    def test_event_export_excludes_reasoning_bodies_and_thread_ids(self):
        spec = importlib.util.spec_from_file_location('model_recorder', ROOT / 'scripts/run_codex.py')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        synthetic = '\n'.join(json.dumps(event) for event in [
            {'type': 'thread.started', 'thread_id': 'private-id'},
            {'type': 'item.completed', 'item': {'type': 'reasoning', 'text': 'private-reasoning'}},
            {'type': 'item.completed', 'item': {'type': 'web_search', 'query': 'public query',
             'results': [{'url': 'https://example.org', 'title': 'Public title', 'snippet': 'third-party body'}]}},
        ])
        exported = json.dumps(module.public_events(synthetic))
        for omitted in ('private-id', 'private-reasoning', 'third-party body'):
            self.assertNotIn(omitted, exported)
        self.assertIn('https://example.org', exported)
