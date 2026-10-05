#!/usr/bin/env python3
"""C17, the checked site manifest ([MEMFN], integration.md §R4.3.4).

Usage: site_manifest_check.py ROOT ROW_FLOOR

ROOT is the tree to check (its src/gen/, src/enc/, src/ and
tests/memfn/{site_manifest,search_vocab}.tsv). ROW_FLOOR is the K35 floor
on the manifest's row count; the caller (run_site_manifest.sh) passes its
own literal, which shares no source with the manifest.

The four failure rules (§R4.3.4):
  1. static half: a function under src/gen/ or src/enc/ spells a vocabulary
     form and no `pending` row names it;
  2. dynamic half: a site reaches mf_emit_site with no `delegated` row --
     UNREACHED (K35) while no pcrec source calls mf_emit_site, and a FAIL
     the day one does and this half is still unbuilt;
  3. a `delegated` row's emitter still spells a form (two spellings of one
     search, D122) -- vacuous while there are no delegated rows, and said so;
  4. a `pending` row's emitter spells nothing: the row is stale.
Plus the manifest's own shape: two-state status, unique ids, every named
function and companion defined, and the row count at or above the floor.

Prints PASS:/FAIL: lines and the `checks passed:`/`checks failed:` totals
tests/mech scrapes. Exit 1 on any FAIL.
"""

import glob
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c17_lex import scan  # noqa: E402

STATUSES = ('delegated', 'pending')     # the ruled vocabulary, no third state
BUDGETS = ('scan', 'loop')
SCAN_DIRS = ('src/gen', 'src/enc')      # [rev4.6] src/enc/ for N7 (Q54)

passed = 0
failed = 0


def ok(msg):
    global passed
    passed += 1
    print('PASS: ' + msg)


def bad(msg):
    global failed
    failed += 1
    print('FAIL: ' + msg)


def read_tsv(path, ncol):
    rows = []
    with open(path, encoding='utf-8') as fh:
        for n, raw in enumerate(fh, 1):
            line = raw.rstrip('\n')
            if not line.strip() or line.startswith('#'):
                continue
            f = line.split('\t')
            if len(f) != ncol:
                bad('%s:%d: %d fields, want %d' % (path, n, len(f), ncol))
                continue
            rows.append((n, f))
    return rows


