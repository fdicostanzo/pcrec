#!/usr/bin/env python3
"""k82cost: the K82(B) expected-cost model, evaluated (litscan_k82b.md §2).

Usage: k82b_model.py FINDB4_TREE SUBJ_DIR [COSTS]
  FINDB4_TREE  a checkout of lane/findb4 (its src/findings/{weblog,log}.rxt
               carry the bigram blocks; src/findings/default.rxt the prior)
  SUBJ_DIR     the bench throughput subjects, as k82diag/gen.py writes them
  COSTS        'linux' (default) or 'mac': which measured cost row (§1.3)

Rates, per cell and per SOURCE:
  none     run-rarity's NONE answer (markov1 over the all-zero table =
           cardinality, findb4 §2.3); byte-rate per the compile (-e byte:
           the builtin prior; -e utf8: NONE = uniform)
  weblog / log   the shipped bundles: markov1 over their bigram block for the
           run, their freq block for bytes
  subj     the bench subject ITSELF analysed as the exemplar (the oracle arm:
           what a perfectly matched exemplar would say)
  actual   counted on the subject: masked-run occurrences, scan-member stops

Float log2 stands in for findb4's L(x) (Q16, last-bit exact): only the
decision's sign is read here, never a bit.
"""
import math, os, re, sys

TREE, SUBJ = sys.argv[1], sys.argv[2]
COSTS = sys.argv[3] if len(sys.argv) > 3 else 'linux'

def bundle(path):
    t = open(path).read()
    parts = re.split(r'\n    (freq|cpfreq|bigram)\n', t)
    blk = dict(zip(parts[1::2], parts[2::2]))
    c1 = [0] * 256
    for a, n in re.findall(r'^        row ([0-9a-f]{2}) (\d+)$', blk['freq'], re.M):
        c1[int(a, 16)] = int(n)
    c2 = None
    if 'bigram' in blk:
        c2 = {}
        for a, b, n in re.findall(r'^        row ([0-9a-f]{2}) ([0-9a-f]{2}) (\d+)$', blk['bigram'], re.M):
            c2[(int(a, 16), int(b, 16))] = int(n)
    return c1, c2

def from_bytes(data):
    c1 = [0] * 256; c2 = {}
    for x in data: c1[x] += 1
    for a, b in zip(data, data[1:]): c2[(a, b)] = c2.get((a, b), 0) + 1
    return c1, c2

def cube(t, k):
    return [b for b in range(256) if (b & k) == t]

def markov1(c2, sets):
    """findings/design.md §2.6 in floats: -log2 occurrences per position."""
    r = [0] * 256
    for (a, b), n in (c2 or {}).items(): r[a] += n
    N = sum(r)
    U = sum(r[a] + 1 for a in sets[0])
    bits = math.log2((N + 256) / U)
    for s0, s1 in zip(sets, sets[1:]):
        D = sum(r[a] + 256 for a in s0)
        T = sum((c2 or {}).get((a, b), 0) + 1 for a in s0 for b in s1)
        bits += math.log2(D / T)
    return bits

def rate(c1, members):
    if c1 is None: return len(members) / 256.0          # MASS NONE: cardinality
    n = sum(c1); return sum(c1[m] for m in members) / n

def pick(c1, sets, idx_default):
    """pcrec_find_pick over the window's positions as cubes, reversed (ties to
    the rightmost). NONE (c1 is None): the rightmost -- today's answer; under
    the k82fix (C) cure it is argmin cardinality, ties rightmost, which for
    these windows is the default index passed in."""
    if c1 is None: return idx_default
    best = None
    for i in range(len(sets) - 1, -1, -1):
        m = rate(c1, sets[i])
        if best is None or m < best[0]: best = (m, i)
    return best[1]

def occurrences(data, sets):
    L = len(sets); ss = [set(s) for s in sets]; occ = 0
    first = sets[0]; fs = ss[0]
    for i in range(len(data) - L + 1):
        if data[i] in fs and all(data[i + j] in ss[j] for j in range(1, L)): occ += 1
    return occ

