import json
import sqlite3
import sys

con = sqlite3.connect(':memory:', autocommit=True)
con.execute('PRAGMA foreign_keys=ON')
con.execute('PRAGMA recursive_triggers=OFF')
con.executescript('''
CREATE TABLE parent(id INTEGER PRIMARY KEY, label TEXT NOT NULL UNIQUE);
CREATE TABLE child(id INTEGER PRIMARY KEY, pid INTEGER NOT NULL REFERENCES parent(id) ON DELETE CASCADE DEFERRABLE INITIALLY DEFERRED);
CREATE TABLE audit(seq INTEGER PRIMARY KEY AUTOINCREMENT, event TEXT NOT NULL);
INSERT INTO parent VALUES(1,'A'),(2,'B'),(3,'C');
INSERT INTO child VALUES(101,1),(102,1),(201,2);
CREATE TRIGGER child_deleted AFTER DELETE ON child BEGIN
  INSERT INTO audit(event) VALUES('c:' || OLD.id);
END;
CREATE TRIGGER parent_deleted AFTER DELETE ON parent BEGIN
  INSERT INTO audit(event) VALUES('p:' || OLD.id);
END;
''')
base = con.total_changes
snapshots = []
errors = []

def snap(name):
    snapshots.append({
        'checkpoint': name,
        'parent': con.execute('SELECT id,label FROM parent ORDER BY id').fetchall(),
        'child': con.execute('SELECT id,pid FROM child ORDER BY id').fetchall(),
        'audit': [row[0] for row in con.execute('SELECT event FROM audit ORDER BY event')],
        'in_transaction': con.in_transaction,
        'foreign_keys': con.execute('PRAGMA foreign_keys').fetchone()[0],
        'changes': con.execute('SELECT changes()').fetchone()[0],
        'total_delta': con.total_changes-base,
        'fk_violations': sorted(con.execute('PRAGMA foreign_key_check').fetchall()),
    })

def attempt(name, operation):
    try:
        operation()
    except sqlite3.IntegrityError as exc:
        errors.append({'operation': name, 'sqlite_errorname': exc.sqlite_errorname})

snap('S0')
con.execute('BEGIN')
con.execute('SAVEPOINT stage')
con.execute("INSERT OR REPLACE INTO parent VALUES(4,'A')")
snap('S1')
attempt('multirow_fail', lambda: con.execute("INSERT OR FAIL INTO parent VALUES(5,'D'),(6,'B'),(7,'E')"))
snap('S2')
con.execute('ROLLBACK TO stage')
snap('S3')
con.execute("INSERT INTO parent VALUES(8,'Z')")
con.execute('INSERT INTO child VALUES(801,99)')
attempt('explicit_commit', lambda: con.execute('COMMIT'))
snap('S4')
con.execute('DELETE FROM child WHERE id=801')
con.execute('COMMIT')
snap('S5')
con.execute('PRAGMA recursive_triggers=ON')
con.execute('BEGIN')
attempt('unique_update', lambda: con.execute("UPDATE parent SET label='B' WHERE id=8"))
con.execute("INSERT OR REPLACE INTO parent VALUES(9,'B')")
snap('S6')
con.execute('ROLLBACK')
snap('S7')
con.autocommit = False
con.execute('PRAGMA foreign_keys=OFF')
with con:
    con.execute('DELETE FROM parent WHERE id=1')
snap('S8')
try:
    with con:
        con.execute('INSERT INTO child VALUES(999,123)')
except sqlite3.IntegrityError as exc:
    errors.append({'operation': 'context_commit', 'sqlite_errorname': exc.sqlite_errorname})
snap('S9')
con.rollback()
con.autocommit = True
con.execute('PRAGMA foreign_keys=OFF')
con.execute('DELETE FROM parent WHERE id=2')
snap('S10')
print(json.dumps({'python': sys.version.split()[0], 'sqlite': sqlite3.sqlite_version, 'base_total_changes': base,
                  'errors': errors, 'snapshots': snapshots}, indent=2))
