# EvidenceTrail

A Python CLI for building inspectable research-task packages: connect answer fields to quoted source evidence, audit retrieved HTML, and bind independent reviews to the exact task version.

A convincing answer is not necessarily a supported answer. EvidenceTrail keeps the research question, expected answer, source locators, per-field quotations, screening records, and review findings together so missing evidence and stale approvals can be found before handoff.

## What it does

- Creates blank packages or drafts candidates using an optional installed Codex CLI.
- Checks answer formats, source references, literal field support, completeness notes, and screening records.
- Retrieves HTML and checks whether recorded facts and quotations appear in the response text.
- Requires separate source, answer-item, and screening-run review records.
- Compares the review's SHA-256 fingerprint with the current task file; subsequent edits invalidate that review.
- Renders readable submission drafts and copyable form fields.

No third-party Python runtime dependencies. Python **3.10+** is required. HTML retrieval additionally needs `curl`; candidate generation needs a separately installed, authenticated Codex CLI. Neither is needed for the offline validation tests.

## Quick start

From a checkout:

```sh
python3 -m evidencetrail --help
python3 -m evidencetrail new MY_RESEARCH --tasks-dir tasks
python3 -m evidencetrail form-fields examples/fictional-task.json
python3 -m evidencetrail fingerprint examples/fictional-task.json
```

Install the command locally if preferred:

```sh
python3 -m pip install .
evidencetrail --help
```

Templates are included in the installed package. Generated tasks and the default blocklist belong to the **current working directory**, not the installation directory.

Run the self-contained offline demonstration:

```sh
python3 examples/offline_demo.py
```

It creates a blank package in a temporary directory, renders the fictional example, computes its fingerprint, and confirms that the fictional data is rejected by the readiness gate. It makes no network requests and does not fabricate an approved research task.

## Recorded executions

A [real public-source execution](examples/executions/README.md) is included, with command logs, timestamps, actual exit codes, source-response hashes, and artifact checksums. Both official release pages were verified. An intentionally incorrect quotation was rejected, and the tool correctly blocked handoff because screening and independent review had not been performed. This is an operational source-audit example, not a model-performance claim.

```sh
python3 examples/live_run.py --output /tmp/evidencetrail-live-new-run
```

This opt-in command makes real public HTML requests and requires a fresh output directory. See the execution guide for the recorded artifacts and limits.

A separate [actual model execution](examples/model-executions/README.md) records the exact prompt, model answer, live web-tool events, and evaluation. The model **passed** the release-date baseline; no break is claimed. Use `examples/model_run.py` to capture another authenticated model run, optionally selecting an explicit model. This invokes an AI service and is separate from the source-audit runner above.

## Workflow

```text
new / optional create
    -> collect sources and per-field evidence
    -> verify-sources -> inspect findings and original context
    -> externally run the final prompt -> attach-screening
    -> check -> independent review -> fingerprint -> review
    -> render a handoff draft
```

1. Create `config/blocklist.txt` using your own source restrictions, one hostname or URL per line. Subdomains are included. This workflow requires a nonempty list; no client policy is bundled. `config/demo-blocklist.txt` is synthetic and is only for examples/tests.
2. Fill `task.json`, including the scope, expected answers, source records, field-level evidence, and research justification. `create` can draft a candidate, but a successful generation command does not mean it is ready.
3. Audit HTML sources with `verify-sources`. Read the underlying sources yourself: text presence does not establish that a quotation supports the claimed fact.
4. Obtain real screening records from your evaluation environment and import them with `attach-screening`. It accepts a JSON list or an object with a `screening` list; it does not run a hosted evaluation or integrate with a labeling vendor.
5. Have a different reviewer reconstruct the answer and complete source/item/run checks in `review.json`. Record `fingerprint` after the review. Rerun `review` after any task edit.

See [the data model](docs/data-model.md) for field groups and review requirements.

## Commands

