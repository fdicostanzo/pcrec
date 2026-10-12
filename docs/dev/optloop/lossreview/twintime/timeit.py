#!/usr/bin/env python3
"""twintime timing driver (scratch tier; QUIET slot only).

    timeit.py CELL REGIME SUBJ_GLOB... [--rounds R] [--inner I] [--core C] [--out TSV]

Runs, for one cell built by build_arms.sh ($LR/tt/CELL/ARM/pPAD/fatime), the
timing driver `fatime I SUBJ...` (the bench's find-all loop, best of I per
subject) once per (pad, arm) per round, ONE process at a time, pinned to
core C, in a shuffled order per round (seeded by the round number, so a rerun
reproduces the order).  Every row is kept: cell regime pad arm round subject ns
ck.  Aborts if any arm's per-subject answer checksum differs from base's.
Env: LR.
"""
import os, random, subprocess, sys, glob

def main():
    a = sys.argv[1:]
    cell, regime = a[0], a[1]
    opts = {'--rounds': '31', '--inner': '11', '--core': '14', '--out': None}
    subj = []
    i = 2
    while i < len(a):
        if a[i] in opts:
            opts[a[i]] = a[i + 1]; i += 2
        else:
            subj += sorted(glob.glob(a[i])); i += 1
    R, I, core = int(opts['--rounds']), opts['--inner'], opts['--core']
    LR = os.environ['LR']
    base = os.path.join(LR, 'tt', cell)
    arms = sorted(d for d in os.listdir(base) if d != 'src')
    pads = sorted({p for d in arms for p in os.listdir(os.path.join(base, d))}, key=lambda s: int(s[1:]))
    out = open(opts['--out'], 'a')
    ref = {}
    jobs = [(p, ar) for p in pads for ar in arms]
    for rnd in range(1, R + 1):
        rng = random.Random(rnd)
        order = jobs[:]; rng.shuffle(order)
        la0 = open('/proc/loadavg').read().split()[0]
        for pad, arm in order:
            exe = os.path.join(base, arm, pad, 'fatime')
            r = subprocess.run(['taskset', '-c', core, 'gnutimeout', '300', exe, I] + subj,
                               capture_output=True, text=True)
            if r.returncode:
                sys.exit('fatime failed: %s %s %s' % (arm, pad, r.stderr))
            for ln in r.stdout.splitlines():
                f = ln.split('\t')
                if f[0] == 'TOTAL':
                    continue
                s = os.path.basename(f[0]); ck = f[2][3:]; ns = f[3].split()[0]
                if s in ref and ref[s] != ck:
                    sys.exit('ANSWER MISMATCH %s %s %s %s' % (cell, arm, pad, s))
                ref.setdefault(s, ck)
                out.write('\t'.join([cell, regime, pad, arm, str(rnd), s, ns, ck]) + '\n')
        out.flush()
        print('%s %s round %d/%d load1 %s -> %s' % (cell, regime, rnd, R, la0, open('/proc/loadavg').read().split()[0]), flush=True)

main()
