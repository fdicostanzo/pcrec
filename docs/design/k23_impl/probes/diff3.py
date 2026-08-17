#!/usr/bin/env python3
"""K23 three-way differential: BASELINE pcrec vs MRL-PRUNED prototype vs python `re`.

For each (pattern, subject) it reports, from ONE emitted matcher per arm:
  * the exact backtrack-resumption count (the step-budget metric, counted at
    engine_m4.md 4.2's single charge point -- see steps.sh for the method),
  * the full capture vector (every slot, not just the span), and
  * python `re`'s answer for the same pair, as the base-tier oracle.

Both pcrec arms are emitted with an effectively-infinite step budget, so a
BUDGET refusal never masquerades as a difference in what the engine explores:
the comparison is between the two SEARCHES, and the budget is applied
afterwards, on paper.

Why a differential and not just a step count: the whole soundness claim for
pruning is "it removes only positions no accepting continuation could use",
and the only way that claim fails is a changed ANSWER. Steps alone would
report a spectacular win for a prototype that had simply stopped searching.

Usage:
  diff3.py --cases CASES.tsv [--out REPORT.tsv]
CASES.tsv columns (tab-separated, '#' comments, blank lines ignored):
  pattern <TAB> outer_min <TAB> inner_min <TAB> stride <TAB> len[,len...]
          [<TAB> unit [<TAB> prefix [<TAB> suffix]]]
`unit` is the byte string the inner body matches (`a`, `ab`, `abc`, ...);
the middle of the subject is that unit repeated and TRUNCATED to `len`
bytes, so a `len` that is not a multiple of the unit's width is a RESIDUE
case -- the axis R26 E2 found missing. The subject is
`prefix + that + suffix`, so a case can put the match
somewhere other than offset 0 (the unanchored-search axis: the clamp is
stated against the SUBJECT END, and a match that starts late must still be
found) and can give the outer loop a non-empty follow.
`outer_min`/`inner_min`/`stride` are the prototype's MRL parameters (see
prune_proto.py); the baseline arm ignores them.
"""
import argparse
import os
import re as _re
import shutil
import subprocess
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
PCREC = os.environ.get('PCREC', os.path.join(ROOT, 'build', 'pcrec'))
CC = os.environ.get('CC', 'gcc')
BUDGET = os.environ.get('K23_BUDGET', '1000000000000')
RUN_TIMEOUT = int(os.environ.get('K23_TIMEOUT', '300'))

# `(BODY{m,M}){p,P}` -- P is what a REPLICATED outer must produce in scan
# sites; anything else means the shape is not what the prototype assumes.
# The body may itself be a non-capturing group (`(?:ab)`), which is how the
# R26 E2 corpus reaches stride > 1, so the body pattern allows one nesting
# level rather than forbidding parentheses outright.
OUTER_MAX = _re.compile(
    r'^\((?:[^()]|\(\?:[^()]*\))*\{\d+,\d+\}\??\)\{\d+,(\d+)\}')

HEAD = '''#include <stdio.h>
#include <stdlib.h>
static long long rx_probe_steps = 0;
static void rx_probe_report(void){ fprintf(stderr, "STEPS %lld\\n", rx_probe_steps); }
'''

# Print EVERY capture slot, not just the span: the soundness question is about
# where the groups land, and PCRE2 leftmost-greedy semantics are exact (D26).
CAPS_PRINT = r'''        { int k_; printf("match");
          for (k_ = 0; k_ < RX_NCAPS; k_++)
              printf(" %td %td", caps[k_][0], caps[k_][1]);
          printf("\n"); }
'''


def instrument(src_text):
    """The two mechanical substitutions, both asserted to have landed."""
    t = src_text.replace(
        'if (--w->budget < 0) return RX_R_STEPS;',
        'rx_probe_steps++; if (--w->budget < 0) return RX_R_STEPS;')
    n_inc = t.count('rx_probe_steps++')
    t = t.replace(
        '    if (argc < 2) { fprintf(stderr, "usage',
        '    atexit(rx_probe_report);\n    if (argc < 2) { fprintf(stderr, "usage')
    n_hook = t.count('atexit(rx_probe_report)')
    t = t.replace('        printf("match %td %td\\n", caps[0][0], caps[0][1]);\n',
                  CAPS_PRINT)
    n_caps = t.count('for (k_ = 0; k_ < RX_NCAPS; k_++)')
    if (n_inc, n_hook, n_caps) != (1, 1, 1):
        raise SystemExit('diff3: instrumentation did not land: '
                         'inc=%d hook=%d caps=%d' % (n_inc, n_hook, n_caps))
    return HEAD + t


