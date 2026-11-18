# Authoring and reviewing a research task

EvidenceTrail packages a bounded research question, its expected answers, the source evidence for each answer field, actual model screenings, and a version-bound independent review. It validates that these records are complete and consistent; reviewers still have to judge factual correctness and source context.

## 1. Create the package and source restrictions

```sh
evidencetrail new MY_RESEARCH --tasks-dir tasks
```

This creates `tasks/MY_RESEARCH/task.json` and `review.json`. Existing or unsafe IDs are rejected. Templates are bundled with the installed package; generated files belong to the current working directory.

Create `config/blocklist.txt` from your own source restrictions, one hostname or URL per line. Subdomains are included. The workflow requires a nonempty list; no client policy is bundled. `config/demo-blocklist.txt` is synthetic and only for examples and tests.

Fill the scope, prompt, bracketed answer format, expected answer items, source locators and quotations, per-field evidence, and research justification. See the [data model](data-model.md). The [fictional example](../examples/fictional-task.json) illustrates the structure but is deliberately rejected for real submission.

Optional candidate drafting:

```sh
evidencetrail create ARCHIVE_RESEARCH --owner 'Your actual name' \
  --topic 'A completed archive suitable for cross-source research' \
  --blocklist config/blocklist.txt --tasks-dir tasks
```

`create` uses a separately installed, authenticated Codex CLI. A successful draft command does not mean the returned task is ready. Inspect its creation report before continuing.

## 2. Verify sources and inspect support

```sh
evidencetrail verify-sources tasks/MY_RESEARCH \
  --blocklist config/blocklist.txt --tasks-dir tasks
evidencetrail form-fields tasks/MY_RESEARCH/task.json
```

HTML retrieval uses `curl`. The audit records retrieval details and checks text presence after markup normalization. Read the original context independently: finding a quote on a page does not establish that it supports the answer. PDF, spreadsheet, chart, and image evidence need separate access/review records.

## 3. Attach actual screenings

Run the exact final prompt in your evaluation environment and record the actual response and trajectory. Optional [runner scripts](../scripts/README.md) can capture responses, but do not decide factual correctness or manufacture screening approvals.

```sh
evidencetrail attach-screening tasks/MY_RESEARCH runs/screenings.json \
  --blocklist config/blocklist.txt --tasks-dir tasks
evidencetrail check tasks/MY_RESEARCH/task.json \
  --blocklist config/blocklist.txt --tasks-dir tasks
```

The import accepts a JSON list or an object with a `screening` list. It is not a hosted evaluation service or labeling-platform integration. Current gates require exactly three complete factual-error records for the final prompt; a correct response, timeout, authentication error, or formatting difference is not a factual failure. Revisit the task rather than rewriting an observed pass into a failure.

Other code-defined defaults are at least two answer items, at least two necessary source domains, and a maximum of five tasks per declared domain in the local batch. These are defaults for this research workflow, not requirements for all evaluations.

## 4. Review the exact task version

A different reviewer reconstructs the answer and completes source, answer-item, and screening-run checks in `review.json`. Record concrete evidence for every check and repair suggestions for failures.

```sh
evidencetrail fingerprint tasks/MY_RESEARCH/task.json
# Record the reviewed task's digest as task_sha256 in review.json.
evidencetrail review tasks/MY_RESEARCH \
  --blocklist config/blocklist.txt --tasks-dir tasks
```

The reviewer name must differ from the task owner's name. This is a consistency check, not identity authentication. Any task-file edit, including whitespace, changes the fingerprint; review the changed version before recording a new digest.

## 5. Render the handoff

```sh
evidencetrail render tasks/MY_RESEARCH/task.json \
  --output tasks/MY_RESEARCH/submission.md \
  --blocklist config/blocklist.txt --tasks-dir tasks
```

`render` checks task readiness; use `review` separately to check independent-review readiness. `APPROVE` and `READY FOR REVIEW` are local outcomes, not factual certification or external acceptance.

Exit codes are **0** for a successful local operation, **1** for a failed validation/review gate, and **2** for a command/file error. Candidate drafting can return 0 while its report still lists blockers. Use each command's `--help` for all arguments.
