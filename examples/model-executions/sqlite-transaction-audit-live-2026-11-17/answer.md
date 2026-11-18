```json
{
  "base_total_changes": 6,
  "errors": [
    {"operation": "multirow_fail", "sqlite_errorname": "SQLITE_CONSTRAINT_UNIQUE"},
    {"operation": "explicit_commit", "sqlite_errorname": "SQLITE_CONSTRAINT_FOREIGNKEY"},
    {"operation": "unique_update", "sqlite_errorname": "SQLITE_CONSTRAINT_UNIQUE"},
    {"operation": "context_commit", "sqlite_errorname": "SQLITE_CONSTRAINT_FOREIGNKEY"}
  ],
  "snapshots": [
    {
      "checkpoint": "S0",
      "parent": [[1, "A"], [2, "B"], [3, "C"]],
      "child": [[101, 1], [102, 1], [201, 2]],
      "audit": [],
      "in_transaction": false,
      "foreign_keys": 1,
      "changes": 3,
      "total_delta": 0,
      "fk_violations": []
    },
    {
      "checkpoint": "S1",
      "parent": [[2, "B"], [3, "C"], [4, "A"]],
      "child": [[201, 2]],
      "audit": ["c:101", "c:102"],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 5,
      "fk_violations": []
    },
    {
      "checkpoint": "S2",
      "parent": [[2, "B"], [3, "C"], [4, "A"], [5, "D"]],
      "child": [[201, 2]],
      "audit": ["c:101", "c:102"],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 6,
      "fk_violations": []
    },
    {
      "checkpoint": "S3",
      "parent": [[1, "A"], [2, "B"], [3, "C"]],
      "child": [[101, 1], [102, 1], [201, 2]],
      "audit": [],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 6,
      "fk_violations": []
    },
    {
      "checkpoint": "S4",
      "parent": [[1, "A"], [2, "B"], [3, "C"], [8, "Z"]],
      "child": [[101, 1], [102, 1], [201, 2], [801, 99]],
      "audit": [],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 8,
      "fk_violations": [["child", 801, "parent", 0]]
    },
    {
      "checkpoint": "S5",
      "parent": [[1, "A"], [2, "B"], [3, "C"], [8, "Z"]],
      "child": [[101, 1], [102, 1], [201, 2]],
      "audit": ["c:801"],
      "in_transaction": false,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 10,
      "fk_violations": []
    },
    {
      "checkpoint": "S6",
      "parent": [[1, "A"], [3, "C"], [8, "Z"], [9, "B"]],
      "child": [[101, 1], [102, 1]],
      "audit": ["c:201", "c:801", "p:2"],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 14,
      "fk_violations": []
    },
    {
      "checkpoint": "S7",
      "parent": [[1, "A"], [2, "B"], [3, "C"], [8, "Z"]],
      "child": [[101, 1], [102, 1], [201, 2]],
      "audit": ["c:801"],
      "in_transaction": false,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 14,
      "fk_violations": []
    },
    {
      "checkpoint": "S8",
      "parent": [[2, "B"], [3, "C"], [8, "Z"]],
      "child": [[201, 2]],
      "audit": ["c:101", "c:102", "c:801", "p:1"],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 20,
      "fk_violations": []
    },
    {
      "checkpoint": "S9",
      "parent": [[2, "B"], [3, "C"], [8, "Z"]],
      "child": [[201, 2]],
      "audit": ["c:101", "c:102", "c:801", "p:1"],
      "in_transaction": true,
      "foreign_keys": 1,
      "changes": 1,
      "total_delta": 21,
      "fk_violations": []
    },
    {
      "checkpoint": "S10",
      "parent": [[3, "C"], [8, "Z"]],
      "child": [[201, 2]],
      "audit": ["c:101", "c:102", "c:801", "p:1", "p:2"],
      "in_transaction": false,
      "foreign_keys": 0,
      "changes": 1,
      "total_delta": 23,
      "fk_violations": [["child", 201, "parent", 0]]
    }
  ],
  "reasoning": [
    "The setup inserts three parents and three children, giving a base of 6. The child insert sets changes() to 3. At S2, OR FAIL preserves the completed insertion of (5, 'D'), stops at the duplicate label B, and leaves the transaction open. SQLite 3.50.4 publishes that one retained change to both counters. The later UNIQUE update uses the default ABORT policy, leaves label Z intact, and sets changes() to 0 with no increase in total_changes. The replacement immediately afterward sets changes() to 1 before S6. [SQLite conflict resolution](https://sqlite.org/lang_conflict.html) [SQLite 3.50.4 statement finalization](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbeaux.c#L3282-L3325) [SQLite extended result codes](https://sqlite.org/rescode.html)",
    "changes() reports direct writes from the latest DML. total_changes also counts writes performed by triggers and foreign-key actions. Both exclude the deletion of the conflicting parent by REPLACE. ROLLBACK TO stage restores the rows and audit contents at S3 while leaving the transaction open. The full ROLLBACK restores the rows and audit contents at S7 and ends the transaction. These rollbacks and the rollback at context exit leave both counters as they stood immediately before the rollback. [SQLite changes](https://sqlite.org/c3ref/changes.html) [SQLite total_changes](https://sqlite.org/c3ref/total_changes.html) [SQLite savepoints](https://sqlite.org/lang_savepoint.html)",
    "At S1, REPLACE removes parent 1 and suppresses its DELETE trigger because recursive_triggers is OFF. Foreign-key enforcement still cascades to both children, and their DELETE trigger records both events. The new parent, two child deletions, and two audit inserts add 5. At S6, recursive_triggers is ON, so removing parent 2 also produces p:2. The new parent, one child deletion, and two audit inserts add 4. The ordinary DELETE at S8 adds 6 from one parent, two children, and three audit inserts. [SQLite REPLACE rules](https://sqlite.org/lang_conflict.html) [SQLite foreign-key actions and recursion](https://sqlite.org/foreignkeys.html#fk_actions) [SQLite 3.50.4 replacement implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/insert.c#L2124-L2136)",
    "The explicit SQL COMMIT fails its deferred foreign-key check and leaves the original transaction open with child 801 still present at S4. Deleting that child adds one direct deletion and one audit insert, then COMMIT succeeds. At context exit, SQLite likewise first rejects COMMIT and leaves the transaction open. CPython then rolls it back, opens a fresh transaction because autocommit is False, and re-raises the original error. S9 therefore has an active transaction with child 999 gone and its insertion still counted. [SQLite deferred foreign keys](https://sqlite.org/foreignkeys.html#fk_deferred) [Python connection context manager](https://docs.python.org/3.14/library/sqlite3.html#how-to-use-the-connection-context-manager) [CPython 3.14.0 context exit implementation](https://github.com/python/cpython/blob/v3.14.0/Modules/_sqlite/connection.c#L2205-L2235)",
    "Python's autocommit attribute selects the driver's transaction policy. in_transaction reflects SQLite's underlying autocommit flag, so explicit BEGIN makes in_transaction true even while Python's autocommit is True. Setting Python's autocommit to False after S7 opens a transaction immediately, so the first foreign_keys=OFF has no effect. The final con.rollback() opens a fresh transaction, and setting autocommit=True commits it. The second foreign_keys=OFF then takes effect. Deleting parent 2 fires its ordinary DELETE trigger and leaves child 201 in place. foreign_key_check detects that orphan even with enforcement off. [Python transaction control](https://docs.python.org/3.14/library/sqlite3.html#transaction-control-via-the-autocommit-attribute) [SQLite foreign_keys](https://sqlite.org/pragma.html#pragma_foreign_keys) [SQLite foreign_key_check](https://sqlite.org/pragma.html#pragma_foreign_key_check)"
  ]
}
```