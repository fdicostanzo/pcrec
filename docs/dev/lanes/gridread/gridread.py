#!/usr/bin/env python3
"""gridread: the READING of the grid1 joint timing slot (lane gridread, 2026-10-13).

ANALYSIS ONLY: no clock, no build.  Every ns is read from the slot's logs
(worktrees/memfn-slot/grid1/, run 2026-10-13 19:33-20:56 EDT, Zen 4 7700X,
CPU 14, 5 launches, A/A pair per group); every count from its no-clock
counting pass (counts.tsv).  The costmodel constants it tests are the
ones costmodel.py printed (costmodel/analysis.txt §C.1), copied below as
CM_* with their labels.

    python3 -I gridread.py OUT > analysis.txt     # OUT = the slot directory
    python3 -I gridread.py --check OUT            # verify SHA256SUMS first

Sections (cut into docs/dev/lanes/gridread_report.md):
  1  noise: A/A floor per group, per-launch spread, unstable groups, NULL rule, quiet gate
  2  re-fit: beta per byte (F3), per-call setup (short subjects), walk decomposition,
     c_cold / c_warm / m per form (F1 rows + counters), overscan; vs costmodel
  3  costmodel's estimator OUT OF SAMPLE on the grid: sign confusion + absExp per regime
  4  crossovers: g*, L*, single-call first mode, block-straddling lengths
  5  regime boundaries: placement, win/loss by regime, best split per form
  6  other axes: fresh, gap shape, alignment, stateless, dfa-hat vs PF, F3 terms
  7  decision table re-priced; regret per information source per regime (absolute ns)
  8  rule-of-thumb evidence rows
"""
import collections, math, os, sys
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np
from grload import *

if '--check' in sys.argv:
    OUT = [a for a in sys.argv[1:] if a != '--check'][0]
    bad = 0
    for ln in open(os.path.join(HERE, 'SHA256SUMS')):
        h, p = ln.split()
        got = sha256(os.path.join(OUT, p))
        if got != h:
            print('MISMATCH', p, got)
            bad += 1
    print('SHA256SUMS: %d inputs, %d mismatched' % (len(open(os.path.join(HERE, 'SHA256SUMS')).readlines()), bad))
    sys.exit(1 if bad else 0)

OUT = sys.argv[1] if len(sys.argv) > 1 else '/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1'
T1 = load_table(os.path.join(OUT, 'time_F1.log'))
T3 = load_table(os.path.join(OUT, 'time_F3.log'))
TX = load_table(os.path.join(OUT, 'time_EXT.log'))
R1, LOAD1, ANS1 = load_raw(os.path.join(OUT, 'time/raw_F1.tsv'))
R3, LOAD3, ANS3 = load_raw(os.path.join(OUT, 'time/raw_F3.tsv'))
RX, LOADX, ANSX = load_raw(os.path.join(OUT, 'time/raw_EXT.tsv'))
NOTES = {p: load_groupnotes(os.path.join(OUT, 'time_%s.log' % p)) for p in ('F1', 'F3', 'EXT')}
CNT = load_counts(os.path.join(OUT, 'counts.tsv'))
FACT = load_facts(os.path.join(OUT, 'subj_facts.tsv'))
G1 = groups(T1)
G3 = groups(T3)
GX = groups(TX)

MIB = 1048576.0
REGIMES = ['DINGHY', 'TUG', 'LINER']


def out(*a):
    print(*a)


def hdr(t):
    out()
    out('=' * 78)
    out(t)
    out('=' * 78)


# ---------------------------------------------------------------------------
# costmodel's numbers under test (costmodel/analysis.txt §C.1 + report §A.1/B.2).
# c_cold, c_warm, m: FITTED (costmodel A.2, PF/HAT kind); beta: MEASURED 1-2 terms,
# DERIVED 3 terms; omega (overscan per cold/warm use) and kappa (kept scanned/advanced):
# MEASURED from counters.
# ---------------------------------------------------------------------------
CM_BT = 0.1894
CM = {  # var: (c_cold, c_warm, m_fresh, beta1, beta2, om_cold, om_warm, kappa)
    'V1': (1.54, 0.96, -0.29, 0.1095, 0.1386, 4.7, 2.62, None),
    'V2': (0.74, 0.72, 0.36, 0.1098, 0.1381, 0.0, 0.01, None),
    'V3': (2.52, 1.40, 0.05, 0.1156, 0.1284, None, None, 1.22),
    'S1': (5.36, 0.72, -1.61, 0.0206, 0.0208, 59.2, 3.63, None),
    'S2': (4.49, 0.80, -0.78, 0.0206, 0.0207, 12.9, 2.13, None),
    'S3': (9.76, 1.08, -1.17, 0.0206, 0.0208, None, None, 1.32),
    'A1': (4.45, 0.65, -1.41, 0.0105, 0.0102, 59.2, 3.63, None),
    'A2': (2.27, 0.57, -0.97, 0.0104, 0.0102, 4.5, 1.17, None),
    'A3': (5.96, 1.04, -1.06, 0.0106, 0.0103, None, None, 1.32),
}
CM_GSTAR, CM_LSTAR = 18.5, 64.0
CM_WALK = dict(F=2.54, u=3.42, b=0.185)          # costmodel §0.1 PF row
CM_GX = {  # costmodel §B.2: g* carried / lost (B)
    'V1': (15.6, 25.7), 'S1': (4.7, 39.0), 'A1': (3.8, 28.4), 'V3': (29.3, None),
    'S3': (6.7, None), 'A3': (5.9, None)}

FORMS = ['V1', 'S1', 'A1', 'V3', 'S3', 'A3', 'Sn', 'An']


# ---------------------------------------------------------------------------
# 1. NOISE
# ---------------------------------------------------------------------------

def launch_vals(R, key, arm):
    d = R[key].get(arm, {})
    return [d[r] for r in sorted(d)]


def aa_stats(G, R):
    """per group: A/A floor (median-level, the log's), the per-launch A/A
    (|walk#b - walk| per round, relative), the base's per-launch spread."""
    st = {}
    for key, g in G.items():
        base = [a for a in g if a.endswith('#b')]
        if not base:
            continue
        bb = base[0]
        b0 = bb[:-2]
        v0 = launch_vals(R, key, b0)
        vb = launch_vals(R, key, bb)
        ref = med(v0)
        st[key] = dict(base=b0, ref=ref, floor=g[bb]['floor'], rel=g[bb]['floor'] / ref,
                       pl=[abs(b - a) / ref for a, b in zip(v0, vb)],
                       spread=(max(v0) - min(v0)) / ref, n=len(v0))
    return st


AA1 = aa_stats(G1, R1)
AA3 = aa_stats(G3, R3)
AAX = aa_stats(GX, RX)
ALLAA = list(AA1.values()) + list(AA3.values())
FRG = float(np.percentile([s['rel'] for s in ALLAA], 90))   # the grid's own p90 A/A


def paired(R, key, arm, base):
    """per-launch paired deltas arm - base (same round)."""
    a = R[key].get(arm, {})
    b = R[key].get(base, {})
    return [a[r] - b[r] for r in sorted(a) if r in b]


def verdict(key, arm, G=None, R=None, AA=None):
    """THE NULL RULE used everywhere below (section 1 derives it):
    NULL when |delta| <= max(A/A floor, FRG * base), OR the five launch-paired
    deltas do not all share the sign of the median delta."""
    G = G or G1; R = R or R1; AA = AA or AA1
    g = G[key]; r = g[arm]
    s = AA[key]
    d = r['delta']
    thr = max(s['floor'], FRG * s['ref'])
    pd = paired(R, key, arm, s['base'])
    cons = all(x > 0 for x in pd) or all(x < 0 for x in pd)
    if abs(d) <= thr or not cons:
        return 'N'
    return 'W' if d < 0 else 'R'


