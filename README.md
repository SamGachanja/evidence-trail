# EvidenceTrail

A Python CLI for authoring and reviewing evidence-backed research tasks. It connects each expected answer to source quotations, checks recorded model screenings, and ties an independent review to the exact task version.

Use it when a research task needs an inspectable trail from **question → answer → evidence → screening → review**. It helps authors and reviewers catch missing support, incomplete checks, and approvals that became stale after an edit.

## Core workflow

1. **Author:** create a task with a clear scope, answer format, expected answers, and source records.
2. **Support:** attach quotations for each answer field and audit the source HTML.
3. **Screen:** run the final prompt in your evaluation environment and attach the actual results.
4. **Review:** have a separate reviewer reconstruct the answer and check the sources and screenings.
5. **Handoff:** validate the package, bind the review to its SHA-256 fingerprint, and render a submission draft.

EvidenceTrail checks the records you provide. Factual judgment remains with the reviewer; a passing local gate is not external approval.

## Quick start

Requires **Python 3.10+** with no third-party Python runtime dependencies.

```sh
python3 -m pip install .
evidencetrail --help
evidencetrail new MY_RESEARCH --tasks-dir tasks
```

Edit the generated `task.json` and `review.json`. Create `config/blocklist.txt` with your own source restrictions; the real list and generated work are ignored by Git. Files are created relative to your current working directory.

Try the offline demonstration from a checkout:

```sh
python3 examples/offline_demo.py
```

The demo uses explicitly fictional data to show packaging, rendering, fingerprinting, and expected validation failures. It makes no network or model calls.

## Commands

| Command | Purpose |
| --- | --- |
| `new` | Create blank task and review files. |
| `create` | Optionally draft a research candidate with an installed Codex CLI. |
| `verify-sources` | Retrieve HTML and check recorded quotations. |
| `attach-screening` | Import external model-screening records. |
| `check` | Check task readiness and local batch constraints. |
| `form-fields` | Render copyable task fields before screening. |
| `fingerprint` | Hash the exact task file for review binding. |
| `review` | Check review coverage and fingerprint agreement. |
| `render` | Render a handoff draft after task checks pass. |

See the [workflow guide](docs/workflow.md) for command examples and gate requirements, and the [data model](docs/data-model.md) for task and review fields.

## Examples and optional runners

The [examples guide](examples/README.md) includes a fictional package and one small, real research example: checking the original release dates of Python 3.12.0 and PostgreSQL 16. The recorded source audit verifies its quotations; a separate model baseline answers correctly. Neither record represents a completed independent review or an approved task.

[Optional runner scripts](scripts/README.md) capture source audits or external model responses. Source retrieval needs `curl` and network access; model runners need their own installed, authenticated CLI and consume its account allowance. Keep fresh run outputs in the ignored `runs/` directory.

## Validation boundaries

- HTML checks establish text presence, not semantic support or factual truth. Other source formats require separate review.
- Fingerprints detect task-file changes; they do not authenticate reviewers or freeze external pages.
- Current workflow defaults require at least two answer items, two necessary source domains, three factual-error screening records, and at most five tasks per declared domain in a local batch. These are workflow-specific gates, not universal evaluation standards.
- Screening records must come from actual executions. A correct model answer or an infrastructure error cannot be relabelled as a factual failure.
- Source retrieval is intended for trusted local use, not as a public URL-fetching service.

## Development

```sh
python3 -m unittest discover -s tests -v
```

The offline suite covers validation, source restrictions and quotations, screening imports, review invalidation, rendering, CLI behavior, and recorded-example integrity. CI also checks the installed command and bundled templates on Linux and macOS.

```text
evidencetrail/    CLI implementation and blank templates
config/          Synthetic blocklist examples
docs/            Workflow and data model
examples/        Offline demo and curated research example
scripts/         Opt-in source/model execution tools
tests/           Offline regression tests
```

[MIT license](LICENSE).
