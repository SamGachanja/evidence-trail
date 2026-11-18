import json
import sqlite3
import sys

cases = {
    'A': ['delete'],
    'B': ['delete', 'defer_off'],
    'C': ['delete', 'defer_off', 'defer_on'],
    'D': ['delete', 'save', 'defer_off', 'rollback_to', 'release'],
    'E': ['delete', 'save', 'defer_off', 'rollback_to', 'release', 'repair'],
    'F': ['save', 'delete', 'defer_off', 'rollback_to', 'release'],
    'G': ['rebuild'],
    'H': ['rebuild', 'defer_off'],
    'I': ['rename_rebuild', 'defer_off'],
    'J': ['delete', 'foreign_off'],
}


def state(db):
    return {
        'parent': db.execute('SELECT id FROM parent ORDER BY id').fetchall(),
        'child': db.execute('SELECT id,pid FROM child ORDER BY id').fetchall(),
        'fk_target': db.execute('PRAGMA foreign_key_list(child)').fetchone()[2],
        'violations': sorted(db.execute('PRAGMA foreign_key_check').fetchall()),
        'foreign_keys': db.execute('PRAGMA foreign_keys').fetchone()[0],
        'defer_foreign_keys': db.execute('PRAGMA defer_foreign_keys').fetchone()[0],
        'in_transaction': db.in_transaction,
    }


def run(steps):
    db = sqlite3.connect(':memory:', autocommit=True)
    db.execute('PRAGMA foreign_keys=ON')
    db.execute('PRAGMA legacy_alter_table=OFF')
    db.executescript('''
    CREATE TABLE parent(id INTEGER PRIMARY KEY);
    CREATE TABLE child(id INTEGER PRIMARY KEY,pid INTEGER REFERENCES parent(id));
    INSERT INTO parent VALUES(1);
    INSERT INTO child VALUES(10,1);
    ''')
    db.execute('BEGIN')
    db.execute('PRAGMA defer_foreign_keys=ON')
    for step in steps:
        if step == 'delete':
            db.execute('DELETE FROM parent WHERE id=1')
        elif step == 'defer_off':
            db.execute('PRAGMA defer_foreign_keys=OFF')
        elif step == 'defer_on':
            db.execute('PRAGMA defer_foreign_keys=ON')
        elif step == 'foreign_off':
            db.execute('PRAGMA foreign_keys=OFF')
        elif step == 'save':
            db.execute('SAVEPOINT x')
        elif step == 'rollback_to':
            db.execute('ROLLBACK TO x')
        elif step == 'release':
            db.execute('RELEASE x')
        elif step == 'repair':
            db.execute('INSERT INTO parent VALUES(1)')
        elif step == 'rebuild':
            db.execute('CREATE TABLE replacement(id INTEGER PRIMARY KEY)')
            db.execute('INSERT INTO replacement SELECT id FROM parent')
            db.execute('DROP TABLE parent')
            db.execute('ALTER TABLE replacement RENAME TO parent')
        elif step == 'rename_rebuild':
            db.execute('ALTER TABLE parent RENAME TO old_parent')
            db.execute('CREATE TABLE parent(id INTEGER PRIMARY KEY)')
            db.execute('INSERT INTO parent SELECT id FROM old_parent')
            db.execute('DROP TABLE old_parent')
        else:
            raise ValueError(step)
    before = state(db)
    try:
        db.execute('COMMIT')
        commit = 'success'
    except sqlite3.IntegrityError as exc:
        commit = exc.sqlite_errorname
    after = state(db)
    db.close()
    return {'before_commit': before, 'commit': commit, 'after_commit': after}


print(json.dumps({'python':sys.version.split()[0], 'sqlite':sqlite3.sqlite_version,
                  'cases':{label:run(steps) for label,steps in cases.items()}},indent=2))
