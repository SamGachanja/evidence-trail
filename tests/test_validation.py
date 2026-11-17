import argparse
import contextlib
import hashlib
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from evidencetrail import REVIEW_KEYS, audit_html_sources, command_attach_screening, command_create, command_render, command_review, literal_excerpt, load_blocklist, render_form_fields, render_submission, resolve_codex_bin, validate_review, validate_task


def valid_task():
    prompt = "Which qualifying records from the finished 2020 archive have the stated attributes?"
    return {
        "id": "T1", "owner": "Trainer", "topic": "Closed archive records",
        "break_pattern": "exhaustive niche set",
        "modality_decision": "Text-webpage route; both sources have raw HTML facts.",
        "prompt": prompt,
        "answer_template": "[item] ([attribute])",
        "example_answer": "Nonqualifying sample (Wrong)",
        "scope": {"inclusion_rule": "All archive records meeting rule X", "start_boundary": "2020-01-01", "end_boundary": "2020-12-31"},
        "golden_answer": ["First item (A)", "Second item (B)"],
        "sources": [
            {"id": "S1", "url": "https://records.example.org/one", "domain": "example.org", "title": "First archive record", "language": "English", "credibility_reason": "Closed official archive record", "retrieved_at": "2020-01-01", "quote_locator": "Record heading", "source_format": "html", "source_fact": "First item (A)", "public": True, "non_social": True, "raw_html_checked": True, "necessary_for": ["First item"]},
            {"id": "S2", "url": "https://archive.example.net/two", "domain": "example.net", "title": "Second archive record", "language": "English", "credibility_reason": "Closed official archive record", "retrieved_at": "2020-01-01", "quote_locator": "Record heading", "source_format": "html", "source_fact": "Second item (B)", "public": True, "non_social": True, "raw_html_checked": True, "necessary_for": ["Second item"]},
        ],
        "evidence": [
            {"answer_item": "First item (A)", "source_ids": ["S1"], "qualification": "S1 establishes the first record", "field_support": [{"field": "item", "value": "First item", "source_id": "S1", "exact_quote": "First item (A)"}, {"field": "attribute", "value": "A", "source_id": "S1", "exact_quote": "First item (A)"}]},
            {"answer_item": "Second item (B)", "source_ids": ["S2"], "qualification": "S2 establishes the second record", "field_support": [{"field": "item", "value": "Second item", "source_id": "S2", "exact_quote": "Second item (B)"}, {"field": "attribute", "value": "B", "source_id": "S2", "exact_quote": "Second item (B)"}]},
        ],
        "research": {
            "search_trial": [{"query": "2020 archive records", "observation": "Needed specialist archives"}],
            "completeness_proof": "The closed archive index enumerates every record",
            "completeness_source_ids": ["S1", "S2"],
            "domain_dependency": "Each domain holds a different record",
            "single_domain_shortcut_test": "Neither site holds both records",
            "prompt_to_source_connection": "The archive and attribute phrasing leads to these records",
            "output_normalization": "English names and source spelling; no unit conversion",
            "constraint_evidence": [{"constraint": "Finished 2020 archive and stated attributes", "source_ids": ["S1", "S2"], "evidence": "Both records belong to the closed 2020 archive and show attributes."}],
            "pretest": {"method": "AI search", "observation": "Returned an incomplete set", "not_run_reason": ""},
            "realistic_reason": "Researchers need these records",
            "timeless_reason": "The archive is closed",
        },
        "screening": [
            {"run_id": f"run-{i}", "model_label": "Example model", "harness": "Official test harness", "run_at": "2020-02-01T00:00:00Z", "screened_prompt": prompt, "model_answer": "Incorrect item", "trajectory": f"https://tool.example/run/{i}", "browsed": True, "outcome": "factual_error", "factual_explanation": "Omitted the first verified record"}
            for i in range(1, 4)
        ],
    }


