#!/usr/bin/env python3
"""tests/memfn/simd_guarded_check.py -- [MEMFN] RQ-3's check (D155 item 9 +
addendum 2; docs/spec/match_api.md §6.3 `<PREFIX>_SIMD_GUARDED_BYTES` (§6.3.10¶8),
docs/spec/limits.md "Size limits and SIMD-guarded bytes"). Driven by
tests/memfn/run_simd_guarded.sh, which builds the WITNESS compiler.

TWO COMPILERS over one population (a corpus sample plus named witnesses) at
six argv arms:

  PLAIN    the tree's build/pcrec. Every compiled artifact carries exactly
           one `<UP>_SIMD_GUARDED_BYTES` line, and its value is at most the
           sum, over the rendered SIMD sites, of each row's own bound
           (D155 addendum 2: a check in place of an aggregate budget). The
           rendered sites are `<UP>_MEMFN_FORMS`' tokens, each bound read
           from tests/memfn/simd_bounds.tsv; a token with no declared bound
           FAILS (UNDECLARED). Today every value is "none", so the check is
           0 <= 0 and this half alone is vacuous by construction.
  WITNESS  the same tree built with -DPCREC_SIMD_WITNESS: a synthetic guarded
           block written through the sink's simd_open/simd_close at file
           scope (both engines) and at the start of the VM program (the
           knee's buffer). It makes the check non-vacuous two ways:
           ARITHMETIC  the stamp equals blocks x the block's uncut size, the
                       same under -fno-comments (muted bytes are counted), and
                       is at most blocks x the `rq3-witness` row's bound;
           NEUTRALITY  rc, stderr and the artifact equal PLAIN's with the
                       blocks and the stamp line removed: every decision that
                       reads a length (the knee and VM_PROGRAM_BYTES, the size
                       term and its ladder, the caps and every quoted figure)
                       read the same with the blocks as without them.

The witness's own rendered-site enumeration is its guard line, counted in
the text; a real SIMD row's is MEMFN_FORMS. The two sources are independent
of the stamp, which pcrec's sink counts.

Prints `checks passed: N` / `checks failed: N`; exit 1 on any failure.
"""
import argparse
import concurrent.futures
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(TREE, 'scripts'))
import emit_sweep as es  # noqa: E402

GUARD = b'#if defined(PCREC_RQ3_WITNESS_GUARD)'
STAMP = re.compile(rb'^#define (\w+)_SIMD_GUARDED_BYTES (0x[0-9a-f]{16})ULL$', re.M)
FORMS = re.compile(rb'^#define \w+_MEMFN_FORMS "([^"\n]*)"$', re.M)
PROG = re.compile(rb'^#define \w+_VM_PROGRAM_BYTES (\d+)ULL$', re.M)
UNROLL_WHY = re.compile(rb'^#define \w+_UNROLL_K_WHY "([^"\n]*)"$', re.M)

LONG_PREFIX = 'rq3_' + 'p' * 50
ARMS = [
    ('default', []),
    ('vm', ['--engine=vm']),
    ('comments', ['-fcomments']),
    ('nocomments', ['-fno-comments']),
    ('longprefix', ['-p', LONG_PREFIX]),
    ('warn', ['--warn-emit-bytes=1']),   # every compile quotes its two sizes
]

# NAMED WITNESSES, each reaching a reader the corpus sample may not: a VM
# artifact below the entry-shape knee (`forward`/`inline`) and one above it,
# the size term's ladder (NEST8, tests/codegen/run_size_term.sh: the ladder
# runs and moves K, so a trial-abort reader that counts the blocks moves it),
# and a DFA artifact. (The `warn` arm makes every compile quote its sizes, the
# caps' figures; the corpus's own refusals are the both-refuse population.)
NAMED = [
    ('knee-below', 'a(b|c)+d'),
    ('knee-above', '(?:(abc)|(def)|(ghi)){1,40}xyz'),
    ('ladder', '((?:(?:(?:[^a]{1,2}|[^a]??|.{0,2}?)+){0,8}(){2,3}){1,2}){2,3}'),
    ('dfa', 'abc[0-9]+def'),
]

