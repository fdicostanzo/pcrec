#!/usr/bin/env python3
"""costmodel: the search-form cost model by REGIME (lane costmodel, 2026-10-13).

ANALYSIS ONLY: no clock is read here, nothing is built.  Every ns figure is
read from logs measured by earlier slots (see cmload.py); every count from a
no-clock counting pass.  Output: one text report on stdout, cut into the
lane report (`docs/dev/lanes/costmodel_report.md`).

    python3 -I costmodel.py [DATADIR] [SLOT2_TIMES_TSV] > analysis.txt
    python3 -I costmodel.py --price kind=PF terms=1 n=1048576 lam=0.15 p=0.85 \
            alpha=0.15 fresh=1 layer=on iterator=0      # price one site

DATADIR defaults to ./data next to this file; SLOT2 to the branch copy
docs/design/memfn/probes/r17/out/slot2/times.tsv (lane/memfn-r17).
"""
import os, sys, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from cmload import *

_POS = [a for a in sys.argv[1:] if not a.startswith('--') and '=' not in a]
DATA = _POS[0] if len(_POS) > 0 else os.path.join(HERE, 'data')
SLOT2 = _POS[1] if len(_POS) > 1 else os.path.join(
    HERE, '..', '..', '..', 'design', 'memfn', 'probes', 'r17', 'out', 'slot2', 'times.tsv')

ALPHA = load_alpha(os.path.join(DATA, 'alpha_time.log'))
SPK = groups(load_spike(os.path.join(DATA, 'spike_time.log')))
SPK2 = groups(load_spike(os.path.join(DATA, 'spike2_time.log')))
C9 = load_cnt9(os.path.join(DATA, 'counts9.txt'))
CV = load_cv(os.path.join(DATA, 'spike_counts.tsv'))
CV2 = load_cv2(os.path.join(DATA, 'spike2_counts2.tsv'))
SUBJ = load_subj(os.path.join(HERE, 'subjstats.tsv'))
S2 = load_slot2(SLOT2)

MIB = 1048576.0
FR = 0.023          # the spike reading's strict floor (p90 of the A/A distribution)


def out(*a):
    print(*a)


def hdr(t):
    out()
    out('=' * 78)
    out(t)
    out('=' * 78)


# ---------------------------------------------------------------------------
# 0. The walk's own cost decomposition: what dominates a pass.
#    V0 = F*calls + u*uses + b_skip*skip + b_cons*(bytes the consumer eats)
#    fitted per site kind over every reached spike group (noise-weighted).
# ---------------------------------------------------------------------------

def facts(c, s, m):
    k = C9[(c, s, m)]
    U, K, C = k['uses'], k['skip'], k['calls']
    n = k['n']
    cold = k['cold']
    scanned = n if m == 'all' else None
    d = dict(U=U, K=K, C=C, n=n, cold=cold, matches=k['matches'],
             cached=k['cached'], masks=k['masks'])
    d['Lact'] = (K + U) / cold if cold else 0.0     # bytes the find advances per activation
    d['g'] = (K + U) / U if U else float('inf')     # bytes advanced per use
    d['lam'] = U / n                                # uses (landings) per subject byte
    return d


# Regime boundaries.  They are DERIVED below from the walk's fitted terms
# (g*: per-use term == per-byte term; L*: one W=64 block) and then fixed here
# so every table uses the same split.  `regime_bounds()` prints the
# derivation and the sensitivity.
G_STAR = 18.0
L_STAR = 64.0


def regime(f):
    if f['U'] == 0:
        return 'UNREACHED'
    if f['Lact'] < L_STAR:
        return 'DINGHY'
    if f['g'] < G_STAR:
        return 'TUG'
    return 'LINER'


REGIMES = ['DINGHY', 'TUG', 'LINER', 'UNREACHED']


def walk_fit():
    X, Y, Wt, lab = [], [], [], []
    for (c, s, m), g in SPK.items():
        f = facts(c, s, m)
        if f['U'] == 0:
            continue
        v0 = g['V0b']['v0']
        fl = g['V0b']['floor']
        span = f['n'] if m == 'all' else (f['K'] + f['U'])
        cons = max(0, span - f['K'])
        X.append([f['C'], f['U'], f['K'], cons])
        Y.append(v0)
        Wt.append(1 / max(fl, 0.01 * v0, 0.2))
        lab.append((c, s, m))
    X = np.array(X, float); Y = np.array(Y); Wt = np.array(Wt)
    res = {}
    for kind in ('PF', 'HAT', 'VM'):
        idx = [i for i, l in enumerate(lab) if KIND[l[0]] == kind]
        co, *_ = np.linalg.lstsq(X[idx] * Wt[idx, None], Y[idx] * Wt[idx], rcond=None)
        pred = X[idx] @ co
        rel = np.abs((Y[idx] - pred) / Y[idx])
        res[kind] = (co, float(np.median(rel)), len(idx))
    return res


def regime_bounds(WF):
    hdr('0.1 The walk decomposed: what a pass is made of (noise-weighted fit, spike V0)')
    out('V0 = F*calls + u*uses + b_skip*skip + b_cons*consumed   [ns]')
    out('kind  n   F/call  u/use  b_skip/B  b_cons/B  median|rel resid|')
    for kind, (co, med, nrow) in WF.items():
        out('%-4s %3d %7.2f %6.2f %9.3f %9.3f   %.2f' % (kind, nrow, co[0], co[1], co[2], co[3], med))
    co = WF['PF'][0]
    out()
    out('Derived boundaries (PF walk): per-use term == per-byte term at g* = u/b_skip = %.1f B;'
        % (co[1] / co[2]))
    out('per-call term == per-byte term at L = F/b_skip = %.1f B.  The fixed L* is the block width'
        % (co[0] / co[2]))
    out('W = 64 (an activation shorter than one W=64 block cannot amortize one block),')
    out('which also bounds the forms\' own cold-use break-even (c_cold / delta-beta, section A).')
    out('Fixed: G_STAR = %.0f B, L_STAR = %.0f B.' % (G_STAR, L_STAR))


# ---------------------------------------------------------------------------
# 0.2-0.4 Placement and absolute re-score
# ---------------------------------------------------------------------------

def cls(delta, floor, ref, strict):
    thr = max(floor, FR * ref) if strict else floor
    if abs(delta) <= thr:
        return 'N'
    return 'W' if delta < 0 else 'R'


def placement():
    hdr('0.2 Every spike group placed (facts from the counting pass; V0 = the walk, ns/pass)')
    out('%-9s %-9s %-5s %7s %7s %8s %7s %7s %-9s %11s %9s' % (
        'cell', 'subject', 'mode', 'calls', 'uses', 'Lact', 'g', 'lam/KB',
        'regime', 'V0 ns/pass', 'V0/call'))
    per = collections.defaultdict(list)
    for (c, s, m), g in SPK.items():
        f = facts(c, s, m)
        rg = regime(f)
        v0 = g['V0b']['v0']
        per[rg].append((v0, v0 / f['C'], f))
        out('%-9s %-9s %-5s %7d %7d %8.1f %7.1f %7.1f %-9s %11.1f %9.1f' % (
            c, s, m, f['C'], f['U'], f['Lact'], min(f['g'], 9999), 1024 * f['lam'], rg, v0, v0 / f['C']))
    hdr('0.3 The regimes: spans of absolute cost (walk, ns) and the facts that place them')
    out('%-9s %5s %22s %22s %18s %18s' % ('regime', 'rows', 'V0 ns/pass (min..max)',
                                           'V0 ns/call (min..max)', 'g B/use (min..max)',
                                           'Lact B (min..max)'))
    for rg in REGIMES:
        L = per.get(rg, [])
        if not L:
            continue
        a = [x[0] for x in L]; b = [x[1] for x in L]
        gg = [x[2]['g'] for x in L if x[2]['U']]
        la = [x[2]['Lact'] for x in L if x[2]['U']]
        out('%-9s %5d %10.1f..%-11.1f %10.1f..%-11.1f %8s %18s' % (
            rg, len(L), min(a), max(a), min(b), max(b),
            ('%.1f..%.0f' % (min(gg), max(gg))) if gg else '-',
            ('%.0f..%.0f' % (min(la), max(la))) if la else '-'))