def valid_review(task):
    return {
        "reviewer": "Independent reviewer", "reviewed_at": "2026-10-19",
        "independent_answer": list(reversed(task["golden_answer"])),
        "source_verification": [
            {"source_id": s["id"], "opened": True, "public_access": True, "fact_in_source_confirmed": True, "raw_html_fact_confirmed": True, "text_retrieval_confirmed": True, "harness_access_confirmed": True, "blocklist_confirmed": True, "credibility_confirmed": True, "notes": "Opened the source and found the quoted value in raw HTML."}
            for s in task["sources"]
        ],
        "item_verification": [
            {"answer_item": e["answer_item"], "source_ids": e["source_ids"], "reproduced": True, "exact_values": True, "qualifies": True, "notes": "Matched each field to the cited source."}
            for e in task["evidence"]
        ],
        "run_verification": [
            {"run_id": r["run_id"], "trajectory_opened": True, "prompt_match_confirmed": True, "searched": True, "opened_pages": True, "substantive_error": True, "not_tool_or_format_issue": True, "error_type": "missing_item", "specific_error": "Omitted the first verified record", "failure_step": "After opening S1", "trajectory_evidence": "The run opened S1 but omitted its record in the final answer."}
            for r in task["screening"]
        ],
        "judge_feedback": {"status": "not_available", "independent_assessment": "No automated judge result was supplied; independently reviewed each run."},
        "checks": {key: {"status": "pass", "evidence": "Independently verified against the cited material."} for key in REVIEW_KEYS},
    }


