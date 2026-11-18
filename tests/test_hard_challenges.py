"""Offline checks for challenge references and recorded outcomes; no model calls."""
import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import unittest

ROOT = Path(__file__).resolve().parents[1]
CHALLENGES = ROOT / 'examples/challenges'


def module(folder, filename):
    spec = importlib.util.spec_from_file_location(folder.replace('-', '_') + filename, CHALLENGES / folder / filename)
    loaded = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(loaded)
    return loaded


class HardChallengeTests(unittest.TestCase):
    def test_small_ring_dp_agrees_with_independent_exhaustive_record(self):
        challenge = CHALLENGES / 'cyclic-schedule-orbits'
        actual = module('cyclic-schedule-orbits', 'reference.py').solve(16)
        independent = json.loads((challenge / 'small-enumeration-output.json').read_text())
        self.assertEqual(actual['rooted_gap_sequences'], independent['rooted_gap_sequences'])
        self.assertEqual(actual['dihedral_orbits'], independent['dihedral_orbits'])
        self.assertEqual({(p['r'], p['f']): p['orbits'] for p in actual['profiles'] if p['orbits']},
                         {(p['rotation_stabilizer'], p['reflection_stabilizer']): p['orbits'] for p in independent['profiles']})

    def test_full_ring_reference_and_orbit_sizes(self):
        expected = json.loads((CHALLENGES / 'cyclic-schedule-orbits/reference-output.json').read_text())
        actual = module('cyclic-schedule-orbits', 'reference.py').solve(24)
        self.assertEqual(json.loads(json.dumps(actual)), expected)
        self.assertEqual(sum(p['orbits'] * (144 // (p['r'] + p['f'])) for p in actual['profiles']), actual['labelled_binary_schedules'])

    def test_ring_grader_rejects_naive_group_order_division(self):
        reference = json.loads((CHALLENGES / 'cyclic-schedule-orbits/reference-output.json').read_text())
        grade = module('cyclic-schedule-orbits', 'grade.py').grade
        self.assertEqual(grade(reference, reference)['verdict'], 'correct')
        shortcut = copy.deepcopy(reference)
        shortcut['dihedral_orbits'] = reference['rooted_gap_sequences'] // 48
        self.assertTrue(grade(shortcut, reference)['model_break_candidate'])
        self.assertFalse(grade({}, reference)['model_break_candidate'])

    def test_recorded_runs_are_hashed_and_sqlite_passes_are_not_breaks(self):
        for run in sorted((ROOT / 'examples/model-executions').iterdir()):
            if not run.is_dir() or not (run / 'evaluation.json').exists():
                continue
            expected = json.loads((run / 'artifact-sha256.json').read_text())
            actual = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in run.iterdir()
                      if p.is_file() and p.name != 'artifact-sha256.json'}
            self.assertEqual(actual, expected, run.name)
            if run.name.startswith('sqlite-'):
                evaluation = json.loads((run / 'evaluation.json').read_text())
                self.assertEqual(evaluation['verdict'], 'correct')
                self.assertFalse(evaluation['model_break_observed'])

    def test_sqlite_graders_catch_changed_numeric_claims(self):
        for folder, field in [('sqlite-transaction-audit', 'checkpoints'), ('sqlite-deferral-matrix', 'cases')]:
            grader = module(folder, 'grade.py')
            reference = json.loads((CHALLENGES / folder / 'reference-output.json').read_text())
            run = ROOT / 'examples/model-executions' / (folder + '-live-2026-11-17')
            parsed = grader.extract_object((run / 'answer.md').read_text())
            self.assertEqual(grader.grade(parsed, reference)['verdict'], 'correct')
            altered = copy.deepcopy(parsed)
            if field == 'cases':
                altered['cases']['B']['commit'] = 'FOREIGN KEY constraint failed'
            else:
                altered['snapshots'][0]['total_delta'] = -1
            self.assertTrue(grader.grade(altered, reference)['model_break_candidate'])