def regime_card(WF):
    hdr('0.3b What dominates each regime: the walk\'s own pass, decomposed with 0.1\'s fit')
    out('Shares of the fitted walk time (PF/HAT/VM fits per row\'s kind), summed over the')
    out('regime\'s rows; then the walk\'s median ns per call and per MiB (all-mode rows).')
    out('%-8s %5s %9s %9s %9s %9s | %12s %12s %12s' % ('regime', 'rows', 'per-call', 'per-use', 'skip B', 'consumed',
                                                      'med ns/call', 'med ns/MiB', 'med MiB/s'))
    for rg in ['DINGHY', 'TUG', 'LINER']:
        acc = collections.Counter(); pc = []; pm = []; nrow = 0
        for (c, s, m), g in SPK.items():
            f = facts(c, s, m)
            if regime(f) != rg:
                continue
            nrow += 1
            co = WF[KIND[c]][0]
            span = f['n'] if m == 'all' else (f['K'] + f['U'])
            cons = max(0, span - f['K'])
            terms = [co[0] * f['C'], co[1] * f['U'], co[2] * f['K'], co[3] * cons]
            for k, t in zip(('call', 'use', 'skip', 'cons'), terms):
                acc[k] += max(t, 0.0)
            v0 = g['V0b']['v0']
            pc.append(v0 / f['C'])
            if m == 'all':
                pm.append(v0 * MIB / f['n'])
        tot = sum(acc.values())
        out('%-8s %5d %8.0f%% %8.0f%% %8.0f%% %8.0f%% | %12.1f %12.0f %12.0f' % (
            rg, nrow, 100 * acc['call'] / tot, 100 * acc['use'] / tot, 100 * acc['skip'] / tot,
            100 * acc['cons'] / tot, np.median(pc), np.median(pm), 1e9 / np.median(pm) if pm else float('nan')))
    out('(negative fitted terms are clipped at 0 for the shares; MiB/s = 1e9 / (ns/MiB))')


def rescore_alpha():
    hdr('0.4 ALPHA (slot25c, R17-b new vs deny) re-scored per regime, ABSOLUTE')
    out('One row per (cell, subject, mode), OFF layer (ON times the identical artifact: a replicate).')
    out('W/R/N = the log\'s verdict.  Sums are of new-deny over the rows of that verdict.')
    out('per MiB = delta * 2^20 / n (all mode: the subject is the work); per call = delta / calls.')
    out()
    rows = [r for r in ALPHA if r['layer'] == 'off']
    tally = collections.defaultdict(lambda: collections.Counter())
    sums = collections.defaultdict(lambda: collections.defaultdict(float))
    lst = collections.defaultdict(list)
    for r in rows:
        f = facts(r['cell'], r['subj'], r['mode'])
        rg = regime(f)
        v = {'WIN': 'W', 'REGRESSION': 'R', 'NULL': 'N'}[r['verdict']]
        tally[rg][v] += 1
        sums[rg][v] += r['delta']
        sums[rg][v + 'mib'] += r['delta'] * MIB / f['n'] if r['mode'] == 'all' else 0.0
        sums[rg][v + 'call'] += r['delta'] / f['C']
        sums[rg]['deny'] += r['deny']
        lst[rg].append((r, f, v))
    out('%-9s %4s %9s | %14s %14s %14s | %14s %14s | %12s' % (
        'regime', 'rows', 'W/R/N', 'sum win ns', 'sum loss ns', 'net ns',
        'win ns/MiB*', 'loss ns/MiB*', 'net % walk'))
    tot = collections.Counter()
    for rg in REGIMES:
        t = tally[rg]
        if not t:
            continue
        s = sums[rg]
        net = s['W'] + s['R'] + s['N']
        out('%-9s %4d %3d/%2d/%2d | %14.1f %14.1f %14.1f | %14.1f %14.1f | %11.2f%%' % (
            rg, sum(t.values()), t['W'], t['R'], t['N'], s['W'], s['R'], net,
            s['Wmib'], s['Rmib'], 100 * net / s['deny']))
        for k in 'WRN':
            tot[k] += t[k]
    out('%-9s %4d %3d/%2d/%2d' % ('ALL', sum(tot.values()), tot['W'], tot['R'], tot['N']))
    out('* all-mode rows only.')
    out()
    out('Both layers (all 160 rows), the headline tally next to its absolute weight:')
    agg = collections.defaultdict(lambda: [0, 0.0])
    for r in ALPHA:
        v = {'WIN': 'W', 'REGRESSION': 'R', 'NULL': 'N'}[r['verdict']]
        agg[v][0] += 1
        agg[v][1] += r['delta']
    for v in 'WRN':
        out('  %s: %3d rows, sum new-deny %+12.1f ns' % (v, agg[v][0], agg[v][1]))
    out()
    out('Per-row detail (OFF layer), by regime:')
    out('%-9s %-9s %-9s %-5s %11s %11s %8s %10s %9s %s' % (
        'regime', 'cell', 'subject', 'mode', 'deny ns', 'new-deny', 'rel', 'per call', 'per MiB', 'verdict'))
    for rg in REGIMES:
        for r, f, v in sorted(lst[rg], key=lambda t: t[0]['delta']):
            permib = r['delta'] * MIB / f['n'] if r['mode'] == 'all' else float('nan')
            out('%-9s %-9s %-9s %-5s %11.1f %+11.1f %+7.1f%% %+10.2f %+9.0f %s' % (
                rg, r['cell'], r['subj'], r['mode'], r['deny'], r['delta'],
                100 * r['delta'] / r['deny'], r['delta'] / f['C'], permib, v))
    return lst


VARS = ['V1', 'V2', 'V3', 'V4', 'S1', 'S2', 'S3', 'S4', 'A1', 'A2', 'A3', 'A4']


def rescore_spike():
    hdr('0.5 SPIKE variants vs the walk, re-scored per regime (strict floor), ABSOLUTE')
    out('Tally W/R/N (strict floor: |d| <= max(A/A, 2.3% of the walk) is NULL).  Sums over the')
    out('rows of the regime: net ns per pass, and net ns per MiB of subject (all-mode rows).')
    out('Six unstable 64K find-all groups (reading §1.3) are kept; their A/A is their floor.')
    for mode in ('all', 'first'):
        out()
        out('mode = %s' % mode)
        out('%-4s ' % 'var' + ' '.join('%-36s' % rg for rg in ['DINGHY', 'TUG', 'LINER']))
        out('     ' + ' '.join('%-36s' % 'W/R/N   net ns/pass   net ns/MiB' for _ in range(3)))
        for v in VARS:
            cells = []
            for rg in ['DINGHY', 'TUG', 'LINER']:
                t = collections.Counter(); net = 0.0; nm = 0.0
                for (c, s, m), g in SPK.items():
                    if m != mode or v not in g:
                        continue
                    f = facts(c, s, m)
                    if regime(f) != rg:
                        continue
                    d = g[v]['delta']
                    t[cls(d, g['V0b']['floor'], g[v]['v0'], True)] += 1
                    net += d
                    nm += d * MIB / f['n'] if m == 'all' else 0.0
                cells.append('%2d/%2d/%2d %+13.0f %12s' % (t['W'], t['R'], t['N'], net,
                                                          ('%+12.0f' % nm) if mode == 'all' else '-'))
            out('%-4s ' % v + ' '.join('%-36s' % x for x in cells))