class TaskValidationTests(unittest.TestCase):
    def test_wrong_example_cannot_leak_golden_entity_and_correct_facts(self):
        task = valid_task()
        task["answer_template"] = "[event] | [car] | [driver] | [count]"
        task["golden_answer"] = ["Australian Grand Prix | 10 | Pierre Gasly | 1", "Other Grand Prix | 20 | Other Driver | 2"]
        task["example_answer"] = "Australian Grand Prix | 10 | Pierre Gasly | 0"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertTrue(any("reuses a golden key entity" in error for error in errors))
        task["example_answer"] = "Fictional Grand Prix | 99 | Example Driver | 0"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertFalse(any("reuses a golden key entity" in error for error in errors))

    def test_derived_field_requires_each_source_backed_part(self):
        task = valid_task()
        task["golden_answer"][0] = "First item (A, B)"
        task["evidence"][0]["answer_item"] = task["golden_answer"][0]
        task["evidence"][0]["source_ids"] = ["S1", "S2"]
        task["evidence"][0]["field_support"][1] = {
            "field": "attribute", "value": "A, B", "derivation_separator": ", ",
            "derivation_parts": [
                {"source_id": "S1", "value": "A", "exact_quote": "First item (A)"},
                {"source_id": "S2", "value": "B", "exact_quote": "Second item (B)"},
            ],
        }
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertEqual(errors, [])
        task["evidence"][0]["field_support"][1]["derivation_parts"][1]["exact_quote"] = "Missing B value"
        task["evidence"][0]["field_support"][1]["derivation_parts"][1]["value"] = "C"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertTrue(any("derivation_parts must join" in error for error in errors))

    def test_official_browser_access_failure_blocks_task(self):
        task = valid_task()
        task["sources"][0]["official_access_status"] = "failed"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertTrue(any("failed official browser access" in error for error in errors))

    def test_literal_excerpt_prefers_exact_case_when_page_has_two_mentions(self):
        page = "All This Could be Different appears in the article. The list prints All This Could Be Different."
        self.assertEqual(literal_excerpt(page, "All This Could Be Different"), "All This Could Be Different")

    def test_html_audit_preserves_words_split_by_inline_markup(self):
        task = valid_task()
        task["sources"] = task["sources"][:1]
        task["evidence"] = task["evidence"][:1]
        task["sources"][0]["source_fact"] = "Writings"
        task["evidence"][0]["field_support"] = [
            {"field": "item", "value": "Writings", "source_id": "S1", "exact_quote": "Writings"}
        ]
        page = b"<html><body><p><em>Writing</em>s</p></body></html>"
        with patch("evidencetrail.fetch_html_source", return_value=(page, task["sources"][0]["url"], "text/html")):
            findings = audit_html_sources(task, set())
        self.assertTrue(findings[0]["verified"])

    def test_html_audit_accepts_source_heading_capitalization(self):
        task = valid_task()
        task["sources"] = task["sources"][:1]
        task["evidence"] = task["evidence"][:1]
        task["evidence"][0]["field_support"][0]["exact_quote"] = "FIRST ITEM"
        page = b"<html><body><h1>First item (A)</h1><h2>FIRST ITEM</h2></body></html>"
        with patch("evidencetrail.fetch_html_source", return_value=(page, task["sources"][0]["url"], "text/html")):
            findings = audit_html_sources(task, set())
        self.assertTrue(findings[0]["verified"])
        self.assertEqual(task["evidence"][0]["field_support"][0]["exact_quote"], "FIRST ITEM")
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertFalse(any("exact_quote must contain" in error for error in errors))

    def test_crater_template_keeps_unsuffixed_prompt_qualifier(self):
        task = valid_task()
        task["prompt"] = "Which unsuffixed lunar crater qualifies, excluding lettered satellite features?"
        task["answer_template"] = "[lunar crater] ([attribute])"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertTrue(any("crater field must include 'unsuffixed'" in error for error in errors))
        task["answer_template"] = "[unsuffixed lunar crater] ([attribute])"
        errors, _ = validate_task(task, set(), Path("/nonexistent"))
        self.assertFalse(any("crater field must include 'unsuffixed'" in error for error in errors))

    def test_html_audit_checks_source_fact_and_field_quotes(self):
        task = valid_task()
        task["sources"] = task["sources"][:1]
        task["evidence"] = task["evidence"][:1]
        task["sources"][0]["source_fact"] = "Feature Name | First item (A)"
        task["evidence"][0]["field_support"][0]["exact_quote"] = "Feature Name | First item (A)"
        page = b"<html><table><tr><th>Feature Name</th><td>First item (A)</td></tr></table></html>"
        with patch("evidencetrail.fetch_html_source", return_value=(page, task["sources"][0]["url"], "text/html")):
            findings = audit_html_sources(task, set())
        self.assertTrue(findings[0]["verified"])
        self.assertTrue(task["sources"][0]["raw_html_checked"])
        self.assertEqual(task["sources"][0]["source_fact"], "Feature Name First item (A)")
        task["evidence"][0]["field_support"][0]["exact_quote"] = "Missing value"
        with patch("evidencetrail.fetch_html_source", return_value=(page, task["sources"][0]["url"], "text/html")):
            findings = audit_html_sources(task, set())
        self.assertFalse(findings[0]["verified"])
        self.assertFalse(task["sources"][0]["raw_html_checked"])

    def test_html_audit_matches_linked_comma_separated_names(self):
        task = valid_task()
        task["sources"] = task["sources"][:1]
        task["evidence"] = task["evidence"][:1]
        task["sources"][0]["source_fact"] = "Fredric Steinkamp, Donald Guidice"
        task["evidence"][0]["field_support"] = [
            {"field": "editors", "value": "Fredric Steinkamp, Donald Guidice", "source_id": "S1", "exact_quote": "Fredric Steinkamp, Donald Guidice"}
        ]
        page = b"<html><body>Editors: <a>Fredric Steinkamp</a> , <a>Donald Guidice</a></body></html>"
        with patch("evidencetrail.fetch_html_source", return_value=(page, task["sources"][0]["url"], "text/html")):
            findings = audit_html_sources(task, set())
        self.assertTrue(findings[0]["verified"])

    def test_resolve_codex_from_vscode_extension_when_path_missing(self):
        with tempfile.TemporaryDirectory() as tmp:
            home = Path(tmp)
            binary = home / ".vscode/extensions/openai.chatgpt-test/bin/macos-aarch64/codex"
            binary.parent.mkdir(parents=True)
            binary.write_text("#!/bin/sh\nexit 0\n", encoding="utf-8")
            binary.chmod(0o755)
            with patch("evidencetrail.shutil.which", return_value=None):
                self.assertEqual(resolve_codex_bin("codex", home), str(binary))
                self.assertIsNone(resolve_codex_bin("missing-custom-codex", home))

    def test_create_rejects_copied_example_values(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            args = argparse.Namespace(
                id="AUTO_0", owner="Your Name", topic="A completed niche topic", seed_url=[],
                screening_file=None, codex_bin="missing", model=None, timeout=10, source_timeout=10,
                blocklist=root / "blocklist.txt", tasks_dir=root / "tasks",
            )
            with contextlib.redirect_stderr(io.StringIO()) as output:
                self.assertEqual(command_create(args), 2)
            self.assertIn("example --owner", output.getvalue())
            self.assertFalse((root / "tasks/AUTO_0").exists())

    def test_create_generates_populated_candidate(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            candidate = valid_task()
            for key in ("id", "owner", "screening"):
                candidate.pop(key)
            output = {"task": candidate, "research_notes": ["Two archive sources checked"], "blockers": []}
            fake_codex = root / "fake-codex"
            fake_codex.write_text(
                "#!/usr/bin/env python3\nimport json, sys\nfrom pathlib import Path\n"
                f"payload = {output!r}\n"
                "Path(sys.argv[sys.argv.index('--output-last-message') + 1]).write_text(json.dumps(payload))\n",
                encoding="utf-8",
            )
            fake_codex.chmod(0o755)
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            args = argparse.Namespace(
                id="AUTO_1", owner="Trainer", topic="Closed archive records", seed_url=[],
                screening_file=None, codex_bin=str(fake_codex), model=None, timeout=10, source_timeout=10,
                blocklist=blocklist, tasks_dir=root / "tasks",
            )
            with patch("evidencetrail.fetch_html_source", side_effect=lambda url, timeout: (f"<html><body>{'First item (A)' if url.endswith('/one') else 'Second item (B)'}</body></html>".encode(), url, "text/html")):
                with contextlib.redirect_stdout(io.StringIO()):
                    self.assertEqual(command_create(args), 0)
            folder = root / "tasks/AUTO_1"
            generated = json.loads((folder / "task.json").read_text(encoding="utf-8"))
            report = json.loads((folder / "creation-report.json").read_text(encoding="utf-8"))
            self.assertEqual(generated["prompt"], valid_task()["prompt"])
            self.assertEqual(generated["screening"], [])
            self.assertTrue(all(source["raw_html_checked"] for source in generated["sources"]))
            self.assertTrue(all(record["verified"] for record in report["source_audit"]))
            self.assertEqual(report["phase"], "screening_required")
            self.assertIn("## goldenAnswer", (folder / "form-fields.md").read_text())
            self.assertFalse((folder / "submission.md").exists())

    def test_form_fields_match_labeling_tool_fields_before_screening(self):
        task = valid_task()
        task["screening"] = []
        draft = render_form_fields(task)
        self.assertLess(draft.index("## goldenAnswer"), draft.index("## Example output format (bracket Notations)"))
        self.assertLess(draft.index("## Example output format (bracket Notations)"), draft.index("## Example Output (Should be incorrect but relevant)"))
        self.assertIn("First item (A)\nSecond item (B)", draft)
        self.assertIn("[item] ([attribute])", draft)
        self.assertIn("Nonqualifying sample (Wrong)", draft)

    def test_create_rejects_blocked_seed_before_generation(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            args = argparse.Namespace(
                id="AUTO_2", owner="Trainer", topic=None, seed_url=["https://apps.blocked.example/story"],
                screening_file=None, codex_bin="python3", model=None, timeout=10, source_timeout=10,
                blocklist=blocklist, tasks_dir=root / "tasks",
            )
            with contextlib.redirect_stderr(io.StringIO()):
                self.assertEqual(command_create(args), 2)
            self.assertFalse((root / "tasks/AUTO_2").exists())

    def test_attach_screening_populates_task_and_render(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "tasks/AUTO_3"
            folder.mkdir(parents=True)
            task = valid_task()
            runs = task.pop("screening")
            (folder / "task.json").write_text(json.dumps(task), encoding="utf-8")
            export = root / "runs.json"
            export.write_text(json.dumps({"screening": runs}), encoding="utf-8")
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            args = argparse.Namespace(folder=folder, runs=export, replace=False, blocklist=blocklist, tasks_dir=root / "tasks")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_attach_screening(args), 0)
            self.assertEqual(len(json.loads((folder / "task.json").read_text())["screening"]), 3)
            self.assertIn("## Model responses", (folder / "submission.md").read_text())

    def test_attach_screening_rejects_prompt_mismatch_without_edit(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            folder = root / "tasks/AUTO_4"
            folder.mkdir(parents=True)
            task = valid_task()
            runs = task.pop("screening")
            runs[0]["screened_prompt"] = "Different prompt"
            task_path = folder / "task.json"
            task_path.write_text(json.dumps(task), encoding="utf-8")
            before = task_path.read_bytes()
            export = root / "runs.json"
            export.write_text(json.dumps(runs), encoding="utf-8")
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            args = argparse.Namespace(folder=folder, runs=export, replace=False, blocklist=blocklist, tasks_dir=root / "tasks")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_attach_screening(args), 1)
            self.assertEqual(task_path.read_bytes(), before)

    def test_valid_package_has_no_errors_or_source_count_quota(self):
        with tempfile.TemporaryDirectory() as tmp:
            errors, warnings = validate_task(valid_task(), {"blocked.example"}, Path(tmp))
        self.assertEqual(errors, [])
        self.assertFalse(any("design target" in w or "necessary unique pages" in w for w in warnings))

    def test_blocked_subdomain_and_missing_item_evidence_fail(self):
        task = valid_task()
        task["sources"][0]["url"] = "https://records.example.org/one"
        task["evidence"] = task["evidence"][:1]
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, {"example.org"}, Path(tmp))
        self.assertTrue(any("blocklist" in e for e in errors))
        self.assertTrue(any("Missing evidence" in e for e in errors))

    def test_correct_screening_response_cannot_pass(self):
        task = valid_task()
        task["screening"][0]["outcome"] = "correct"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("outcome must be factual_error" in e for e in errors))

    def test_screening_must_use_final_prompt(self):
        task = valid_task()
        task["screening"][1]["screened_prompt"] = "An older version of the question"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("differs from the final prompt" in e for e in errors))

    def test_each_answer_field_needs_a_matching_literal_quote(self):
        task = valid_task()
        task["evidence"][0]["field_support"][1]["exact_quote"] = "Unrelated value"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("literal field value" in e for e in errors))

    def test_source_metadata_and_public_domain_are_required(self):
        task = valid_task()
        task["sources"][0].pop("quote_locator")
        task["sources"][1]["url"] = "http://localhost/two"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("quote_locator" in e for e in errors))
        self.assertTrue(any("public http(s)" in e for e in errors))

    def test_blocklist_parser_and_batch_cap(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            blocklist = root / "blocklist.txt"
            blocklist.write_text("# current list\nhttps://blocked.example.org/path\n", encoding="utf-8")
            errors = []
            self.assertEqual(load_blocklist(blocklist, errors), {"blocked.example.org"})
            self.assertEqual(errors, [])
            tasks_dir = root / "tasks"
            for i in range(5):
                folder = tasks_dir / f"T{i}"
                folder.mkdir(parents=True)
                other = valid_task()
                other["id"] = f"T{i}"
                (folder / "task.json").write_text(json.dumps(other), encoding="utf-8")
            current = valid_task()
            current["id"] = "T6"
            errors, _ = validate_task(current, set(), tasks_dir)
            self.assertTrue(any("cap is five" in e for e in errors))

    def test_review_failure_requires_actionable_location_and_fix(self):
        review = {"reviewer": "Independent reviewer", "reviewed_at": "2026-10-19", "checks": {key: {"status": "pass", "evidence": "I opened the source and checked the stated fact."} for key in REVIEW_KEYS}}
        self.assertEqual(validate_review(review), [])
        review["checks"]["answer_exactness"] = {"status": "fail", "evidence": "Wrong year", "location": "evidence[0]", "fix": "Correct the year and rescreen"}
        self.assertTrue(any("Wrong year" in e and "Correct the year" in e for e in validate_review(review)))

    def test_review_is_invalidated_after_task_change(self):
        with tempfile.TemporaryDirectory() as tmp:
            tasks_dir = Path(tmp) / "tasks"
            folder = tasks_dir / "T1"
            folder.mkdir(parents=True)
            task_path = folder / "task.json"
            task_path.write_text(json.dumps(valid_task()), encoding="utf-8")
            blocklist = Path(tmp) / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            review = valid_review(valid_task())
            review["task_sha256"] = hashlib.sha256(task_path.read_bytes()).hexdigest()
            (folder / "review.json").write_text(json.dumps(review), encoding="utf-8")
            args = argparse.Namespace(folder=folder, blocklist=blocklist, tasks_dir=tasks_dir)
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_review(args), 0)
            task = valid_task()
            task["prompt"] += " Please answer fully."
            task_path.write_text(json.dumps(task), encoding="utf-8")
            with contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(command_review(args), 1)
            self.assertIn("current task SHA-256", output.getvalue())

    def test_review_requires_every_source_item_and_run(self):
        task = valid_task()
        review = valid_review(task)
        self.assertEqual(validate_review(review, task), [])
        review["source_verification"] = review["source_verification"][:1]
        review["run_verification"] = review["run_verification"][:2]
        problems = validate_review(review, task)
        self.assertTrue(any("Missing source verification for S2" in p for p in problems))
        self.assertTrue(any("Missing run verification for run-3" in p for p in problems))

    def test_review_requires_credibility_and_prompt_checks(self):
        task = valid_task()
        review = valid_review(task)
        review["source_verification"][0]["credibility_confirmed"] = False
        review["run_verification"][0]["prompt_match_confirmed"] = False
        problems = validate_review(review, task)
        self.assertTrue(any("credibility_confirmed" in p for p in problems))
        self.assertTrue(any("prompt_match_confirmed" in p for p in problems))

    def test_render_contains_all_submission_sections(self):
        draft = render_submission(valid_task())
        self.assertIn("## Golden answer\n\n- First item (A)", draft)
        self.assertIn("## Example answer (intentionally incorrect)", draft)
        self.assertIn("## Prompt condition evidence", draft)
        self.assertIn("## Answer-item verification", draft)
        self.assertIn("## Model responses and error explanations", draft)

    def test_pdf_source_uses_text_retrieval_gate(self):
        task = valid_task()
        task["sources"][0].update(source_format="pdf", text_accessible=True, raw_html_checked=False)
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertEqual(errors, [])
        review = valid_review(task)
        review["source_verification"][0]["text_retrieval_confirmed"] = False
        self.assertTrue(any("text_retrieval_confirmed" in p for p in validate_review(review, task)))

    def test_visual_source_requires_harness_evidence(self):
        task = valid_task()
        task["sources"][0]["source_format"] = "image_or_chart"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("modality decision" in e for e in errors))
        task["sources"][0].update(harness_access_confirmed=True, modality_exception="Approved hover state exposes the fact to the official harness")
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertEqual(errors, [])

    def test_review_requires_trajectory_and_judge_assessment(self):
        task = valid_task()
        review = valid_review(task)
        review["run_verification"][0]["trajectory_evidence"] = ""
        review["judge_feedback"]["independent_assessment"] = ""
        problems = validate_review(review, task)
        self.assertTrue(any("trajectory_evidence" in p for p in problems))
        self.assertTrue(any("judge_feedback" in p for p in problems))

    def test_malformed_review_types_return_findings(self):
        task = valid_task()
        review = valid_review(task)
        review["run_verification"][0]["error_type"] = []
        review["judge_feedback"]["status"] = {}
        problems = validate_review(review, task)
        self.assertTrue(any("error_type" in p for p in problems))
        self.assertTrue(any("judge_feedback" in p for p in problems))

    def test_na_failure_explanation_is_rejected(self):
        task = valid_task()
        task["screening"][1]["factual_explanation"] = "N/A"
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("specific factual error" in e for e in errors))

    def test_example_and_constraint_map_required(self):
        task = valid_task()
        task["example_answer"] = task["golden_answer"][0]
        task["modality_decision"] = ""
        task["research"]["constraint_evidence"] = []
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("example_answer" in e for e in errors))
        self.assertTrue(any("modality_decision" in e for e in errors))
        self.assertTrue(any("constraint_evidence" in e for e in errors))

    def test_synthetic_blocklist_blocks_subdomains(self):
        snapshot = Path(__file__).parent.parent / "config/demo-blocklist.txt"
        errors = []
        blocked = load_blocklist(snapshot, errors)
        self.assertEqual(errors, [])
        self.assertIn("blocked.example", blocked)
        task = valid_task()
        task["sources"][0]["url"] = "https://apps.blocked.example/one"
        task["sources"][0]["domain"] = "blocked.example"
        with tempfile.TemporaryDirectory() as tmp:
            findings, _ = validate_task(task, blocked, Path(tmp))
        self.assertTrue(any("blocklist" in e for e in findings))

    def test_render_refuses_an_incomplete_task(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            task = valid_task()
            task["screening"] = []
            path = root / "task.json"
            path.write_text(json.dumps(task), encoding="utf-8")
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            output_path = root / "submission.md"
            args = argparse.Namespace(task=path, output=output_path, blocklist=blocklist, tasks_dir=root / "tasks")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_render(args), 1)
            self.assertFalse(output_path.exists())

    def test_render_writes_consolidated_markdown(self):
        with tempfile.TemporaryDirectory() as tmp:
            root = Path(tmp)
            path = root / "task.json"
            path.write_text(json.dumps(valid_task()), encoding="utf-8")
            blocklist = root / "blocklist.txt"
            blocklist.write_text("blocked.example\n", encoding="utf-8")
            output_path = root / "submission.md"
            args = argparse.Namespace(task=path, output=output_path, blocklist=blocklist, tasks_dir=root / "tasks")
            with contextlib.redirect_stdout(io.StringIO()):
                self.assertEqual(command_render(args), 0)
            rendered = output_path.read_text(encoding="utf-8")
            for heading in ("## Prompt", "## Answer format", "## Example answer", "## Golden answer", "## Sources and evidence", "## Model responses and error explanations"):
                self.assertIn(heading, rendered)

    def test_malformed_field_types_return_errors_instead_of_crashing(self):
        task = valid_task()
        task["evidence"][0]["source_ids"] = [{"bad": "id"}]
        task["evidence"][0]["field_support"][0]["field"] = ["item"]
        task["research"]["completeness_source_ids"] = [{"bad": "id"}]
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(task, set(), Path(tmp))
        self.assertTrue(any("source_ids" in e for e in errors))
        self.assertTrue(any("field and value" in e for e in errors))

    def test_fictional_example_is_not_submittable(self):
        example = json.loads((Path(__file__).parent.parent / "examples/fictional-task.json").read_text())
        with tempfile.TemporaryDirectory() as tmp:
            errors, _ = validate_task(example, set(), Path(tmp))
        self.assertTrue(any("Fictional example packages" in e for e in errors))


if __name__ == "__main__":
    unittest.main()