def noise():
    hdr('1. NOISE: the A/A floor per group, per-launch spread, the NULL rule, the quiet gate')
    for name, AA in (('F1', AA1), ('F3', AA3), ('EXT', AAX)):
        rel = np.array([s['rel'] for s in AA.values()])
        pl = np.array([x for s in AA.values() for x in s['pl']])
        sp = np.array([s['spread'] for s in AA.values()])
        out('%-4s groups %3d  A/A (|median#b - median|/base): median %.3f%%  p90 %.3f%%  max %.2f%%'
            % (name, len(rel), 100 * np.median(rel), 100 * np.percentile(rel, 90), 100 * rel.max()))
        out('      per-launch A/A (|#b - base| in one round): median %.3f%%  p90 %.3f%%  max %.2f%%'
            % (100 * np.median(pl), 100 * np.percentile(pl, 90), 100 * pl.max()))
        out('      base per-launch spread (max-min)/median:   median %.3f%%  p90 %.3f%%  max %.2f%%'
            % (100 * np.median(sp), 100 * np.percentile(sp, 90), 100 * sp.max()))
    out()
    out('FRG = p90 of the A/A over F1+F3 groups = %.3f%% of the base (costmodel used 2.3%% from the spike).' % (100 * FRG))
    out()
    out('Unstable groups (A/A > 1% of base, or base spread > 5%):')
    out('%-8s %-36s %-5s %10s %8s %8s' % ('cell', 'subject', 'mode', 'base ns', 'A/A %', 'spread%'))
    for key, s in list(AA1.items()) + list(AA3.items()):
        if s['rel'] > 0.01 or s['spread'] > 0.05:
            out('%-8s %-36s %-5s %10.1f %8.2f %8.2f' % (key[0], key[1], key[2], s['ref'], 100 * s['rel'], 100 * s['spread']))
    out()
    out('Per-arm per-launch spread (max-min)/median over F1 groups, median / p90 / max, and the')
    out('count of groups where that arm spreads > 5%:')
    for arm in ['walk'] + FORMS:
        sp = []
        for key in G1:
            v = launch_vals(R1, key, arm)
            if len(v) >= 2:
                sp.append((max(v) - min(v)) / med(v))
        if sp:
            sp = np.array(sp)
            out('  %-5s n %3d  %6.2f%% %6.2f%% %6.2f%%  >5%%: %d' % (arm, len(sp), 100 * np.median(sp),
                100 * np.percentile(sp, 90), 100 * sp.max(), int((sp > 0.05).sum())))
    # NULL rule comparison
    out()
    out('Verdict counts, F1 non-A/A rows, three rules:')
    c = collections.Counter()
    flips = []
    for key, g in G1.items():
        for arm, r in g.items():
            if arm.endswith('#b'):
                continue
            log = {'WIN': 'W', 'LOSS': 'R', 'NULL': 'N'}[r['verdict']]
            s = AA1[key]
            thr = max(s['floor'], 0.023 * s['ref'])
            cm = 'N' if abs(r['delta']) <= thr else ('W' if r['delta'] < 0 else 'R')
            v = verdict(key, arm)
            c[('log', log)] += 1; c[('cm', cm)] += 1; c[('grid', v)] += 1
            if v != log:
                flips.append((key, arm, log, v, r['delta'], s['ref']))
    for rule, lab in (('log', "time.sh's (|d| <= A/A floor)"), ('cm', "costmodel's strict (max(A/A, 2.3%))"),
                      ('grid', 'this reading (max(A/A, FRG) + 5/5 launch sign)')):
        out('  %-46s W %4d  R %4d  N %4d' % (lab, c[(rule, 'W')], c[(rule, 'R')], c[(rule, 'N')]))
    out('  rows whose verdict this reading changes from the log: %d (all to NULL: %s)'
        % (len(flips), all(f[3] == 'N' for f in flips)))
    big = sorted(flips, key=lambda f: -abs(f[4]))[:8]
    for key, arm, log, v, d, ref in big:
        out('    %-8s %-34s %-5s %-4s log %s -> %s  delta %+.1f ns (%.2f%% of base)' % (key[0], key[1], key[2], arm, log, v, d, 100 * d / ref))
    # quiet gate
    out()
    out('Quiet gate (LOADMAX 1.5, load1 sampled at every launch; the timed process itself is one runnable task):')
    for p, L in (('F1', LOAD1), ('F3', LOAD3), ('EXT', LOADX)):
        n = NOTES[p]
        out('  %-4s launches %5d  load1 min %.2f median %.2f max %.2f  >1.5: %d   groups %d, waits>0: %d'
            % (p, len(L), min(L), np.median(L), max(L), sum(1 for x in L if x > 1.5), len(n),
               sum(1 for x in n if x['waits'] > 0)))
    # answers: every launch of a group agrees
    bad = sum(1 for k, a in list(ANS1.items()) + list(ANS3.items()) + list(ANSX.items()) if len(a) != 1)
    out('  groups whose launches printed more than one answer line: %d' % bad)


# ---------------------------------------------------------------------------
# row facts from the counters (no clock)
# ---------------------------------------------------------------------------

def per_pass(c, key, arm):
    k = (key[0], arm, key[1], key[2])
    if k not in CNT:
        return None
    d = CNT[k]
    nb = d['nbuf']
    return {x: v / nb for x, v in d.items()}


def rowfacts(key):
    """workload facts of one F1 group from the planted counts + the site's counters."""
    cell, subj, mode = key
    f = FACT[base_name(subj)]
    nb = f['nbuf']
    n = f['n']
    site = per_pass(CNT, key, 'site(G1)')
    U = site['uses']
    A = site['cold']              # activations: the first use of each call (costmodel: V1's cold)
    calls = site['calls']
    m = f['pm'] / nb
    if mode == 'all':
        ADV = n - m * TOKC[cell]
    else:   # first: one call to the first match (or the whole subject)
        ADV = (min(f['L'], n) - TOKLEN[cell] + 1) if f['L'] else n
        ADV = max(ADV, 1.0)
    d = dict(cell=cell, n=n, g=f['g'], L=f['L'], shape=f['shape'], reuse=f['reuse'], off=offset(subj),
             U=U, A=A, calls=calls, matches=m, landings=f['pl'] / nb, ADV=ADV,
             fresh=1 if f['reuse'] == 'S' else 0, mode=mode)
    d['Lact'] = ADV / A if A else float('inf')
    d['gu'] = ADV / U if U else float('inf')
    d['rg'] = regime(d)
    return d


def regime(d, L_STAR=CM_LSTAR, G_STAR=CM_GSTAR):
    if d['U'] == 0:
        return 'UNREACHED'
    if d['Lact'] < L_STAR:
        return 'DINGHY'
    if d['gu'] < G_STAR:
        return 'TUG'
    return 'LINER'


RF = {key: rowfacts(key) for key in G1}


def arm_rows(arms=None, keys=None, mode=None):
    """every (group, arm) F1 row with its facts and its arm's counters."""
    out_ = []
    for key, g in G1.items():
        if keys is not None and key not in keys:
            continue
        if mode and key[2] != mode:
            continue
        for arm, r in g.items():
            if arm in ('walk', 'walk#b') or (arms and arm not in arms):
                continue
            c = per_pass(CNT, key, arm)
            if c is None:
                continue
            s = AA1[key]
            out_.append(dict(key=key, arm=arm, f=RF[key], c=c, d=r['delta'], ns=r['ns'], v0=s['ref'],
                             fl=s['floor'], cls=verdict(key, arm)))
    return out_



# ---------------------------------------------------------------------------
# 2. RE-FIT costmodel's terms on the controlled data
# ---------------------------------------------------------------------------

def nsof(G, key, arm):
    """ns per pass of ARM in group KEY (the base `walk` reads the log's base column)."""
    g = G[key]
    if arm == 'walk':
        return g['walk#b']['base']
    return g[arm]['ns'] if arm in g else None


F3ARMS = ['walk', 'V1', 'V2', 'S1', 'S2', 'A1', 'A2', 'Sn', 'An']


def f3_rates():
    """beta per byte per (terms, arm): the slope between the 64 KiB and 1 MiB
    member-free one-call rows (MEASURED; the intercept is the per-call term,
    poorly determined here).  f3-<cell> carries 1/2/3/4 cover terms."""
    B = {}
    for cell in ('f3-dig', 'f3-hex-run', 'f3-word-eq', 'f3-quad'):
        k64 = (cell, 'g1-%s-n64k-ginf-Lnone' % cell, 'first')
        k1m = (cell, 'g1-%s-n1m-ginf-Lnone' % cell, 'first')
        for arm in F3ARMS:
            a = nsof(G3, k64, arm)
            b = nsof(G3, k1m, arm)
            slope = (b - a) / (MIB - 65536)
            B[(TERMS[cell], arm)] = dict(slope=slope, at64=a / 65536, at1m=b / MIB, icpt=a - slope * 65536)
    return B


F3 = f3_rates()
BT = F3[(1, 'walk')]['slope']          # the walk's per-byte rate (MEASURED, 1-term cell)


def beta(arm, terms):
    a = {'V3': 'V1', 'S3': 'S1', 'A3': 'A1'}.get(arm, arm)
    return F3[(terms, a)]['slope']


