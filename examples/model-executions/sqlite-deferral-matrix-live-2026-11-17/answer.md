{
  "cases": {
    "A": {
      "before_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true},
      "commit": "SQLITE_CONSTRAINT_FOREIGNKEY",
      "after_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true}
    },
    "B": {
      "before_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "success",
      "after_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": false}
    },
    "C": {
      "before_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true},
      "commit": "success",
      "after_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": false}
    },
    "D": {
      "before_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "SQLITE_CONSTRAINT_FOREIGNKEY",
      "after_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true}
    },
    "E": {
      "before_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "SQLITE_CONSTRAINT_FOREIGNKEY",
      "after_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true}
    },
    "F": {
      "before_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "success",
      "after_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": false}
    },
    "G": {
      "before_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true},
      "commit": "SQLITE_CONSTRAINT_FOREIGNKEY",
      "after_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true}
    },
    "H": {
      "before_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "success",
      "after_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "parent", "violations": [], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": false}
    },
    "I": {
      "before_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "old_parent", "violations": [["child", 10, "old_parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": true},
      "commit": "success",
      "after_commit": {"parent": [[1]], "child": [[10, 1]], "fk_target": "old_parent", "violations": [["child", 10, "old_parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 0, "in_transaction": false}
    },
    "J": {
      "before_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true},
      "commit": "SQLITE_CONSTRAINT_FOREIGNKEY",
      "after_commit": {"parent": [], "child": [[10, 1]], "fk_target": "parent", "violations": [["child", 10, "parent", 0]], "foreign_keys": 1, "defer_foreign_keys": 1, "in_transaction": true}
    }
  },
  "reasoning": [
    "SQLite tracks this immediate constraint in the connection's nDeferredImmCons counter while defer_foreign_keys is on. COMMIT rejects a positive sum of the two deferred counters before switching SQLite back to autocommit mode. A successful COMMIT clears the counters and the deferral flag. CPython reports in_transaction from SQLite's autocommit state and exposes the extended constraint code as sqlite_errorname. [SQLite counter routing](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbe.c#L7179-L7197) [SQLite COMMIT](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbe.c#L3803-L3839) [SQLite commit check and reset](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbeaux.c#L3121-L3274) [CPython transaction state](https://github.com/python/cpython/blob/v3.14.0/Modules/_sqlite/connection.c#L1646-L1657) [CPython exception mapping](https://github.com/python/cpython/blob/v3.14.0/Modules/_sqlite/util.c#L30-L142)",
    "A leaves the delete's count of 1 pending. B clears both deferred counters by setting defer_foreign_keys=OFF. C then sets the flag back to 1, with the counters still at zero. J attempts to disable foreign_keys inside the explicit transaction, where SQLite masks out that change. Its pending count is still 1. [SQLite flag pragma implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/pragma.c#L1086-L1125)",
    "ROLLBACK TO restores database contents and both deferred counters to their savepoint values. The connection's deferral flag stays off, and RELEASE of the nested savepoint leaves the outer transaction open. D and E took the savepoint after the delete, so rollback restores the count of 1 and the parent remains absent at that step. F took it before the delete, so rollback restores parent row 1 and the zero count. [SQLite savepoint implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbe.c#L3655-L3784)",
    "In E, inserting row 1 repairs the actual reference. With deferral off, SQLite skips the child scan for this top-level, single-row parent insert against an immediate constraint. The restored count of 1 therefore survives the insert. With deferral on, an ordinary insert into the referenced parent would scan matching children and could decrement that count. In G and H, the copy goes into replacement before the drop, while the child still references parent. The drop's implicit DELETE creates a pending count of 1. Renaming replacement to parent makes the existing reference resolve again through the schema, without a parent-row insert at that point to decrement the count. G fails with an empty check result. H clears the count and commits with the reference satisfied. [SQLite parent insert and delete accounting](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/fkey.c#L963-L1002) [SQLite DROP TABLE foreign-key handling](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/fkey.c#L682-L737) [SQLite rename implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/alter.c#L150-L262)",
    "In I, renaming the original parent rewrites the child's declared target to old_parent. The new parent receives row 1, but the child still refers to old_parent when it is dropped. Turning deferral off clears the count from that drop. The foreign_key_check scan reports the child row against the missing old_parent table, and COMMIT succeeds. In G and H, the source name of the rename is replacement, so the child's existing target parent is left intact. [SQLite rename rules](https://www.sqlite.org/lang_altertable.html#alter_table_rename) [Pinned foreign-key target rewrite](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/alter.c#L1690-L1703) [Pinned foreign_key_check implementation](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/pragma.c#L1487-L1556)",
    "The proposed policy is false. B, C, and I commit with foreign_keys=1 and a reported orphan. F and H commit with foreign_keys=1 and no reported violation. E and G show the reverse distinction: the current rows pass foreign_key_check, yet the pending counter causes COMMIT to fail. [SQLite pragma documentation](https://www.sqlite.org/pragma.html#pragma_defer_foreign_keys) [Pinned COMMIT check](https://github.com/sqlite/sqlite/blob/version-3.50.4/src/vdbeaux.c#L3131-L3144)"
  ]
}