def rescore_spike2():
    hdr('0.6 SPIKE2 (dfa-hat multi-position filter) vs the walk, per regime, ABSOLUTE')
    agg = collections.defaultdict(lambda: [0.0, 0.0, collections.Counter()])
    for (c, s, m), g in SPK2.items():
        f = facts(c, s, m)
        rg = regime(f)
        for v in ['V1', 'S1', 'A1', 'P2w', 'P3w', 'P4w', 'PWw', 'P2s', 'P3s', 'P4s', 'PWs', 'P2a', 'P3a', 'P4a', 'PWa']:
            if v not in g:
                continue
            d = g[v]['delta']
            a = agg[(v, rg)]
            a[0] += d
            a[1] += d * MIB / f['n'] if m == 'all' else 0.0
            a[2][cls(d, g['V0b']['floor'], g[v]['v0'], True)] += 1
    out('%-5s ' % 'var' + ' '.join('%-34s' % rg for rg in ['DINGHY', 'TUG', 'LINER']))
    for v in ['V1', 'P2w', 'P3w', 'P4w', 'PWw', 'S1', 'P2s', 'P3s', 'P4s', 'PWs', 'A1', 'P2a', 'P3a', 'P4a', 'PWa']:
        cells = []
        for rg in ['DINGHY', 'TUG', 'LINER']:
            a = agg.get((v, rg))
            if not a:
                cells.append('-')
                continue
            t = a[2]
            cells.append('%2d/%2d/%2d %+12.0f %+12.0f' % (t['W'], t['R'], t['N'], a[0], a[1]))
        out('%-5s ' % v + ' '.join('%-34s' % x for x in cells))
    out('(cells: W/R/N vs the walk, net ns/pass summed, net ns/MiB summed over all-mode rows)')



def medians_spike():
    hdr('0.7 SPIKE variants vs the walk: per-row MEDIANS per regime (both modes)')
    out('rel = delta / walk; per call = delta / calls; per MiB = delta * 2^20 / n (all-mode rows).')
    out('%-4s ' % 'var' + ' '.join('%-30s' % rg for rg in ['DINGHY', 'TUG', 'LINER']))
    out('     ' + ' '.join('%-30s' % 'rel%   ns/call   ns/MiB' for _ in range(3)))
    for v in VARS:
        cells = []
        for rg in ['DINGHY', 'TUG', 'LINER']:
            rel, pc, pm = [], [], []
            for (c, s, m), g in SPK.items():
                if v not in g:
                    continue
                f = facts(c, s, m)
                if regime(f) != rg:
                    continue
                d = g[v]['delta']
                rel.append(100 * d / g[v]['v0'])
                pc.append(d / f['C'])
                if m == 'all':
                    pm.append(d * MIB / f['n'])
            cells.append('%+6.1f %+9.2f %+11.0f' % (np.median(rel), np.median(pc), np.median(pm) if pm else float('nan')))
        out('%-4s ' % v + ' '.join('%-30s' % x for x in cells))


# ---------------------------------------------------------------------------
# A. THE DRIVERS: a mechanical model per form, constants measured where the
#    data isolate them, the per-use terms fitted.
#
#    delta_f = c_cold*cold_f + c_warm*(U - cold_f)        per-use terms (fitted)
#            + beta_f(terms)*blocks_f*W_f                 the form's block scans (MEASURED rate)
#            - beta_t*(K + U)                             the walk's byte tests (MEASURED rate)
#            + m*U*fresh                                  1 MiB subjects: the walk's
#                                                         unlearned branch (fitted)
#            [+ h*head_bytes]                             prologue variants only (fitted)
#    beta_f*blocks_f*W_f - beta_t*(K+U) splits into the per-byte saving
#    (beta_f - beta_t)*(K+U) and the WASTED SCAN beta_f*(blocks_f*W_f - (K+U)).
# ---------------------------------------------------------------------------

WIDTH = {'V': 8, 'S': 64, 'A': 64}


def measured_rates():
    """beta per byte, MEASURED on the sparse spike rows (one use, whole subject)."""
    def rate(c, s, v):
        g = SPK[(c, s, 'all')]
        return (g[v]['v0'] + g[v]['delta'] if v != 'V0' else g['V0b']['v0']) / NBYTES[s]
    bt = np.mean([rate('dig', 'prose64k', 'V0'), rate('dig', 'prose1m', 'V0'),
                  rate('dfa-hat', 'digits64k', 'V0'), rate('dfa-hat', 'mix64k', 'V0')])
    beta = {}
    for v in VARS:
        b1 = np.mean([rate('dig', 'prose64k', v), rate('dig', 'prose1m', v)])
        b2 = np.mean([rate('dfa-hat', 'digits64k', v), rate('dfa-hat', 'mix64k', v)])
        beta[(v, 1)] = (b1, 'MEASURED')
        beta[(v, 2)] = (b2, 'MEASURED')
        beta[(v, 3)] = (b2 + (b2 - b1), 'DERIVED (linear in terms)')
    return bt, beta


BT, BETA = measured_rates()


def spike_rows(v, kinds=('PF', 'HAT', 'VM')):
    out_ = []
    for (c, s, m), g in SPK.items():
        if v not in g or KIND[c] not in kinds:
            continue
        f = facts(c, s, m)
        if f['U'] == 0:
            continue
        cv = CV[(c, v, s, m)]
        r = dict(c=c, s=s, m=m, f=f, U=f['U'], K=f['K'], C=f['C'], cold=cv['cold'],
                 blocks=cv['blocks'], headb=cv['head_bytes'], xcall=cv['xcall'],
                 hit=cv['cache_hit'], d=g[v]['delta'], v0=g[v]['v0'],
                 fl=g['V0b']['floor'], fresh=1 if NBYTES[s] >= MIB else 0,
                 terms=TERMS[c], rg=regime(f), real=s in REALTEXT)
        b = BETA[(v, r['terms'])][0]
        r['scan_form'] = b * r['blocks'] * WIDTH[v[0]]
        r['scan_walk'] = BT * (r['K'] + r['U'])
        r['waste'] = b * (r['blocks'] * WIDTH[v[0]] - (r['K'] + r['U']))
        r['save'] = (b - BT) * (r['K'] + r['U'])
        out_.append(r)
    return out_


def sigma(r):
    return max(r['fl'], 0.01 * r['v0'], 0.3)


def feats_of(v):
    fs = ['cold', 'warm', 'Ufresh']
    if v[1] in '24':
        fs.append('headb')
    return fs


def featval(r, f):
    return {'cold': r['cold'], 'warm': r['U'] - r['cold'], 'Ufresh': r['U'] * r['fresh'],
            'headb': r['headb']}[f]


def fit_variant(v, rs):
    fs = feats_of(v)
    X = np.array([[featval(r, f) for f in fs] for r in rs], float)
    Y = np.array([r['d'] - r['scan_form'] + r['scan_walk'] for r in rs])
    Wt = np.array([1 / sigma(r) for r in rs])
    co, *_ = np.linalg.lstsq(X * Wt[:, None], Y * Wt, rcond=None)
    return fs, co


def predict(v, fs, co, r):
    return sum(c * featval(r, f) for f, c in zip(fs, co)) + r['scan_form'] - r['scan_walk']


def strict_cls(r, d=None):
    d = r['d'] if d is None else d
    thr = max(r['fl'], FR * r['v0'])
    return 'N' if abs(d) <= thr else ('W' if d < 0 else 'R')


