#!/usr/bin/env python3
"""SIM critic: span_pick rev 5's priced action implemented from the design TEXT only
(§The pick 1-7, the price formula, the band, "With data"), before reading smp20.py.
Pattern smp20 (?i)x/1234: positions @0 {X,x} @1 {/} @2 {1} @3 {2} @4 {3} @5 {4}.
Stand-ins per the design §Robustness: byte(memchr)=0.06, byte(PAIR)=k*0.06, hit 20, cmp 2.5
(cmp0 = cmp1/2 = 2.5), enter 20. Exact rationals; final price rounded half away from zero."""
import sys
from fractions import Fraction as F

POS = [(0, (0x58, 0x78)), (1, (0x2f,)), (2, (0x31,)), (3, (0x32,)), (4, (0x33,)), (5, (0x34,))]

def load(path):
    r, s = {}, 0
    for ln in open(path):
        ln = ln.rstrip('\n')
        if ln == '#section freq': s = 1; continue
        if ln.startswith('#section'): s = 0; continue
        if s and not ln.startswith('#'):
            k, c, p = ln.split('\t'); r[int(k, 16)] = int(p)
    return r

def mass(r, S): return sum(r.get(b, 0) for b in S)

def rnd(x):
    x = F(x); n = abs(x); i = int(n); i += 1 if n - i >= F(1, 2) else 0
    return i if x >= 0 else -i

def price(r, cand, k, h1, hP, cmp=F(5, 2), enter=20, bm=F(6, 100), exact=False):
    """stream method price per 1e6 bytes. cand = position index."""
    p, S = POS[cand]
    meth = 'PAIR' if len(S) == 2 else 'memchr'
    byte = bm * k if meth == 'PAIR' else bm
    hit = hP if meth == 'PAIR' else h1
    m = mass(r, S)
    others = sorted([q for q in POS if q[0] != p], key=lambda q: (mass(r, q[1]), q[0]))
    ver, pr = F(0), F(1)
    for _, Sj in others:
        pj = F(mass(r, Sj), 10**6)
        ver += cmp * pr          # cmp0 == cmp1/2 -> cmp(f,p) constant
        pr *= pj
    passes = m * pr
    v = byte * 10**6 + m * (hit + ver) + passes * enter
    return v if exact else rnd(v)

def least(r, cands, **kw):
    ps = {c: price(r, c, **kw) for c in cands}
    return min(ps, key=lambda c: (ps[c], c)), ps

def pick(r, inc, cands, band=0, **kw):
    """§The pick 3: qualifiers beat the incumbent by more than band; cheapest qualifier, else incumbent.
    Ties among qualifiers within band of the cheapest -> TIE (here: lowest position, a stand-in)."""
    ps = {c: price(r, c, **kw) for c in cands}
    if inc not in ps: return None, ps
    q = [c for c in cands if ps[inc] - ps[c] > band]
    if not q: return inc, ps
    return min(q, key=lambda c: (ps[c], c)), ps

NAME = {0: '{X,x}', 1: "'/'", 2: "'1'", 3: "'2'", 4: "'3'", 5: "'4'"}

if __name__ == '__main__':
    B = sys.argv[1]
    R = {n: load(f'{B}/{n}.list') for n in ('default', 'prose', 'log', 'weblog')}
    ALL = [0, 1, 2, 3, 4, 5]
    print('== table, k=2 h1=20, hP 20 (40)')
    for n, r in R.items():
        a = {c: price(r, c, k=2, h1=20, hP=20) for c in ALL}
        b0 = price(r, 0, k=2, h1=20, hP=40)
        print(n, {NAME[c]: a[c] for c in ALL}, 'PAIR@hP40', b0,
              'least', NAME[min(a, key=a.get)])
    # exact k* (default arm, blind = P): {X,x} vs '/'
    print('== k* blind P, {X,x} vs cheapest one-member')
    P = R['default']
    for mult in (1, 2, 4, 8):
        row = []
        for h1 in (5, 10, 20, 40):
            one = min(range(1, 6), key=lambda c: price(P, c, k=1, h1=h1, hP=h1, exact=True))
            p1 = price(P, one, k=1, h1=h1, hP=h1, exact=True)
            p0k0 = price(P, 0, k=0, h1=h1, hP=mult * h1, exact=True)
            ks = (p1 - p0k0) / (F(6, 100) * 10**6)
            row.append((NAME[one], float(ks)))
        print(f'{mult}x', [f'{a} {b:.4f}' for a, b in row])
    print('== at k=2, hP boundary per h1')
    for h1 in (5, 10, 20, 40):
        p1 = price(P, 1, k=1, h1=h1, hP=h1, exact=True)
        p0h0 = price(P, 0, k=2, h1=h1, hP=0, exact=True)
        m0 = mass(P, POS[0][1])
        print(h1, float((p1 - p0h0) / m0))
    print('== with-data grid, k 1.00..12.00 by 0.05 x h1 x mult (argmin and band-0 pick)')
    INC = {'default': 0, 'prose': 5, 'log': 0, 'weblog': 0}
    for n, r in R.items():
        cnt, cntp, npts = {}, {}, 0
        for h1 in (5, 10, 20, 40):
            for mult in (1, 2, 4, 8):
                for i in range(221):
                    k = F(100 + 5 * i, 100)
                    l, _ = least(r, ALL, k=k, h1=h1, hP=mult * h1)
                    pk, _ = pick(r, INC[n], ALL, k=k, h1=h1, hP=mult * h1)
                    cnt[NAME[l]] = cnt.get(NAME[l], 0) + 1
                    cntp[NAME[pk]] = cntp.get(NAME[pk], 0) + 1
                    npts += 1
        print(n, npts, 'least', cnt, 'pick(band0)', cntp)