def build(tmp, name, pattern, prune=None):
    src = os.path.join(tmp, name + '.c')
    r = subprocess.run([PCREC, '-p', 'rx', '--emit-main',
                        '--step-budget=' + BUDGET, '-o', src, '--', pattern],
                       capture_output=True, text=True)
    if r.returncode != 0:
        return None, 'emit-fail: ' + r.stderr.strip().splitlines()[-1:][0] if r.stderr else 'emit-fail'
    if prune is not None:
        omin, imin, stride = prune
        pruned = os.path.join(tmp, name + '.pruned.c')
        cmd = [sys.executable, os.path.join(HERE, 'prune_proto.py'),
               src, pruned, '--outer-min', str(omin),
               '--inner-min', str(imin), '--stride', str(stride)]
        # Pass the ASSUMPTION GUARD whenever the pattern is the two-level
        # shape the prototype claims: the outer maximum is how many scan
        # sites a replicated outer must produce. A shape that produces a
        # different number is one the prototype must DECLINE, not patch --
        # the randomized sweep found 44 wrong answers from exactly that
        # mis-fire (k23_design.md section 11.1).
        omax = OUTER_MAX.match(pattern)
        if omax:
            cmd += ['--replicas', omax.group(1)]
        p = subprocess.run(cmd, capture_output=True, text=True)
        if p.returncode == 2:
            return None, 'declined: ' + p.stderr.strip().splitlines()[-1]
        if p.returncode != 0:
            return None, 'prune-fail: ' + p.stderr.strip()
        src = pruned
    inst = os.path.join(tmp, name + '.i.c')
    with open(inst, 'w') as f:
        f.write(instrument(open(src).read()))
    exe = os.path.join(tmp, name + '.bin')
    c = subprocess.run([CC, '-O2', '-o', exe, inst], capture_output=True, text=True)
    if c.returncode != 0:
        return None, 'cc-fail'
    return exe, None


def run(exe, subject):
    try:
        r = subprocess.run([exe, subject], capture_output=True, text=True,
                           timeout=RUN_TIMEOUT)
    except subprocess.TimeoutExpired:
        return None, None
    m = _re.search(r'^STEPS (\d+)$', r.stderr, _re.M)
    steps = int(m.group(1)) if m else None
    out = r.stdout.strip()
    if out.startswith('match'):
        v = tuple(int(x) for x in out.split()[1:])
    elif out.startswith('nomatch'):
        v = ()
    else:
        v = None
    return steps, v


def oracle(pattern, subject):
    m = _re.compile(pattern).search(subject)
    if not m:
        return ()
    out = []
    for k in range(m.re.groups + 1):
        s, e = m.span(k)
        out.extend((s, e))
    return tuple(out)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--cases', required=True)
    ap.add_argument('--out', default='-')
    a = ap.parse_args()

    rows = []
    for line in open(a.cases):
        line = line.rstrip('\n')
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        f = line.split('\t')
        rows.append((f[0], int(f[1]), int(f[2]), int(f[3]), f[4],
                     f[5] if len(f) > 5 else 'a',
                     f[6] if len(f) > 6 else '',
                     f[7] if len(f) > 7 else ''))

    out = sys.stdout if a.out == '-' else open(a.out, 'w')
    print('pattern\tn\tbase_steps\tprune_steps\tbase_caps\tprune_caps'
          '\toracle_caps\tverdict', file=out)
    ndiff = nagree = 0
    for pat, omin, imin, stride, lens, ch, pre, suf in rows:
        tmp = tempfile.mkdtemp(prefix='k23diff.')
        try:
            b, err = build(tmp, 'base', pat)
            if b is None:
                print('%s\t-\t-\t-\t-\t-\t-\t%s' % (pat, err), file=out)
                continue
            p, err = build(tmp, 'prune', pat, prune=(omin, imin, stride))
            if p is None:
                print('%s\t-\t-\t-\t-\t-\t-\t%s' % (pat, err), file=out)
                continue
            for L in (int(x) for x in lens.split(',')):
                reps = -(-L // len(ch)) if ch else 0
                subj = pre + (ch * reps)[:L] + suf
                bs, bv = run(b, subj)
                ps, pv = run(p, subj)
                ov = oracle(pat, subj)
                if bv == pv == ov:
                    verdict = 'AGREE'
                    nagree += 1
                else:
                    verdict = 'DIFFER'
                    ndiff += 1
                print('%s\t%d\t%s\t%s\t%s\t%s\t%s\t%s'
                      % (pat, L, bs, ps, bv, pv, ov, verdict), file=out)
                out.flush()
        finally:
            shutil.rmtree(tmp, ignore_errors=True)
    print('# agree=%d differ=%d' % (nagree, ndiff), file=out)
    if out is not sys.stdout:
        out.close()
    sys.exit(1 if ndiff else 0)


if __name__ == '__main__':
    main()