def quality(rs, preds):
    D = np.array([r['d'] for r in rs]); P = np.array(preds)
    Wt = np.array([1 / sigma(r) for r in rs])
    res = D - P
    if len(rs) > 1:
        mu = np.average(D, weights=Wt ** 2)
        wr2 = 1 - np.sum((res * Wt) ** 2) / max(np.sum(((D - mu) * Wt) ** 2), 1e-9)
    else:
        wr2 = float('nan')
    ae = 1 - np.sum(np.abs(res)) / max(np.sum(np.abs(D)), 1e-9)
    nonnull = [(r, p) for r, p in zip(rs, preds) if strict_cls(r) != 'N']
    serr = sum(1 for r, p in nonnull if np.sign(p) != np.sign(r['d']))
    return wr2, ae, serr, len(nonnull), float(np.median(np.abs(res) / np.array([r['v0'] for r in rs])))


FITS = {}


def drivers():
    hdr('A.1 Constants measured where the data isolate them (Zen 4 7700X, CPU 14, gcc 15.2 -O2)')
    out('beta_t (the 256-byte table walk, per byte tested)      = %.4f ns/B  MEASURED' % BT)
    out('   (dig prose64k/prose1m, dfa-hat digits64k/mix64k: one use, the whole subject)')
    out('beta_f per byte a form\'s blocks cover, by width and cover terms:')
    out('%-4s %-5s %10s %10s %10s   %s' % ('var', 'width', '1 term', '2 terms', '3 terms', 'label of the 3-term value'))
    for v in VARS:
        out('%-4s %-5d %10.4f %10.4f %10.4f   %s' % (v, WIDTH[v[0]], BETA[(v, 1)][0], BETA[(v, 2)][0],
                                                   BETA[(v, 3)][0], BETA[(v, 3)][1]))
    out('(no 3- or 4-term set is ever sparse in this table: word-eq\'s per-byte rate is DERIVED)')
    out()
    out('A.1b The wasted scan: bytes a form evaluates beyond what the walk tests,')
    out('     overscan = blocks*W - (K+U), regressed on (cold uses, warm uses):')
    for v in ['V1', 'S1', 'A1', 'V2', 'S2', 'A2']:
        rs = spike_rows(v)
        X = np.array([[r['cold'], r['U'] - r['cold']] for r in rs], float)
        Y = np.array([r['blocks'] * WIDTH[v[0]] - (r['K'] + r['U']) for r in rs], float)
        co, *_ = np.linalg.lstsq(X, Y, rcond=None)
        tot = sum(r['blocks'] * WIDTH[v[0]] for r in rs); adv = sum(r['K'] + r['U'] for r in rs)
        out('  %-3s overscan = %7.1f B per cold use + %5.2f B per warm use   (scanned/advanced %.2f)'
            % (v, co[0], co[1], tot / adv))
        FITS[('omega', v)] = co
    for v in ['V3', 'S3', 'A3', 'V4', 'S4', 'A4']:
        rs = spike_rows(v)
        tot = sum(r['blocks'] * WIDTH[v[0]] for r in rs); adv = sum(r['K'] + r['U'] for r in rs)
        FITS[('kappa', v)] = tot / adv
        out('  %-3s (kept: the state spans calls) scanned/advanced %.2f; no per-activation overscan' % (v, tot / adv))

    hdr('A.2 The per-use terms, fitted per form and site kind (noise-weighted; sigma = max(A/A, 1% of walk, 0.3 ns))')
    out('Residual target: delta - beta_f*blocks*W + beta_t*(K+U).')
    out('%-4s %-6s %4s %8s %8s %8s %8s | %6s %7s %9s %6s' % (
        'var', 'kind', 'rows', 'c_cold', 'c_warm', 'm_fresh', 'h_head', 'wR2', 'absExp', 'signErr', 'LOCO'))
    for v in VARS:
        for kg, kinds in (('PF/HAT', ('PF', 'HAT')), ('VM', ('VM',))):
            rs = spike_rows(v, kinds)
            if not rs:
                continue
            fs, co = fit_variant(v, rs)
            FITS[(v, kg)] = (fs, co)
            preds = [predict(v, fs, co, r) for r in rs]
            wr2, ae, se, nn, mr = quality(rs, preds)
            # leave-one-cell-out sign errors
            loco = 0
            for cell in {r['c'] for r in rs}:
                tr = [r for r in rs if r['c'] != cell]; te = [r for r in rs if r['c'] == cell]
                if len(tr) < len(fs) + 1:
                    continue
                fs2, co2 = fit_variant(v, tr)
                for r in te:
                    if strict_cls(r) != 'N' and np.sign(predict(v, fs2, co2, r)) != np.sign(r['d']):
                        loco += 1
            vals = dict(zip(fs, co))
            out('%-4s %-6s %4d %+8.2f %+8.2f %+8.2f %8s | %6.2f %7.2f %4d/%-4d %6d' % (
                v, kg, len(rs), vals['cold'], vals['warm'], vals['Ufresh'],
                ('%+.3f' % vals['headb']) if 'headb' in vals else '-', wr2, ae, se, nn, loco))
    out('absExp = 1 - sum|resid| / sum|delta| (ABSOLUTE ns explained); signErr over strict non-NULL rows;')
    out('LOCO = sign errors when each cell is predicted by a fit that never saw it.')

    hdr('A.3 Fit quality PER REGIME (the model of A.2, by kind group)')
    out('%-4s %-9s %4s %7s %7s %9s %14s %14s' % ('var', 'regime', 'rows', 'wR2', 'absExp', 'signErr', 'sum|delta| ns', 'sum|resid| ns'))
    for v in ['V1', 'S1', 'A1', 'V3', 'S3', 'A3', 'A2']:
        allr = []
        for kg, kinds in (('PF/HAT', ('PF', 'HAT')), ('VM', ('VM',))):
            fs, co = FITS[(v, kg)]
            for r in spike_rows(v, kinds):
                allr.append((r, predict(v, fs, co, r)))
        for rg in ['DINGHY', 'TUG', 'LINER']:
            sel = [(r, p) for r, p in allr if r['rg'] == rg]
            rs = [x[0] for x in sel]; ps = [x[1] for x in sel]
            wr2, ae, se, nn, mr = quality(rs, ps)
            out('%-4s %-9s %4d %7.2f %7.2f %4d/%-4d %14.0f %14.0f' % (
                v, rg, len(rs), wr2, ae, se, nn, sum(abs(r['d']) for r in rs),
                sum(abs(r['d'] - p) for r, p in zip(rs, ps))))

    hdr('A.4 The terms, summed per regime: what drives each regime\'s delta (model of A.2)')
    out('Columns are each term\'s contribution in ns per pass, summed over the regime\'s rows.')
    out('%-4s %-9s %12s %12s %12s %12s %12s %12s | %12s' % (
        'var', 'regime', 'cold uses', 'warm uses', 'per-byte', 'wasted scan', 'fresh(walk)', 'head', 'measured'))
    for v in ['V1', 'S1', 'A1', 'V3', 'S3', 'A3', 'V2', 'A2']:
        for rg in ['DINGHY', 'TUG', 'LINER']:
            acc = collections.Counter(); meas = 0.0
            for kg, kinds in (('PF/HAT', ('PF', 'HAT')), ('VM', ('VM',))):
                fs, co = FITS[(v, kg)]
                vals = dict(zip(fs, co))
                for r in spike_rows(v, kinds):
                    if r['rg'] != rg:
                        continue
                    acc['cold'] += vals['cold'] * r['cold']
                    acc['warm'] += vals['warm'] * (r['U'] - r['cold'])
                    acc['byte'] += r['save']
                    acc['waste'] += r['waste']
                    acc['fresh'] += vals['Ufresh'] * r['U'] * r['fresh']
                    acc['head'] += vals.get('headb', 0.0) * r['headb']
                    meas += r['d']
            out('%-4s %-9s %+12.0f %+12.0f %+12.0f %+12.0f %+12.0f %+12.0f | %+12.0f' % (
                v, rg, acc['cold'], acc['warm'], acc['byte'], acc['waste'], acc['fresh'], acc['head'], meas))

    hdr('A.5 Largest absolute residuals (V1, S1, A1), with the facts that place them')
    for v in ['V1', 'S1', 'A1']:
        allr = []
        for kg, kinds in (('PF/HAT', ('PF', 'HAT')), ('VM', ('VM',))):
            fs, co = FITS[(v, kg)]
            for r in spike_rows(v, kinds):
                allr.append((r, predict(v, fs, co, r)))
        allr.sort(key=lambda t: -abs(t[0]['d'] - t[1]))
        out('%s:' % v)
        for r, p in allr[:8]:
            sj = SUBJ[(r['c'], r['s'])]
            out('  %-8s %-9s %-5s %-6s delta %+10.0f pred %+10.0f  U=%d g=%.1f gcv=%.2f n=%d' % (
                r['c'], r['s'], r['m'], r['rg'], r['d'], p, r['U'], r['f']['g'], sj['gcv'], r['f']['n']))