# ---- the cells (facts from `pcrec --emit-facts`, worktree build at 940fa06e)
# name, subject, enc, window T hex, window K hex, scan idx, set members
CELLS = [
    ('mod-i',         'syn/t-64k', 'byte', '434154', 'dfdfdf', 0, []),
    ('cls-fold-pair', 'syn/t-64k', 'byte', '634174', 'ffdfff', 0, [99, 116]),
    ('cls-pair-ctl',  'syn/t-64k', 'byte', '636174', 'fffdff', 0, [99, 116]),
    ('ci-strasse',    'u8/t-64k',  'utf8', '545241', 'dfdfdf', 2, []),
    ('alt-shared(C fixed)', 'u8/t-64k', 'utf8', 'e697a5e4', 'fffffffd', 2, [151, 165, 230]),
    ('userpass',      'cap/t-64k', 'byte', '55534552', 'dfdfdfdf', 0, [61]),
    ('union-select',  'cap/t-64k', 'byte', '53454c454354', 'dfdfdfdfdfdf', 4, []),
    ('ci-ascii-ctl',  'u8/t-64k',  'utf8', '414243', 'dfdfdf', 2, []),
    ('slack',         'cap/t-64k', 'byte', '5256494345532f54', 'dfdfdfdfdfdfffdf', 6, [47, 58]),
    ('http-5xx',      'log/t-064k-fail', 'byte', '5454502f312e3022', 'fffffffffffffeff', 2,
                      [32, 34, 46, 47, 49, 53, 72, 80, 84]),
    ('stack-frame',   'log/t-064k-fail', 'byte', '617420', 'ffffff', 0, [32, 40, 41, 46, 97, 116]),
]
# E: the engine's per-byte cost when the gate passes or is absent = the DENY
# arm's ns/B (Linux: r1read_report.md §3 base column; Mac: k82diag §3 deny).
# userpass: the hybrid's DFA prefilter pass, NEW's 0.95 (its gate made 2
# compares/call, so NEW ~= the engine).  http-5xx/stack-frame: log fail base.
E = {'linux': {'mod-i': .96, 'cls-fold-pair': .59, 'cls-pair-ctl': .59, 'ci-strasse': .68,
               'alt-shared(C fixed)': .09, 'userpass': .95, 'union-select': .75,
               'ci-ascii-ctl': .70, 'slack': .24, 'http-5xx': .022, 'stack-frame': .35},
     'mac':   {'mod-i': .75, 'cls-fold-pair': .58, 'cls-pair-ctl': .58, 'ci-strasse': .53,
               'alt-shared(C fixed)': .07, 'userpass': .62, 'union-select': .56,
               'ci-ascii-ctl': .53, 'slack': .24, 'http-5xx': .022, 'stack-frame': .35}}[COSTS]
# The machine cost row (§1.3): f = ns per memchr call entry, beta = ns per
# byte memchr reads, s = ns per stop (a re-search entry + the masked compare).
# mac: memchr_cal.c on the M1 (memchr_cal.mac.out). linux: k82diag §2
# (two fresh memchr = 6.8 ns -> f 3.4; 8-11 ns per scan hit on the
# throughput cells, §1.B -> s 8.0; the short-call +4.4 is a warm-cache low),
# beta assumed equal to the Mac's (glibc AVX2 is not slower; OWED, §1.3).
CST = {'mac': dict(f=3.7, beta=0.020, s=7.5), 'linux': dict(f=3.4, beta=0.020, s=8.0)}[COSTS]

def gate_cost(rho, sigma_streams, W, M):
    """Expected ns per subject of W bytes for a discard-gate, find-all, with
    M matches (calls = M+1).  Each call reads to the first occurrence
    (Poisson, rate rho) or the end; every stream pays f per call plus beta
    per byte; stops at the summed stream rate pay s.  M=0 is the gate's best
    case; M>0 only adds passing calls (the residual, §3)."""
    k = len(sigma_streams); sig = sum(sigma_streams)
    per_byte = k * CST['beta'] + sig * CST['s']
    over = CST['beta'] * sum(min(W, 1 / sj) for sj in sigma_streams if sj > 0) if k > 1 else 0.0
    if M == 0:
        read = (1 - math.exp(-rho * W)) / rho if rho > 0 else W
        return k * CST['f'] + per_byte * read + over
    # M matches spread over W: every call passes but the last; the gate reads
    # the whole subject once, and every call pays entry + overshoot
    return (M + 1) * (k * CST['f'] + over) + per_byte * W

def reject_saving(rho, W, Ecell):
    """Expected engine ns saved: the engine's scan of a subject (or tail) the
    gate proves free of the guard's necessary thing."""
    return Ecell * W * math.exp(-rho * W)

