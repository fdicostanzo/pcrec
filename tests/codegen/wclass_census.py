#!/usr/bin/env python3
"""tests/codegen/wclass_census.py -- [CLS-TREE] S3's A_WCLASS switch census.

`-Wswitch` forces every `AKind` switch to TOUCH `A_WCLASS`; it cannot make the
arm RIGHT (docs/design/cls_tree_design.md §7 a2, r1 SEM-1), and plain `make`
only warns. This census asserts the three structural facts a reviewer would
otherwise read by eye, over every `switch` in src/ whose top-level labels name
an `AKind` member:

  [5a] every one carries a `case A_WCLASS` label;
  [5b] no label run (the labels sharing one body) holds both `A_CLASS` and
       `A_WCLASS` -- the `A_CLASS` arm reads the code-point SET, and a wide
       class confined to U+0080..U+00FF (`é`) renders as a valid bitmap of
       the wrong bytes (r54 E1; docs/dev/cls_s3_reader_inventory.md §4);
  [5c] none carries a depth-1 `default:`, which `-Wswitch` cannot see
       through (D-6 converted the last five).

The AKind member list is READ from src/core/internal.h's enum, never written
here. The population must reach a FLOOR (K35: a scanner whose regex stopped
matching reads as "nothing wrong"), and a SELF-TEST runs the same scanner over
a synthetic source that violates each rule and demands each violation be
reported -- the failing-direction story, run on every invocation.

Usage: wclass_census.py SRC_DIR   (prints PASS:/FAIL: lines; exit 1 on FAIL)
"""
import glob
import os
import re
import sys

POPULATION_FLOOR = 49   # the inventory's measured count at S3 (50 on landing)


def strip_comments(txt):
    """Blank comments, keeping newlines so line numbers survive."""
    txt = re.sub(r'/\*.*?\*/',
                 lambda m: re.sub(r'[^\n]', ' ', m.group(0)), txt, flags=re.S)
    return re.sub(r'//[^\n]*', '', txt)


def akind_members(internal_h):
    txt = strip_comments(open(internal_h).read())
    m = re.search(r'typedef\s+enum\s*\{([^}]*)\}\s*AKind\s*;', txt)
    if not m:
        return []
    return re.findall(r'\b(A_[A-Z0-9_]+)\b', m.group(1))


def switches(txt, members):
    """Yield (line, top-level body text) for every switch naming a member."""
    label_re = re.compile(r'case\s+(%s)\b' % '|'.join(map(re.escape, members)))
    for m in re.finditer(r'\bswitch\s*\(', txt):
        i = txt.find('{', m.end())
        if i < 0:
            continue
        d, j = 0, i
        while j < len(txt):
            if txt[j] == '{':
                d += 1
            elif txt[j] == '}':
                d -= 1
                if d == 0:
                    break
            j += 1
        top, d = [], 0
        for c in txt[i + 1:j]:
            if c == '{':
                d += 1
            elif c == '}':
                d -= 1
            top.append(c if d == 0 or c == '\n' else ' ')
        top = ''.join(top)
        if label_re.search(top):
            yield txt.count('\n', 0, m.start()) + 1, top


def label_runs(top):
    """Maximal runs of case/default labels sharing one body."""
    runs, run = [], []
    for t in re.split(r'(case\s+[A-Za-z_0-9]+\s*:|default\s*:)', top):
        if re.match(r'(case\s+[A-Za-z_0-9]+\s*:|default\s*:)', t):
            run.append(t)
        elif t.strip():
            if run:
                runs.append(run)
            run = []
    if run:
        runs.append(run)
    return runs


