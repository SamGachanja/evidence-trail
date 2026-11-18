# Actual model executions

## Release-date baseline — 17 November 2026

This is a **real model execution** through the authenticated Codex CLI with live web search enabled. The model returned both historical release dates correctly. **No model break occurred.**

- [Exact model prompt](release-dates-baseline-2026-11-17/prompt.txt)
- [Actual model answer](release-dates-baseline-2026-11-17/answer.md)
- [Recorded web-tool events](release-dates-baseline-2026-11-17/tool-events.json)
- [Execution timing, invocation, and model-identity limits](release-dates-baseline-2026-11-17/execution.json)
- [Reference task](release-dates-baseline-2026-11-17/task.reference.json) and [answer evaluation](release-dates-baseline-2026-11-17/evaluation.json)
- [Artifact checksums](release-dates-baseline-2026-11-17/artifact-sha256.json)

The completed web-tool event contains both official release pages. The final table gives the same dates as those verified in the [separate source audit](../executions/README.md), with a citation for each row. The model received only the question and public-web instructions through stdin; the reference answer was not passed to it. It ran from an isolated temporary working directory, away from the repository's task/evidence files, under the CLI's read-only sandbox.

The actual CLI default model was used. Its resolved model identifier was not reported in the captured event stream, so the record does not invent a model name. The CLI version is recorded. This was one baseline run, not three screenings. The comparison was made by the assistant against the official records, not by an independent human reviewer. Because the answer is correct, it must not be imported as a factual-error screening to make the task pass a failure-only gate.

The trace retains event kinds, web queries/actions, source URLs/titles, and usage. It intentionally omits private reasoning, thread IDs, thumbnails, and third-party response bodies. Original local paths in the invocation are represented by placeholders. The final answer is retained verbatim. Raw capture files were kept locally during the run; no client packages or private work records were used.

## Run another actual model execution

Requires a separately installed/authenticated Codex CLI and network access. This consumes your configured account allowance; offline tests do not call a model.

```sh
python3 examples/model_run.py \
  --task examples/executions/public-release-dates-live-2026-11-17/package/task.json \
  --output /tmp/evidencetrail-new-model-run
```

Use `--model PROVIDER_MODEL_ID` to request a specific available model and `--codex-bin PATH` if discovery fails. The requested ID is recorded separately from the resolved model identity. Choose a fresh output directory. The runner appends explicit public-web/citation instructions and a prohibition on reading local files; the exact resulting prompt is saved in `prompt.txt`.

New executions start with `outcome: not_assessed`. Inspect the answer, consulted sources, errors, and limitations before writing an evaluation. A correct answer is a pass; a tool outage is an infrastructure limitation; only a demonstrated factual/reasoning error is a model failure. A timeout or absent answer must never be marked as a factual break. Record failures honestly rather than repeatedly editing the outcome to make a benchmark look successful.

## Hard-challenge trials

Three additional isolated actual model trials were completed. **All three passed; no model break was observed.** Directory date labels are organizational names; each `execution.json` records the actual start and finish timestamps.

| Challenge | Actual answer | Evaluation | Exact task and solution |
|---|---|---|---|
| Transaction audit | [Answer](sqlite-transaction-audit-live-2026-11-17/answer.md) | [Correct](sqlite-transaction-audit-live-2026-11-17/evaluation.json) | [Package](../challenges/sqlite-transaction-audit/) |
| Deferral/migration matrix | [Answer](sqlite-deferral-matrix-live-2026-11-17/answer.md) | [Correct](sqlite-deferral-matrix-live-2026-11-17/evaluation.json) | [Package](../challenges/sqlite-deferral-matrix/) |
| Cyclic schedules | [Answer](cyclic-schedule-orbits-live-2026-11-17/answer.md) | [Correct](cyclic-schedule-orbits-live-2026-11-17/evaluation.json) | [Package](../challenges/cyclic-schedule-orbits/) |

Each record contains its exact prompt, reduced tool events, invocation metadata, final answer, evaluation, and checksums. The same identity limits and isolation rules as the baseline apply. These are single trials on three distinct tasks, not repeated failure screenings or a success-rate estimate. The reference executions and independent small-case check are described in the [challenge index](../challenges/README.md).

## Claude Haiku browser trials — 18 November 2026

The visible model selector in the signed-in Safari session showed **Haiku 5.5 Medium**. Its underlying API model ID was not exposed. The previous Codex passing trials remain separate; they are not relabelled as Claude trials. CLI Haiku 4.5 launch attempts returned authentication errors and generated no task responses, so those do not count as model failures.

| Browser trial | Observed outcome | Review |
|---|---|---|
| [Transaction audit](haiku-browser-transaction-audit-2026-11-18/) | Verified semantic failure | At S3, failed to restore parent 1 and children 101/102 on savepoint rollback; subsequent counts also diverged. |
| [Deferral matrix](haiku-browser-deferral-matrix-2026-11-18/) | Verified semantic failure | Claimed H's commit fails; the pinned Python 3.14.0/SQLite 3.50.4 execution succeeds. |
| [Cyclic schedules](haiku-browser-cyclic-schedule-2026-11-18/) | Numerical pass | All three totals and all eight stabilizer cells match. |

These are actual browser submissions in three separate Claude chats. The local browser records contain observed excerpts, selected fields, evaluations and private conversation URLs; **they are not full transcripts or provider tool traces**. The long JSON blocks were truncated by accessibility capture, so no exhaustive machine-grading claim is made for those browser answers. The matrix prompt used a condensed equivalent program and shortened wording, so this is not a controlled byte-identical provider comparison. The complete originals remain in the user's Claude account. No public share link has been created. Both SQLite references were rerun on the pinned runtime and exactly matched their saved reference outputs.
