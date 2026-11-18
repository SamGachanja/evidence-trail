# Hard challenges with actual model trials

These are original, synthetic challenge packages. Each includes the exact prompt, an executable reference, saved reference output, and a grader. None contains client tasks or private work records. The reference is kept outside the isolated model workspace.

| Challenge | Main traps | Initial Codex execution outcome |
|---|---|---|
| [SQLite transaction audit](sqlite-transaction-audit/prompt.txt) | Partial writes, replacement triggers, cascades, rollback, cumulative counters, context managers | Correct: all 11 checkpoints |
| [SQLite deferral/migration matrix](sqlite-deferral-matrix/prompt.txt) | Deferred constraint counters, PRAGMA toggles, savepoints, replacement tables | Correct: all 10 cases |
| [Cyclic telemetry schedules](cyclic-schedule-orbits/prompt.txt) | Circular restrictions, periodicity, rotation/reflection stabilizers, distinct rooting conventions | Correct: all totals and eight stabilizer cells |

The initial Codex trials did **not** establish a model break. Subsequent actual Haiku 5.5 Medium browser trials did establish two SQLite reasoning failures; their excerpts and limitations are documented in the execution index. Difficulty is not evidence of failure. The SQLite references were executed on the pinned Python/SQLite versions in their prompts. The combinatorics reference uses exact integer counting and includes an independent smaller-case exhaustive enumeration. Final mathematical derivations and technical explanations were reviewed by the assistant, not an independent human reviewer.

The tasks ask for reasoning without code execution. This is part of their stated evaluation scope, not evidence about unrestricted tool-assisted performance. The model runner still allows public web research and saves the exact appended instructions. Raw private reasoning is not retained. Full records are linked in [actual model executions](../model-executions/README.md); runtime timestamps there are authoritative.

## Reproduce reference counts

```sh
python3 examples/challenges/cyclic-schedule-orbits/reference.py 24
python3 examples/challenges/cyclic-schedule-orbits/small_enumeration.py
```

SQLite references require the exact runtime versions stated in each prompt; other versions must not silently replace the pinned answer key. Offline CI tests verify the saved records, graders, and portable mathematical reference without calling a model.