def evaluate(name, subj, enc, th, kh, idx, setm, src, c1, c2, data, W, M):
    T = bytes.fromhex(th); K = bytes.fromhex(kh)
    sets = [cube(t, k) for t, k in zip(T, K)]
    rho = 2.0 ** -markov1(c2, sets)
    idx = pick(c1, sets, idx)
    scan = sets[idx]
    sig_streams = [rate(c1, [m]) for m in scan]          # one memchr stream per member
    Ec = E[name]
    out = {}
    out['none'] = 0.0
    out['run'] = gate_cost(rho, sig_streams, W, M) - reject_saving(rho, W, Ec)
    if setm:
        pb = min(setm, key=lambda b: (rate(c1, [b]), -b))
        p = rate(c1, [pb])
        rho_b = p
        out['byte'] = gate_cost(rho_b, [p], W, M) - reject_saving(rho_b, W, Ec)
        # byte-then-run: the byte's memchr first; the run block only on the
        # subjects that hold the byte (prob 1-e^{-pW}); rejection = either absent
        pr_b = 1 - math.exp(-rho_b * W)
        both = 1 - (1 - math.exp(-rho_b * W)) * (1 - math.exp(-rho * W))
        out['byte+run'] = (gate_cost(rho_b, [p], W, M) + pr_b * gate_cost(rho, sig_streams, W, M)
                           - Ec * W * both)
    return rho, sig_streams, out

# Linux measured deltas, ns/B at 64 KiB (r1read_report.md §3: NEW - BASE)
MEASURED = {'mod-i': +.65, 'cls-fold-pair': +.37, 'cls-pair-ctl': +.37, 'ci-strasse': +.09,
            'alt-shared(C fixed)': None, 'userpass': +.93, 'union-select': -.50,
            'ci-ascii-ctl': -.50, 'slack': -.003, 'http-5xx': -.001, 'stack-frame': None}

def window(W_lo_hi_f):
    """the (W_lo, W_hi) interval of subject lengths on which a guard pays,
    found by scanning W over powers of 2^(1/4) from 1 B to 2^30 B"""
    ws = [2 ** (q / 4) for q in range(0, 121)]
    pays = [w for w in ws if W_lo_hi_f(w) < 0]
    if not pays: return None
    return (pays[0], pays[-1])

def fmtw(iv):
    if iv is None: return 'never'
    lo, hi = iv
    f = lambda w: ('%dB' % w) if w < 1024 else ('%dK' % (w / 1024)) if w < 1 << 20 else ('%dM' % (w / (1 << 20))) if w < 1 << 30 else 'inf'
    return '%s..%s' % (f(lo), f(hi))

def main():
    d1, _ = bundle(os.path.join(TREE, 'src/findings/default.rxt'))
    srcs = {b: bundle(os.path.join(TREE, 'src/findings/%s.rxt' % b)) for b in ('weblog', 'log')}
    print('# costs: %s %s' % (COSTS, CST))
    print('# per source: run bits (markov1), picked scan idx, stream rates; the W window on which')
    print('# the RUN guard pays (M=0); delta ns/B at W=64K for M=0 and M=occ (all guards); argmin')
    for (name, subj, enc, th, kh, idx, setm) in CELLS:
        data = open(os.path.join(SUBJ, subj + '.bin'), 'rb').read()
        T = bytes.fromhex(th); K = bytes.fromhex(kh)
        sets = [cube(t, k) for t, k in zip(T, K)]
        occ = occurrences(data, sets); n = len(data)
        print('\n== %s (%s, -e %s, %s/%s, set %s) n=%d; on the subject: %d run occurrences (%.1f bits)%s'
              % (name, subj, enc, th, kh, ','.join(map(str, setm)) or '-', n, occ,
                 -math.log2(max(occ, .5) / n),
                 '' if MEASURED[name] is None else '; Linux measured delta %+.3f ns/B' % MEASURED[name]))
        rows = [('none', None if enc == 'utf8' else d1, None),
                ('weblog',) + srcs['weblog'], ('log',) + srcs['log'],
                ('subj',) + from_bytes(data)]
        for src, c1, c2 in rows:
            rho = 2.0 ** -markov1(c2, sets); pi = pick(c1, sets, idx)
            ss = [rate(c1, [m]) for m in sets[pi]]
            iv = window(lambda w: evaluate(name, subj, enc, th, kh, idx, setm, src, c1, c2, data, w, 0)[2]['run'])
            _, _, o0 = evaluate(name, subj, enc, th, kh, idx, setm, src, c1, c2, data, n, 0)
            _, _, o1 = evaluate(name, subj, enc, th, kh, idx, setm, src, c1, c2, data, n, occ)
            b0 = min(o0, key=lambda g: (o0[g], g != 'none')); b1 = min(o1, key=lambda g: (o1[g], g != 'none'))
            print('  %-6s %5.1f bits @%d %-13s run pays W %-11s | M=0: %s -> %-8s | M=occ: %s -> %s' % (
                src, -math.log2(rho), pi, '+'.join('%.4f' % x for x in ss), fmtw(iv),
                ' '.join('%s%+.3f' % (g, v / n) for g, v in o0.items() if g != 'none'), b0,
                ' '.join('%s%+.3f' % (g, v / n) for g, v in o1.items() if g != 'none'), b1))

main()