def alpha_oos():
    hdr('A.6 Out of sample: the V1 model fitted on the spike, applied to ALPHA (slot25c, both layers)')
    out('Same artifact family (spike V1 = R17-b new), a different run (slot25c, load1 0.72).')
    conf = collections.defaultdict(collections.Counter)
    absres = collections.defaultdict(float); absd = collections.defaultdict(float)
    for r0 in ALPHA:
        f = facts(r0['cell'], r0['subj'], r0['mode'])
        if f['U'] == 0:
            continue
        rg = regime(f)
        kg = 'VM' if KIND[r0['cell']] == 'VM' else 'PF/HAT'
        fs, co = FITS[('V1', kg)]
        cv = CV[(r0['cell'], 'V1', r0['subj'], r0['mode'])]
        r = dict(cold=cv['cold'], U=f['U'], K=f['K'], headb=0, fresh=1 if f['n'] >= MIB else 0)
        b = BETA[('V1', TERMS[r0['cell']])][0]
        p = sum(c * featval(r, x) for x, c in zip(fs, co)) + b * cv['blocks'] * 8 - BT * (f['K'] + f['U'])
        v = {'WIN': 'W', 'REGRESSION': 'R', 'NULL': 'N'}[r0['verdict']]
        conf[rg][(v, 'W' if p < 0 else 'R')] += 1
        absres[rg] += abs(r0['delta'] - p); absd[rg] += abs(r0['delta'])
    out('%-7s %-12s %-12s %-12s %-12s %-12s %-12s %8s' % ('regime', 'W->predW', 'W->predR', 'R->predW', 'R->predR', 'N->predW', 'N->predR', 'absExp'))
    for rg in ['DINGHY', 'TUG', 'LINER']:
        c = conf[rg]
        out('%-7s %-12d %-12d %-12d %-12d %-12d %-12d %8.2f' % (rg, c[('W', 'W')], c[('W', 'R')], c[('R', 'W')],
                                                               c[('R', 'R')], c[('N', 'W')], c[('N', 'R')],
                                                               1 - absres[rg] / absd[rg]))


# ---------------------------------------------------------------------------
# B. THE DENSITY QUESTION
# ---------------------------------------------------------------------------

GBINS = [(0, 4), (4, 8), (8, 16), (16, 32), (32, 128), (128, 1e18)]
PBINS = [(0, 1), (1, 50000), (50000, 100000), (100000, 300000), (300000, 600000), (600000, 1000001)]


def density():
    hdr('B.1 Win/loss against GAP (bytes per use, g) and against BYTE DENSITY (p of S), all reached spike rows')
    for v in ['V1', 'S1', 'A1', 'A3']:
        out('%s:' % v)
        out('  %-12s %5s %9s %11s %12s   ||  %-14s %5s %9s %11s %12s' % (
            'g bin (B)', 'rows', 'W/R/N', 'med d/use', 'sum ns/MiB', 'p bin (ppm)', 'rows', 'W/R/N', 'med d/use', 'sum ns/MiB'))
        rs = spike_rows(v)
        lines_g, lines_p = [], []
        for lo, hi in GBINS:
            sel = [r for r in rs if lo <= r['f']['g'] < hi]
            t = collections.Counter(strict_cls(r) for r in sel)
            md = np.median([r['d'] / r['U'] for r in sel]) if sel else float('nan')
            pm = sum(r['d'] * MIB / r['f']['n'] for r in sel if r['m'] == 'all')
            lines_g.append('%-12s %5d %3d/%2d/%2d %+11.2f %+12.0f' % ('[%g,%s)' % (lo, ('%g' % hi) if hi < 1e17 else 'inf'), len(sel), t['W'], t['R'], t['N'], md, pm))
        for lo, hi in PBINS:
            sel = [r for r in rs if lo <= SUBJ[(r['c'], r['s'])]['ppm'] < hi]
            t = collections.Counter(strict_cls(r) for r in sel)
            md = np.median([r['d'] / r['U'] for r in sel]) if sel else float('nan')
            pm = sum(r['d'] * MIB / r['f']['n'] for r in sel if r['m'] == 'all')
            lines_p.append('%-14s %5d %3d/%2d/%2d %+11.2f %+12.0f' % ('[%d,%d)' % (lo, hi), len(sel), t['W'], t['R'], t['N'], md, pm))
        for a, b in zip(lines_g, lines_p):
            out('  ' + a + '   ||  ' + b)
    out('d/use = delta / uses (for one-use whole-subject rows it is the whole pass).')

    hdr('B.2 Crossovers implied by the model (A.2 coefficients, PF/HAT unless noted)')
    out('Per byte the find advances, a form saves (beta_t - beta_f) and pays, per use,')
    out('c_warm + beta_f*omega_warm (state carried) or c_cold + beta_f*omega_cold (state lost).')
    out('Break-even gap g* = per-use cost / per-byte saving; lam* = 1/g* (uses per byte).')
    out('%-4s %-7s %6s %10s %12s %12s %12s %12s' % ('var', 'kind', 'terms', 'save/B', 'g* carried', 'g* lost', 'land/KB*car', 'land/KB*lost'))
    for v in ['V1', 'S1', 'A1', 'V3', 'S3', 'A3']:
        for kg in ('PF/HAT', 'VM'):
            fs, co = FITS[(v, kg)]
            vals = dict(zip(fs, co))
            kept = v in KEPT
            om = FITS[('omega', v)] if not kept else None
            for terms in (1, 2, 3):
                b = BETA[(v, terms)][0]
                save = BT - (b * FITS[('kappa', v)] if kept else b)
                if save <= 0:
                    out('%-4s %-7s %6d %10.4f   never (the form scans slower than the walk)' % (v, kg, terms, save))
                    continue
                if kept:
                    # the kept state never goes cold within a pass: one figure
                    gc = vals['warm'] / save
                    gl = gc
                else:
                    gc = (vals['warm'] + b * om[1]) / save
                    gl = (vals['cold'] + b * om[0]) / save
                out('%-4s %-7s %6d %10.4f %12.1f %12.1f %12.1f %12.1f' % (
                    v, kg, terms, save, gc, gl, 1024 / gc if gc > 0 else float('inf'),
                    1024 / gl if gl > 0 else float('inf')))
    out('(a negative g* means the per-use term is itself a saving: the form wins at every gap;')
    out(' kept rows: save/B nets the kept overscan kappa, and "lost" equals "carried" by construction)')


