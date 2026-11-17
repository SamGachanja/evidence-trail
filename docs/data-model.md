# Data model and review lifecycle

A package directory contains `task.json` and `review.json`. Generated candidates may also contain `creation-report.json`, `form-fields.md`, and `submission.md`.

## Task fields

| Group | Key fields | Purpose |
| --- | --- | --- |
| Identity | `id`, `owner`, `topic`, `break_pattern`, `modality_decision` | Identify the author and research operation. |
| Question | `prompt`, `answer_template`, `example_answer` | State the question and a bracketed output format, with a disjoint deliberately incorrect example. |
| Scope | `inclusion_rule`, `start_boundary`, `end_boundary` | Define which records qualify and the boundaries of the requested set. |
| Answer | `golden_answer` | One expected item per line, matching the template. |
| Sources | `sources` | Unique IDs, public URLs, titles, locators, quoted facts, retrieval dates, format/access metadata, and necessity notes. |
| Evidence | `evidence` | Connect each answer item and each template field to source IDs and exact supporting quotations. |
| Research | `research` | Search observations, completeness argument, cross-domain dependence, normalization decisions, and per-constraint evidence. |
| Screening | `screening` | External run identity, exact screened prompt, response, trajectory, outcome, and concrete factual-error explanation. |

Use the [blank task template](../evidencetrail/templates/task.json) as the starting point. The [fictional example](../examples/fictional-task.json) illustrates the full structure; its access flags and model results are fictional, not observations of real runs. The validator deliberately refuses fictional package IDs.

For a directly sourced field, `field_support` specifies `field`, `value`, `source_id`, and `exact_quote`. The value must match its answer-template field and be supported literally. A derived field can instead provide `derivation_parts` with separate values/quotations/source IDs and a `derivation_separator`; the parts must join to the recorded field value. Inspect the source context independently even when literal checks pass.

## Independent review

The [review template](../evidencetrail/templates/review.json) separates three lists:

- `source_verification`: one record per source, including access, factual support, credibility, and observation notes.
- `item_verification`: one record per answer item, recording independent reproduction, exact values, and qualification.
- `run_verification`: one record per screening, recording prompt agreement, trajectory inspection, and the specific substantive error.

It also requires an independent answer, judge-feedback assessment, reviewer/date, and the named checklist entries. A passing check requires concrete evidence. A failed check requires evidence, an exact location, and a repair suggestion. Unverified entries remain blockers.

The reviewer name must differ from the task owner. This is a consistency check, not identity verification. Every task-file edit, including whitespace, changes the fingerprint and requires the review to be rechecked.

```sh
evidencetrail fingerprint tasks/MY_RESEARCH/task.json
# After completing the independent review, record that digest as task_sha256.
evidencetrail review tasks/MY_RESEARCH --blocklist config/blocklist.txt
```

Do not copy example screening or review assertions into a real package. Use observations from actual runs and independent review.