# K35 FLOORS, literal: each population a reader needs, counted over the run.
FLOORS = {
    'compiled': 600,        # PLAIN artifacts checked
    'vm': 200,              # artifacts carrying VM_PROGRAM_BYTES (the knee)
    'dfa': 100,             # artifacts with one block only (no VM program)
    'two-blocks': 200,      # WITNESS artifacts with the VM program's block
    'ladder-moved': 1,      # UNROLL_K_WHY "size-model" (the ladder ran)
    'refused': 1,           # both sides refused alike, stderr included
}


def strip_blocks(text):
    """The artifact with every witness block (guard line through its
    `#endif`) and the stamp line removed; also the block count and the
    bytes of the first block."""
    out, n, first, cur, inside = [], 0, None, [], False
    for ln in text.split(b'\n'):
        if inside:
            cur.append(ln)
            if ln == b'#endif':
                inside = False
                if first is None:
                    first = len(b'\n'.join(cur)) + 1
            continue
        if ln == GUARD:
            inside, n, cur = True, n + 1, [ln]
            continue
        if STAMP.match(ln):
            continue
        out.append(ln)
    return b'\n'.join(out), n, first


def compile_one(binary, pattern, argv_arm, timeout):
    argv = [binary, '--features', 'all']
    if '-p' not in argv_arm:
        argv += ['-p', 'rx']
    argv += argv_arm + ['-o', '-'] + es._pattern_argv(binary, pattern)
    return es.run(argv, timeout)