def slot2_crossovers():
    hdr('B.3 The kernel-only sweep (slot2, 14 real cells, i.i.d. placement): form/table per ppm')
    out('Median over the 14 cells of ns_per_call(form)/ns_per_call(table); "x" marks the first')
    out('ppm where the median exceeds 1.016 (the slot\'s noise band).  calls = finds per pass.')
    real = 'adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc'.split()
    idx = collections.defaultdict(dict)
    for r in S2:
        if r['cell'] not in real or r['align'] != '0' or r['g'] != '0.0':
            continue
        key = (r['regime'], r['n'], r['span'], r['reset'])
        idx[key].setdefault((r['cell'], int(r['ppm'])), {})[r['form']] = float(r['ns_per_call_min'])
    forms = ['swar', 'mask8_swar', 'mask64_swar', 'mask64_sse2', 'mask64_avx2', 'sse2', 'avx2', 'adapt_swar']
    for key in sorted(idx):
        d = idx[key]
        ppms = sorted({p for (_, p) in d})
        out()
        out('%s n=%s span=%s reset=%s' % key)
        out('  %-12s ' % 'form' + ' '.join('%7d' % p for p in ppms))
        for f in forms:
            meds = []
            for p in ppms:
                rr = [d[(c, p)][f] / d[(c, p)]['table'] for c in real if (c, p) in d and f in d[(c, p)] and 'table' in d[(c, p)]]
                meds.append(np.median(rr) if rr else float('nan'))
            out('  %-12s ' % f + ' '.join(('%6.2f%s' % (m, 'x' if m > 1.016 else ' ')) if not math.isnan(m) else '      -' for m in meds))


def nondensity():
    hdr('B.4 Losses that are NOT gap-density: rows with g >= G_STAR (or single-call DINGHY) that lose')
    for v in ['V1', 'S1', 'A1']:
        out('%s:' % v)
        for r in spike_rows(v):
            if strict_cls(r) != 'R':
                continue
            if r['f']['g'] >= G_STAR or (r['rg'] == 'DINGHY' and r['C'] == 1):
                out('  %-8s %-9s %-5s %-6s n=%-7d g=%-8.1f Lact=%-8.1f delta %+9.2f ns (%+.0f%%)' % (
                    r['c'], r['s'], r['m'], r['rg'], r['f']['n'], min(r['f']['g'], 99999), r['f']['Lact'],
                    r['d'], 100 * r['d'] / r['v0']))


def contrived_vs_real():
    hdr('B.5 Contrived (slot25c) vs real-text (docs/code) subjects, per variant')
    out('%-4s %-24s %-24s' % ('var', 'contrived W/R/N  med rel', 'real-text W/R/N  med rel'))
    for v in ['V1', 'V3', 'S1', 'S3', 'A1', 'A3']:
        rs = spike_rows(v)
        cells = []
        for real in (False, True):
            sel = [r for r in rs if r['real'] == real]
            t = collections.Counter(strict_cls(r) for r in sel)
            cells.append('%2d/%2d/%2d  %+6.1f%%' % (t['W'], t['R'], t['N'], np.median([100 * r['d'] / r['v0'] for r in sel])))
        out('%-4s %-24s %-24s' % (v, cells[0], cells[1]))
    out()
    out('Placement of the real-text rows by regime (V1 rows):')
    c = collections.Counter((r['rg'], r['real']) for r in spike_rows('V1'))
    for rg in ['DINGHY', 'TUG', 'LINER']:
        out('  %-7s contrived %3d   real-text %3d' % (rg, c[(rg, False)], c[(rg, True)]))

# ---------------------------------------------------------------------------
# C. THE ESTIMATOR, in facts a site and a workload can state.
#
#   per pass, for form f at a site of kind k with `terms` cover terms:
#     delta_f = c_cold(f,k)*A + c_warm(f,k)*(U - A) + m(f,k)*U*fresh
#             + (beta_f - beta_t)*ADV + beta_f*OVER
#   ADV  = bytes the find advances (skip + hit bytes)           ~ phi * n_scan
#   U    = uses (landings the find stops at)                     ~ lam * n_scan
#   A    = activations that reach the site (calls; 1 per pass when the state
#          is kept across calls)                                  ~ alpha * n_scan
#   OVER = overscan = omega_cold*A + omega_warm*(U-A)   (unkept forms)
#          or (kappa - 1)*ADV                            (kept forms)
#   fresh = the subject is not re-scanned warm (1 MiB rows here).
#  Divided by n_scan: delta/byte = c_cold*alpha + c_warm*(lam-alpha) + m*lam*fresh
#                                 - (beta_t - beta_f)*phi + beta_f*over/byte
# ---------------------------------------------------------------------------

KEPT = {'V3', 'S3', 'A3', 'V4', 'S4', 'A4'}


def est_delta(v, kind, terms, U, ADV, A, fresh, headb=0.0):
    kg = 'VM' if kind == 'VM' else 'PF/HAT'
    fs, co = FITS[(v, kg)]
    vals = dict(zip(fs, co))
    b = BETA[(v, terms)][0]
    if v in KEPT:
        A_eff = 1.0 if A > 0 else 0.0
        over = (FITS[('kappa', v)] - 1.0) * ADV
    else:
        A_eff = A
        om = FITS[('omega', v)]
        over = om[0] * A + om[1] * max(U - A, 0)
    d = vals['cold'] * A_eff + vals['warm'] * max(U - A_eff, 0) + vals['Ufresh'] * U * fresh
    d += (b - BT) * ADV + b * max(over, 0.0)
    d += vals.get('headb', 0.0) * headb
    return d


def estimator_report():
    hdr('C.1 The estimator\'s constants (this box; labels as in A.1/A.2)')
    out('%-4s %-6s %8s %8s %8s %9s %9s %9s %9s' % ('var', 'kind', 'c_cold', 'c_warm', 'm_fresh',
                                                     'beta(1t)', 'beta(2t)', 'om_cold', 'om_warm'))
    for v in VARS:
        for kg in ('PF/HAT', 'VM'):
            fs, co = FITS[(v, kg)]
            vals = dict(zip(fs, co))
            if v in KEPT:
                om = ('kappa %.2f' % FITS[('kappa', v)], '')
            else:
                om = ('%.1f' % FITS[('omega', v)][0], '%.2f' % FITS[('omega', v)][1])
            out('%-4s %-6s %+8.2f %+8.2f %+8.2f %9.4f %9.4f %9s %9s' % (
                v, kg, vals['cold'], vals['warm'], vals['Ufresh'], BETA[(v, 1)][0], BETA[(v, 2)][0], om[0], om[1]))
    out('beta_t = %.4f.  c_*, m: FITTED (A.2); beta: MEASURED (1-2 terms) / DERIVED (3);' % BT)
    out('omega/kappa: MEASURED from the counters (A.1b).')

    hdr('C.2 Predicted vs measured sign, from the workload facts alone (U, ADV, A, fresh; no blocks counter)')
    out('Confusion per regime: measured class (strict floor) x predicted sign.')
    out('%-4s %-7s %10s %10s %10s %10s %10s %10s %8s' % ('var', 'regime', 'W->W', 'W->R', 'R->W', 'R->R', 'N->W', 'N->R', 'agree'))
    for v in ['V1', 'S1', 'A1', 'V3', 'S3', 'A3', 'A2']:
        for rg in ['DINGHY', 'TUG', 'LINER']:
            c = collections.Counter()
            for r in spike_rows(v):
                if r['rg'] != rg:
                    continue
                A = CV[(r['c'], v[0] + '1', r['s'], r['m'])]['cold']
                p = est_delta(v, KIND[r['c']], r['terms'], r['U'], r['K'] + r['U'], A, r['fresh'], r['headb'])
                c[(strict_cls(r), 'W' if p < 0 else 'R')] += 1
            nonnull = c[('W', 'W')] + c[('W', 'R')] + c[('R', 'W')] + c[('R', 'R')]
            agree = (c[('W', 'W')] + c[('R', 'R')]) / nonnull if nonnull else float('nan')
            out('%-4s %-7s %10d %10d %10d %10d %10d %10d %7.0f%%' % (
                v, rg, c[('W', 'W')], c[('W', 'R')], c[('R', 'W')], c[('R', 'R')], c[('N', 'W')], c[('N', 'R')], 100 * agree))