def refit():
    hdr('2. RE-FIT on the controlled data (MEASURED unless labelled FITTED)')
    out('2.1 beta per byte, F3 (one `first` call over a member-free 64 KiB and 1 MiB subject; slope between them)')
    out('%-5s %10s %10s %10s %10s   %s' % ('arm', '1 term', '2 terms', '3 terms', '4 terms', 'costmodel (1t / 2t / 3t)'))
    for arm in F3ARMS:
        cm = ''
        if arm == 'walk':
            cm = '%.4f (beta_t)' % CM_BT
        elif arm in CM:
            v = CM[arm]
            cm = '%.4f / %.4f / %.4f DERIVED' % (v[3], v[4], 2 * v[4] - v[3])
        out('%-5s %10.4f %10.4f %10.4f %10.4f   %s' % (arm, *[F3[(t, arm)]['slope'] for t in (1, 2, 3, 4)], cm))
    out('ns per byte at 1 MiB (incl. the call): ' + '  '.join('%s %.4f' % (a, F3[(1, a)]['at1m']) for a in F3ARMS))
    out('per-byte saving vs the walk (beta_t - beta_f), by terms:')
    for arm in F3ARMS[1:]:
        out('  %-4s ' % arm + '  '.join('%dt %+.4f' % (t, F3[(t, 'walk')]['slope'] - F3[(t, arm)]['slope']) for t in (1, 2, 3, 4)))
    out('the walk itself by terms (it reads one 256-byte table, so terms should not move it): '
        + '  '.join('%dt %.4f' % (t, F3[(t, 'walk')]['slope']) for t in (1, 2, 3, 4)))

    # 2.2 per-call setup on short member-free single calls
    out()
    out('2.2 The per-call term: one `first` call over a member-free n-byte subject (D5-sparse, dig).')
    out('    F(n) = ns - beta*n with the F3 1-term beta: the fixed part of a single call, by length.')
    arms = ['walk', 'V1', 'S1', 'A1', 'Sn', 'An']
    out('%-5s ' % 'n' + ''.join('%10s' % a for a in arms) + '   (ns per call, measured)')
    rows = {}
    for n in (48, 63, 64, 65, 128):
        key = ('dig', 'g1-dig-n%d-ginf-Lnone' % n, 'first')
        g = G1[key]
        ns = {a: nsof(G1, key, a) for a in arms}
        rows[n] = ns
        out('%-5d ' % n + ''.join('%10.2f' % ns[a] for a in arms))
    out('%-5s ' % 'F(n)' + '   (ns - beta*n; costmodel/regimefacts F: walk 4.29, V1 3.09, S1 20.45, A1 10.54 at n=40)')
    for n in (48, 64, 128):
        out('%-5d ' % n + ''.join('%10.2f' % (rows[n][a] - beta(a, 1) * n) for a in arms))
    key = ('dig', 'g1-dig-n64k-ginf-L64k', 'all')
    out('one 64 KiB call (ginf L64k all: 1 match at the end), ns - beta*n: ' +
        '  '.join('%s %.0f' % (a, nsof(G1, key, a) - beta(a, 1) * 65536)
                  for a in ['walk', 'V1', 'S1', 'A1']) + '   (the consumer and the 2 calls are in it)')

    # 2.3 the absolute per-arm fits (the walk and every form, per cell)
    out()
    out('2.3 Every arm decomposed, per cell (FITTED; relative LS over the F1 all-mode groups with n = 64 KiB):')
    out('    T - beta*bytes = F*A + w*(U - A) + p*U*[streamed, u-shape] + q*U*[repeated, u-shape]')
    out('    A = activations (the site\'s cold uses: calls that reach a use), U = uses (landings + matches),')
    out('    bytes = ADV for the walk, blocks*W for a form (counters); beta MEASURED on the cell\'s own')
    out('    ginf-L64k row (one 64 KiB call, one match at its end).  p, q: the per-use cost of a landing')
    out('    whose position the predictor cannot have learned (streamed u-shape: every buffer differs;')
    out('    repeated u-shape: one 64 KiB pattern repeated, partly learnable; reg/burst: fixed offsets).')
    for cell in ('dig', 'bounded', 'dfa-hat'):
        out('  cell %s (%s, %d term%s): beta per byte from ginf-L64k: ' % (cell, KIND[cell], TERMS[cell], 's' if TERMS[cell] > 1 else '')
            + '  '.join('%s %.4f' % (a, BCELL[(cell, a)]) for a in ['walk'] + FORMS))
        out('  %-5s %5s %8s %8s %8s %8s %7s %8s' % ('arm', 'rows', 'F/act', 'w/warm', 'p/u-S', 'q/u-rep', 'absExp', 'med|rel|'))
        for arm in ['walk'] + FORMS:
            r = ABSFIT.get((cell, arm))
            if r is None:
                continue
            out('  %-5s %5d %8.2f %8.2f %8.2f %8.2f %7.3f %8.3f' % (arm, r['n'], *r['co'], r['ae'], r['mrel']))
    out()
    out('    Walk-internal crossovers (FITTED): g* = w_walk / beta_t (a pass is half per-use, half per-byte),')
    out('    L*_walk = F_walk / beta_t:')
    for cell in ('dig', 'bounded', 'dfa-hat'):
        co = ABSFIT[(cell, 'walk')]['co']; bt = BCELL[(cell, 'walk')]
        out('      %-8s g* %.1f B  (with the u-S landing cost w+p: %.1f B)   L*_walk %.1f B' % (cell, co[1] / bt, (co[1] + co[2]) / bt, co[0] / bt))
    out('    costmodel (PF, real text): u 3.42 ns, b 0.185 -> g* 18.5 B; F 2.54 -> L*_walk 13.8 B')

    out()
    out('2.3b costmodel\'s per-use DELTA terms, recomputed as differences of the absolute fits (form - walk):')
    out('     c_cold = F_form - F_walk + ... (per activation), c_warm = w_form - w_walk, m(u-S) = p_form - p_walk')
    out('%-3s %-8s %8s %8s %8s %8s   %-24s %s' % ('var', 'cell', 'c_cold', 'c_warm', 'm(u-S)', 'm(u-rep)', 'costmodel', 'verdict (cold / warm / fresh)'))
    for arm in FORMS:
        for cell in ('dig', 'bounded', 'dfa-hat'):
            f = ABSFIT.get((cell, arm)); w = ABSFIT[(cell, 'walk')]
            if f is None:
                continue
            d = [f['co'][i] - w['co'][i] for i in range(4)]
            DFIT[(arm, cell)] = d
            cm = CM.get(arm)
            cms = '%+.2f/%+.2f/%+.2f' % (cm[0], cm[1], cm[2]) if cm else '-'
            vd = ' / '.join(judge(x, c) for x, c in zip(d[:3], cm[:3])) if cm else ''
            out('%-3s %-8s %+8.2f %+8.2f %+8.2f %+8.2f   %-24s %s' % (arm, cell, d[0], d[1], d[2], d[3], cms, vd))
    out('verdict rule: CONFIRMED if |grid - costmodel| <= max(0.5 ns, 25%); MOVED if the sign holds; REFUTED if the sign flips (|diff| > 0.5 ns).')
    out('NOTE: costmodel\'s "fresh" was its 1 MiB real-text subjects; the grid\'s analogue is the streamed u-shape term p.')
    out('      Streamed reg/burst rows carry no such term (their landing offsets repeat in every buffer).')

    # 2.4 overscan
    out()
    out('2.4 Overscan (MEASURED from the counters): blocks*W - ADV regressed on (cold, warm) uses; kept forms kappa = blocks*W/ADV')
    for arm in ['V1', 'S1', 'A1', 'Sn', 'An', 'V3', 'S3', 'A3']:
        rs = arm_rows([arm], mode='all')
        rs = [r for r in rs if r['f']['n'] >= 65536]
        W_ = WIDTH[arm]
        if arm in KEPT:
            k = np.array([r['c']['blocks'] * W_ / r['f']['ADV'] for r in rs])
            cm = CM[arm][7]
            out('  %-3s kappa median %.3f  (p10 %.3f p90 %.3f, %d rows)   costmodel %.2f' % (arm, np.median(k), np.percentile(k, 10), np.percentile(k, 90), len(k), cm))
        else:
            X = np.array([[r['c']['cold'], r['c']['uses'] - r['c']['cold']] for r in rs], float)
            Y = np.array([r['c']['blocks'] * W_ - r['f']['ADV'] for r in rs])
            co, *_ = np.linalg.lstsq(X, Y, rcond=None)
            cm = CM.get(arm)
            out('  %-3s omega cold %6.1f B  warm %5.2f B per use (%d rows)   costmodel %s'
                % (arm, co[0], co[1], len(rs), ('%.1f / %.2f' % (cm[5], cm[6])) if cm else '-'))
            scanned = np.array([r['c']['blocks'] * W_ / r['f']['ADV'] for r in rs])
            out('      bytes evaluated per byte advanced: median %.2f, max %.2f' % (np.median(scanned), scanned.max()))

    # 2.5 fit quality per regime of the DELTA predicted from the two absolute fits
    out()
    out('2.5 Fit quality per regime: delta predicted as fit(form) - fit(walk), against the measured delta')
    out('    (in sample; LOCO = both fits refitted without the row\'s (g) value, sign errors on non-NULL rows):')
    out('%-3s %-7s %5s %7s %10s %10s' % ('var', 'regime', 'rows', 'absExp', 'sign err', 'LOCO err'))
    for arm in FORMS:
        rs = [r for r in arm_rows([arm], mode='all') if r['f']['n'] >= 65536 and not r['f']['off']]
        for rg in REGIMES:
            sub = [r for r in rs if r['f']['rg'] == rg]
            if not sub:
                continue
            P = [abs_pred(r['key'][0], arm, r) - abs_pred(r['key'][0], 'walk', r, walk=True) for r in sub]
            D = np.array([r['d'] for r in sub])
            ae = 1 - np.sum(np.abs(D - np.array(P))) / max(np.sum(np.abs(D)), 1e-9)
            nn = [(r, p_) for r, p_ in zip(sub, P) if r['cls'] != 'N']
            se = sum(1 for r, p_ in nn if np.sign(p_) != np.sign(r['d']))
            le = 0
            for r in sub:
                if r['cls'] == 'N':
                    continue
                lp = loco_pred(r, arm)
                if lp is not None and np.sign(lp) != np.sign(r['d']):
                    le += 1
            out('%-3s %-7s %5d %7.2f %6d/%-3d %10d' % (arm, rg, len(sub), ae, se, len(nn), le))