def load_bounds(path):
    bounds = {}
    with open(path) as f:
        for ln in f:
            ln = ln.strip()
            if not ln or ln.startswith('#'):
                continue
            form, b = ln.split('\t')
            bounds[form] = int(b)
    return bounds


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--plain', required=True)
    ap.add_argument('--witness', required=True)
    ap.add_argument('--every', type=int, default=10)
    ap.add_argument('--jobs', type=int, default=8)
    ap.add_argument('--timeout', type=int, default=120)
    a = ap.parse_args()

    bounds = load_bounds(os.path.join(HERE, 'simd_bounds.tsv'))
    passed, failed = [0], []

    def ok(msg):
        passed[0] += 1
        print('PASS: ' + msg)

    def bad(msg):
        failed.append(msg)
        print('FAIL: ' + msg)

    if 'rq3-witness' not in bounds:
        bad('simd_bounds.tsv declares no `rq3-witness` bound')
        bounds['rq3-witness'] = 0

    corpus = es.enumerate_corpus(a.plain, TREE, 30)
    sample = [('%s:%s' % (f, k), p) for i, (f, k, p) in enumerate(corpus)
              if i % a.every == 0]
    pop = [('named:' + n, p) for n, p in NAMED] + sample
    print('== RQ-3 guarded-bytes check: %d corpus rows, %d sampled, %d named, %d arms =='
          % (len(corpus), len(sample), len(NAMED), len(ARMS)))

    jobs = [(key, pat, arm, argv) for key, pat in pop for arm, argv in ARMS]

    def one(job):
        key, pat, arm, argv = job
        pr = compile_one(a.plain, pat, argv, a.timeout)
        wr = compile_one(a.witness, pat, argv, a.timeout)
        rec = {'key': key, 'arm': arm, 'issues': [], 'counts': []}
        prc, pout, perr = pr
        wrc, wout, werr = wr
        if prc is None or wrc is None:
            rec['issues'].append('timeout (plain rc %s, witness rc %s)' % (prc, wrc))
            return rec
        if prc != wrc:
            rec['issues'].append('rc differs: plain %d, witness %d (%s)'
                                 % (prc, wrc, werr.decode(errors='replace')[:160].strip()))
            return rec
        if perr != werr:
            rec['issues'].append('stderr differs: %r vs %r' % (perr[:120], werr[:120]))
        if prc != 0:
            rec['counts'].append('refused')
            return rec
        rec['counts'].append('compiled')
        # PLAIN: one stamp line, value <= the declared bounds of its forms.
        st = STAMP.findall(pout)
        fm = FORMS.findall(pout)
        if len(st) != 1 or len(fm) != 1:
            rec['issues'].append('plain carries %d stamp / %d MEMFN_FORMS lines' % (len(st), len(fm)))
            return rec
        v = int(st[0][1], 16)
        sites = [] if fm[0] == b'none' else fm[0].decode().split(',')
        total = 0
        for site in sites:
            form = site.split('@')[0]
            if form not in bounds:
                rec['issues'].append('MEMFN_FORMS token %r has no declared bound (UNDECLARED)' % site)
            total += bounds.get(form, 0)
        if v > total:
            rec['issues'].append('plain stamp %d exceeds the sum of its rows\' bounds %d' % (v, total))
        if PROG.search(pout):
            rec['counts'].append('vm')
        why = UNROLL_WHY.search(pout)
        if why and why.group(1) == b'size-model':
            rec['counts'].append('ladder-moved')
        # WITNESS: arithmetic, then neutrality.
        sw = STAMP.findall(wout)
        if len(sw) != 1:
            rec['issues'].append('witness carries %d stamp lines' % len(sw))
            return rec
        vw = int(sw[0][1], 16)
        wstrip, nblk, _ = strip_blocks(wout)
        pstrip, pblk, _ = strip_blocks(pout)
        if pblk:
            rec['issues'].append('plain artifact carries %d witness blocks' % pblk)
        if nblk == 0:
            rec['issues'].append('witness artifact carries no block')
        rec['counts'].append('two-blocks' if nblk >= 2 else 'dfa')
        rec['vw'], rec['nblk'] = vw, nblk
        if vw > nblk * bounds['rq3-witness']:
            rec['issues'].append('witness stamp %d exceeds %d blocks x bound %d'
                                 % (vw, nblk, bounds['rq3-witness']))
        if wstrip != pstrip:
            rec['issues'].append('NEUTRALITY: the artifact moved under the guarded blocks: '
                                 + es.first_diff_hunk(pstrip, wstrip)[:400])
        return rec

    counts = {}
    per_block = {}
    with concurrent.futures.ThreadPoolExecutor(a.jobs) as ex:
        for rec in ex.map(one, jobs):
            for c in rec['counts']:
                counts[c] = counts.get(c, 0) + 1
            for i in rec['issues']:
                bad('%s [%s]: %s' % (rec['key'], rec['arm'], i))
            if 'vw' in rec and rec['nblk']:
                per_block.setdefault(rec['arm'], set()).add(
                    (rec['vw'] // rec['nblk'], rec['vw'] % rec['nblk']))

    # ARITHMETIC: one uncut block size, the same in every arm (comments on or
    # off, any prefix), and every stamp an exact multiple of it.
    sizes = set()
    for arm, s in per_block.items():
        for q, r in s:
            if r:
                bad('arithmetic [%s]: a stamp is not a multiple of its block count' % arm)
            sizes.add(q)
    if len(sizes) == 1:
        ok('arithmetic: every witness stamp is blocks x %d bytes, in every arm '
           '(comments on/off, prefix rx/long)' % next(iter(sizes)))
        if next(iter(sizes)) <= bounds['rq3-witness']:
            ok('arithmetic: the block (%d) is within the rq3-witness bound (%d)'
               % (next(iter(sizes)), bounds['rq3-witness']))
        else:
            bad('arithmetic: the block (%d) exceeds the rq3-witness bound (%d)'
                % (next(iter(sizes)), bounds['rq3-witness']))
    else:
        bad('arithmetic: the uncut block size differs across artifacts/arms: %s'
            % sorted(sizes)[:8])

    for k, floor in FLOORS.items():
        n = counts.get(k, 0)
        if n >= floor:
            ok('population %s: %d (floor %d)' % (k, n, floor))
        else:
            bad('population %s: %d below its floor %d (a reader this check needs is unreached)'
                % (k, n, floor))
    if not failed:
        ok('neutrality and the bound hold on all %d (pattern, arm) cells' % len(jobs))
    print('checks passed: %d' % passed[0])
    print('checks failed: %d' % len(failed))
    return 1 if failed else 0


if __name__ == '__main__':
    sys.exit(main())
