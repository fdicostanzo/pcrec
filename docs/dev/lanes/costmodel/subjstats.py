#!/usr/bin/env python3
"""costmodel: SUBJECT facts per (cell, subject), counted from the subject
files (no clock).  For each cell's scanned set S (r17loss §1, read off the
emitted __mask):

  n         subject bytes
  ppm       members of S per million bytes (byte density)
  land      LANDINGS: maximal runs of S (a run-consuming scan stops once per run)
  gmean     mean bytes between consecutive landing starts (n / land when land > 0)
  gcv       coefficient of variation of the inter-landing gaps (irregularity)
  g_lt8     share of inter-landing gaps < 8 bytes (inside one SWAR word)
  g_lt64    share of inter-landing gaps < 64 bytes (inside one W=64 block)
  runmean   mean S-run length
  skmean    mean length of the non-member runs between landings (what a walk skips)
  skcv      their coefficient of variation
  skmode    share of those runs whose length equals the most common length
            (a proxy for how predictable the walk's loop exit is)

usage: python3 -I subjstats.py SUBJDIR SHORTFILE > subjstats.tsv
"""
import sys, os, statistics

SETS = {
    'dig': set(range(0x30, 0x3a)),
    'email': set(range(0x61, 0x7b)),
    'bounded': set(range(0x61, 0x7b)),
    'word-eq': set(range(0x41, 0x5b)) | {0x5f} | set(range(0x61, 0x7b)),
    'hex-run': set(range(0x30, 0x3a)) | set(range(0x61, 0x67)),
    'dfa-hat': {0x66, 0x6e, 0x74},
    'vm-hat': {0x61, 0x62},
    'vm-hat-1': {0x71},
}
CELLS = "dig email word-eq hex-run bounded dfa-hat vm-hat vm-hat-1".split()
SUBS = "short prose64k digits64k prose1m mix64k docs64k docs1m code64k code1m".split()


def stats(b, S):
    n = len(b)
    mem = 0
    starts = []
    runs = []
    prev = False
    cur = 0
    for i, c in enumerate(b):
        m = c in S
        if m:
            mem += 1
            if not prev:
                starts.append(i)
                cur = 0
            cur += 1
        elif prev:
            runs.append(cur)
        prev = m
    if prev:
        runs.append(cur)
    land = len(starts)
    gaps = [starts[i + 1] - starts[i] for i in range(land - 1)]
    gmean = n / land if land else float('inf')
    if len(gaps) >= 2:
        mu = statistics.mean(gaps)
        cv = statistics.pstdev(gaps) / mu if mu else 0.0
        lt8 = sum(g < 8 for g in gaps) / len(gaps)
        lt64 = sum(g < 64 for g in gaps) / len(gaps)
    else:
        cv = lt8 = lt64 = float('nan')
    rm = statistics.mean(runs) if runs else 0.0
    # non-member runs strictly between two landings
    sk = []
    cur = 0
    inside = False
    for c in b:
        m = c in S
        if m:
            if inside and cur > 0:
                sk.append(cur)
            inside = True
            cur = 0
        elif inside:
            cur += 1
    if len(sk) >= 2:
        skm = statistics.mean(sk)
        skcv = statistics.pstdev(sk) / skm
        cnt = {}
        for x in sk:
            cnt[x] = cnt.get(x, 0) + 1
        skmode = max(cnt.values()) / len(sk)
    else:
        skm = skcv = skmode = float('nan')
    return dict(n=n, ppm=round(mem * 1e6 / n), land=land, gmean=gmean, gcv=cv,
                g_lt8=lt8, g_lt64=lt64, runmean=rm, skmean=skm, skcv=skcv, skmode=skmode)


def main():
    sd, short = sys.argv[1], sys.argv[2]
    print("cell\tsubject\tn\tppm\tland\tgmean\tgcv\tg_lt8\tg_lt64\trunmean\tskmean\tskcv\tskmode")
    for s in SUBS:
        path = short if s == 'short' else os.path.join(sd, s)
        b = open(path, 'rb').read()
        for c in CELLS:
            r = stats(b, SETS[c])
            print("\t".join([c, s, str(r['n']), str(r['ppm']), str(r['land']),
                             "%.2f" % r['gmean'], "%.3f" % r['gcv'],
                             "%.3f" % r['g_lt8'], "%.3f" % r['g_lt64'],
                             "%.2f" % r['runmean'], "%.2f" % r['skmean'],
                             "%.3f" % r['skcv'], "%.3f" % r['skmode']]))


if __name__ == '__main__':
    main()
