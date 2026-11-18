# Reference: migration and deferral matrix

The complete [JSON reference](reference-output.json) was produced by running [reference.py](reference.py) on CPython 3.14.0 linked against SQLite 3.50.4. Each case uses a fresh in-memory database. The model sees the exact program but not its output; it is asked for a documentation/source-code audit without execution.

| Case | Before-commit FK target | Actual FK violations | Deferral flag | Commit result | Transaction active afterward |
| --- | --- | --- | ---: | --- | --- |
| A | parent | child 10 → missing parent 1 | 1 | FOREIGNKEY error | yes |
| B | parent | child 10 → missing parent 1 | 0 | success | no |
| C | parent | child 10 → missing parent 1 | 1 | success | no |
| D | parent | child 10 → missing parent 1 | 0 | FOREIGNKEY error | yes |
| E | parent | none | 0 | FOREIGNKEY error | yes |
| F | parent | none | 0 | success | no |
| G | parent | none | 1 | FOREIGNKEY error | yes |
| H | parent | none | 0 | success | no |
| I | old_parent | child 10 → missing old_parent 1 | 0 | success | no |
| J | parent | child 10 → missing parent 1 | 1 | FOREIGNKEY error | yes |

`foreign_keys` remains 1 throughout every case, including J: the attempted toggle in J occurs in a transaction. All before-commit states have an active transaction. After successful COMMIT the deferral flag is 0; after a failed COMMIT it retains the before-commit value. The child row remains `[10, 1]` in every case. Parent is empty in A-D and J, and contains `[1]` in E-I. The full reference includes every state field before and after commit.

## Mechanisms

A has the ordinary unresolved deferred violation. B manually disables deferral and clears the tracking state, allowing an orphan to commit. Turning deferral on again in C does not reconstruct the lost history.

D creates a savepoint after the violation, clears deferral tracking, and then rolls back to the savepoint. That restores the saved constraint accounting, but it does not undo the connection's pragma setting. In E, the subsequent parent repair occurs with deferral off; the pinned engine does not discharge the restored deferred-immediate accounting in the same way as the original deferred operation. The final row-level check is empty, yet COMMIT still fails. F saved the pre-violation state instead, so rollback restores the parent and its earlier zero accounting.

G rebuilds the parent through DROP and replacement rename. The data is logically repaired but the earlier violation accounting is stale; COMMIT fails. H clears that accounting explicitly and commits a genuinely valid row state. I renames the original parent first, which also rewrites the child's referenced table name. Creating a new table under the old name does not redirect the child back to it; the dropped `old_parent` remains its FK target. Clearing the accounting then permits a real orphan to commit.

The policy in the question is therefore false for this pinned behavior: B, C, and I each commit with foreign-key enforcement enabled while `foreign_key_check` still reports an orphan.

## Primary references and reproducibility limits

- [Pragma documentation](https://www.sqlite.org/pragma.html#pragma_defer_foreign_keys): manual disabling of deferral can reset enforcement accounting; foreign-key enforcement itself cannot be toggled inside a transaction.
- [SQLite maintainer explanation of migration/constraint accounting](https://sqlite.org/forum/info/64fb781a226df95c0f4edc474e590214c28ae1b4b5ddeee8f7ec4ad77286796c): a table rebuild can leave pending accounting even when a row-level check is clear.
- [SQLite 3.50.4 pragma implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/pragma.c), [savepoint VM implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbe.c), and [foreign-key implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/fkey.c): inspect counter restoration and flag-dependent repair paths.
- [ALTER TABLE](https://www.sqlite.org/lang_altertable.html): renaming the original table can rewrite foreign-key references; renaming a replacement is not the same operation.

The matrix is a runtime-specific reference, not advice to bypass constraints or a promise that future versions behave identically. For a production migration, keep explicit integrity checks and use the supported migration procedure. A different engine build must be tested separately before reusing this oracle.