FITS = {}


DFIT = {}


def cell_beta(cell, arm):
    key = (cell, 'g1-%s-n64k-ginf-L64k' % cell, 'all')
    return nsof(G1, key, arm) / 65536.0


BCELL = {}


def abs_rows(cell, arm, exclude_g=None):
    rows = []
    for key, g in G1.items():
        f = RF[key]
        if key[0] != cell or key[2] != 'all' or f['n'] < 65536 or f['off']:
            continue
        if exclude_g is not None and f['g'] == exclude_g:
            continue
        T = nsof(G1, key, arm)
        if T is None:
            continue
        if arm == 'walk':
            byts = f['ADV']
        else:
            c = per_pass(CNT, key, arm)
            if c is None:
                continue
            byts = c['blocks'] * WIDTH[arm]
        rows.append((key, f, T, byts))
    return rows


def abs_feats(f):
    uS = 1.0 if (f['reuse'] == 'S' and f['shape'] == 'u' and f['g'] >= 4) else 0.0
    uR = 1.0 if (f['reuse'] == 'rep' and f['shape'] == 'u' and f['g'] >= 4) else 0.0
    return [f['A'], f['U'] - f['A'], f['U'] * uS, f['U'] * uR]


def abs_fit(cell, arm, exclude_g=None):
    rows = abs_rows(cell, arm, exclude_g)
    if len(rows) < 6:
        return None
    b = BCELL[(cell, arm)]
    X = np.array([abs_feats(f) for _, f, _, _ in rows], float)
    Y = np.array([T - b * byts for _, _, T, byts in rows])
    Tt = np.array([T for _, _, T, _ in rows])
    W = 1.0 / (0.01 * Tt + 0.3)
    co, *_ = np.linalg.lstsq(X * W[:, None], Y * W, rcond=None)
    P = X @ co + np.array([b * byts for _, _, _, byts in rows])
    ae = 1 - np.sum(np.abs(Tt - P)) / np.sum(Tt)
    mrel = float(np.median(np.abs(Tt - P) / Tt))
    return dict(co=co, n=len(rows), ae=ae, mrel=mrel)


def abs_pred(cell, arm, r, walk=False, co=None):
    f = r['f']
    co = ABSFIT[(cell, arm)]['co'] if co is None else co
    if arm == 'walk':
        byts = f['ADV']
    else:
        byts = r['c']['blocks'] * WIDTH[arm]
    return float(np.dot(abs_feats(f), co)) + BCELL[(cell, arm)] * byts


def loco_pred(r, arm):
    cell = r['key'][0]
    g = r['f']['g']
    fw = abs_fit(cell, 'walk', exclude_g=g)
    ff = abs_fit(cell, arm, exclude_g=g)
    if fw is None or ff is None:
        return None
    return abs_pred(cell, arm, r, co=ff['co']) - abs_pred(cell, 'walk', r, co=fw['co'])


for _c in ('dig', 'bounded', 'dfa-hat'):
    for _a in ['walk'] + FORMS:
        BCELL[(_c, _a)] = cell_beta(_c, _a)
ABSFIT = {}
for _c in ('dig', 'bounded', 'dfa-hat'):
    for _a in ['walk'] + FORMS:
        _f = abs_fit(_c, _a)
        if _f:
            ABSFIT[(_c, _a)] = _f


def judge(g, c):
    if g is None:
        return '-'
    if abs(g - c) <= max(0.5, 0.25 * abs(c)):
        return 'CONFIRMED'
    if np.sign(g) == np.sign(c) or abs(g - c) <= 0.5:
        return 'MOVED %+.2f' % (g - c)
    return 'REFUTED %+.2f' % (g - c)


def sigma(r):
    return max(r['fl'], 0.01 * r['v0'], 0.3)


def form_target(arm, r):
    t = TERMS[r['key'][0]]
    return r['d'] - beta(arm, t) * r['c']['blocks'] * WIDTH[arm] + BT * r['f']['ADV']


def form_feats(arm, r):
    c = r['c']
    if arm in STATELESS:
        return {'use': c['uses'], 'Ufresh': c['uses'] * r['f']['fresh']}
    return {'cold': c['cold'], 'warm': c['uses'] - c['cold'], 'Ufresh': c['uses'] * r['f']['fresh']}


def fit_form(arm, rs):
    fs = list(form_feats(arm, rs[0]).keys())
    X = np.array([[form_feats(arm, r)[f] for f in fs] for r in rs], float)
    Y = np.array([form_target(arm, r) for r in rs])
    W = np.array([1 / sigma(r) for r in rs])
    co, *_ = np.linalg.lstsq(X * W[:, None], Y * W, rcond=None)
    pred = [predict_form(arm, fs, co, r) for r in rs]
    return fs, co, rs, pred


def predict_form(arm, fs, co, r):
    ff = form_feats(arm, r)
    t = TERMS[r['key'][0]]
    return sum(c * ff[f] for f, c in zip(fs, co)) + beta(arm, t) * r['c']['blocks'] * WIDTH[arm] - BT * r['f']['ADV']


def quality(rs, preds):
    D = np.array([r['d'] for r in rs]); P = np.array(preds)
    W = np.array([1 / sigma(r) for r in rs])
    res = D - P
    if len(rs) > 1:
        mu = np.average(D, weights=W ** 2)
        wr2 = 1 - np.sum((res * W) ** 2) / max(np.sum(((D - mu) * W) ** 2), 1e-9)
    else:
        wr2 = float('nan')
    ae = 1 - np.sum(np.abs(res)) / max(np.sum(np.abs(D)), 1e-9)
    nn = [(r, p) for r, p in zip(rs, preds) if r['cls'] != 'N']
    serr = sum(1 for r, p in nn if np.sign(p) != np.sign(r['d']))
    return wr2, ae, serr, len(nn)


# ---------------------------------------------------------------------------
# 3. costmodel's estimator OUT OF SAMPLE (its constants, the grid's workload facts)
# ---------------------------------------------------------------------------

def cm_est(arm, terms, U, ADV, A, fresh):
    """costmodel.est_delta with its printed constants (PF/HAT kind)."""
    cc, cw, m, b1, b2, oc, ow, kap = CM[arm]
    b = b1 if terms == 1 else (b2 if terms == 2 else 2 * b2 - b1)
    if arm in KEPT:
        Ae = 1.0 if A > 0 else 0.0
        over = (kap - 1.0) * ADV
    else:
        Ae = A
        over = oc * A + ow * max(U - A, 0)
    d = cc * Ae + cw * max(U - Ae, 0) + m * U * fresh
    return d + (b - CM_BT) * ADV + b * max(over, 0.0)