# ---------------------------------------------------------------------------
# C.3 The decision as a declared row table with a priced argmin.
# ---------------------------------------------------------------------------

# One row per FORM.  `layer` = which build may take it (off = SIMD-off,
# on = -fmemfn-simd); `needs` = a fact that must hold for the row to APPLY
# (the find-all iterator's carried state, D165, for the kept rows); the
# PRICE is est_delta (the walk prices 0).  Regime is NOT a column: it is
# a function of the facts the price reads, so an applicable row is priced
# in every regime; the regime only changes which term dominates the price.
FORM_ROWS = [
    # name          var    layer  needs
    ('walk',        None,  'off', ()),
    ('mask8',       'V1',  'off', ()),
    ('mask8+head',  'V2',  'off', ()),
    ('mask8+keep',  'V3',  'off', ('iterator',)),
    ('sse2',        'S1',  'on',  ()),
    ('sse2+head',   'S2',  'on',  ()),
    ('sse2+keep',   'S3',  'on',  ('iterator',)),
    ('avx2',        'A1',  'on',  ()),
    ('avx2+head',   'A2',  'on',  ()),
    ('avx2+keep',   'A3',  'on',  ('iterator',)),
]


def measured_ns(g, v):
    """ns per pass of variant v in group g; a kept variant not timed in
    `first` (built identical to its unkept twin, reading §1.1) takes the twin's."""
    if v is None:
        return g['V0b']['v0']
    if v in g:
        return g[v]['ns']
    twin = v[0] + '1'
    return g[twin]['ns'] if twin in g else None


def applicable(row, layer, have):
    name, v, lay, needs = row
    if layer == 'off' and lay == 'on':
        return False
    return all(n in have for n in needs)


def choose(cands, price):
    best = None
    for row in cands:
        pr = price(row)
        if pr is None:
            continue
        if best is None or pr < best[1]:
            best = (row, pr)
    return best[0]


def row_facts(c, s, m):
    f = facts(c, s, m)
    return dict(U=f['U'], ADV=f['K'] + f['U'], A=CV[(c, 'V1', s, m)]['cold'] if f['U'] else 0,
                fresh=1 if NBYTES[s] >= MIB else 0, n=f['n'], rg=regime(f), terms=TERMS[c], kind=KIND[c])


def prior_facts(c, s, m):
    """What the shipped prior alone states: p from the unigram rates over S,
    landings by independence lam = p(1-p), phi = 1 - p + lam, subject length
    and mode unknown -> one call over a long subject (state carried)."""
    p = PRIOR[c] / 1e6
    lam = p * (1 - p)
    n = 65536.0
    return dict(U=lam * n, ADV=(1 - p + lam) * n, A=1.0, fresh=1, n=n, terms=TERMS[c], kind=KIND[c])


def exemplar_facts(c, s, m, call_pattern):
    """An exemplar of the subject (bigram counts give p and landings exactly);
    with or without the call pattern (mode and matches per pass)."""
    sj = SUBJ[(c, s)]
    f = facts(c, s, m)
    n = sj['n']
    p = sj['ppm'] / 1e6
    lam = sj['land'] / n
    if call_pattern:
        # the call pattern states how many calls a pass makes and how far
        # each call scans (all: the subject; first: up to the first match);
        # the exemplar's own density then scales to that span
        A = CV[(c, 'V1', s, m)]['cold']
        span = n if m == 'all' else (f['K'] + f['U'])
        U = lam * span; ADV = (1 - p + lam) * span
    else:
        A = 1.0
        U = lam * n; ADV = (1 - p + lam) * n
    return dict(U=U, ADV=ADV, A=A, fresh=1 if n >= MIB else 0, n=n, terms=TERMS[c], kind=KIND[c])


def price_with(fx):
    def pr(row):
        name, v, lay, needs = row
        if v is None:
            return 0.0
        # every activation ends in at least one use (a scan that finds nothing
        # returns the bound), so a stated density of 0 still prices A uses
        U = max(fx['U'], fx['A'])
        return est_delta(v, fx['kind'], fx['terms'], U, fx['ADV'], fx['A'], fx['fresh'])
    return pr


def decisions():
    hdr('C.3 The decision table (FORM_ROWS) and its priced argmin vs the measured best')
    out('%-11s %-4s %-5s %-12s' % ('row', 'var', 'layer', 'needs'))
    for name, v, lay, needs in FORM_ROWS:
        out('%-11s %-4s %-5s %-12s' % (name, v or '-', lay, ','.join(needs) or '-'))
    out()
    out('Argmin of the price (oracle workload facts) vs the measured fastest applicable row:')
    for layer in ('off', 'on'):
        for have in ((), ('iterator',)):
            cands = [r for r in FORM_ROWS if applicable(r, layer, have)]
            agree = collections.Counter(); tot = collections.Counter()
            regret = collections.defaultdict(float); walkns = collections.defaultdict(float)
            for (c, s, m), g in SPK.items():
                fx = row_facts(c, s, m)
                if fx['U'] == 0:
                    continue
                meas = {r[0]: measured_ns(g, r[1]) for r in cands}
                meas = {k: v for k, v in meas.items() if v is not None}
                bestm = min(meas, key=meas.get)
                pick = choose([r for r in cands if r[0] in meas], price_with(fx))[0]
                rg = fx['rg']
                tot[rg] += 1
                agree[rg] += pick == bestm
                regret[rg] += meas[pick] - meas[bestm]
                walkns[rg] += g['V0b']['v0']
            out('  layer=%-3s iterator=%-3s ' % (layer, 'yes' if have else 'no') + '  '.join(
                '%s %d/%d regret %+.0f ns (%.2f%% of walk)' % (rg, agree[rg], tot[rg], regret[rg], 100 * regret[rg] / walkns[rg])
                for rg in ['DINGHY', 'TUG', 'LINER']))


# ---------------------------------------------------------------------------
# D. WHAT INFORMATION DECIDES: the regret of each information source.
# ---------------------------------------------------------------------------

