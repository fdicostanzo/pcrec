#!/usr/bin/env python3
"""C12, C13 and C14 ([MEMFN], integration.md §9.3 I5, §10.5, §14.6, §14.7).

Usage: form_checks.py ROOT CC CEIL_ROWS_FLOOR

C12  the emitted-form ratchet: per (emitter file, vocabulary line, libc call)
     the search forms pcrec's emitters spell, against tests/memfn/
     c12_ceilings.tsv. Ceilings only DESCEND; both a rise and a stale high
     ceiling are red (see the TSV's header). CEIL_ROWS_FLOOR is the K35 floor
     on the TSV's row count, a literal the caller holds.
C13  `on_cand` duplicability: declared UNREACHED while no `on_cand` producer
     exists under src/, cli/ or lib/ (R4e is the first); and RED the day one
     exists with C13 still unbuilt, so it can never pass vacuously.
C14  shape bounds: a TU compiled with $CC against the tree's own core/internal.h
     (so limits.def's CURRENT values) and memfn.h asserts MF_MAX_TERM >=
     PCREC_OFSK_MAX_SET + 1, npred wide enough for every byte (uint16_t),
     MF_MAX_BACK covering today's deepest rewind (-1), and (M6, MF_SITE_ABI 8)
     MF_MAX_TERM >= src/gen/emit_vm.c's VM_MAX_STRIDE (the VM cursor rung's
     widest body is one strided ADVANCE site, one SET term per position; the
     enum is read from the source, hard-failing if absent, and passed in as
     C14_VM_MAX_STRIDE). Two controls compile the same asserts against copies
     of memfn.h with MF_MAX_TERM lowered below each bound and require the
     compile to FAIL on that bound's own assert (each assert can fire).

Prints PASS:/FAIL:/UNREACHED: lines and the `checks passed:`/`checks failed:`
totals tests/mech scrapes. Exit 1 on any FAIL.
"""

import glob
import os
import re
import shutil
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from c17_lex import scan  # noqa: E402

SCAN_DIRS = ('src/gen', 'src/enc')
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


def tsv(path, ncol):
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
            rows.append(f)
    return rows


def c12(root, floor):
    vocab = []
    for cls, lid, rx, _doc in tsv(os.path.join(root, 'tests/memfn/search_vocab.tsv'), 4):
        vocab.append((cls, lid, re.compile(rx)))
    count = {}
    sites = {}
    for d in SCAN_DIRS:
        for path in sorted(glob.glob(os.path.join(root, d, '*.[ch]'))):
            rel = os.path.relpath(path, root)
            lits, _defs = scan(path)
            for fn, line, text in lits:
                if fn.startswith('#'):
                    continue
                for _cls, lid, rx in vocab:
                    for m in rx.finditer(text):
                        call = m.group(0).split('(')[0] if lid == 'libc-call' else '-'
                        key = (rel, lid, call)
                        count[key] = count.get(key, 0) + 1
                        sites.setdefault(key, []).append('%s:%d (%s)' % (rel, line, fn))
    ceil = {}
    rows = tsv(os.path.join(root, 'tests/memfn/c12_ceilings.tsv'), 5)
    for path, lid, call, n, _note in rows:
        key = (path, lid, call)
        if key in ceil:
            bad('c12_ceilings.tsv: duplicate row %r' % (key,))
        ceil[key] = int(n)
    total, ctotal = sum(count.values()), sum(ceil.values())
    print('C12: %d forms in %d (file, line, call) groups; %d ceiling rows, ceilings sum %d'
          % (total, len(count), len(ceil), ctotal))
    by = {}
    for (rel, lid, call), n in count.items():
        k = lid if call == '-' else call
        by[k] = by.get(k, 0) + n
    print('  by class: ' + ', '.join('%s %d' % kv for kv in sorted(by.items())))
    if len(ceil) < floor:
        bad('C12: the ceiling table holds %d rows, below its K35 floor of %d: a row was '
            'deleted (a form with no row has ceiling 0, so this would hide a lowering '
            'that was never earned)' % (len(ceil), floor))
    else:
        ok('C12: ceiling row count %d >= K35 floor %d' % (len(ceil), floor))
    r = 0
    for key in sorted(set(count) | set(ceil)):
        have, cap = count.get(key, 0), ceil.get(key, 0)
        if have > cap:
            r += 1
            bad('C12: %s %s %s: %d form(s) spelled, ceiling %d -- a replaced form came back or a '
                'new one was spelled outside the kit (%s)'
                % (key[0], key[1], key[2], have, cap, '; '.join(sites[key][cap:cap + 3])))
        elif have < cap:
            r += 1
            bad('C12: %s %s %s: %d form(s) spelled, ceiling %d -- STALE ceiling: lower the row '
                '(the ratchet only descends), or the lexer/vocabulary stopped seeing a form'
                % (key[0], key[1], key[2], have, cap))
    if not r:
        ok('C12: every group is at its ceiling (%d forms in %d groups)' % (total, len(count)))