def oos():
    hdr("3. costmodel's estimator OUT OF SAMPLE: its constants, the grid's workload facts (U, ADV, A, fresh)")
    out('Measured class by this reading\'s NULL rule x predicted sign; absExp = 1 - sum|meas-pred| / sum|meas|.')
    out('%-3s %-7s %5s %6s %6s %6s %6s %6s %6s %7s %8s %12s %12s' % ('var', 'regime', 'rows', 'W->W', 'W->R', 'R->W', 'R->R',
        'N->W', 'N->R', 'agree', 'absExp', 'sum meas', 'sum pred'))
    tot = collections.Counter()
    for arm in ['V1', 'S1', 'A1', 'V3', 'S3', 'A3']:
        rs = arm_rows([arm], mode='all')
        for rg in REGIMES + ['ALL']:
            c = collections.Counter(); D = []; P = []
            for r in rs:
                f = r['f']
                if rg != 'ALL' and f['rg'] != rg:
                    continue
                p = cm_est(arm, TERMS[r['key'][0]], f['U'], f['ADV'], f['A'], f['fresh'])
                c[(r['cls'], 'W' if p < 0 else 'R')] += 1
                D.append(r['d']); P.append(p)
            if not D:
                continue
            nn = c[('W', 'W')] + c[('W', 'R')] + c[('R', 'W')] + c[('R', 'R')]
            ag = (c[('W', 'W')] + c[('R', 'R')]) / nn if nn else float('nan')
            D = np.array(D); P = np.array(P)
            ae = 1 - np.sum(np.abs(D - P)) / np.sum(np.abs(D))
            if rg != 'ALL':
                for k_ in c:
                    tot[(rg,) + k_] += c[k_]
            out('%-3s %-7s %5d %6d %6d %6d %6d %6d %6d %6.0f%% %8.2f %12.0f %12.0f' % (arm, rg, len(D), c[('W', 'W')], c[('W', 'R')],
                c[('R', 'W')], c[('R', 'R')], c[('N', 'W')], c[('N', 'R')], 100 * ag, ae, D.sum(), P.sum()))
    out()
    out('Pooled over the six forms, per regime (sign agreement on non-NULL rows):')
    for rg in REGIMES:
        nn = sum(tot[(rg, a, b)] for a in 'WR' for b in 'WR')
        ag = tot[(rg, 'W', 'W')] + tot[(rg, 'R', 'R')]
        out('  %-7s %4d / %4d = %.0f%%   (costmodel in-sample C.2: DINGHY 86-91%%, TUG 93-100%%, LINER 96-100%%)' % (rg, ag, nn, 100 * ag / nn))
    # the misses, largest absolute first
    out()
    out('Largest absolute misses (V1, A1, A3):')
    miss = []
    for arm in ['V1', 'A1', 'A3']:
        for r in arm_rows([arm], mode='all'):
            f = r['f']
            p = cm_est(arm, TERMS[r['key'][0]], f['U'], f['ADV'], f['A'], f['fresh'])
            miss.append((abs(r['d'] - p), arm, r, p))
    for m_, arm, r, p in sorted(miss, key=lambda x: -x[0])[:12]:
        f = r['f']
        out('  %-3s %-8s %-30s %-6s meas %+9.0f pred %+9.0f  (L %.0f g %.1f)' % (arm, r['key'][0], r['key'][1], f['rg'], r['d'], p, f['Lact'], f['gu']))


# ---------------------------------------------------------------------------
# 4. CROSSOVERS, measured (and the fitted ones beside them)
# ---------------------------------------------------------------------------

G8 = [2, 4, 8, 16, 32, 64, 256, 0]


def gkey(cell, g, L, n=65536, shape='u', reuse='rep', mode='all'):
    def k(v):
        return 'inf' if v == 0 else (('%dm' % (v >> 20)) if v >= MIB and v % (1 << 20) == 0 else
                                     ('%dk' % (v >> 10)) if v >= 1024 and v % 1024 == 0 else str(v))
    nm = 'g1-%s-n%s-g%s-L%s' % (cell, k(n), k(g), 'none' if L == 0 else k(L))
    if g not in (0, 2):
        nm += '-' + shape
    if reuse == 'S':
        nm += '-S'
    return (cell, nm, mode)


def cross(xs, ds):
    """interpolated zero crossing of delta(x) going from loss (+) to win (-) as x grows,
    in log2 x; None when there is none.  Returns (x*, 'lo..hi')."""
    pts = [(x, d) for x, d in zip(xs, ds) if d is not None]
    for (x0, d0), (x1, d1) in zip(pts, pts[1:]):
        if d0 > 0 and d1 <= 0:
            l0 = math.log2(x0); l1 = math.log2(x1)
            t = d0 / (d0 - d1)
            return 2 ** (l0 + t * (l1 - l0)), '%g..%g' % (x0, x1)
    if pts and all(d <= 0 for _, d in pts):
        return 0.0, 'wins at every point'
    if pts and all(d > 0 for _, d in pts):
        return float('inf'), 'loses at every point'
    return None, 'no single crossing'


def crossovers():
    hdr('4. CROSSOVERS (MEASURED from the deltas; interpolation in log2 is labelled)')
    out('4.1 g*: the landing gap at which a form starts to win, per cell, call span L and reuse.')
    out('    Row string: the verdict at g = 2 4 8 16 32 64 256 inf (W win, R loss, N null, . not timed).')
    out('    g* = interpolated zero crossing of the delta in log2 g (FITTED by interpolation).')
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for reuse in ('rep', 'S'):
            for L in (8, 32, 1024, 65536):
                keys = [gkey(cell, g, L, reuse=reuse) for g in G8]
                if not any(k in G1 for k in keys):
                    continue
                out('  %-8s %-3s L=%-6d' % (cell, reuse, L))
                for arm in FORMS:
                    vs, ds, xs = '', [], []
                    for g, k in zip(G8, keys):
                        if k in G1 and arm in G1[k]:
                            v = verdict(k, arm)
                            vs += v
                            ds.append(G1[k][arm]['delta']); xs.append(g if g else 4096)
                        else:
                            vs += '.'
                    if not xs:
                        continue
                    x, lab = cross(xs, ds)
                    xs_ = ('%.1f' % x) if x not in (None, 0.0, float('inf')) else '-'
                    out('    %-3s %s   g* %6s B  (%s)' % (arm, vs.replace('W', 'W').replace('R', 'R'), xs_, lab))
    out()
    out('4.1b g* FITTED from section 2.3b (per-use extra cost / per-byte saving, dig):')
    out('    carried = c_warm/dbeta (state carried within a long call), lost = (c_cold)/dbeta (one use per')
    out('    activation), u-S = (c_warm + m(u-S))/dbeta (unpredictable fresh landings); costmodel carried / lost.')
    for cell in ('dig', 'bounded', 'dfa-hat'):
        for arm in FORMS:
            d = DFIT.get((arm, cell))
            if d is None:
                continue
            db = BCELL[(cell, 'walk')] - BCELL[(cell, arm)]
            cmx = CM_GX.get(arm, (None, None))
            out('  %-8s %-3s dbeta %.4f  carried %6.1f  lost %6.1f  u-S %6.1f   costmodel %s / %s' % (
                cell, arm, db, d[1] / db, d[0] / db, (d[1] + d[2]) / db,
                cmx[0] if cmx[0] is not None else '-', cmx[1] if cmx[1] is not None else '-'))

    out()
    out('4.2 L*: the call span at which a form starts to pay (find-all, n = 64 KiB, a match every L bytes).')
    out('    Row: delta ns per pass at L = 8 32 128 1k 64k (blank = not timed) with its verdict letter.')
    for cell, gs in (('dig', (4, 64, 0)), ('dfa-hat', (4, 64, 0)), ('bounded', (2, 32, 0))):
        for g in gs:
            out('  %-8s g=%s' % (cell, g if g else 'inf'))
            for arm in FORMS:
                xs, ds, txt = [], [], ''
                for L in (8, 32, 128, 1024, 65536):
                    k = gkey(cell, g, L)
                    if k in G1 and arm in G1[k]:
                        d = G1[k][arm]['delta']
                        xs.append(L); ds.append(d)
                        txt += '%10.0f%s' % (d, verdict(k, arm))
                    else:
                        txt += '%11s' % ''
                if not xs:
                    continue
                x, lab = cross(xs, ds)
                xs_ = ('%.0f' % x) if x not in (None, 0.0, float('inf')) else '-'
                out('    %-3s %s   L* %6s B (%s)' % (arm, txt, xs_, lab))
    out('  FITTED L* = c_cold / dbeta (an activation with no landing pays for itself after L* bytes), dig:')
    out('    ' + '  '.join('%s %.0f' % (a, DFIT[(a, 'dig')][0] / (BCELL[('dig', 'walk')] - BCELL[('dig', a)])) for a in FORMS))
    out('  costmodel: 19 B (V1), 25 B (A1), 32 B (S1) + overscan; L* = 64 B; regimefacts n* ~1 KB (SIMD, F/c one call)')

    out()
    out('4.3 One `first` call of span ~L (D4 dig / H4 dfa-hat: landings every g inside it): delta ns per call')
    for cell in ('dig', 'dfa-hat'):
        for g in (2, 8, 0):
            out('  %-8s g=%-4s walk ns at L=8/32/128: %s' % (cell, g if g else 'inf', ' / '.join(
                '%.1f' % nsof(G1, gkey(cell, g, L, mode='first'), 'walk') for L in (8, 32, 128) if gkey(cell, g, L, mode='first') in G1)))
            for arm in ['V1', 'S1', 'A1', 'Sn', 'An']:
                txt = ''
                for L in (8, 32, 128):
                    k = gkey(cell, g, L, mode='first')
                    if k in G1 and arm in G1[k]:
                        txt += '%9.2f%s' % (G1[k][arm]['delta'], verdict(k, arm))
                out('    %-3s %s' % (arm, txt))
    out('  single member-free calls (D5-sparse, D6-first): delta ns per call')
    for nm in ['g1-dig-n48-ginf-Lnone', 'g1-dig-n63-ginf-Lnone', 'g1-dig-n64-ginf-Lnone', 'g1-dig-n65-ginf-Lnone',
               'g1-dig-n128-ginf-Lnone', 'g1-dig-n64k-ginf-L64k@0']:
        k = ('dig', nm, 'first')
        if k not in G1:
            continue
        out('    %-28s walk %8.2f  ' % (nm, nsof(G1, k, 'walk')) + '  '.join(
            '%s %+8.2f%s' % (a, G1[k][a]['delta'], verdict(k, a)) for a in ['V1', 'S1', 'S2', 'A1', 'A2', 'Sn', 'An'] if a in G1[k]))

    out()
    out('4.4 The block-straddling lengths n = 48 63 64 65 128 (dig; ns per pass):')
    for mode, nmf in (('first', 'g1-dig-n%d-ginf-Lnone'), ('all', 'g1-dig-n%d-g8-L32-u')):
        out('  %s (%s)' % (mode, 'member-free, one call' if mode == 'first' else 'g=8, a match every 32 B'))
        arms = ['walk', 'V1', 'S1', 'A1', 'V3', 'S3', 'A3', 'Sn', 'An']
        out('    %-5s' % 'n' + ''.join('%9s' % a for a in arms))
        for n in (48, 63, 64, 65, 128):
            k = ('dig', nmf % n, mode)
            if k not in G1:
                continue
            out('    %-5d' % n + ''.join(('%9.2f' % nsof(G1, k, a)) if nsof(G1, k, a) is not None else '%9s' % '-' for a in arms))


