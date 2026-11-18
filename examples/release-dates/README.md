# Release-date research example

**Question:** For the initial stable releases Python 3.12.0 and PostgreSQL 16, report the release name and release date on the respective official release page or announcement, retaining its human-readable date spelling.

This small example demonstrates the difference between source verification, model screening, and independent review. It is an operational example of EvidenceTrail, not a difficult benchmark.

## EvidenceTrail source audit

The [recorded audit](source-audit/execution.json) ran the real CLI on 17 November 2026 and retrieved the official [Python release page](https://www.python.org/downloads/release/python-3120/) and [PostgreSQL announcement](https://www.postgresql.org/about/news/postgresql-16-released-2715/).

| Check | Observed result |
| --- | --- |
| HTML evidence | Both sources retrieved; all recorded quotations matched. |
| Negative probe | An intentionally changed quotation was rejected. |
| Task-readiness gate | Blocked because the three required screenings were missing. |
| Independent review | Blocked because the review was unfilled. |
| Submission rendering | Blocked; no submission was generated. |

Inspect the [task](source-audit/package/task.json), [audit report](source-audit/package/creation-report.json), [negative probe](source-audit/negative-probe/creation-report.json), [command logs](source-audit/logs), and [checksums](source-audit/artifact-sha256.json). Empty stderr files are preserved as part of that original record.

## Separate actual model baseline

A [real model execution](model-run/execution.json) subsequently returned both dates correctly. The [answer](model-run/answer.md), [exact prompt](model-run/prompt.txt), [reduced tool events](model-run/tool-events.json), [evaluation](model-run/evaluation.json), and [checksums](model-run/artifact-sha256.json) are retained.

The authenticated Codex CLI default model was used; its resolved identifier was not reported. This is one passing baseline, not a model failure, three screenings, or independent human review. It cannot satisfy the failure-only gate by being relabelled.

## Reproduce and interpret

From the repository root, with `curl` and network access:

```sh
python3 scripts/run_source_audit.py --output runs/release-date-audit
```

Choose a fresh directory. This script exercises source auditing only. For optional model response capture, see the [runner guide](../../scripts/README.md).

Recorded artifacts were moved here during repository organization without changing their contents. Historical metadata may therefore mention the original script paths. The manifest paths remain relative to each record and still verify. Source hashes capture retrieved bytes, not ongoing public access or factual support; records are unsigned. Only local directory paths were redacted in the original logs; third-party page bodies are not redistributed. No completed research submission is claimed.
