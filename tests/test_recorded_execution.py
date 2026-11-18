"""Check committed execution records without repeating live network requests."""
import hashlib
import json
from pathlib import Path
import unittest

from evidencetrail import validate_task

ROOT = Path(__file__).resolve().parents[1]
RUN = ROOT / 'examples/release-dates/source-audit'


class RecordedExecutionTests(unittest.TestCase):
    def test_recorded_artifact_manifest_is_complete_and_matches_files(self):
        expected = json.loads((RUN / 'artifact-sha256.json').read_text())
        actual = {str(p.relative_to(RUN)): hashlib.sha256(p.read_bytes()).hexdigest()
                  for p in RUN.rglob('*') if p.is_file() and p.name != 'artifact-sha256.json'}
        self.assertEqual(expected, actual)

    def test_record_separates_verified_sources_from_missing_screenings(self):
        execution = json.loads((RUN / 'execution.json').read_text())
        self.assertFalse(execution['external_model_screening_performed'])
        self.assertFalse(execution['independent_review_performed'])
        self.assertTrue(all(c['exit_code'] == c['expected_exit_code'] for c in execution['commands']))
        report = json.loads((RUN / 'package/creation-report.json').read_text())
        self.assertEqual(len(report['source_audit']), 2)
        self.assertTrue(all(source['verified'] for source in report['source_audit']))
        task = json.loads((RUN / 'package/task.json').read_text())
        errors, _ = validate_task(task, {'blocked.example'}, RUN / 'batch')
        self.assertEqual(errors, ['screening must contain exactly three official runs'])
        self.assertFalse((RUN / 'package/submission.md').exists())

    def test_bad_quote_is_a_separate_rejected_live_probe(self):
        negative = json.loads((RUN / 'negative-probe/creation-report.json').read_text())
        first = negative['source_audit'][0]
        self.assertFalse(first['verified'])
        self.assertIn('Could not locate exact_quote', first['reason'])
        canonical = json.loads((RUN / 'package/creation-report.json').read_text())
        self.assertTrue(canonical['source_audit'][0]['verified'])