# ---------------------------------------------------------------------------
# 5. REGIME BOUNDARIES
# ---------------------------------------------------------------------------

def stump(rows, feat, wins_high=True):
    """best threshold t on feature: predict W iff feat >= t; returns (t, errors, n)."""
    pts = sorted((r['f'][feat], r['cls']) for r in rows if r['cls'] != 'N')
    if not pts:
        return None, 0, 0
    cands = sorted(set(x for x, _ in pts)) + [float('inf')]
    best = None
    for t in cands:
        err = sum(1 for x, c in pts if (x >= t) != (c == 'W'))
        if best is None or err < best[1]:
            best = (t, err)
    return best[0], best[1], len(pts)


def boundaries():
    hdr('5. REGIME BOUNDARIES')
    out('5.1 Placement of the F1 all-mode groups by costmodel\'s rule (L = ADV/A, g = ADV/U; L* 64, g* 18.5):')
    c = collections.Counter((k[0], RF[k]['rg']) for k in G1 if k[2] == 'all')
    for cell in ('dig', 'dfa-hat', 'bounded'):
        out('  %-8s ' % cell + '  '.join('%s %d' % (rg, c[(cell, rg)]) for rg in REGIMES))
    out()
    out('5.2 W/R/N per form per regime (all-mode, this reading\'s NULL rule), with the summed delta (ns/pass):')
    out('%-3s ' % 'var' + ''.join('%-30s' % rg for rg in REGIMES))
    for arm in FORMS:
        txt = ''
        for rg in REGIMES:
            rs = [r for r in arm_rows([arm], mode='all') if r['f']['rg'] == rg]
            cc = collections.Counter(r['cls'] for r in rs)
            txt += '%-30s' % ('%d/%d/%d %+.0f' % (cc['W'], cc['R'], cc['N'], sum(r['d'] for r in rs)))
        out('%-3s %s' % (arm, txt))
    out()
    out('5.3 The measured boundary per form: the single threshold on L (calls) and on g (landings) that best')
    out('    separates wins from losses (non-NULL rows; errors / rows), all cells, then per cell:')
    out('%-3s %-8s %18s %22s %26s' % ('var', 'cell', 'win iff L >= t', 'win iff g >= t', 'win iff g >= t | L >= 64'))
    for arm in FORMS:
        for cell in ('ALL', 'dig', 'dfa-hat', 'bounded'):
            rs = [r for r in arm_rows([arm], mode='all') if cell == 'ALL' or r['key'][0] == cell]
            rs = [dict(r, f=dict(r['f'], L_=r['f']['Lact'], g_=r['f']['gu'])) for r in rs]
            tL, eL, nL = stump(rs, 'L_')
            tg, eg, ng = stump(rs, 'g_')
            rl = [r for r in rs if r['f']['Lact'] >= 64]
            tg2, eg2, ng2 = stump(rl, 'g_')
            fmt = lambda t: ('%.1f' % t) if t not in (None, float('inf')) else '-'
            out('%-3s %-8s %8s (%2d/%3d) %12s (%2d/%3d) %16s (%2d/%3d)' % (arm, cell, fmt(tL), eL, nL, fmt(tg), eg, ng, fmt(tg2), eg2, ng2))
    out()
    out('5.4 The 2-D boundary: the (L*, g*) pair minimising errors for "win iff L >= L* and g >= g*":')
    Ls = [8, 16, 24, 32, 48, 64, 96, 128, 256, 512, 1024]
    gs = [1, 2, 3, 4, 5, 6, 8, 10, 12, 16, 20, 24, 32, 48, 64, 128]
    for arm in FORMS:
        rs = [r for r in arm_rows([arm], mode='all') if r['cls'] != 'N']
        best = None
        for L in Ls:
            for g in gs:
                e = sum(1 for r in rs if ((r['f']['Lact'] >= L and r['f']['gu'] >= g) != (r['cls'] == 'W')))
                if best is None or e < best[2]:
                    best = (L, g, e)
        cm = sum(1 for r in rs if ((r['f']['Lact'] >= 64 and r['f']['gu'] >= 18.5) != (r['cls'] == 'W')))
        out('  %-3s best L* %4d g* %4d: %2d errors / %d    (costmodel 64 / 18.5: %d errors)' % (arm, best[0], best[1], best[2], len(rs), cm))
    out()
    out('5.5 Absolute cost per regime (all-mode groups, n = 64 KiB; medians over the regime\'s groups):')
    out('    walk ns per call, walk ns per MiB, and per form the median delta per call and per MiB of subject')
    out('%-7s %5s %10s %12s   ' % ('regime', 'grps', 'walk/call', 'walk/MiB') + ''.join('%28s' % a for a in ['V1', 'A1', 'A3', 'An']))
    for rg in REGIMES:
        ks = [k for k in G1 if k[2] == 'all' and RF[k]['rg'] == rg and RF[k]['n'] >= 65536 and not RF[k]['off']]
        wc = [nsof(G1, k, 'walk') / RF[k]['calls'] for k in ks]
        wm = [nsof(G1, k, 'walk') * MIB / RF[k]['n'] for k in ks]
        txt = ''
        for a in ['V1', 'A1', 'A3', 'An']:
            k2 = [k for k in ks if a in G1[k]]
            dc = [G1[k][a]['delta'] / RF[k]['calls'] for k in k2]
            dm = [G1[k][a]['delta'] * MIB / RF[k]['n'] for k in k2]
            txt += '%28s' % ('%+.1f /call %+.0f /MiB' % (med(dc), med(dm)))
        out('%-7s %5d %10.1f %12.0f   %s' % (rg, len(ks), med(wc), med(wm), txt))
    out('    (a call\'s span differs by regime, so per call and per MiB rank the regimes differently)')


# ---------------------------------------------------------------------------
# 6. THE OTHER AXES
# ---------------------------------------------------------------------------