def main():
    if len(sys.argv) != 3:
        print('usage: site_manifest_check.py ROOT ROW_FLOOR', file=sys.stderr)
        return 2
    root, floor = sys.argv[1], int(sys.argv[2])
    mpath = os.path.join(root, 'tests/memfn/site_manifest.tsv')
    vpath = os.path.join(root, 'tests/memfn/search_vocab.tsv')

    # -- the vocabulary ----------------------------------------------------
    vocab = []
    for n, (cls, lid, rx, _doc) in read_tsv(vpath, 4):
        try:
            vocab.append((cls, lid, re.compile(rx)))
        except re.error as e:
            bad('%s:%d: line %s does not compile: %s' % (vpath, n, lid, e))
    if not vocab:
        bad('the search vocabulary is EMPTY: the static half would see nothing')
    else:
        ok('search vocabulary: %d lines in %d classes'
           % (len(vocab), len({c for c, _, _ in vocab})))

    # -- the emitters ------------------------------------------------------
    files = []
    for d in SCAN_DIRS:
        files += sorted(glob.glob(os.path.join(root, d, '*.c')))
        files += sorted(glob.glob(os.path.join(root, d, '*.h')))
    defined = set()
    spells = {}         # function -> [(file:line, line-id, excerpt)]
    by_class = {}
    for path in files:
        lits, defs = scan(path)
        defined |= defs
        rel = os.path.relpath(path, root)
        for fn, line, text in lits:
            if fn.startswith('#'):
                continue
            for cls, lid, rx in vocab:
                m = rx.search(text)
                if m:
                    spells.setdefault(fn, []).append(
                        ('%s:%d' % (rel, line), lid, text[m.start():m.start() + 48]))
                    by_class[cls] = by_class.get(cls, 0) + 1
    nforms = sum(len(v) for v in spells.values())
    print('static half: %d files under %s; %d forms in %d functions (%s)'
          % (len(files), ' and '.join(d + '/' for d in SCAN_DIRS), nforms,
             len(spells), ', '.join('%s %d' % kv for kv in sorted(by_class.items()))))
    memchr = sum(1 for v in spells.values() for _, lid, ex in v
                 if lid == 'libc-call' and ex.startswith('memchr('))
    print('  (C12 reading, information only until C12 is born at R4c: '
          'emitted-text memchr( calls = %d)' % memchr)

    # -- the manifest's shape ----------------------------------------------
    rows = read_tsv(mpath, 8)
    seen = {}
    pend_fns, deleg_fns = {}, {}
    counts = {s: 0 for s in STATUSES}
    for n, (site, emitters, _op, budget, _step, status, comps, _ref) in rows:
        where = '%s:%d (%s)' % (os.path.relpath(mpath, root), n, site)
        if site in seen:
            bad('%s: duplicate site id (first at line %d)' % (where, seen[site]))
        seen.setdefault(site, n)
        if status not in STATUSES:
            bad('%s: status %r is not one of %s -- the vocabulary has no third '
                'state' % (where, status, '/'.join(STATUSES)))
            continue
        counts[status] += 1
        if budget not in BUDGETS:
            bad('%s: budget %r is not one of %s' % (where, budget, '/'.join(BUDGETS)))
        fns = [e for e in emitters.split(',') if e]
        if not fns:
            bad('%s: names no emitter' % where)
        for fn in fns + [c for c in comps.split(',') if c]:
            if fn not in defined:
                bad('%s: %s is defined nowhere under %s (renamed or removed?)'
                    % (where, fn, ' or '.join(SCAN_DIRS)))
        for fn in fns:
            (pend_fns if status == 'pending' else deleg_fns).setdefault(fn, []).append(site)
    total = counts['delegated'] + counts['pending']
    print('manifest: %d rows -- delegated %d / pending %d (K35 floor %d)'
          % (total, counts['delegated'], counts['pending'], floor))
    if total < floor:
        bad('the manifest holds %d rows, below its K35 floor of %d: a row was '
            'deleted without the floor being lowered in the same change' % (total, floor))
    else:
        ok('manifest row count %d >= K35 floor %d' % (total, floor))

    # -- rule 1: an unlisted site, static half -----------------------------
    r1 = 0
    for fn in sorted(spells):
        if fn in pend_fns:
            continue
        if fn in deleg_fns:
            continue                    # rule 3's case, reported there
        r1 += 1
        for at, lid, ex in spells[fn]:
            bad('rule 1 (static half): %s in %s spells a %s form (%r) and no '
                'pending row names it' % (at, fn, lid, ex))
    if r1 == 0:
        ok('rule 1 (static half): every one of the %d functions that spell a '
           'form is named by a pending row' % len(spells))

    # -- rule 2: an unlisted site, dynamic half ----------------------------
    calls = 0
    for path in glob.glob(os.path.join(root, 'src', '**', '*.[ch]'), recursive=True):
        with open(path, encoding='utf-8', errors='replace') as fh:
            code = re.sub(r'/\*.*?\*/|//[^\n]*', ' ', fh.read(), flags=re.S)
            calls += len(re.findall(r'\bmf_emit_site\s*\(', code))
    if calls == 0:
        print('UNREACHED: rule 2 (dynamic half): no pcrec source calls '
              'mf_emit_site, so the corpus compile pass has no site call to '
              'count -- declared UNREACHED (K35), not passed. Site calls '
              'counted: 0.')
    else:
        bad('rule 2 (dynamic half): %d mf_emit_site call(s) under src/ but the '
            'dynamic half (the corpus pass census against delegated rows) is not '
            'built -- it is no longer unreachable; build it in this change' % calls)

    # -- rule 3: a delegated row whose emitter still spells a form ----------
    if counts['delegated'] == 0:
        print('VACUOUS: rule 3 (delegated emitter still spells a form): 0 '
              'delegated rows, nothing to check -- not counted as a pass.')
    else:
        r3 = 0
        for fn in sorted(deleg_fns):
            for at, lid, ex in spells.get(fn, []):
                r3 += 1
                bad('rule 3: %s in %s (delegated: %s) still spells a %s form (%r): '
                    'two spellings of one search (D122)'
                    % (at, fn, ','.join(deleg_fns[fn]), lid, ex))
        if r3 == 0:
            ok('rule 3: no emitter of the %d delegated rows spells a form'
               % counts['delegated'])

    # -- rule 4: a pending row whose emitter spells nothing ----------------
    for fn in sorted(pend_fns):
        if fn not in defined:
            continue                    # already a FAIL above
        if fn in spells:
            ok('rule 4: %s (pending: %s) spells %d form(s)'
               % (fn, ','.join(pend_fns[fn]), len(spells[fn])))
        else:
            bad('rule 4: %s (pending: %s) spells no vocabulary form: the row is '
                'stale (flip it to delegated in its step\'s REPLACE commit, or '
                'teach search_vocab.tsv the form it now spells)'
                % (fn, ','.join(pend_fns[fn])))

    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