def census(files, members):
    """Returns (population, missing, shared, defaults) as lists of sites."""
    pop, missing, shared, defaults = [], [], [], []
    for f in files:
        txt = strip_comments(open(f).read())
        for line, top in switches(txt, members):
            site = '%s:%d' % (f, line)
            pop.append(site)
            if not re.search(r'case\s+A_WCLASS\b', top):
                missing.append(site)
            if re.search(r'\bdefault\s*:', top):
                defaults.append(site)
            for run in label_runs(top):
                j = ' '.join(run)
                if re.search(r'\bA_CLASS\b', j) and re.search(r'\bA_WCLASS\b', j):
                    shared.append(site)
    return pop, missing, shared, defaults


SELFTEST = r'''
int good(const Ast *a) { switch (a->k) { case A_WCLASS: return f(a->l);
    case A_CLASS: return 1; case A_CAT: return 2; } return 0; }
int missing(const Ast *a) { switch (a->k) { case A_CLASS: return 1; } return 0; }
int shared(const Ast *a) { switch (a->k) { case A_WCLASS: /* x */
    case A_CLASS: return 1; } return 0; }
int dflt(const Ast *a) { switch (a->k) { case A_WCLASS: return 0;
    case A_CLASS: return 1; default: return 2; } }
'''


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else 'src'
    fails = 0

    def ok(msg):
        print('PASS: ' + msg)

    def bad(msg):
        nonlocal fails
        fails += 1
        print('FAIL: ' + msg)

    members = akind_members(os.path.join(src, 'core', 'internal.h'))
    if 'A_CLASS' in members and 'A_WCLASS' in members and len(members) >= 10:
        ok('[5] AKind read from internal.h: %d members incl. A_CLASS, A_WCLASS'
           % len(members))
    else:
        bad('[5] could not read the AKind enum from %s/core/internal.h '
            '(got %r) -- the census below would count nothing' % (src, members))
        return 1

    # The failing direction, every run: each planted violation must be seen.
    tmp = os.path.join(os.environ.get('TMPDIR', '/tmp'),
                       'wclass_census_selftest_%d.c' % os.getpid())
    with open(tmp, 'w') as fh:
        fh.write(SELFTEST)
    try:
        p, mi, sh, de = census([tmp], members)
    finally:
        os.unlink(tmp)
    if (len(p) == 4 and len(mi) == 1 and len(sh) == 1 and len(de) == 1):
        ok('[5] self-test: the scanner reports a missing arm, a shared '
           'A_CLASS/A_WCLASS run and a default: in a synthetic source')
    else:
        bad('[5] self-test: expected 4 switches / 1 missing / 1 shared / 1 '
            'default, got %d/%d/%d/%d -- the scanner is blind'
            % (len(p), len(mi), len(sh), len(de)))

    files = sorted(glob.glob(os.path.join(src, '**', '*.c'), recursive=True)
                   + glob.glob(os.path.join(src, '**', '*.h'), recursive=True))
    pop, missing, shared, defaults = census(files, members)
    if len(pop) >= POPULATION_FLOOR:
        ok('[5] population: %d AKind switches (floor %d)'
           % (len(pop), POPULATION_FLOOR))
    else:
        bad('[5] population: %d AKind switches, below the floor %d -- a '
            'census that stopped finding switches reads as clean'
            % (len(pop), POPULATION_FLOOR))
    if missing:
        bad('[5a] %d AKind switch(es) with no case A_WCLASS: %s'
            % (len(missing), ', '.join(missing)))
    else:
        ok('[5a] every AKind switch (%d) handles A_WCLASS' % len(pop))
    if shared:
        bad('[5b] A_WCLASS shares an arm with A_CLASS (that arm reads the '
            'SET; a wide class must walk its byte child): %s'
            % ', '.join(shared))
    else:
        ok('[5b] no arm shares A_WCLASS with A_CLASS')
    if defaults:
        bad('[5c] default: on an AKind switch (-Wswitch cannot see a kind '
            'falling into it): %s' % ', '.join(defaults))
    else:
        ok('[5c] no AKind switch carries a default:')
    return 1 if fails else 0


if __name__ == '__main__':
    sys.exit(main())