def strip_comments(text):
    return re.sub(r'/\*.*?\*/|//[^\n]*', ' ', text, flags=re.S)


def c13(root):
    producers = 0
    for d in ('src', 'cli', 'lib'):
        for dp, _dns, fns in os.walk(os.path.join(root, d)):
            for fn in fns:
                if fn.endswith(('.c', '.h')):
                    with open(os.path.join(dp, fn), encoding='utf-8', errors='replace') as fh:
                        producers += len(re.findall(r'\bon_cand\b', strip_comments(fh.read())))
    if producers == 0:
        print('UNREACHED: C13 (on_cand duplicability): no on_cand producer exists under src/, cli/ '
              'or lib/ (the first arrives with R4e), so there is nothing to render twice -- '
              'declared UNREACHED (K35), not passed. Producers counted: 0.')
    else:
        bad('C13: %d on_cand reference(s) under src/, cli/ or lib/ but the duplicability check '
            '(render every producer twice in one function, compile under -Werror, token-scan '
            'for return/goto) is unbuilt -- it is no longer unreachable; build it in this change'
            % producers)


C14_TU = r'''
#include "core/internal.h"
#include "memfn.h"
_Static_assert(MF_MAX_TERM >= PCREC_OFSK_MAX_SET + 1,
               "C14: MF_MAX_TERM must hold PCREC_OFSK_MAX_SET offsets plus the run term");
_Static_assert(sizeof(((mf_site *)0)->npred) >= 2,
               "C14: npred must index every byte (N4's set may hold 256)");
_Static_assert(MF_MAX_BACK >= 1, "C14: MF_MAX_BACK must cover today's deepest rewind (-1)");
_Static_assert(MF_MAX_TERM >= C14_VM_MAX_STRIDE,
               "C14 stride: MF_MAX_TERM must hold VM_MAX_STRIDE positions (one strided site)");
int c14_unused;
'''


def c14_compile(cc, root, tmp, include_dir, name, stride):
    src = os.path.join(tmp, name + '.c')
    with open(src, 'w') as fh:
        fh.write(C14_TU)
    r = subprocess.run([cc, '-std=gnu11', '-fsyntax-only', '-DC14_VM_MAX_STRIDE=%d' % stride,
                        '-I' + os.path.join(root, 'lib'),
                        '-I' + os.path.join(root, 'src'), '-I' + include_dir, src],
                       capture_output=True, text=True)
    return r.returncode, r.stderr