| Command | Purpose |
| --- | --- |
| `new ID --tasks-dir DIR` | Create blank task and review files; refuse duplicate/unsafe IDs. |
| `create ID --topic TEXT --owner NAME` | Draft a research candidate through the installed Codex CLI. |
| `verify-sources FOLDER` | Re-fetch HTML, check recorded quotations, and update audit findings. |
| `attach-screening FOLDER RUNS.json` | Validate and attach three external screening records. |
| `check TASK.json` | Run task-readiness checks and local batch-domain checks. |
| `form-fields TASK.json [--output FILE]` | Render copyable fields before screening. |
| `fingerprint TASK.json` | Print SHA-256 of the exact task-file bytes. |
| `review FOLDER` | Check task, independent review, and fingerprint agreement. |
| `render TASK.json [--output FILE]` | Render a submission draft only after task checks pass. |

Validation commands accept `--blocklist FILE` and, where relevant, `--tasks-dir DIR`. Check each command's `--help` for its full arguments. Exit codes: **0** successful local operation, **1** failed validation/review gate, **2** command/file error. Candidate creation may return 0 while its creation report still contains blockers.

Optional agent-assisted drafting:

```sh
evidencetrail create ARCHIVE_RESEARCH --owner 'Your actual name' \
  --topic 'A completed archive suitable for cross-source research' \
  --blocklist config/blocklist.txt --tasks-dir tasks
```

This invokes your installed coding agent and may use its account allowance. The agent runs in read-only sandbox mode; EvidenceTrail writes its returned candidate afterward. Review your working directory and the data you supply before invoking an external agent. No API key is bundled or required by the offline CLI.

## Workflow-specific defaults

This version retains opinionated research-evaluation gates: at least two answer items, at least two necessary source domains, exactly three recorded factual-error screenings, and a maximum of five tasks per declared domain in a local batch. These are **implementation defaults for this workflow**, not universal research standards, certifications, or a claim that every evaluation should require model failure. They are currently code-defined rather than configurable.

`APPROVE` and `READY FOR REVIEW` are local gate outcomes. They do not certify factual accuracy, reviewer identity, external acceptance, or the authenticity of recorded screening runs.

## Tests and CI

```sh
python3 -m unittest discover -s tests -v
```

Tests use synthetic packages, mocked source retrieval, and a fake agent executable. They cover source restrictions, evidence-field matching, HTML text handling, incomplete screenings, prompt mismatches, independent-review coverage, review invalidation, rendering, and candidate creation. CI runs Python 3.10/3.13 on Linux/macOS and checks the installed command and bundled templates outside the checkout.

## Limits

- Source auditing currently fetches HTML only. PDF, spreadsheet, image, and chart evidence require separate access/review records; this tool does not extract those formats.
- HTML text matching is tolerant of case/markup and is not a semantic entailment test or a full browser renderer.
- A SHA-256 fingerprint detects changes to task bytes; it is not a signed approval, proof of reviewer identity, or a snapshot of external pages.
- Public-domain checks are lightweight hostname checks, not a Public Suffix List implementation or a network sandbox. Use source auditing locally with trusted URLs; do not expose it as an untrusted URL-fetching service.
- Source retrieval can fail or change over time. A recorded source hash cannot prove that a page remains publicly accessible.
- Candidate generation depends on the installed Codex CLI's supported flags and authentication. Offline tests do not establish live model performance.
- Local tasks, reviews, archives, credentials, and the real blocklist are ignored by Git. No real task submissions, screening logs, client guides, or client domain lists are included.

## Layout

```text
evidencetrail/          CLI, validation, rendering, source auditing
  templates/           Blank task and independent-review templates
examples/              Offline demo, live source/model runners, and recorded executions
config/                Synthetic blocklist and format example
docs/                  Public data-model documentation
tests/                 Offline regression and CLI tests
.github/workflows/     Linux/macOS CI
```

MIT license. See [LICENSE](LICENSE).