def axes():
    hdr('6. THE OTHER AXES')
    out('6.1 Repeated vs streamed (fresh) at equal (g, L, shape): walk ns, and each form\'s delta (ns/pass).')
    out('    per-landing = (walk_S - walk_rep) / landings per buffer: the walk\'s extra cost per landing on fresh data.')
    arms = ['V1', 'A1', 'A3', 'An']
    out('  %-8s %-26s %9s %9s %8s %8s  ' % ('cell', 'subject (rep / S)', 'walk rep', 'walk S', 'S/rep', '/landing') + ''.join('%17s' % ('%s rep>S' % a) for a in arms))
    for key in G1:
        if key[2] != 'all' or not key[1].endswith('-S'):
            continue
        kr = (key[0], key[1][:-2], 'all')
        if kr not in G1:
            continue
        f = RF[key]
        wr, ws = nsof(G1, kr, 'walk'), nsof(G1, key, 'walk')
        lpb = f['landings']
        per = (ws - wr) / lpb if lpb else float('nan')
        txt = ''
        for a in arms:
            if a in G1[kr] and a in G1[key]:
                txt += '%17s' % ('%+.0f>%+.0f' % (G1[kr][a]['delta'], G1[key][a]['delta']))
            else:
                txt += '%17s' % '-'
        out('  %-8s %-26s %9.0f %9.0f %8.2f %8.2f  %s' % (key[0], kr[1][3:], wr, ws, ws / wr, per, txt))
    out()
    out('6.2 Gap shape at equal mean (dig, L = 1k): walk ns, A/A, and deltas; reg = exactly g, u = uniform,')
    out('    burst = 8 landings 2 B apart per 8g; streamed reg/burst buffers repeat their landing offsets.')
    out('  %-4s %-6s %-4s %9s %7s %8s ' % ('g', 'shape', 'reuse', 'walk', 'A/A%', 'spread%') + ''.join('%9s' % a for a in FORMS))
    for g in (8, 32):
        for sh in ('reg', 'u', 'burst'):
            for reuse in ('rep', 'S'):
                k = gkey('dig', g, 1024, shape=sh, reuse=reuse)
                if k not in G1:
                    continue
                s_ = AA1[k]
                out('  %-4d %-6s %-4s %9.0f %7.2f %8.2f ' % (g, sh, reuse, s_['ref'], 100 * s_['rel'], 100 * s_['spread'])
                    + ''.join(('%8.0f%s' % (G1[k][a]['delta'], verdict(k, a))) if a in G1[k] else '%9s' % '-' for a in FORMS))
    out()
    out('6.2b The walk\'s per-launch values on the u-shape repeated groups (the bimodality the A/A shows), ns:')
    for key in G1:
        f = RF[key]
        if key[2] == 'all' and f['shape'] == 'u' and f['reuse'] == 'rep' and AA1[key]['spread'] > 0.10 and not f['off']:
            out('  %-8s %-28s walk %s   walk#b %s' % (key[0], key[1], ' '.join('%.0f' % v for v in launch_vals(R1, key, 'walk')),
                                                     ' '.join('%.0f' % v for v in launch_vals(R1, key, 'walk#b'))))

    out()
    out('6.3 Start alignment (D6: subject placed 64-aligned + 0 / 7 / 31): ns per pass; S2/A2 = the prologue arms.')
    for nm, mode in (('g1-dig-n64k-ginf-L64k', 'first'), ('g1-dig-n65-ginf-Lnone', 'first'), ('g1-dig-n64k-g8-L1k-u', 'all')):
        out('  %s (%s)' % (nm, mode))
        for off in (0, 7, 31):
            k = ('dig', '%s@%d' % (nm, off), mode)
            if k not in G1:
                continue
            s_ = AA1[k]
            out('    off %-3d walk %10.2f (A/A %5.2f%%)  ' % (off, s_['ref'], 100 * s_['rel']) + '  '.join(
                '%s %10.2f %+8.2f%s' % (a, G1[k][a]['ns'], G1[k][a]['delta'], verdict(k, a)) for a in ('S1', 'S2', 'A1', 'A2')))
    out('  F3 (one member-free call, 64 KiB / 1 MiB): S2-S1 and A2-A1 ns per call:')
    for cell in ('f3-dig', 'f3-hex-run', 'f3-word-eq', 'f3-quad'):
        for n in ('64k', '1m'):
            k = (cell, 'g1-%s-n%s-ginf-Lnone' % (cell, n), 'first')
            g = G3[k]
            out('    %-11s %-4s S2-S1 %+8.1f  A2-A1 %+8.1f  V2-V1 %+8.1f' % (cell, n, g['S2']['ns'] - g['S1']['ns'], g['A2']['ns'] - g['A1']['ns'], g['V2']['ns'] - g['V1']['ns']))

    out()
    out('6.4 Stateless (Sn/An: every use rescans from lo, no cache) vs stateful (S1/A1, S3/A3), all-mode,')
    out('    by call span L (the dinghy spans are L <= 32): summed delta ns/pass and W/R/N over the groups at that L.')
    for L in (8, 32, 128, 1024, 65536):
        ks = [k for k in G1 if k[2] == 'all' and RF[k]['L'] == L and RF[k]['n'] >= 65536 and not RF[k]['off']]
        txt = ''
        for a in ('S1', 'S3', 'Sn', 'A1', 'A3', 'An'):
            ks2 = [k for k in ks if a in G1[k]]
            if not ks2:
                txt += '%22s' % '-'
                continue
            c = collections.Counter(verdict(k, a) for k in ks2)
            txt += '%22s' % ('%s %+8.0f %d/%d/%d' % (a, sum(G1[k][a]['delta'] for k in ks2), c['W'], c['R'], c['N']))
        out('  L=%-6d groups %2d %s' % (L, len(ks), txt))
    out('  by landing gap at L = 32 (dig, dfa-hat, bounded): An - A1 delta per pass')
    for cell in ('dig', 'dfa-hat', 'bounded'):
        txt = ''
        for g in G8:
            k = gkey(cell, g, 32)
            if k in G1 and 'An' in G1[k] and 'A1' in G1[k]:
                txt += '  g%s %+7.0f' % (g if g else 'inf', G1[k]['An']['ns'] - G1[k]['A1']['ns'])
        out('    %-8s%s' % (cell, txt))
    out('  first mode (D4/H4), An - A1 and Sn - S1 ns per call: see 4.3 (same rows).')

    out()
    out('6.5 dfa-hat (the DFA hat, 2 terms) vs the PF cells: the walk\'s own per-landing costs (2.3) and the deltas')
    out('    at equal (g, L), rep, u-shape:')
    for g in (4, 8, 16, 32, 64):
        for L in (1024,):
            kd, kh = gkey('dig', g, L), gkey('dfa-hat', g, L)
            if kd in G1 and kh in G1:
                out('  g=%-3d L=%-5d walk dig %7.0f hat %7.0f   ' % (g, L, nsof(G1, kd, 'walk'), nsof(G1, kh, 'walk')) + '  '.join(
                    '%s %+7.0f/%+7.0f' % (a, G1[kd][a]['delta'], G1[kh][a]['delta']) for a in ('V1', 'A1', 'A3')))
    out('  g=2 (reg shape) L=1k  walk dig %.0f hat %.0f   A1 %+.0f / %+.0f' % (nsof(G1, gkey('dig', 2, 1024), 'walk'), nsof(G1, gkey('dfa-hat', 2, 1024), 'walk'),
        G1[gkey('dig', 2, 1024)]['A1']['delta'], G1[gkey('dfa-hat', 2, 1024)]['A1']['delta']))

    out()
    out('6.6 F3: beta per byte by cover terms and width (section 2.1), and the SWAR term limit:')
    out('  cover terms:     1 = [0-9] (one range); 2 = [a-f0-9] (two ranges); 3 = [A-Za-z_]; 4 = [0-9A-Fa-f_]')
    for arm in ('V1', 'S1', 'A1'):
        out('  %-3s ' % arm + '  '.join('%dt %.4f (saving %+.4f)' % (t, F3[(t, arm)]['slope'], F3[(t, 'walk')]['slope'] - F3[(t, arm)]['slope']) for t in (1, 2, 3, 4)))
    out('  the dfa-hat cell\'s own 2-term cover (cube {f,n} + eq t) per byte from ginf-L64k: V1 %.4f  S1 %.4f  A1 %.4f  (walk %.4f)'
        % (BCELL[('dfa-hat', 'V1')], BCELL[('dfa-hat', 'S1')], BCELL[('dfa-hat', 'A1')], BCELL[('dfa-hat', 'walk')]))

    out()
    out('6.7 EXT (main\'s pcrec engine arms, read only to place them): rows, verdicts per cell')
    c = collections.Counter()
    for key, g in GX.items():
        for arm, r in g.items():
            if arm.endswith('#b'):
                continue
            c[(key[0], arm, verdict(key, arm, GX, RX, AAX))] += 1
    for (cell, arm, v), n in sorted(c.items()):
        out('  %-9s %-4s %s %d' % (cell, arm, v, n))


# ---------------------------------------------------------------------------
# 7. THE DECISION TABLE RE-PRICED, and the regret of each information source
# ---------------------------------------------------------------------------

LAYERS = [('off', ['walk', 'V1']), ('off+iter', ['walk', 'V1', 'V3']),
          ('on', ['walk', 'V1', 'S1', 'A1', 'Sn', 'An']),
          ('on+iter', ['walk', 'V1', 'S1', 'A1', 'Sn', 'An', 'V3', 'S3', 'A3'])]
PRIOR = {'dig': 74760, 'bounded': 663413, 'dfa-hat': 119624}     # shipped unigram prior over S (ppm; costmodel cmload)
OMEGA = {}