def regret_by_source():
    hdr('D.1 Regret per information source, per regime, ABSOLUTE (spike rows, measured ns)')
    out('Each policy picks one form per (cell, subject, mode) from the rows applicable to the')
    out('layer; regret = measured ns of its pick - measured ns of the fastest applicable row.')
    out('Summed per regime: ns per pass and ns per MiB (all-mode rows), and % of the walk.')
    out('The kept rows need the find-all iterator (D165) and are offered only where noted.')
    pols = []

    def fixed(name):
        return lambda c, s, m, cands: name

    def r17loss(c, s, m, cands):              # compile-time: decline iff prior >= 100k
        return 'walk' if PRIOR[c] >= 100000 else ('mask8' if any(r[0] == 'mask8' for r in cands) else 'walk')

    def d162(c, s, m, cands):                 # setfind §9.2 with MEASURED (P): decline iff prior >= 300k and upa < 3
        f = facts(c, s, m)
        upa = f['U'] / max(f['cold'], 1)
        return 'walk' if (PRIOR[c] >= 300000 and upa < 3) else 'mask8'

    def model(src):
        def pol(c, s, m, cands):
            if src == 'prior':
                fx = prior_facts(c, s, m)
            elif src == 'exemplar':
                fx = exemplar_facts(c, s, m, False)
            elif src == 'exemplar+calls':
                fx = exemplar_facts(c, s, m, True)
            else:
                fx = row_facts(c, s, m)
            return choose(cands, price_with(fx))[0]
        return pol

    def regime_hint(table):
        def pol(c, s, m, cands):
            return table[regime(facts(c, s, m))]
        return pol

    # the regime hint's per-regime choice: the row with the least summed
    # measured ns over that regime (learned from the same table: an upper bound
    # on what a regime label alone can buy)
    def best_per_regime(cands):
        acc = collections.defaultdict(lambda: collections.defaultdict(float))
        for (c, s, m), g in SPK.items():
            f = facts(c, s, m)
            if f['U'] == 0:
                continue
            for r in cands:
                v = measured_ns(g, r[1])
                if v is not None:
                    acc[regime(f)][r[0]] += v
        return {rg: min(d, key=d.get) for rg, d in acc.items()}

    for layer, have in (('off', ()), ('off', ('iterator',)), ('on', ()), ('on', ('iterator',))):
        cands = [r for r in FORM_ROWS if applicable(r, layer, have)]
        names = [r[0] for r in cands]
        policies = [('always walk', fixed('walk'))]
        policies.append(('always mask8 (R17-b)', fixed('mask8')))
        if layer == 'on':
            policies.append(('always avx2', fixed('avx2')))
            if have:
                policies.append(('always avx2+keep', fixed('avx2+keep')))
        policies.append(('prior >= 100k declines (r17loss)', r17loss))
        policies.append(('setfind 9.2 (prior>=300k & upa<3)', d162))
        policies.append(('model, compile-time prior', model('prior')))
        policies.append(('model, exemplar (p, landings)', model('exemplar')))
        policies.append(('model, exemplar + call pattern', model('exemplar+calls')))
        bpr = best_per_regime(cands)
        policies.append(('regime hint -> %s' % '/'.join(bpr[r] for r in ['DINGHY', 'TUG', 'LINER']), regime_hint(bpr)))

        def regime_hint_loco(c, s, m, cands_, _cands=cands):
            # the per-regime row learned WITHOUT the cell being decided
            acc = collections.defaultdict(float)
            rg0 = regime(facts(c, s, m))
            for (c2, s2, m2), g2 in SPK.items():
                if c2 == c:
                    continue
                f2 = facts(c2, s2, m2)
                if f2['U'] == 0 or regime(f2) != rg0:
                    continue
                for r in _cands:
                    v = measured_ns(g2, r[1])
                    if v is not None:
                        acc[r[0]] += v
            return min(acc, key=acc.get)
        policies.append(('regime hint, row learned leave-one-cell-out', regime_hint_loco))

        def regime_from(src):
            # the regime DERIVED from a gap estimate alone (call span unknown ->
            # assumed long), then the regime's row
            def pol(c, s, m, cands_):
                if src == 'prior':
                    p = PRIOR[c] / 1e6
                    g_est = 1 / max(p * (1 - p), 1e-9)
                else:
                    sj = SUBJ[(c, s)]
                    g_est = sj['n'] / max(sj['land'], 1)
                rg = 'TUG' if g_est < G_STAR else 'LINER'
                return bpr[rg]
            return pol
        policies.append(('regime from prior gap (span unknown)', regime_from('prior')))
        policies.append(('regime from exemplar gap (span unknown)', regime_from('exemplar')))
        policies.append(('model, oracle facts', model('oracle')))
        out()
        out('layer=%s iterator=%s  rows offered: %s' % (layer, 'yes' if have else 'no', ', '.join(names)))
        out('  %-46s ' % 'policy' + ' '.join('%-30s' % rg for rg in ['DINGHY', 'TUG', 'LINER']))
        out('  %-46s ' % '' + ' '.join('%-30s' % 'ns/pass   ns/MiB  %walk' for _ in range(3)))
        for pname, pol in policies:
            acc = collections.defaultdict(lambda: [0.0, 0.0, 0.0])
            for (c, s, m), g in SPK.items():
                f = facts(c, s, m)
                if f['U'] == 0:
                    continue
                meas = {r[0]: measured_ns(g, r[1]) for r in cands}
                meas = {k: v for k, v in meas.items() if v is not None}
                pick = pol(c, s, m, [r for r in cands if r[0] in meas])
                if pick not in meas:
                    pick = 'walk'
                rg = regime(f)
                reg = meas[pick] - min(meas.values())
                a = acc[rg]
                a[0] += reg
                a[1] += reg * MIB / f['n'] if m == 'all' else 0.0
                a[2] += g['V0b']['v0']
            out('  %-46s ' % pname + ' '.join('%-30s' % ('%+9.0f %+9.0f %5.1f%%' % (acc[rg][0], acc[rg][1], 100 * acc[rg][0] / acc[rg][2]))
                                                for rg in ['DINGHY', 'TUG', 'LINER']))


def adaptive_slot2():
    hdr('D.2 Runtime adaptivity (slot2 kernel rows): adapt_* vs the best fixed form, per regime')
    real = 'adl qdm alt2 alt2r bkn bpr sig tki kel hbr hbrc u8l dig lc'.split()
    idx = collections.defaultdict(dict)
    for r in S2:
        if r['cell'] not in real or r['align'] != '0' or r['g'] != '0.0':
            continue
        idx[(r['regime'], r['n'], r['span'], r['reset'], int(r['ppm']), r['cell'])][r['form']] = float(r['ns_per_call_min'])
    out('Median over cells of adapt_X / min(table, X, mask forms of the same layer)')
    for key in sorted({k[:4] for k in idx}):
        ppms = sorted({k[4] for k in idx if k[:4] == key})
        cells = []
        for p in ppms:
            rs = []
            for c in real:
                d = idx.get(key + (p, c))
                if not d or 'adapt_swar' not in d:
                    continue
                best = min(d[f] for f in ('table', 'swar', 'mask8_swar', 'mask64_swar') if f in d)
                rs.append(d['adapt_swar'] / best)
            cells.append('%d:%.2f' % (p, np.median(rs)) if rs else '%d:-' % p)
        out('  %s n=%s span=%s reset=%s  adapt_swar/best-SIMD-off: %s' % (key + (' '.join(cells),)))
def price_cli(argv):
    """--price key=val ...: price every FORM_ROWS row for a hypothetical site.
    keys: kind (PF|HAT|VM), terms (1-3), n (bytes per pass), lam (uses per byte),
    alpha (activations per byte; 1/n for one call), phi (advance share, default
    1 - p + lam with p given), p, fresh (0|1), layer (off|on), iterator (0|1)."""
    kv = dict(a.split('=', 1) for a in argv)
    n = float(kv.get('n', 65536)); lam = float(kv['lam'])
    p = float(kv.get('p', lam))
    phi = float(kv.get('phi', 1 - p + lam))
    alpha = float(kv.get('alpha', 1.0 / n))
    fx = dict(U=lam * n, ADV=phi * n, A=max(alpha * n, 1.0), fresh=int(kv.get('fresh', 1)),
              n=n, terms=int(kv.get('terms', 1)), kind=kv.get('kind', 'PF'))
    have = ('iterator',) if kv.get('iterator', '0') == '1' else ()
    cands = [r for r in FORM_ROWS if applicable(r, kv.get('layer', 'on'), have)]
    pr = price_with(fx)
    rows = sorted(((pr(r), r[0]) for r in cands))
    print('site facts: %s' % fx)
    for d, name in rows:
        print('  %-11s %+12.1f ns/pass  %+9.4f ns/B' % (name, d, d / n))
    print('argmin: %s' % rows[0][1])


if __name__ == '__main__':
    if len(sys.argv) > 1 and sys.argv[1] == '--price':
        WF = walk_fit()
        import io, contextlib
        with contextlib.redirect_stdout(io.StringIO()):
            drivers()
        price_cli(sys.argv[2:])
        sys.exit(0)
    WF = walk_fit()
    regime_bounds(WF)
    placement()
    regime_card(WF)
    rescore_alpha()
    rescore_spike()
    rescore_spike2()
    medians_spike()
    drivers()
    alpha_oos()
    density()
    slot2_crossovers()
    nondensity()
    contrived_vs_real()
    estimator_report()
    decisions()
    regret_by_source()
    adaptive_slot2()