def c14(root, cc, tmpbase):
    limits = os.path.join(root, 'src/core/limits.def')
    with open(limits, encoding='utf-8') as fh:
        m = re.findall(r'^PCREC_LIMIT\(PCREC_OFSK_MAX_SET,\s*(\d+),', fh.read(), re.M)
    hdr = os.path.join(root, 'memfn/include/memfn.h')
    with open(hdr, encoding='utf-8') as fh:
        htxt = fh.read()
    mt = re.search(r'^#define MF_MAX_TERM\s+(\d+)', htxt, re.M)
    with open(os.path.join(root, 'src/gen/emit_vm.c'), encoding='utf-8') as fh:
        ms = re.findall(r'^enum \{ VM_MAX_STRIDE = (\d+) \};', fh.read(), re.M)
    if len(m) != 1 or not mt or len(ms) != 1:
        bad('C14: cannot read the bound (limits.def rows %d, MF_MAX_TERM %s, VM_MAX_STRIDE rows %d)'
            % (len(m), 'found' if mt else 'absent', len(ms)))
        return
    stride = int(ms[0])
    print('C14: limits.def PCREC_OFSK_MAX_SET = %s, memfn.h MF_MAX_TERM = %s (a run term needs %d; '
          'emit_vm.c VM_MAX_STRIDE = %d)' % (m[0], mt.group(1), int(m[0]) + 1, stride))
    tmp = tempfile.mkdtemp(prefix='c14.', dir=tmpbase)
    try:
        rc, err = c14_compile(cc, root, tmp, os.path.join(root, 'memfn/include'), 'real', stride)
        if rc == 0:
            ok('C14: the shape asserts compile against the tree\'s limits.def and memfn.h')
        else:
            bad('C14: a shape bound fails: %s' % ' '.join(err.split())[:300])
        # control: the same asserts against a header with MF_MAX_TERM below the bound
        cdir = os.path.join(tmp, 'inc')
        os.makedirs(cdir)
        lowered = int(m[0])
        with open(os.path.join(cdir, 'memfn.h'), 'w') as fh:
            fh.write(re.sub(r'^(#define MF_MAX_TERM\s+)\d+', r'\g<1>%d' % lowered, htxt, flags=re.M))
        rc2, err2 = c14_compile(cc, root, tmp, cdir, 'ctl', stride)
        if rc2 != 0 and 'C14: MF_MAX_TERM must hold PCREC_OFSK_MAX_SET' in err2:
            ok('C14 control: MF_MAX_TERM lowered to %d (below the bound) makes the assert FIRE' % lowered)
        else:
            bad('C14 control: the lowered header did not trip the assert (rc %d): the check cannot '
                'fail' % rc2)
        # the stride bound's own control: lowered to one below VM_MAX_STRIDE,
        # which still holds the offset-skip bound, so only the stride assert fires
        sdir = os.path.join(tmp, 'incs')
        os.makedirs(sdir)
        with open(os.path.join(sdir, 'memfn.h'), 'w') as fh:
            fh.write(re.sub(r'^(#define MF_MAX_TERM\s+)\d+', r'\g<1>%d' % (stride - 1), htxt,
                            flags=re.M))
        rc3, err3 = c14_compile(cc, root, tmp, sdir, 'ctls', stride)
        if rc3 != 0 and 'C14 stride' in err3 and 'PCREC_OFSK_MAX_SET' not in err3:
            ok('C14 stride control: MF_MAX_TERM lowered to %d (below VM_MAX_STRIDE) makes the '
               'stride assert FIRE' % (stride - 1))
        else:
            bad('C14 stride control: the lowered header did not trip the stride assert alone '
                '(rc %d): the check cannot fail' % rc3)
    finally:
        shutil.rmtree(tmp, ignore_errors=True)


def main():
    if len(sys.argv) != 4:
        print('usage: form_checks.py ROOT CC CEIL_ROWS_FLOOR', file=sys.stderr)
        return 2
    root, cc, floor = sys.argv[1], sys.argv[2], int(sys.argv[3])
    c12(root, floor)
    c13(root)
    c14(root, cc, os.environ.get('TMPDIR'))
    print('checks passed: %d' % passed)
    print('checks failed: %d' % failed)
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
