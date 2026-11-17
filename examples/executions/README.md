# Recorded live execution

[Public release-date audit, 17 November 2026](public-release-dates-live-2026-11-17/execution.json)

This record was produced by actually running EvidenceTrail with network access. It uses the [official Python 3.12.0 release page](https://www.python.org/downloads/release/python-3120/) and the [official PostgreSQL 16 release announcement](https://www.postgresql.org/about/news/postgresql-16-released-2715/). The package is a deliberately simple operational example, not a claim of a difficult benchmark or production deployment.

## Observed results

| Stage | Actual result |
| --- | --- |
| Before-audit readiness check | Rejected: source flags not yet verified, and screening absent. |
| Real HTML source audit | Both pages retrieved; all three recorded quotations per page matched. |
| After-audit readiness check | Rejected: three external screening runs are still missing. |
| Form fields and fingerprint | Produced successfully from the audited task. |
| Submission rendering | Blocked; no submission file produced. |
| Independent-review gate | Blocked; review remains an unfilled template. |
| Deliberately incorrect quotation | Rejected by another live audit; the original task remains unchanged. |

The rejected stages are expected outcomes. Passing source retrieval must not silently turn an unscreened task into an approved submission.

## Inspect the evidence

- [Execution metadata and actual exit codes](public-release-dates-live-2026-11-17/execution.json): command arguments, start/end timestamps, timings, Python/platform, implementation hash, and source commit.
- [Before-audit task](public-release-dates-live-2026-11-17/task.before.json) and [audited task](public-release-dates-live-2026-11-17/package/task.json).
- [Source audit report](public-release-dates-live-2026-11-17/package/creation-report.json): actual fetch timestamps, final URLs, content types, raw-response hashes, matched-quotation counts, and remaining blockers.
- [Command stdout/stderr](public-release-dates-live-2026-11-17/logs): all eight commands. Empty stderr files are retained.
- [Negative-probe report](public-release-dates-live-2026-11-17/negative-probe/creation-report.json): the intentionally changed quotation fails; it is not a proposed answer.
- [Artifact SHA-256 manifest](public-release-dates-live-2026-11-17/artifact-sha256.json): hashes of each recorded file, excluding the manifest itself.

Only checkout/run directory paths in command arguments and stdout/stderr were replaced with `<checkout>` and `<run>`. No response content or exit status was rewritten. The source pages are linked with short quotations; full third-party HTML responses are not redistributed. Their hashes record what was fetched but cannot recreate a page or guarantee its future contents. These records are unsigned and are not external attestation.

## Reproduce

From the repository root, with Python 3.10+, `curl`, and network access:

```sh
python3 examples/live_run.py --output /tmp/evidencetrail-live-new-run
```

Choose a **fresh** directory. The script refuses to overwrite existing execution records. It runs the real CLI in subprocesses, performs real HTML requests, saves stdout/stderr, and checks the expected results. The script does not invoke an AI model, fabricate screenings, fill an independent review, or submit anything externally. It uses the synthetic demo blocklist, not a client restriction list.

Timestamps, page hashes, and sometimes page text will differ on a later run. If a source changes or cannot be fetched, the script stops and preserves the commands already recorded; inspect their logs instead of treating a failed retrieval as successful. Network-dependent reruns are opt-in and are not part of offline CI.
