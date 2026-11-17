import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class CommandLineTests(unittest.TestCase):
    def run_cli(self, *args):
        return subprocess.run([sys.executable, '-m', 'evidencetrail', *map(str, args)],
                              cwd=ROOT, capture_output=True, text=True)

    def test_new_uses_bundled_templates_and_refuses_duplicates(self):
        with tempfile.TemporaryDirectory() as temporary:
            first = self.run_cli('new', 'MY_TASK', '--tasks-dir', temporary)
            self.assertEqual(first.returncode, 0, first.stderr)
            folder = Path(temporary) / 'MY_TASK'
            task = json.loads((folder / 'task.json').read_text())
            self.assertEqual(task['id'], 'MY_TASK')
            before = (folder / 'task.json').read_bytes()
            self.assertTrue((folder / 'review.json').is_file())
            self.assertNotEqual(self.run_cli('new', 'MY_TASK', '--tasks-dir', temporary).returncode, 0)
            self.assertEqual((folder / 'task.json').read_bytes(), before)

    def test_path_escape_id_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            result = self.run_cli('new', '../escaped', '--tasks-dir', temporary)
            self.assertEqual(result.returncode, 2)
            self.assertFalse((Path(temporary).parent / 'escaped').exists())

    def test_offline_demo_runs_without_network(self):
        result = subprocess.run([sys.executable, str(ROOT / 'examples/offline_demo.py')],
                                cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn('No real sources or model runs were claimed', result.stdout)