def omega_fit():
    """bytes a form evaluates = ADV + oc*A + ow*(U - A) (unkept, stateless) or kappa*ADV (kept): MEASURED (2.4)."""
    for arm in FORMS:
        rs = [r for r in arm_rows([arm], mode='all') if r['f']['n'] >= 65536]
        if arm in KEPT:
            OMEGA[arm] = ('kappa', float(np.median([r['c']['blocks'] * WIDTH[arm] / r['f']['ADV'] for r in rs])))
        else:
            X = np.array([[r['f']['A'], r['f']['U'] - r['f']['A']] for r in rs], float)
            Y = np.array([r['c']['blocks'] * WIDTH[arm] - r['f']['ADV'] for r in rs])
            co, *_ = np.linalg.lstsq(X, Y, rcond=None)
            OMEGA[arm] = ('omega', co)


omega_fit()


def price(cell, arm, U, A, ADV, uS, uR, fits=None):
    """the re-fitted closed form: absolute ns per pass of ARM (section 2.3's fit; bytes from 2.4)."""
    co = (fits or ABSFIT)[(cell, arm)]['co']
    U = max(U, A)
    t = co[0] * A + co[1] * (U - A) + co[2] * U * uS + co[3] * U * uR
    if arm == 'walk':
        b = ADV
    elif OMEGA[arm][0] == 'kappa':
        b = OMEGA[arm][1] * ADV
    else:
        oc, ow = OMEGA[arm][1]
        b = ADV + oc * A + ow * (U - A)
    return t + BCELL[(cell, arm)] * b


def facts_for(key, src):
    f = RF[key]
    cell = key[0]
    n = f['n']
    uS = 1.0 if (f['reuse'] == 'S' and f['shape'] == 'u' and f['g'] >= 4) else 0.0
    uR = 1.0 if (f['reuse'] == 'rep' and f['shape'] == 'u' and f['g'] >= 4) else 0.0
    p = PRIOR[cell] / 1e6
    Up = p * (1 - p) * n
    if src == 'prior':          # compile time: the unigram over S, one long call, predictable
        return dict(U=Up, A=1.0, ADV=n, uS=0.0, uR=0.0)
    if src == 'gap':            # an exemplar: landings and their shape; no call span
        return dict(U=f['U'], A=1.0, ADV=f['ADV'], uS=uS, uR=uR)
    if src == 'span':           # the call pattern / the iterator: calls, no landing facts
        return dict(U=max(Up, f['A']), A=f['A'], ADV=f['ADV'], uS=0.0, uR=0.0)
    if src == 'gap+span':       # both: the oracle facts
        return dict(U=f['U'], A=f['A'], ADV=f['ADV'], uS=uS, uR=uR)
    raise ValueError(src)


def model_pick(key, arms, src, fits=None):
    fx = facts_for(key, src)
    return min(arms, key=lambda a: price(key[0], a, fits=fits, **fx))


_LOGO = {}


def logo_fits(cell, g):
    """the absolute fits refitted without the groups of landing gap G (leave-one-g-out)."""
    if (cell, g) not in _LOGO:
        d = {}
        for a in ['walk'] + FORMS:
            f = abs_fit(cell, a, exclude_g=g)
            d[(cell, a)] = f if f else ABSFIT[(cell, a)]
        _LOGO[(cell, g)] = d
    return _LOGO[(cell, g)]


def decide():
    hdr('7. THE DECISION TABLE RE-PRICED (FORM_ROWS with the re-fitted constants), and the regret per information source')
    out('7.1 The priced rows: per cell, the closed form of section 2.3 (FITTED F, w, p, q; MEASURED beta, omega/kappa):')
    out('    price(arm) = F*A + w*(U-A) + p*U*[u-S] + q*U*[u-rep] + beta*bytes,  bytes = ADV + oc*A + ow*(U-A)  (kept: kappa*ADV)')
    out('%-8s %-5s %-9s %8s %8s %8s %8s %8s %8s %8s' % ('cell', 'arm', 'layer', 'F', 'w', 'p', 'q', 'beta', 'oc|kap', 'ow'))
    lay = {'walk': 'off', 'V1': 'off', 'V3': 'off+iter', 'S1': 'on', 'A1': 'on', 'Sn': 'on', 'An': 'on', 'S3': 'on+iter', 'A3': 'on+iter'}
    for cell in ('dig', 'bounded', 'dfa-hat'):
        for arm in ['walk', 'V1', 'V3', 'S1', 'A1', 'Sn', 'An', 'S3', 'A3']:
            co = ABSFIT[(cell, arm)]['co']
            om = OMEGA.get(arm)
            o1 = '-' if om is None else ('%.3f' % om[1] if om[0] == 'kappa' else '%.1f' % om[1][0])
            o2 = '-' if om is None or om[0] == 'kappa' else '%.2f' % om[1][1]
            out('%-8s %-5s %-9s %8.2f %8.2f %8.2f %8.2f %8.4f %8s %8s' % (cell, arm, lay[arm], co[0], co[1], co[2], co[3], BCELL[(cell, arm)], o1, o2))

    keys = [k for k in G1 if k[2] == 'all' and not RF[k]['off'] and all(a in G1[k] or a == 'walk' for a in LAYERS[-1][1])]
    out()
    out('7.2 Regret = measured ns of a policy\'s pick - measured ns of the fastest row the layer offers, summed over the')
    out('    regime\'s groups (all-mode groups timing all nine forms: %d; regime by costmodel\'s rule).' % len(keys))
    out('    Given as absolute us per pass summed (and % of the walk\'s summed ns).  The model rows are IN SAMPLE')
    out('    (their constants are fitted on these groups) except LOGO: refitted without the row\'s landing gap g.  Sources:')
    out('      prior    = compile time: the shipped unigram over S, landings p(1-p), one long call, predictable gaps')
    out('      gap      = an exemplar: true landings and gap shape, no call span (A = 1)')
    out('      span     = the call pattern / iterator: true calls, landings from the prior')
    out('      gap+span = both (the model with oracle facts)')
    out('      hint     = the regime is known: the one row best over that regime\'s groups (in sample; LOCO = learned on the other cells)')
    walk_sum = collections.Counter()
    for k in keys:
        walk_sum[RF[k]['rg']] += nsof(G1, k, 'walk')
    for lname, arms in LAYERS:
        out()
        out('  layer %s (rows: %s)' % (lname, ', '.join(arms)))
        out('  %-22s ' % 'policy' + ''.join('%26s' % rg for rg in REGIMES))
        best = {k: min(nsof(G1, k, a) for a in arms) for k in keys}

        def show(name, pick):
            txt = ''
            for rg in REGIMES:
                ks = [k for k in keys if RF[k]['rg'] == rg]
                reg = sum(nsof(G1, k, pick(k)) - best[k] for k in ks)
                txt += '%26s' % ('%9.1f us (%5.1f%%)' % (reg / 1000, 100 * reg / walk_sum[rg]))
            out('  %-22s %s' % (name, txt))
        for a in arms:
            show('always ' + a, lambda k, a=a: a)
        for src in ('prior', 'gap', 'span', 'gap+span'):
            show('model, ' + src, lambda k, src=src: model_pick(k, arms, src))
        show('model, gap+span, LOGO', lambda k: model_pick(k, arms, 'gap+span', logo_fits(k[0], RF[k]['g'])))
        # regime hint: one row per regime
        hint = {}
        for rg in REGIMES:
            ks = [k for k in keys if RF[k]['rg'] == rg]
            hint[rg] = min(arms, key=lambda a: sum(nsof(G1, k, a) for k in ks))
        show('hint ' + '/'.join(hint[rg] for rg in REGIMES), lambda k: hint[RF[k]['rg']])

        def loco(k):
            ks = [j for j in keys if RF[j]['rg'] == RF[k]['rg'] and j[0] != k[0]]
            return min(arms, key=lambda a: sum(nsof(G1, j, a) for j in ks)) if ks else hint[RF[k]['rg']]
        show('hint, LOCO by cell', loco)
        # agreement of the oracle-facts argmin with the measured best
        ag = collections.Counter()
        for k in keys:
            mb = min(arms, key=lambda a: nsof(G1, k, a))
            ag[(RF[k]['rg'], model_pick(k, arms, 'gap+span') == mb)] += 1
        out('  %-22s ' % 'model==measured best' + ''.join('%26s' % ('%d/%d' % (ag[(rg, True)], ag[(rg, True)] + ag[(rg, False)])) for rg in REGIMES))
    out()
    out('  summed walk ns per regime over these groups: ' + '  '.join('%s %.1f us' % (rg, walk_sum[rg] / 1000) for rg in REGIMES))

# @@SECTIONS@@

if __name__ == '__main__':
    noise()
    refit()
    oos()
    crossovers()
    boundaries()
    axes()
    decide()
