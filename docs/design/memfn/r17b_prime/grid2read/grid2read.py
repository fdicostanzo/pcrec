#!/usr/bin/env python3
"""grid2read: the READING of the zen4-grid2 timing slot (lane grid2read, 2026-10-16).

ANALYSIS ONLY: no timing, no build, no `make`.  Every ns is read from the finished slot
(worktrees/memfn-slot/grid2/, method kit-grid@2, Zen 4 7700X, CPU 14, compiler = lane/memfn-r17
c90d65e53, abi 77).  Run:

    python3 -I grid2read.py [--check] [OUT] > analysis.txt        (writes keys.tsv beside this file)

`--check` verifies SHA256SUMS (the inputs read) first and stops on a mismatch.  The report
(docs/dev/lanes/grid2read_report.md) cites sections of analysis.txt as "an. N.M".

Labels: MEASURED (read from a row or a counter), FITTED (least squares / interpolation),
DERIVED (arithmetic on measured values), INTERPRETATION (mine).

The NULL rule (gridread's, regime-split): a delta is NULL when |delta| <= max(the group's own A/A
floor, FRG[regime] x base) or when the launch-paired deltas do not all share the sign of the median
delta.  The group's A/A floor is max(|base#b - base|, |base#c - base|) (both copies; time.sh prints
only #b).  FRG[regime] is that regime's own p90 of the A/A (section 3).
"""
import collections, math, os, sys, time

os.environ['TZ'] = 'America/New_York'          # the slot's local time (EDT); the window is stated in it
time.tzset()
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import numpy as np                              # noqa: E402
from grload2 import *                           # noqa: E402,F401
import grload2 as gl                            # noqa: E402

ARGS = [a for a in sys.argv[1:] if not a.startswith('--')]
OUT = ARGS[0] if ARGS else '/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid2'

if '--sums' in sys.argv:
    with open(os.path.join(HERE, 'SHA256SUMS'), 'w') as f:
        for p_ in gl.INPUTS:
            f.write('%s  %s\n' % (gl.sha256(os.path.join(OUT, p_)), p_))
    print('wrote SHA256SUMS: %d inputs' % len(gl.INPUTS))
    sys.exit(0)

if '--check' in sys.argv:
    bad = 0
    for ln in open(os.path.join(HERE, 'SHA256SUMS')):
        h, p = ln.split(None, 1)
        p = p.strip()
        got = gl.sha256(os.path.join(OUT, p))
        if got != h:
            print('MISMATCH', p)
            bad += 1
    print('check: %d inputs, %d mismatched' % (sum(1 for _ in open(os.path.join(HERE, 'SHA256SUMS'))), bad))
    sys.exit(1 if bad else 0)


def out(*a):
    print(*a)


def hdr(t):
    out()
    out('=' * 100)
    out(t)
    out('=' * 100)


KEYS = []            # rows of keys.tsv: (key, unit, value_e6, abs_ns_e6, status, regime, layer, floor, source)


def key(k, unit, val, ab, status, regime, layer, floor, src):
    KEYS.append((k, unit, val, ab, status, regime, layer, floor, src))


def e6(x):
    return int(round(x * 1e6))


# ------------------------------------------------------------------------------------------
# load
# ------------------------------------------------------------------------------------------
PH = ['F1', 'F3', 'OB', 'TRIG']
VIS = {p: visits('%s/time/raw_%s.tsv' % (OUT, p), p) for p in PH}
BYKEY = {p: collections.defaultdict(list) for p in PH}
for p in PH:
    for v in VIS[p]:
        BYKEY[p][v.key].append(v)
ALL = [v for p in PH for v in VIS[p]]
CNT = load_counts('%s/counts.tsv' % OUT)
FACT = load_facts('%s/subj_facts.tsv' % OUT)


def vis(p, cell, subj, mode):
    """the CHOSEN visit of a group: the last visit that does not overlap the contamination window
    (a requeue's clean visit replaces the contaminated first one)."""
    c = [v for v in BYKEY[p].get((cell, subj, mode), []) if not v.overlap]
    return c[-1] if c else None


def base(v):
    return base_of(v)


def ns(v, arm):
    return v.med(arm)


def aa(v):
    """(|b - base|, |c - base|) in ns."""
    b = base(v)
    return abs(v.med(b + '#b') - v.med(b)), abs(v.med(b + '#c') - v.med(b))


def floor(v):
    return max(aa(v))


def paired_sign(v, arm):
    """True iff arm - base has the sign of the median delta in every launch."""
    b = base(v)
    rs = sorted(set(v.arm_vals[arm]) & set(v.arm_vals[b]))
    d = [v.arm_vals[arm][r] - v.arm_vals[b][r] for r in rs]
    md = ns(v, arm) - ns(v, b)
    return all(x > 0 for x in d) if md > 0 else all(x < 0 for x in d)


FRG = {}              # regime -> fraction (filled in section 3)


def verdict(v, arm, regime):
    """W (arm faster), R (slower), N (NULL), under the regime-split NULL rule."""
    b = base(v)
    d = ns(v, arm) - ns(v, b)
    thr = max(floor(v), FRG.get(regime, 0.0) * ns(v, b))
    if abs(d) <= thr or not paired_sign(v, arm):
        return 'N'
    return 'W' if d < 0 else 'R'


def regime_of(v):
    if v.phase == 'F3':
        return 'slope'
    if v.phase == 'F1':
        return 'findall' if v.key[2] == 'all' else 'short'
    if v.phase == 'OB':
        return 'ob_all' if v.key[2] == 'all' else 'ob_first'
    return 'trig'


def pct(x):
    return '%.3f%%' % (100 * x)


def pctl(a, q):
    return float(np.percentile(np.array(a), q))


# ------------------------------------------------------------------------------------------
# 1. provenance, gates, phases
# ------------------------------------------------------------------------------------------
def provenance():
    hdr('1. PROVENANCE AND GATES (MEASURED: slot.status, provenance.txt, check.log)')
    st = open('%s/slot.status' % OUT).read().splitlines()
    for ln in st:
        if ln.split(' ', 1)[0] in ('SLOT_START', 'COMPILER', 'BUILD', 'CHECK', 'CHECK_OK', 'QUIET', 'COUNTS',
                                   'ESTIMATE', 'WALL', 'COMPLETE') or ' time.sh: COMPLETE' in ln \
                or ln.split(' ', 1)[0] in ('F1', 'F3', 'OB', 'F2', 'F2S', 'TRIG') or ln.startswith('F2_DONE') \
                or ln.startswith('F2S_') and 'END' in ln:
            out(ln)
    out()
    prov = dict(l.split('=', 1) for l in open('%s/provenance.txt' % OUT).read().splitlines() if '=' in l)
    for k in ('compiler_commit', 'compiler_branch', 'compiler_abi', 'compiler_sha256', 'compiler_mtime',
              'compiler_inputs_dirty_files', 'compiler_pf_terms_mask_deny', 'grid2_commit',
              'grid2_harness_dirty_files', 'gcc'):
        out('  %-30s %s' % (k, prov.get(k, '?')))
    out('  prov.status: %s ; census.status: %s ; check2.status: %s'
        % (open('%s/prov.status' % OUT).read().strip().replace('\n', ' | '),
           open('%s/census.status' % OUT).read().strip(),
           open('%s/check2.status' % OUT).read().strip().replace('\n', ' | ')))
    out('  prov.out: %s' % open('%s/prov.out' % OUT).read().strip())
    mm = 0
    for p in PH:
        for ln in open('%s/time_%s.log' % (OUT, p)):
            if 'ANSWER MISMATCH' in ln:
                mm += 1
    out('  ANSWER MISMATCH lines in the four time logs: %d' % mm)
    amb = sum(1 for v in ALL for a in v.answers if len(v.answers[a]) != 1)
    diff = 0
    for v in ALL:
        b = base(v)
        s = {frozenset(v.answers[a]) for a in v.arm_vals}
        # arms of one group print one answer line each (the harness compares them to the base)
        if len(s) != 1:
            diff += 1
    out('  arm-launches whose answer line is not unique within the arm: %d; groups whose arms printed different answers: %d'
        % (amb, diff))
    out()
    out('Phases (visits = groups timed, a requeue is a second visit of one key):')
    out('%-5s %7s %8s %8s %9s %6s' % ('phase', 'visits', 'keys', 'rows', 'rerun-rd', 'reqd'))
    for p in PH:
        n_rows = sum(len(v.rows) for v in VIS[p])
        rer = sum(1 for v in VIS[p] if v.launches > 3)
        rq = sum(1 for k, vl in BYKEY[p].items() if len(vl) > 1)
        out('%-5s %7d %8d %8d %9d %6d' % (p, len(VIS[p]), len(BYKEY[p]), n_rows, rer, rq))
    out('  all: %d visits, %d raw launch rows' % (len(ALL), sum(len(v.rows) for v in ALL)))


# ------------------------------------------------------------------------------------------
# 2. contamination, loads
# ------------------------------------------------------------------------------------------
def contamination():
    hdr('2. CONTAMINATION WINDOW AND LOAD ACCOUNTING')
    out('The binding window: 2026-10-16 %s .. %s EDT (epoch %.0f .. %.0f).  A launch is stamped AFTER it ends and lasts'
        % (hms(WIN[0]), hms(WIN[1]), WIN[0], WIN[1]))
    out('<= ~0.95 s, so it overlaps iff stamp >= window start and stamp - 1.0 s <= window end.')
    out()
    out('2.1 Visits overlapping the window (every phase):')
    ov = [v for v in ALL if v.overlap]
    for v in ov:
        out('  %s %s %s visit %d  %s..%s  %d launch rows (%d launches x %d arms), %d in the window, load1 max %.2f, %d rows load1>1.5'
            % (v.phase, v.key[0], v.key[1], v.vid, hms(v.t0), hms(v.t1), len(v.rows), v.launches, len(v.arm_vals),
               v.n_in_win, v.loadmax, v.n_load_hi))
    out('  COUNT: %d group visit(s), %d launch rows of %d (%.2f%%); F1 last launch ended %s (%.1f s before the window), F3 first launch %s'
        % (len(ov), sum(len(v.rows) for v in ov), sum(len(v.rows) for v in ALL),
           100.0 * sum(len(v.rows) for v in ov) / sum(len(v.rows) for v in ALL),
           hms(max(r['ts'] for r in VIS['F1'][-1].rows)), WIN[0] - max(r['ts'] for r in VIS['F1'][-1].rows),
           hms(min(r['ts'] for r in VIS['F3'][0].rows))))
    out('  The window is 79 s; the F3 phase ran %s..%s.  Only the FIRST F3 group (f3-dig n64k) was inside it: the harness'
        % (hms(VIS['F3'][0].t0), hms(VIS['F3'][-1].t1)))
    out('  saw its end load1 reach 3.12 (>= LOADBREACH 3.0), re-queued it ("BREACH(requeue)") and timed it again at the end of the phase.')
    out('  After it the harness waited 10 x 20 s for load1 < 1.5 before group 2 (time_F3.log line 16), so no later group started in the window.')
    c1 = [v for v in BYKEY['F3'][('f3-dig', 'g2-f3-dig-n64k-ginf-Lnone-S', 'first')]]
    out()
    out('2.2 The contaminated visit against its clean re-queue (median ns over launches; MEASURED):')
    bad, good = c1[0], c1[-1]
    out('  visit 1 (launches=%d, load1 max %.2f) vs visit %d (launches=%d, load1 max %.2f, %s..%s)'
        % (bad.launches, bad.loadmax, good.vid, good.launches, good.loadmax, hms(good.t0), hms(good.t1)))
    out('  %-8s %10s %10s %8s   %s' % ('arm', 'contam', 'clean', 'ratio', 'per-launch (contam)'))
    for a in ['walk', 'walk#b', 'walk#c', 'V1', 'S1', 'A1', 'tw0', 'tw1', 'tw2']:
        pv = [bad.arm_vals[a][r] for r in sorted(bad.arm_vals[a])]
        out('  %-8s %10.1f %10.1f %8.3f   %s' % (a, bad.med(a), good.med(a), bad.med(a) / good.med(a),
                                                   ' '.join('%.0f' % x for x in pv)))
    out('  The contaminated visit\'s A/A (walk#b, walk#c vs walk) reads %.2f%% / %.2f%%; the clean one %.2f%% / %.2f%%.'
        % (100 * aa(bad)[0] / bad.med('walk'), 100 * aa(bad)[1] / bad.med('walk'),
           100 * aa(good)[0] / good.med('walk'), 100 * aa(good)[1] / good.med('walk')))
    out('  time_F3.log prints BOTH tables for this group (the contaminated one at group 1, the clean one under "# requeue"):')
    out('  a reader that takes the first occurrence of the key reads the contaminated numbers.  This reading uses visit %d only.' % good.vid)
    out()
    out('2.3 Load1 per phase (MEASURED, every launch row; the timed process itself is one runnable task, so the quiet baseline is 1.0):')
    out('%-5s %7s %6s %7s %6s %7s %7s' % ('phase', 'rows', 'min', 'median', 'max', '>1.5', '>1.3'))
    for p in PH:
        L = [r['load'] for v in VIS[p] for r in v.rows]
        out('%-5s %7d %6.2f %7.2f %6.2f %7d %7d' % (p, len(L), min(L), pctl(L, 50), max(L), sum(x > 1.5 for x in L), sum(x > 1.3 for x in L)))
    out()
    out('2.4 Visits that breached the harness\'s own LOADMAX (1.5) at any launch, OUTSIDE the stated window'
        ' (the gate is checked at group start only, and a BREACH is logged only at end-load >= 3.0):')
    ls = [v for v in ALL if v.n_load_hi and not v.overlap]
    for v in ls:
        ld = collections.OrderedDict()
        for r in v.rows:
            ld[r['rnd']] = max(ld.get(r['rnd'], 0), r['load'])
        b = base(v)
        out('  %s %s %s: %s..%s  rows>1.5: %d of %d, load1 by launch %s, launches=%d, A/A %.2f%% / %.2f%% of base'
            % (v.phase, v.key[0], v.key[1], hms(v.t0), hms(v.t1), v.n_load_hi, len(v.rows),
               ['%.2f' % ld[k] for k in sorted(ld)], v.launches, 100 * aa(v)[0] / v.med(b), 100 * aa(v)[1] / v.med(b)))
    out('  (none in OB or TRIG; the harness logged none of these: its only load lines are "quiet gate waited" and BREACH.)')
    out()
    out('2.4a What the harness itself logged (the "# group N done" and "# quiet gate" lines of time_*.log; the gate is evaluated at group START only):')
    out('%-5s %7s %9s %9s %9s %8s %8s' % ('phase', 'groups', 'start max', 'end max', 'waited>0', 'BREACH', 'requeue'))
    for p_ in PH:
        st, en, wt, br, rq = [], [], 0, 0, 0
        for ln in open('%s/time_%s.log' % (OUT, p_)):
            if ln.startswith('# group'):
                m = re.search(r'load1-at-start=([\d.]+) load1-at-end=([\d.]+) waits=(\d+)', ln)
                st.append(float(m.group(1)))
                en.append(float(m.group(2)))
                wt += int(m.group(3)) > 0
                br += 'BREACH' in ln
            if ln.startswith('# requeue'):
                rq += 1
        out('%-5s %7d %9.2f %9.2f %9d %8d %8d' % (p_, len(st), max(st), max(en), wt, br, rq))
    out('  F1: start load1 max 1.43 (< 1.5), no wait, no BREACH: the harness logged NO violation in F1.  Its raw rows nevertheless show one group (above) at load1 1.70 mid-group,')
    out("  which the group-start gate cannot see and the log does not mention.  The one-minute load average lags, so a row's load1 bounds a disturbance only loosely (an. 2.5).")
    ob = max(VIS['OB'][-1].rows, key=lambda r: r['ts'])
    tg = min(VIS['TRIG'][0].rows, key=lambda r: r['ts'])
    out()
    out('2.4b F2 / F2S (the optional perf passes, 20:01:47..20:04:27): f2perf.sh has NO quiet gate and writes NO load or timestamp column; the harness logged no violation because it records none.')
    out('  Bracketing readings: the last OB launch ended %s with load1 %.2f; the first TRIG launch ended %s with load1 %.2f.  Both are quiet (baseline 1.0 + <= 0.23).' % (hms(ob['ts']), ob['load'], hms(tg['ts']), tg['load']))
    out('  F2 is user-space COUNTS of one pinned process (instructions, branches, branch misses are load-invariant to first order; cycles:u is not strictly): used as a diagnosis only, never as a timed verdict.')
    out()
    out('2.5 What each load-suspect visit looks like against a clean twin (MEASURED; the clean twin has the same arms'
        ' in a quiet visit):')
    def cmp(v, twin, arms):
        for a in arms:
            if a in v.arm_vals and a in twin.arm_vals:
                out('    %-6s suspect %10.1f   twin %10.1f   ratio %.3f   per-launch %s'
                    % (a, v.med(a), twin.med(a), v.med(a) / twin.med(a),
                       ' '.join('%.0f' % v.arm_vals[a][r] for r in sorted(v.arm_vals[a]))))
    v = vis('F3', 'f3-word-eq', 'g2-f3-word-eq-n1m-ginf-Lnone-S', 'first')
    t = vis('F3', 'f3-quad', 'g2-f3-quad-n1m-ginf-Lnone-S', 'first')
    out('  f3-word-eq n1m (walk has the same beta at any term count, so f3-quad n1m is the twin for the walk arms):')
    cmp(v, t, ['walk', 'walk#b', 'walk#c', 'sc0'])
    out('    walk by launch: %s  (launch 1 load1 %.2f, quiet)' % (' '.join('%.0f' % v.arm_vals['walk'][r] for r in sorted(v.arm_vals['walk'])),
                                                                max(r['load'] for r in v.rows if r['rnd'] == 1)))
    v1 = vis('F3', 'f3-word-eq', 'g2-f3-word-eq-n1m-ginf-Lnone-S', 'first')
    tq = vis('F3', 'f3-quad', 'g2-f3-quad-n1m-ginf-Lnone-S', 'first')
    out('  word-eq n1m LAUNCH 1 in launch order (load1 is a lagging 1-minute average: it read 1.04 on every row of this launch and 2.07 on the next,')
    out('  so a low load1 on a row does NOT prove the row quiet).  ns against the quiet twin of the same arm family:')
    r1 = sorted([r for r in v1.rows if r['rnd'] == 1], key=lambda r: r['pos'])
    for r in r1:
        a = r['arm']
        tw = ''
        if a in ('walk', 'walk#b', 'walk#c', 'tw0', 'sc0'):
            ref = tq.med('walk') if a in ('walk', 'walk#b', 'walk#c', 'sc0') else tq.med('tw0')
            tw = '  vs quiet walk-family %.0f: %.3f' % (ref, r['ns'] / ref)
        out('    pos %d %-7s %10.1f  load1 %.2f  t+%.1fs%s' % (r['pos'], a, r['ns'], r['load'], r['ts'] - r1[0]['ts'], tw))
    out('  walk/walk#b/walk#c/V1/S1 (pos 0-4) are at the quiet level (V1 and S1 slopes within 0.4% of grid1, section 4); A1, tw0 and sc0 (pos 5-9) read +5..+9%:')
    out('  the disturbance began between S1 and A1 inside launch 1.  Launch 1 is therefore used for walk/V1/S1 only.')
    v = vis('F3', 'f3-quad', 'g2-f3-quad-n64k-ginf-Lnone-S', 'first')
    t = vis('F3', 'f3-word-eq', 'g2-f3-word-eq-n64k-ginf-Lnone-S', 'first')
    out('  f3-quad n64k (twin for the walk arms: f3-word-eq n64k, quiet):')
    cmp(v, t, ['walk', 'walk#b', 'walk#c', 'sc0'])
    v = vis('F1', 'dig', 'g2-dig-n64k-g8-L1k-u-S@7', 'all')
    t = vis('F1', 'dig', 'g2-dig-n64k-g8-L1k-u-S@0', 'all')
    out('  F1 dig g8 L1k u @7 (twin: the same subject at offset @0 and @31, quiet):')
    cmp(v, t, ['walk', 'walk#b', 'walk#c', 'V1', 'S1', 'A1', 'A3'])


# ------------------------------------------------------------------------------------------
# 3. noise, the NULL rule, the eps tokens
# ------------------------------------------------------------------------------------------
import re                                       # noqa: E402


def subj_L(name):
    m = re.search(r'-L(\w+?)-', name)
    return m.group(1) if m else ''


GRID1 = dict(eps_slope=0.00173, eps_findall=0.03365, eps_ext=0.00382, frg=0.0309,
             beta_walk=0.1892,
             beta=dict(  # fdb2 generate.py BETA (gridread_report §2.1), by shape (range, eq, cube)
                 WALK={(1, 0, 0): .1892, (2, 0, 0): .1877, (2, 0, 1): .1896, (3, 1, 0): .1891, (0, 1, 1): .1877},
                 V1={(1, 0, 0): .1082, (2, 0, 0): .1851, (2, 0, 1): .2141, (3, 1, 0): .2667, (0, 1, 1): .1384},
                 S1={(1, 0, 0): .0205, (2, 0, 0): .0334, (2, 0, 1): .0417, (3, 1, 0): .0540, (0, 1, 1): .0212},
                 A1={(1, 0, 0): .0106, (2, 0, 0): .0150, (2, 0, 1): .0192, (3, 1, 0): .0270, (0, 1, 1): .0107}),
             F=dict(walk=4.74, V1=4.18, S1=4.70, A1=4.98), F48=dict(walk=4.84, V1=4.17, S1=24.54, A1=14.73),
             ccold=dict(V1=2.47, S1=2.90, A1=2.91), wuse=dict(walk=1.67, V1=2.38, S1=2.22, A1=2.23))
SHAPE = {'f3-dig': (1, 0, 0), 'f3-hex-run': (2, 0, 0), 'f3-word-eq': (2, 0, 1), 'f3-quad': (3, 1, 0),
         'f3-wcls': (3, 0, 1), 'f3-c020': (0, 2, 0), 'f3-c001': (0, 0, 1), 'f3-c110': (1, 1, 0)}


def aa_rels(v):
    b = base(v)
    m = v.med(b)
    return abs(v.med(b + '#b') - m) / m, abs(v.med(b + '#c') - m) / m


def noise():
    hdr('3. NOISE, THE NULL RULE AND THE eps TOKENS (MEASURED)')
    R = collections.defaultdict(list)
    for v in ALL:
        if v.overlap or v.n_load_hi:
            continue
        rb, rc = aa_rels(v)
        reg = regime_of(v)
        R[reg].append((rb, rc, v))
        if reg == 'findall':
            R['findall_L64k' if subj_L(v.key[1]) == '64k' else 'findall_L<=1k'].append((rb, rc, v))
        if reg == 'slope':
            pass
    out('Visits excluded from every statistic here: %d overlapping the window, %d load-suspect (section 2).'
        % (sum(v.overlap for v in ALL), sum(1 for v in ALL if v.n_load_hi and not v.overlap)))
    out()
    out('A/A = |median(copy) - median(base)| / median(base), copies #b and #c (the harness prints #b only; #c is held out of NULL).')
    out('%-14s %5s | %-26s | %-26s | %-26s' % ('regime', 'n', '#b: med / p90 / max %', '#c: med / p90 / max %', 'both pooled: p90 %'))
    for reg in ['slope', 'findall', 'findall_L64k', 'findall_L<=1k', 'short', 'ob_first', 'ob_all', 'trig']:
        L = R.get(reg, [])
        if not L:
            continue
        b = [x[0] for x in L]
        c = [x[1] for x in L]
        pool = b + c
        out('%-14s %5d | %7.3f %7.3f %9.2f | %7.3f %7.3f %9.2f | %7.3f' % (
            reg, len(L), 100 * pctl(b, 50), 100 * pctl(b, 90), 100 * max(b), 100 * pctl(c, 50), 100 * pctl(c, 90), 100 * max(c),
            100 * pctl(pool, 90)))
        if reg in ('slope', 'findall', 'short', 'ob_first', 'ob_all', 'trig'):
            FRG[reg] = pctl(pool, 90)
    out()
    out('grid1 (gridread): F3 p90 0.173% (kit.eps.streamed.slope), F1 p90 3.365% (kit.eps.findall.l64k), pooled FRG 3.09%, EXT 0.382%.')
    s = pctl([x[0] for x in R['slope']], 90)
    f = pctl([x[0] for x in R['findall']], 90)
    out('grid2 #b-only p90 (the grid1 definition): slope %.3f%% (grid1 0.173%%), findall %.3f%% (grid1 3.365%%).' % (100 * s, 100 * f))
    out('FRG used by the NULL rule below = the pooled (#b and #c) p90 of the regime: ' +
        ', '.join('%s %.3f%%' % (k, 100 * v) for k, v in FRG.items()))
    key('kit.eps.streamed.slope', 'ratio', e6(s), '-', 'measured', 'streamed member-free single calls (F3, n64k/1m)', 'all', 0, 'grid2read an. 3 (F3 A/A #b p90, n=%d)' % len(R['slope']))
    key('kit.eps.findall.l64k', 'ratio', e6(f), '-', 'measured', 'streamed find-all (F1 all-mode, the grid1 definition: all L)', 'all', 0, 'grid2read an. 3 (F1 A/A #b p90, n=%d)' % len(R['findall']))
    key('kit.eps.streamed.short', 'ratio', e6(pctl([x[0] for x in R['short']], 90)), '-', 'measured', 'streamed first-mode short calls n<=128 (F1)', 'all', 0, 'grid2read an. 3 (n=%d)' % len(R['short']))
    out()
    out('Per-launch spread of the base (max-min over launches, as % of the median):')
    for reg in ['slope', 'findall', 'short', 'ob_first', 'ob_all', 'trig']:
        sp = []
        for x in R.get(reg, []):
            v = x[2]
            b = base(v)
            vals = list(v.arm_vals[b].values())
            sp.append((max(vals) - min(vals)) / hmed(vals))
        if sp:
            out('  %-9s n %3d  median %.3f%%  p90 %.3f%%  max %.2f%%   groups > 5%%: %d' % (reg, len(sp), 100 * pctl(sp, 50), 100 * pctl(sp, 90), 100 * max(sp), sum(x > 0.05 for x in sp)))
    out()
    out('Rerun accounting (time.sh\'s pre-registered rules, from the logs):')
    for p in PH:
        tot = reruns = xr = 0
        for ln in open('%s/time_%s.log' % (OUT, p)):
            if ln.startswith('# rerun:'):
                reruns += 1
                if re.search(r'cross-launch spread of \S+ beyond max\(A/A floor, NULL\)=\S+: 1', ln):
                    xr += 1
        done = open('%s/time_%s.log' % (OUT, p)).read().splitlines()[-1]
        out('  %-4s %s' % (p, done))
    out('  F1 groups reran: %d of %d (%.0f%%); the cross-launch trigger fired in %d of them.' % (
        sum(1 for v in VIS['F1'] if v.launches > 3), len(VIS['F1']), 100.0 * sum(1 for v in VIS['F1'] if v.launches > 3) / len(VIS['F1']),
        28))


# ------------------------------------------------------------------------------------------
# 4. beta (M1-M5, M19/M20 slopes), the unit, the shape table, R0 / R7
# ------------------------------------------------------------------------------------------
D1M = 1048576 - 65536
BETA = {}            # (cell, arm) -> dict(beta, note)
UNIT = [None]


def f3pair(cell, flags=False):
    a = vis('F3', cell, 'g2-%s-n64k-ginf-Lnone-S' % cell, 'first')
    b = vis('F3', cell, 'g2-%s-n1m-ginf-Lnone-S' % cell, 'first')
    return a, b


def beta_table():
    hdr('4. beta PER BYTE, THE UNIT u, THE SHAPE TABLE (M1-M5; F3 member-free single calls, slope n64k -> n1m)')
    out('beta = (T(1 MiB) - T(64 KiB)) / (1 MiB - 64 KiB), T the median ns over launches of one single call on a distinct streamed')
    out('buffer; a copy\'s beta (walk#b, walk#c) is the A/A of the SLOPE.  Quiet visits only, except where a LOAD-SUSPECT visit is the')
    out('only source (marked; the restriction used is stated).')
    arms = ['walk', 'walk#b', 'walk#c', 'V1', 'S1', 'A1', 'tw0', 'tw1', 'tw2', 'sc0']
    cells = list(SHAPE)
    sus = {}
    for cell in cells:
        a, b = f3pair(cell)
        row = {}
        rounds_a = rounds_b = None
        note = ''
        # restrictions for the two load-suspect visits (section 2.5): word-eq n1m -> launch 1 (load1 1.04, quiet);
        # quad n64k -> launches 3-5 (A/A 0.08%/0.42%, the walk stable to 0.1%)
        if b.n_load_hi and cell == 'f3-word-eq':
            rounds_b = [1]
            note = 'word-eq n1m: LOAD-SUSPECT visit, launch 1 only; arms timed after the onset (A1, tw*, sc0) dropped'
        if a.n_load_hi and cell == 'f3-quad':
            rounds_a = [3, 4, 5]
            note = 'quad n64k: LOAD-SUSPECT visit, launches 3-5 only (A/A 0.08%)'
        for arm in arms:
            if arm not in a.arm_vals or arm not in b.arm_vals:
                continue
            if cell == 'f3-word-eq' and arm in ('A1', 'tw0', 'tw1', 'tw2', 'sc0'):
                continue            # launch 1 of the suspect visit: these arms ran after the disturbance began (section 2.5)
            ta = hmed([a.arm_vals[arm][r] for r in (rounds_a or a.arm_vals[arm])])
            tb = hmed([b.arm_vals[arm][r] for r in (rounds_b or b.arm_vals[arm])])
            row[arm] = (tb - ta) / D1M
            row[arm + '@64k'] = ta
            row[arm + '@1m'] = tb
        BETA[cell] = row
        sus[cell] = note
    UNIT[0] = BETA['f3-dig']['walk']
    u = UNIT[0]
    out('u = beta_walk(f3-dig) = %.4f ns/B  (grid1 0.1892)   walk#b %.4f  walk#c %.4f' % (u, BETA['f3-dig']['walk#b'], BETA['f3-dig']['walk#c']))
    out()
    out('%-11s %-7s %7s %7s %7s | %7s %7s %7s %7s | %7s %7s %7s %7s' % ('cell', 'shape', 'walk', 'wk#b', 'wk#c', 'V1', 'S1', 'A1', 'sc0', 'sV1', 'sS1', 'sA1', 'tw1/V1'))
    for cell in cells:
        r = BETA[cell]
        w = r['walk']
        f = lambda a: ('%7.4f' % r[a]) if a in r else '      -'
        sv = lambda a: ('%+7.3f' % (1 - r[a] / w)) if a in r else '      -'
        tw = ('%7.3f' % (r['tw1'] / r['V1'])) if 'tw1' in r and 'V1' in r else '      -'
        out('%-11s %-7s %7.4f %7.4f %7.4f | %s %s %s %s | %s %s %s %s%s' % (cell, SHAPE[cell], w, r['walk#b'], r['walk#c'], f('V1'), f('S1'), f('A1'), f('sc0'),
                                                                         sv('V1'), sv('S1'), sv('A1'), tw, ('   <- ' + sus[cell]) if sus[cell] else ''))
    out('(sX = saving = 1 - beta_X / beta_walk of the same cell; positive = X faster per byte.)')
    out()
    out('Slope A/A (the relative disagreement of the walk copies\' slopes, per cell) and the saving\'s own uncertainty:')
    EPSB = {}
    for cell in cells:
        r = BETA[cell]
        e = max(abs(r['walk#b'] - r['walk']), abs(r['walk#c'] - r['walk'])) / r['walk']
        EPSB[cell] = e
        out('  %-11s slope A/A %.3f%%' % (cell, 100 * e))
    out('  pooled over the %d cells: p90 %.3f%%, max %.3f%%  (kit.eps.streamed.slope is the per-call-group A/A p90 of section 3; this is the' % (len(cells), 100 * pctl(list(EPSB.values()), 90), 100 * max(EPSB.values())))
    out('  slope-based figure, which is the noise of the quantity the saving keys are actually derived from)')
    key('kit.eps.beta.slope', 'ratio', e6(pctl(list(EPSB.values()), 90)), '-', 'measured', 'streamed beta slope (copies b/c vs base, p90 over F3 cells)', 'all', 0, 'grid2read an. 4 (a candidate token; the design spells only kit.eps.streamed.slope)')
    out()
    out('Against grid1 (fdb2 generate.py BETA, gridread_report §2.1), by shape [relative to u]:')
    out('%-9s %-11s %-8s %9s %9s %8s' % ('arm', 'cell', 'shape', 'grid2', 'grid1', 'ratio'))
    for arm in ('V1', 'S1', 'A1'):
        for cell in ['f3-dig', 'f3-hex-run', 'f3-word-eq', 'f3-quad']:
            sh = SHAPE[cell]
            g1 = GRID1['beta'][arm][sh]
            if arm not in BETA[cell]:
                out('%-9s %-11s %-8s %9s %9.4f %8s' % (arm, cell, sh, 'dropped', g1, '-'))
                continue
            g2 = BETA[cell][arm]
            out('%-9s %-11s %-8s %9.4f %9.4f %8.3f' % (arm, cell, sh, g2, g1, g2 / g1))
    out('(the walk by terms: ' + ', '.join('%s %.4f' % (c, BETA[c]['walk']) for c in cells) + ')')
    # keys
    shname = lambda sh: 'r%de%dc%d' % sh
    for cell in cells:
        sh = SHAPE[cell]
        for arm in ('walk', 'V1', 'S1', 'A1'):
            if arm in BETA[cell]:
                st = 'measured'
                key('kit.beta.%s.DFA_SCAN.%s' % (arm.upper() if arm == 'walk' else arm, shname(sh)), 'ratio', e6(BETA[cell][arm] / u), e6(BETA[cell][arm]), st,
                    'streamed member-free single calls, slope 64Ki-1Mi' + (' [%s]' % sus[cell] if sus[cell] and arm in ('walk', 'V1', 'S1', 'A1') else ''), 'off' if arm in ('walk', 'V1') else ('w16' if arm == 'S1' else 'w32'),
                    e6(EPSB[cell]), 'grid2read an. 4')
        for arm in ('V1', 'S1', 'A1'):
            if arm in BETA[cell]:
                key('kit.saving.%s.WALK.%s' % (arm, shname(sh)), 'ratio', e6(1 - BETA[cell][arm] / BETA[cell]['walk']), '-', 'derived',
                    'derived: 1 - beta_f/beta_walk', 'off' if arm == 'V1' else ('w16' if arm == 'S1' else 'w32'), e6(EPSB[cell]), 'grid2read an. 4')
    return EPSB, sus


def derived_rules(EPSB):
    hdr('4b. R0 / R7 UNDER THE MEASURED SAVINGS AND EACH CANDIDATE FLOOR (DERIVED)')
    eps_slope = [k for k in KEYS if k[0] == 'kit.eps.streamed.slope'][0][2] / 1e6
    eps_fa = [k for k in KEYS if k[0] == 'kit.eps.findall.l64k'][0][2] / 1e6
    eps_beta = [k for k in KEYS if k[0] == 'kit.eps.beta.slope'][0][2] / 1e6
    out('Rule text (rev 3 §1.3): R0 holds when kit.saving.V1.WALK.r2 <= kit.eps.<regime>; R7 holds when kit.saving.V1.WALK.<shape> > kit.eps.<regime>.')
    out('The shipped finder (fdb2, finder.c) reads kit.eps.streamed.slope.  grid2 values: streamed.slope %.4f%%, findall.l64k %.3f%%, slope-based %.4f%%.' % (100 * eps_slope, 100 * eps_fa, 100 * eps_beta))
    out()
    out('%-11s %-7s %9s | %-22s | %-22s | %-22s' % ('cell', 'shape', 'saving V1', 'floor = streamed.slope', 'floor = findall.l64k', 'floor = slope-based'))
    for cell in SHAPE:
        r = BETA[cell]
        if 'V1' not in r:
            continue
        sv = 1 - r['V1'] / r['walk']
        def rule(e):
            return 'R7 (V1 wins)' if sv > e else ('R0 (WALK)' if sv > -e else 'V1 LOSES: R0')
        out('%-11s %-7s %+8.3f%% | %-22s | %-22s | %-22s' % (cell, SHAPE[cell], 100 * sv, rule(eps_slope), rule(eps_fa), rule(eps_beta)))
    out('(R0 reads the r2 class = max over the 2+-RANGE shapes: hex-run (2,0,0), word-eq (2,0,1), quad (3,1,0), wcls (3,0,1): its saving key is the best of them.)')
    r2 = [1 - BETA[c]['V1'] / BETA[c]['walk'] for c in ('f3-hex-run', 'f3-word-eq', 'f3-quad')]
    out('kit.saving.V1.WALK.r2 (grid1 class: hex-run, word-eq, quad) = max(%s) = %+.4f; with wcls (3,0,1) it is unchanged (wcls %+.4f).' % (
        ', '.join('%+.4f' % x for x in r2), max(r2), 1 - BETA['f3-wcls']['V1'] / BETA['f3-wcls']['walk']))
    key('kit.saving.V1.WALK.r2', 'ratio', e6(max(r2)), '-', 'derived', 'max over r2e0c0, r2e0c1, r3e1c0', 'off', e6(eps_beta), 'grid2read an. 4b')
    out()
    out('Item 3a (R7 on three UNMEASURED shapes, V1 vs walk, member-free): saving %s' % ', '.join(
        '%s %+.3f' % (SHAPE[c], 1 - BETA[c]['V1'] / BETA[c]['walk']) for c in ('f3-c020', 'f3-c001', 'f3-c110')))
    out('  (grid1 had no value for these; every one exceeds every candidate floor, so R7 fires for them under the design\'s rule.)')



# ------------------------------------------------------------------------------------------
# 5. single calls: F, the staircase, crossovers, block step, delta keys (M7-M12)
# ------------------------------------------------------------------------------------------
def dig_first_groups():
    """member-free single-call groups of the dig cell: {n: visit} (F1 first-mode ginf-Lnone, no offset) + F3's 64 KiB / 1 MiB."""
    G = {}
    for v in VIS['F1']:
        if v.key[0] == 'dig' and v.key[2] == 'first' and not v.overlap:
            m = re.match(r'g2-dig-n(\d+)-ginf-Lnone-S$', v.key[1])
            if m:
                G[int(m.group(1))] = v
    a, b = f3pair('f3-dig')
    G[65536] = a
    G[1048576] = b
    return dict(sorted(G.items()))


def win_n(v, arm, thr_extra=0.0):
    """True iff arm beats the base beyond the NULL rule (regime 'short' or 'slope' by size)."""
    return verdict(v, arm, regime_of(v)) == 'W'


def single_calls():
    hdr('5. SINGLE CALLS: THE FIXED PART F, THE V1 STAIRCASE, CROSSOVERS, THE BLOCK STEP (M7-M12; member-free dig, streamed distinct buffers)')
    u = UNIT[0]
    G = dig_first_groups()
    out('One call over a member-free subject of n bytes (n8..n128 in F1; n64k, n1m are F3); ns are the median over launches; floor = the')
    out('group\'s A/A (max of #b, #c); verdict under the NULL rule (regime short: FRG %.3f%%).  delta = arm - walk (ns).' % (100 * FRG['short']))
    out('%7s %6s | %8s | %8s %7s %-3s | %8s %7s %-3s | %8s %7s %-3s | %5s' % ('n', 'floor', 'walk', 'V1', 'dV1', 'v', 'S1', 'dS1', 'v', 'A1', 'dA1', 'v', 'L'))
    for n, v in G.items():
        fl = floor(v)
        def c(a):
            if a not in v.arm_vals:
                return '        -       -   -'
            d = v.med(a) - v.med('walk')
            return '%8.2f %+7.2f %-3s' % (v.med(a), d, verdict(v, a, regime_of(v)))
        out('%7d %6.3f | %8.2f | %s | %s | %s | %5d' % (n, fl, v.med('walk'), c('V1'), c('S1'), c('A1'), v.launches))
    # F per arm from n in {64, 65, 128}
    betas = {a: BETA['f3-dig'][a] for a in ('walk', 'V1', 'S1', 'A1', 'tw0', 'tw1', 'tw2')}
    out()
    out('F = T(n) - beta_arm * n (beta from section 4, f3-dig), ns; median over n of {64, 65, 128} (n >= one block of 64):')
    out('%-5s %8s %8s %8s | %8s %8s | %s' % ('arm', 'n=64', 'n=65', 'n=128', 'F (median)', 'u*B', 'grid1 F (ns) / F(n=48) / grid2 F(n=48)'))
    Fv = {}
    for a in ('walk', 'V1', 'S1', 'A1'):
        xs = []
        row = []
        for n in (64, 65, 128):
            f = G[n].med(a) - betas[a] * n if a in G[n].arm_vals else None
            row.append(f)
            if f is not None:
                xs.append(f)
        F = hmed(xs) if len(xs) == 3 else sum(xs) / len(xs)
        Fv[a] = F
        f48 = G[48].med(a) - betas[a] * 48
        out('%-5s %8.2f %8.2f %8.2f | %8.2f %8.1f | %.2f / %.2f / %.2f' % (a, row[0] if row[0] is not None else float('nan'), row[1] if row[1] is not None else float('nan'),
                                                                         row[2] if row[2] is not None else float('nan'), F, F / u, GRID1['F'][a], GRID1['F48'][a], f48))
        form = 'WALK' if a == 'walk' else ('V1' if a == 'V1' else 'W64')
        key('kit.f.%s.DFA_SCAN.n64' % form, 'walkbytes', e6((G[64].med(a) - betas[a] * 64) / u), e6(G[64].med(a) - betas[a] * 64), 'measured',
            'streamed member-free single call, fresh buffers (layer %s)' % ('OFF' if a in ('walk', 'V1') else ('W16' if a == 'S1' else 'W32')), 'off' if a in ('walk', 'V1') else ('w16' if a == 'S1' else 'w32'), e6(floor(G[64]) / u), 'grid2read an. 5')
        key('kit.f.%s.DFA_SCAN.n48' % form, 'walkbytes', e6(f48 / u), e6(f48), 'measured', 'sub-block tail (n=48)', 'off' if a in ('walk', 'V1') else ('w16' if a == 'S1' else 'w32'), e6(floor(G[48]) / u), 'grid2read an. 5')
    out('  (grid1 F is the intercept at n >= 64 with repeated-condition buffers; grid2\'s are fresh streamed buffers.)')

    # the staircase (rule: kit r17b_prime §2.6 C5)
    Ns = [n for n in G if 'V1' in G[n].arm_vals]
    out()
    out('5.1 THE V1 STAIRCASE (rule §2.6 [C5]: the smallest measured N from which V1 - walk <= -floor at EVERY measured point above it)')
    out('%7s %9s %9s %7s %7s  %s' % ('N', 'V1-walk', 'floor', 'ratio', 'u*B', 'verdict (NULL rule)'))
    wins = {}
    for n in Ns:
        v = G[n]
        d = v.med('V1') - v.med('walk')
        wins[n] = (d <= -floor(v))
        out('%7d %+9.3f %9.3f %7.3f %+7.1f  %s%s' % (n, d, floor(v), v.med('V1') / v.med('walk'), d / u, verdict(v, 'V1', regime_of(v)), '' if wins[n] else '   <- not <= -floor'))
    Nstar = None
    for i, n in enumerate(Ns):
        if all(wins[m] for m in Ns[i:]):
            Nstar = n
            break
    low = Ns[0]
    out('  measured Ns: %s' % Ns)
    out('  smallest N with V1 faster than the walk beyond the floor at every measured N above it: N* = %s' % Nstar)
    if Nstar == low:
        out('  => N* is the LOWEST measured point (%d B): the crossover is BELOW the staircase, NOT LOCATED by this slot.  grid1\'s 36 B (INTERPOLATED(32,48)) is' % low)
        out('     not reproduced: with the compiler\'s own V1 text V1 beats the walk at every N from %d B up.' % low)
    key('kit.xover.V1.WALK.DFA_SCAN', 'bytes', e6(Nstar), '-', 'derived', 'NOT LOCATED: N* is the lowest measured point (staircase rule)' if Nstar == low else 'staircase rule',
        'off', 0, 'grid2read an. 5.1 (grid1: 36 B INTERPOLATED(32,48))')
    # M10
    out()
    out('5.2 S1 / A1 against the walk (single calls), the smallest N from which the form wins at every higher measured N (M10, M11):')
    for a in ('S1', 'A1'):
        Na = [n for n in G if a in G[n].arm_vals]
        ww = {n: (G[n].med(a) - G[n].med('walk')) <= -floor(G[n]) for n in Na}
        nst = None
        for i, n in enumerate(Na):
            if all(ww[m] for m in Na[i:]):
                nst = n
                break
        sgn = ' '.join('%d:%+.2f' % (n, G[n].med(a) - G[n].med('walk')) for n in Na)
        out('  %s: delta(ns) by N: %s' % (a, sgn))
        out('      N* (win at every measured N >= N*) = %s;  grid1: S1 18 B / A1 20 B (single-call crossover, interpolated)' % nst)
        lastlose = [n for n in Na if not ww[n]]
        out('      N where it does NOT win beyond the floor: %s' % lastlose)
        key('kit.xover.%s.WALK.DFA_SCAN' % ('W64'), 'bytes', e6(nst) if nst else -1, '-', 'derived', 'single call, win at every measured N >= N*', 'w16' if a == 'S1' else 'w32', 0, 'grid2read an. 5.2 (%s)' % a)
    out()
    out('5.3 THE BLOCK STEP (T(64) - T(63), ns; the walk\'s own step is its beta; M11):')
    for a in ('walk', 'V1', 'S1', 'A1'):
        if a in G[63].arm_vals and a in G[64].arm_vals:
            out('  %-5s T(63) %7.2f  T(64) %7.2f  step %+7.2f (%+.1f u*B)   T(48) %7.2f  T(65) %7.2f' % (a, G[63].med(a), G[64].med(a), G[64].med(a) - G[63].med(a), (G[64].med(a) - G[63].med(a)) / u, G[48].med(a), G[65].med(a)))
    out('  W64 forms fall by %.1f (S1) and %.1f (A1) ns across 63 -> 64; the walk and V1 rise by their per-byte cost: the W64 block is 64 B (CONFIRMED, M11 = 64).' % (
        G[63].med('S1') - G[64].med('S1'), G[63].med('A1') - G[64].med('A1')))
    key('kit.block.W64', 'bytes', 64000000, '-', 'derived', 'step MEASURED at n 63->64 (S1 -%.1f ns, A1 -%.1f ns)' % (G[63].med('S1') - G[64].med('S1'), G[63].med('A1') - G[64].med('A1')), 'w16/w32', 0, 'grid2read an. 5.3')

    out()
    out('5.4 V1 - walk at N = 8, 32, 48, 63 (M12) in ns and u*B, with the kit.delta key orientation (delta ALT PICK = cost(ALT) - cost(PICK)):')
    out('%5s %9s %9s %9s %9s %9s %9s' % ('N', 'V1-walk', 'A1-walk', 'S1-walk', 'A1-V1', 'S1-V1', 'floor'))
    for n in (8, 32, 48, 63, 64, 65, 128):
        v = G[n]
        f = lambda a, b: ('%+9.2f' % (v.med(a) - v.med(b))) if a in v.arm_vals and b in v.arm_vals else '        -'
        out('%5d %s %s %s %s %s %9.3f' % (n, f('V1', 'walk'), f('A1', 'walk'), f('S1', 'walk'), f('A1', 'V1'), f('S1', 'V1'), floor(v)))
        for alt, pick, an, pn in (('V1', 'WALK', 'V1', 'walk'), ('WALK', 'V1', 'walk', 'V1'), ('W64', 'V1', 'A1', 'V1'), ('WALK', 'W64', 'walk', 'A1'), ('V1', 'W64', 'V1', 'A1')):
            if an in v.arm_vals and pn in v.arm_vals and n in (8, 32, 48, 63, 64, 65, 128):
                d = v.med(an) - v.med(pn)
                key('kit.delta.%s.%s.DFA_SCAN.n%d' % (alt, pick, n), 'walkbytes', e6(d / u), e6(d), 'measured', 'streamed fresh member-free single call; layer %s' % ('OFF' if 'A1' not in (an, pn) else 'W32'),
                    'off' if 'A1' not in (an, pn) else 'w32', e6(floor(v) / u), 'grid2read an. 5.4')
                key('kit.dfloor.%s.%s.DFA_SCAN.n%d' % (alt, pick, n), 'walkbytes', e6(floor(v) / u), e6(floor(v)), 'measured', 'A/A floor of the group (max of #b, #c)', 'all', 0, 'grid2read an. 5.4')
        for fm, an in (('WALK', 'walk'), ('V1', 'V1'), ('W64', 'A1')):
            if an in v.arm_vals:
                key('kit.ffloor.%s.DFA_SCAN.n%d' % (fm, n), 'walkbytes', e6(floor(v) / u), e6(floor(v)), 'measured', 'A/A floor of the group', 'all', 0, 'grid2read an. 5.4')
    out('(grid1 at N = 8, 32, 48, 63 (V1-walk): +2.3, +0.6, -4.5, -5.6 ns.  grid2: %s ns.)' % ', '.join('%+.2f' % (G[n].med('V1') - G[n].med('walk')) for n in (8, 32, 48, 63)))
    out('The delta ALT PICK spelling is the shipped finder\'s (finder.c pay_fill: key "kit.delta.<alt>.<pick>.<kind>.n<N>" = cost(alt) - cost(pick)); grid1\'s interim set holds only V1.WALK')
    out('(= V1 - walk, R1\'s orientation); R2 (pick V1, unpaid WALK) reads WALK.V1 (= walk - V1), a key the interim set does NOT hold: with grid1 R2 fails T1 for want of the key.')
    return G, Fv


def alignment(G):
    hdr('5b. ALIGNMENT (member-free dig, start offset 0 / 7 / 31 into the buffer; single call and find-all)')
    for nm, mode in (('g2-dig-n64k-ginf-L64k-S', 'first'), ('g2-dig-n65-ginf-Lnone-S', 'first'), ('g2-dig-n64k-g8-L1k-u-S', 'all')):
        vs = []
        for off in ('@0', '@7', '@31'):
            v = vis('F1', 'dig', nm + off, mode)
            if v is not None:
                vs.append((off, v))
        if not vs:
            continue
        out('  %s (%s):' % (nm, mode))
        for off, v in vs:
            ld = '  LOAD-SUSPECT' if v.n_load_hi else ''
            out('    %-3s walk %10.2f  V1 %10.2f  S1 %10.2f  A1 %10.2f%s' % (off, v.med('walk'), v.med('V1'), v.med('S1') if 'S1' in v.arm_vals else float('nan'), v.med('A1') if 'A1' in v.arm_vals else float('nan'), ld))
        base0 = vs[0][1]
        for off, v in vs[1:]:
            out('    %s vs @0: ' % off + ', '.join('%s %+.2f%%' % (a, 100 * (v.med(a) / base0.med(a) - 1)) for a in ('walk', 'V1', 'S1', 'A1') if a in v.arm_vals and a in base0.arm_vals))



# ------------------------------------------------------------------------------------------
# 6. find-all: per-landing facts, the absolute fit (M13, M14), g* (M15), the regimes
# ------------------------------------------------------------------------------------------
TOKC = {'dig': 1.0, 'dfa-hat': 10.0 / 3.0, 'bounded': 0.0}
L_STAR, G_STAR = 64.0, 18.5            # costmodel's boundaries (gridread tested them)
ARMS_FA = ['walk', 'V1', 'S1', 'A1', 'A3']


def bname(subj):
    return subj.split('@')[0]


def cnt_of(cell, arm, subj, mode):
    k = (cell, 'site(G1)' if arm == 'walk' else arm, bname(subj), mode)
    d = CNT.get(k)
    return d


def facts_of(v):
    cell, subj, mode = v.key
    f = FACT[bname(subj)]
    nb = f['nbuf']
    site = cnt_of(cell, 'walk', subj, mode)
    if site is None:
        return None
    U = site['uses'] / nb
    A = site['cold'] / nb
    m = f['pm'] / nb
    n = f['n']
    ADV = n - m * TOKC.get(cell, 0.0) if mode == 'all' else n
    d = dict(n=n, g=f['g'], L=f['L'], shape=f['shape'], U=U, A=A, W=max(U - A, 0.0), calls=site['calls'] / nb, m=m, ADV=ADV,
             PL=f['pl'] / nb, PU=(f['pl'] / nb) if f['shape'] == 'u' else 0.0, nbuf=nb)
    d['Lact'] = ADV / A if A else float('inf')
    d['gu'] = ADV / U if U else float('inf')
    d['regime'] = 'UNREACHED' if U == 0 else ('DINGHY' if d['Lact'] < L_STAR else ('TUG' if d['gu'] < G_STAR else 'LINER'))
    return d


def fa_groups(cell):
    out_ = []
    for v in VIS['F1']:
        if v.key[0] == cell and v.key[2] == 'all' and not v.overlap:
            out_.append(v)
    return out_


def own_counts(v, arm):
    c = cnt_of(v.key[0], arm, v.key[1], 'all')
    if c is None:
        return None
    nb = FACT[bname(v.key[1])]['nbuf']
    return {k: x / nb for k, x in c.items() if isinstance(x, (int, float))}


def findall():
    hdr('6. FIND-ALL: THE ABSOLUTE FIT (M13 c_cold, M14 w_use), g* (M15), THE REGIMES (streamed buffers, all-mode, ns per pass over one 64 KiB buffer)')
    u = UNIT[0]
    out('Model per arm (FITTED, weighted by 1/T):  T = F*A + w*(U-A) + p*PU + beta*ADV')
    out('  A = cold activations per pass (the arm\'s own `cold` counter; A3: its `calls`), U = uses, PU = planted landings on the u-shaped (unpredictable landing offsets) groups, ADV = bytes the find advances.')
    out('  F = cost per cold activation (a call + its first use), w = cost per warm use, p = extra per UNPREDICTABLE landing, beta per byte.')
    FIT = {}
    for cell in ('dig', 'dfa-hat', 'bounded'):
        gs = [v for v in fa_groups(cell) if not v.n_load_hi and facts_of(v) and facts_of(v)['n'] == 65536]
        out()
        out('%s: %d all-mode groups at n = 64 KiB (the n <= 128 groups are single-call: section 5)' % (cell, len(gs)))
        out('  %-5s %8s %8s %8s %9s | %7s %5s | %s' % ('arm', 'F', 'w', 'p', 'beta', 'med|res|', 'rows', 'vs walk: dF, dw, dp, dbeta'))
        for arm in ARMS_FA:
            rows = []
            for v in gs:
                if arm not in v.arm_vals:
                    continue
                f = facts_of(v)
                cc = own_counts(v, arm)
                if cc is None:
                    continue
                A = cc['calls'] if arm == 'A3' else cc['cold']        # A3 keeps state across calls: its cold count is ~0, its per-call cost is the unit
                Uu = cc['uses']
                W = max(Uu - A, 0.0)
                rows.append((v, [A, W, f['PU'], f['ADV']], v.med(arm)))
            if len(rows) < 6:
                continue
            X = np.array([r[1] for r in rows], float)
            T = np.array([r[2] for r in rows], float)
            wgt = 1.0 / T
            coef, *_ = np.linalg.lstsq(X * wgt[:, None], T * wgt, rcond=None)
            res = np.abs((X @ coef - T) / T)
            FIT[(cell, arm)] = dict(coef=coef, medres=float(np.median(res)), n=len(rows), res=res, rows=rows)
            ref = FIT.get((cell, 'walk'))
            dd = ('%+7.2f %+7.2f %+7.2f %+8.4f' % tuple(coef - ref['coef'])) if ref is not None and arm != 'walk' else ''
            out('  %-5s %8.2f %8.2f %8.2f %9.4f | %7.1f%% %5d | %s' % (arm, coef[0], coef[1], coef[2], coef[3], 100 * float(np.median(res)), len(rows), dd))
    out()
    out('Against grid1 (gridread §2.3-2.4, dig/PF, repeated+streamed mixed): c_cold V1/S1/A1 +2.47/+2.90/+2.91 ns over the walk; warm use walk/V1/S1/A1 1.67/2.38/2.22/2.23 ns.')
    for cell, kind in (('dig', 'DFA_SCAN'), ('dfa-hat', 'DFA_HAT'), ('bounded', 'DFA_SCAN')):
        w = FIT.get((cell, 'walk'))
        if w is None:
            continue
        for arm in ('V1', 'S1', 'A1', 'A3'):
            f = FIT.get((cell, arm))
            if f is None:
                continue
            dF = f['coef'][0] - w['coef'][0]
            lay = 'off' if arm in ('V1',) else ('w16' if arm == 'S1' else ('w32' if arm == 'A1' else 'iter'))
            form = 'V1' if arm == 'V1' else ('W64' if arm in ('S1', 'A1') else 'A3')
            key('kit.ccold.%s.%s%s' % (form, kind, '' if cell != 'bounded' else '.bounded'), 'walkbytes', e6(dF / u), e6(dF), 'fitted',
                'streamed find-all, FITTED F_arm - F_walk (cell %s; fit residual %.1f%%)' % (cell, 100 * f['medres']), lay, e6(100 * f['medres'] / 100), 'grid2read an. 6')
        for arm in ('walk', 'V1', 'S1', 'A1', 'A3'):
            f = FIT.get((cell, arm))
            if f is None:
                continue
            form = 'WALK' if arm == 'walk' else ('V1' if arm == 'V1' else ('W64' if arm in ('S1', 'A1') else 'A3'))
            key('kit.wuse.%s.%s%s' % (form, kind, '' if cell != 'bounded' else '.bounded'), 'walkbytes', e6(f['coef'][1] / u), e6(f['coef'][1]), 'fitted',
                'streamed find-all, FITTED warm-use cost w (cell %s)' % cell, 'off' if arm in ('walk', 'V1') else ('w16' if arm == 'S1' else ('w32' if arm == 'A1' else 'iter')), e6(f['medres']), 'grid2read an. 6')
    return FIT


def gstar_tables(FIT):
    hdr('6b. g* AND THE (g, L) GRID: arm - walk per pass, % of the walk, with the NULL-rule verdict W/N/R (all-mode, streamed)')
    GSEQ = [2, 4, 8, 16, 32, 64, 256, 0]
    CROSS = {}
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for Ls, Lname in ((65536, '64k'), (1024, '1k'), (32, '32')):
            rows = {}
            for v in fa_groups(cell):
                f = FACT[bname(v.key[1])]
                if f['L'] != Ls or v.key[1].count('@') or f['n'] != 65536 or f['shape'] in ('reg', 'burst') and f['g'] not in (2,):
                    continue
                if v.n_load_hi:
                    continue
                rows[f['g']] = v
            if len(rows) < 4:
                continue
            out()
            out('%s, L = %s:    %s' % (cell, Lname, ''.join('%14s' % ('g=%s' % ('inf' if g == 0 else g)) for g in GSEQ if g in rows)))
            out('   walk ns      ' + ''.join('%14.0f' % rows[g].med('walk') for g in GSEQ if g in rows))
            for arm in ('V1', 'S1', 'A1', 'A3'):
                cells = []
                ok = False
                for g in GSEQ:
                    if g not in rows:
                        continue
                    v = rows[g]
                    if arm not in v.arm_vals:
                        cells.append('%14s' % '-')
                        continue
                    ok = True
                    d = v.med(arm) - v.med('walk')
                    cells.append('%9.1f%% %-3s' % (100 * d / v.med('walk'), verdict(v, arm, 'findall')))
                if ok:
                    out('   %-4s d%%     ' % arm + ''.join(cells))
                    # crossover over the u-shape series g>=4 (g=2 is the reg-shaped dense point)
                    seq = [(g if g else 1 << 20, rows[g].med(arm) / rows[g].med('walk') - 1.0) for g in [4, 8, 16, 32, 64, 256, 0] if g in rows and arm in rows[g].arm_vals]
                    cr = None
                    for (g1, d1), (g2, d2) in zip(seq, seq[1:]):
                        if d1 > 0 and d2 <= 0 and g2 < (1 << 20):
                            t = d1 / (d1 - d2)
                            cr = math.exp(math.log(g1) + t * (math.log(g2) - math.log(g1)))
                            break
                        if d1 > 0 and d2 <= 0:
                            cr = float(g1) * 2
                            break
                    allw = all(d <= 0 for _, d in seq)
                    CROSS[(cell, Lname, arm)] = cr if cr is not None else ('all-win' if allw else 'no-win')
    out()
    out('g* (log-interpolated zero crossing of arm - walk over the u-shaped series g = 4..256; "all-win" = faster at every g; "no-win" = never faster):')
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for Lname in ('64k', '1k', '32'):
            r = ['%s %s' % (a, ('%.1f B' % CROSS[(cell, Lname, a)]) if isinstance(CROSS.get((cell, Lname, a)), float) else CROSS.get((cell, Lname, a), '-'))
                 for a in ('V1', 'S1', 'A1', 'A3') if (cell, Lname, a) in CROSS]
            if r:
                out('  %-8s L=%-3s  %s' % (cell, Lname, '   '.join(r)))
    out('grid1 (M15): V1 10.8-16.7 (PF) / 3.0-3.3 (HAT) / 21.5 (bounded); S1 4.3-4.7 / 2.1-2.4 / 3.6-5.8; A1 4.2-4.4 / 2.1-2.3 / 2.4-3.0.')
    for (cell, Lname, arm), cr in CROSS.items():
        if Lname != '64k':
            continue
        kind = 'DFA_HAT' if cell == 'dfa-hat' else 'DFA_SCAN'
        form = 'V1' if arm == 'V1' else ('W64' if arm in ('S1', 'A1') else 'A3')
        if isinstance(cr, float):
            key('kit.gstar.%s.%s%s' % (form, kind, '.bounded' if cell == 'bounded' else ''), 'bytes', e6(cr), '-', 'derived', 'streamed find-all L=64k, u-shaped g=4..256, log2-interpolated (%s)' % arm,
                'off' if arm == 'V1' else ('w16' if arm == 'S1' else ('w32' if arm == 'A1' else 'iter')), 0, 'grid2read an. 6b')
        else:
            key('kit.gstar.%s.%s%s' % (form, kind, '.bounded' if cell == 'bounded' else ''), 'bytes', -1, '-', 'derived', 'streamed find-all L=64k: %s over g=4..256 (%s)' % (cr, arm), 'off' if arm == 'V1' else 'w16/w32/iter', 0, 'grid2read an. 6b (no crossover value)')
    return CROSS


def regimes_tally():
    hdr('6c. VERDICTS BY NAMED REGIME AND BY LAYER (all-mode, all three cells, quiet visits, NULL rule regime findall; costmodel boundaries L* = 64 B, g* = 18.5 B)')
    out('Regime of a group from its own counters: DINGHY (bytes advanced per activation < 64), TUG (bytes per landing < 18.5), else LINER.  W/N/R = arm faster / NULL / slower than the walk.')
    T = collections.defaultdict(lambda: collections.Counter())
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for v in fa_groups(cell):
            if v.n_load_hi:
                continue
            f = facts_of(v)
            if f is None or f['regime'] == 'UNREACHED':
                continue
            for arm in ARMS_FA[1:]:
                if arm not in v.arm_vals:
                    continue
                T[(cell, arm, f['regime'])][verdict(v, arm, 'findall')] += 1
    layer = {'V1': 'OFF', 'S1': 'ON/W16', 'A1': 'ON/W32', 'A3': 'ITER'}
    out('%-8s %-4s %-7s | %-15s %-15s %-15s' % ('cell', 'arm', 'layer', 'DINGHY W/N/R', 'TUG W/N/R', 'LINER W/N/R'))
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for arm in ARMS_FA[1:]:
            if not any(k[0] == cell and k[1] == arm for k in T):
                continue
            def c(rg):
                x = T[(cell, arm, rg)]
                return '%d/%d/%d (%d)' % (x['W'], x['N'], x['R'], sum(x.values()))
            out('%-8s %-4s %-7s | %-15s %-15s %-15s' % (cell, arm, layer[arm], c('DINGHY'), c('TUG'), c('LINER')))
    # sign of the gap by regime for V1 at OFF: absolute magnitudes
    out()
    out('Absolute deltas (ns per 64 KiB pass) where the verdict is not NULL, median [min, max], V1 at OFF and A1 at ON/W32, by regime:')
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for arm in ('V1', 'A1'):
            line = []
            for rg in ('DINGHY', 'TUG', 'LINER'):
                ds = []
                for v in fa_groups(cell):
                    if v.n_load_hi or arm not in v.arm_vals:
                        continue
                    f = facts_of(v)
                    if f is None or f['regime'] != rg:
                        continue
                    if verdict(v, arm, 'findall') != 'N':
                        ds.append(v.med(arm) - v.med('walk'))
                line.append('%s %s' % (rg, ('%+.0f [%+.0f, %+.0f] n=%d' % (hmed(ds), min(ds), max(ds), len(ds))) if ds else '-'))
            out('  %-8s %-3s  %s' % (cell, arm, '   '.join(line)))
    return T



def verdict_pair(v, a, b, regime):
    """a vs b (neither the base): W a faster / R a slower / N."""
    d = v.med(a) - v.med(b)
    thr = max(floor(v), FRG.get(regime, 0.0) * v.med(b))
    rs = sorted(set(v.arm_vals[a]) & set(v.arm_vals[b]))
    dd = [v.arm_vals[a][r] - v.arm_vals[b][r] for r in rs]
    cons = all(x > 0 for x in dd) if d > 0 else all(x < 0 for x in dd)
    if abs(d) <= thr or not cons:
        return 'N'
    return 'W' if d < 0 else 'R'


def wide_vs_v1():
    hdr('6c2. THE WIDE FORMS AGAINST V1 (the SIMD-on layer against the SIMD-off layer), all-mode quiet groups, NULL rule regime findall')
    out('%-8s %-4s | %-14s %-14s %-14s' % ('cell', 'arm', 'all cells W/N/R', 'g=2 (reg) W/N/R', 'L=32 W/N/R'))
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for arm in ('S1', 'A1', 'A3'):
            tot = collections.Counter()
            g2 = collections.Counter()
            l32 = collections.Counter()
            for v in fa_groups(cell):
                if v.n_load_hi or arm not in v.arm_vals or 'V1' not in v.arm_vals:
                    continue
                f = facts_of(v)
                if f is None or f['n'] != 65536 or f['U'] == 0:
                    continue
                vd = verdict_pair(v, arm, 'V1', 'findall')
                tot[vd] += 1
                if f['g'] == 2:
                    g2[vd] += 1
                if f['L'] == 32:
                    l32[vd] += 1
            c = lambda x: '%d/%d/%d (%d)' % (x['W'], x['N'], x['R'], sum(x.values()))
            out('%-8s %-4s | %-14s %-14s %-14s' % (cell, arm, c(tot), c(g2), c(l32)))
    TOT = collections.defaultdict(collections.Counter)
    for cell in ('dig', 'dfa-hat', 'bounded'):
        for arm in ('S1', 'A1', 'A3'):
            for v in fa_groups(cell):
                if v.n_load_hi or arm not in v.arm_vals or 'V1' not in v.arm_vals:
                    continue
                f = facts_of(v)
                if f is None or f['n'] != 65536 or f['U'] == 0:
                    continue
                TOT[arm][verdict_pair(v, arm, 'V1', 'findall')] += 1
                if f['g'] == 2:
                    TOT[arm + '@g2'][verdict_pair(v, arm, 'V1', 'findall')] += 1
    out('  totals over the three cells: ' + '; '.join('%s vs V1 W/N/R = %d/%d/%d' % (a, TOT[a]['W'], TOT[a]['N'], TOT[a]['R']) for a in ('S1', 'A1', 'A3')) + '.')
    out('  at g = 2 (V1 itself slower than the walk): ' + '; '.join('%s %d/%d/%d' % (a, TOT[a + '@g2']['W'], TOT[a + '@g2']['N'], TOT[a + '@g2']['R']) for a in ('S1', 'A1', 'A3')) + ': a W64 form displaces V1 there without a g threshold.')
    out('  S1 and A1 differ little (SSE2 vs AVX2 at the same 64 B block); the single-call region below 64 B is the exception (an. 5.4: V1 is the best form below the block).')


def predictability():
    hdr('6d. PREDICTABILITY: the same mean gap with regular, bursty and unpredictable landing offsets (dig, L = 1k, ns per pass) and the F2 perf diagnosis')
    out('Landing offsets: reg = exactly g apart (repeats every buffer), burst = clustered, u = uniform-random per buffer (every buffer differs).')
    out('%-5s %-6s %9s | %9s %7s %-2s | %9s %7s %-2s | %9s %7s %-2s' % ('g', 'shape', 'walk', 'V1', 'd%', 'v', 'S1', 'd%', 'v', 'A1', 'd%', 'v'))
    for g in (8, 32):
        for sh in ('u', 'reg', 'burst'):
            nm = 'g2-dig-n64k-g%d-L1k-%s-S' % (g, sh)
            v = vis('F1', 'dig', nm, 'all')
            if v is None:
                continue
            row = '%-5d %-6s %9.0f' % (g, sh, v.med('walk'))
            for a in ('V1', 'S1', 'A1'):
                d = v.med(a) - v.med('walk')
                row += ' | %9.0f %+6.1f%% %-2s' % (v.med(a), 100 * d / v.med('walk'), verdict(v, a, 'findall'))
            out(row)
    out('  (grid1 found the same: streamed reg/burst buffers run within ~1% of repeated; the u-shape on fresh data costs the walk 4-7 ns per landing.)')
    out()
    # F2 perf
    path = '%s/f2.log' % OUT
    rows = []
    for ln in open(path):
        p = ln.split()
        if len(p) == 8 and p[0] != 'cell' and not ln.startswith('#'):
            try:
                rows.append(dict(cell=p[0], subj=p[1], arm=p[2], cyc=float(p[3]), ins=float(p[4]), br=float(p[5]), miss=float(p[6]), mk=float(p[7])))
            except ValueError:
                pass
    R = {(r['cell'], r['subj'], r['arm']): r for r in rows}
    out('F2 (optional, item 6): user-space counters, perf_event_paranoid=2 (the counters WERE available, so no SUGGESTION text was needed).')
    out('%d rows in f2.log.  Branch misses per pass and per planted landing, dig, L = 1k:' % len(rows))
    out('%-26s %-5s %10s %10s %9s' % ('subject', 'arm', 'cycles', 'misses', 'miss/lnd'))
    for g in (8, 32):
        for sh in ('u', 'reg', 'burst'):
            nm = 'g2-dig-n64k-g%d-L1k-%s-S' % (g, sh)
            f = FACT.get(nm)
            for a in ('walk', 'V1', 'A1'):
                r = R.get(('dig', nm, a))
                if r is None or f is None:
                    continue
                lnd = f['pl'] / f['nbuf']
                out('%-26s %-5s %10.0f %10.0f %9.3f' % (nm.replace('g2-dig-n64k-', ''), a, r['cyc'], r['miss'], r['miss'] / lnd))
    out('  planted landings per pass: g8 = %.0f, g32 = %.0f.' % (FACT['g2-dig-n64k-g8-L1k-u-S']['pl'] / 64, FACT['g2-dig-n64k-g32-L1k-u-S']['pl'] / 64))
    # ns per miss implied: walk u minus walk reg
    for g in (8, 32):
        nu = 'g2-dig-n64k-g%d-L1k-u-S' % g
        nr = 'g2-dig-n64k-g%d-L1k-reg-S' % g
        if ('dig', nu, 'walk') in R and ('dig', nr, 'walk') in R:
            vu, vr = vis('F1', 'dig', nu, 'all'), vis('F1', 'dig', nr, 'all')
            dm = R[('dig', nu, 'walk')]['miss'] - R[('dig', nr, 'walk')]['miss']
            dt = vu.med('walk') - vr.med('walk')
            dc = R[('dig', nu, 'walk')]['cyc'] - R[('dig', nr, 'walk')]['cyc']
            out('  g=%d walk, u minus reg: +%.0f misses, +%.0f ns, +%.0f cycles => %.2f ns per extra miss (%.1f cycles/miss)' % (g, dm, dt, dc, dt / dm, dc / dm))
    out('  The walk\'s extra cost on fresh data is branch mispredictions at the landings (about 1-1.4 per landing, ~4-5 ns = ~25 cycles each); the wide forms')
    out('  take ~0.1 miss per landing and pay no such price: the predictability of the landing offsets, not the cache, separates the forms.')
    return R


# ------------------------------------------------------------------------------------------
# 7. the dispatch twins, the scaffold, and the pay rule (M16-M18, T1-T3)
# ------------------------------------------------------------------------------------------
TWIN = {'tw0': ('walk', 'WALK', 'OFF', 2), 'tw1': ('V1', 'V1', 'OFF', 2), 'tw2': ('A1', 'W64', 'W32', 3)}


def dispatch():
    hdr('7. DISPATCH TWINS AND THE SCAFFOLD: C_disp_call (M16), C_disp_use (M17), C_scaffold (M18); THE PAY RULE T1-T3 ON THESE OPERANDS')
    u = UNIT[0]
    out('tw0/tw1: the WALK+V1 scaffold with the form byte f FORCED to WALK / V1 (nforms = 2, layer OFF); tw2: WALK+V1+W64 with f forced to W64 = A1 (nforms = 3, layer W32).')
    out('The charge of a twin is its time minus the SINGLE-FORM artifact\'s (walk, V1, A1) in the same interleaved group: it prices the dispatch mechanism (the opaque form')
    out('compare, the struct, the __next call) with the form held fixed.')
    out()
    out('7.1 PER ACTIVATION (member-free single calls, fresh buffers; ns):')
    out('%7s %6s | %8s %8s %-3s | %8s %8s %-3s | %8s %8s %-3s' % ('N', 'floor', 'tw0-walk', 'in u*B', 'v', 'tw1-V1', 'in u*B', 'v', 'tw2-A1', 'in u*B', 'v'))
    CALL = collections.defaultdict(list)
    for cell, getg in (('dig', dig_first_groups()),):
        for n, v in getg.items():
            if 'tw0' not in v.arm_vals:
                continue
            row = '%7d %6.3f |' % (n, floor(v))
            for tw, (single, form, ly, nf) in TWIN.items():
                if tw in v.arm_vals and single in v.arm_vals:
                    d = v.med(tw) - v.med(single)
                    # the charge is real when beyond the group's NULL threshold
                    thr = max(floor(v), FRG.get(regime_of(v), 0.0) * v.med(single))
                    vd = 'N' if abs(d) <= thr else ('W' if d < 0 else 'R')
                    CALL[tw].append((n, d, floor(v), vd))
                    row += ' %+8.3f %+8.1f %-3s |' % (d, d / u, vd)
                else:
                    row += ' %8s %8s %-3s |' % ('-', '-', '-')
            out(row.rstrip('|'))
    # other F3 cells, large N
    for cell in ('f3-hex-run', 'f3-word-eq', 'f3-quad', 'f3-wcls'):
        for nm in ('n64k', 'n1m'):
            v = vis('F3', cell, 'g2-%s-%s-ginf-Lnone-S' % (cell, nm), 'first')
            if v is None or v.n_load_hi:
                continue
            ds = []
            for tw, (single, form, ly, nf) in TWIN.items():
                if tw in v.arm_vals and single in v.arm_vals:
                    ds.append('%s %+8.1f' % (tw, v.med(tw) - v.med(single)))
            out('  %-11s %-5s: ' % (cell, nm) + '  '.join(ds) + '   (ns; %s)' % ('includes the walk-in-helper beta difference' if cell != 'f3-dig' else ''))
    out()
    # summarize the per-activation charge at fixed overhead N in {8..128}
    summ = {}
    for tw, L in CALL.items():
        sm = [(n, d, fl, vd) for (n, d, fl, vd) in L if n <= 128]
        ds = [d for n, d, fl, vd in sm]
        summ[tw] = dict(med=hmed(ds), mx=max(ds), mn=min(ds), n=len(ds), real=sum(1 for x in sm if x[3] == 'R'), fl=max(fl for _, _, fl, _ in sm))
        out('  %s (single = %s, N <= 128, %d points): charge median %+.2f ns [%+.2f, %+.2f], beyond-NULL slower at %d of %d points'
            % (tw, TWIN[tw][0], len(ds), summ[tw]['med'], summ[tw]['mn'], summ[tw]['mx'], summ[tw]['real'], len(ds)))
    big = []
    for tw, sg in (('tw0', 'walk'), ('tw1', 'V1'), ('tw2', 'A1')):
        for nm in ('n64k', 'n1m'):
            vv = vis('F3', 'f3-dig', 'g2-f3-dig-%s-ginf-Lnone-S' % nm, 'first')
            big.append(vv.med(tw) - vv.med(sg))
    out('  at the large N (n64k, n1m) the twins differ from the single forms by the scaffold\'s own beta, not the dispatch: dig tw0-walk %+.1f / %+.1f ns, tw1-V1 %+.1f / %+.1f, tw2-A1 %+.1f / %+.1f' % tuple(big))
    grp = collections.defaultdict(list)
    for tw, (single, form, ly, nf) in TWIN.items():
        grp[(ly, nf)].append(tw)
        d = summ[tw]['mx']
        key('kit.cdisp_call.DFA_SCAN.%s.%d.%sPATH' % (ly, nf, form), 'walkbytes', e6(d / u), e6(d), 'measured',
            'UPPER bound over N<=128 of (%s - %s) on dig member-free single calls, fresh buffers (path-specific; NOT a finder key)' % (tw, single), ly.lower(), e6(summ[tw]['fl'] / u), 'grid2read an. 7.1 (%s)' % tw)
    for (ly, nf), tws in grp.items():
        d = max(summ[t]['mx'] for t in tws)
        fl = max(summ[t]['fl'] for t in tws)
        key('kit.cdisp_call.DFA_SCAN.%s.%d' % (ly, nf), 'walkbytes', e6(d / u), e6(d), 'measured',
            'UPPER bound over N<=128 and over the dispatched paths %s (the finder key names no path)' % '+'.join(TWIN[t][1] for t in tws), ly.lower(), e6(max(summ[t]['fl'] for t in tws) / u), 'grid2read an. 7.1')
        key('kit.cfloor.DFA_SCAN.%s.%d' % (ly, nf), 'walkbytes', e6(fl / u), e6(fl), 'measured', 'worst A/A floor of the groups the charge was read from', ly.lower(), 0, 'grid2read an. 7.1')
    return CALL, summ


def dispatch_use():
    u = UNIT[0]
    out()
    out('7.2 PER USE (the dense F1 groups at n = 64 KiB, dig; charge = twin - single form per pass; per use = charge / uses per pass):')
    out('%-24s %6s %7s | %-27s | %-27s | %-27s' % ('group', 'A', 'U', 'tw0-walk  ns/use  v', 'tw1-V1  ns/use  v', 'tw2-A1  ns/use  v'))
    USE = collections.defaultdict(list)
    for v in fa_groups('dig'):
        if 'tw0' not in v.arm_vals or v.n_load_hi:
            continue
        f = facts_of(v)
        if f is None or f['n'] != 65536:
            continue
        cc = own_counts(v, 'walk')
        parts = []
        for tw, (single, form, ly, nf) in TWIN.items():
            d = v.med(tw) - v.med(single)
            thr = max(floor(v), FRG['findall'] * v.med(single))
            vd = 'N' if abs(d) <= thr else ('R' if d > 0 else 'W')
            USE[tw].append((d / cc['uses'], floor(v) / cc['uses'], vd, v.key[1]))
            parts.append('%+7.0f %+7.3f %s  ' % (d, d / cc['uses'], vd))
        out('%-24s %6.0f %7.0f | %s | %s | %s' % (v.key[1].replace('g2-dig-n64k-', ''), cc['cold'], cc['uses'], *parts))
    out()
    SUMU = {}
    for tw in TWIN:
        L = USE[tw]
        SUMU[tw] = dict(mx=max(x[0] for x in L), mn=min(x[0] for x in L), fl=max(x[1] for x in L), nR=sum(1 for x in L if x[2] == 'R'), n=len(L))
        out('  %s: per-use charge %+.3f .. %+.3f ns (median %+.3f); beyond the NULL rule SLOWER in %d of %d dense groups; worst per-use group floor %.3f ns' % (
            tw, SUMU[tw]['mn'], SUMU[tw]['mx'], hmed([x[0] for x in L]), SUMU[tw]['nR'], SUMU[tw]['n'], SUMU[tw]['fl']))
    out('  The charge is NOT proportional to the uses: the same ~1-2 us per pass appears at U = 2,000 and at U = 32,000 (tw1: +984 ns at U=2048, +1868 ns at U=32767), so a')
    out('  per-use rate is an UPPER bound only where U is small; the per-activation term of 7.1 plus a per-PASS (per landing-run) term is the better model.  (A least-squares')
    out('  a*A + b*U over the 11 groups gives b = +0.05..+0.06 ns/use for every twin with a residual of 0.3-2 us per pass, larger than the signal: not used.)')
    grp = collections.defaultdict(list)
    for tw, (single, form, ly, nf) in TWIN.items():
        grp[(ly, nf)].append(tw)
        key('kit.cdisp_use.DFA_SCAN.%s.%d.%sPATH' % (ly, nf, form), 'walkbytes', e6(SUMU[tw]['mx'] / u), e6(SUMU[tw]['mx']), 'measured',
            'UPPER bound: max over the dense dig groups (n=64Ki, streamed) of (%s - %s)/uses; NOT proportional to uses (an. 7.2); path-specific, NOT a finder key' % (tw, single), ly.lower(), e6(SUMU[tw]['fl'] / u), 'grid2read an. 7.2 (%s)' % tw)
    for (ly, nf), tws in grp.items():
        d = max(SUMU[t]['mx'] for t in tws)
        fl = max(SUMU[t]['fl'] for t in tws)
        key('kit.cdisp_use.DFA_SCAN.%s.%d' % (ly, nf), 'walkbytes', e6(d / u), e6(d), 'measured', 'UPPER bound over the dense dig groups and the dispatched paths %s; NOT proportional to uses (an. 7.2)' % '+'.join(TWIN[t][1] for t in tws), ly.lower(), e6(fl / u), 'grid2read an. 7.2')
        key('kit.ufloor.DFA_SCAN.%s.%d' % (ly, nf), 'walkbytes', e6(fl / u), e6(fl), 'measured', 'worst per-use A/A floor of the dense groups', ly.lower(), 0, 'grid2read an. 7.2')
    return SUMU


def scaffold():
    u = UNIT[0]
    out()
    out('7.3 THE WALK-IN-HELPER SCAFFOLD (sc0, M18): sc0 - walk, member-free, per call (fresh buffers; hex-run, word-eq, wcls):')
    for cell in ('f3-hex-run', 'f3-word-eq', 'f3-wcls'):
        for nm in ('n64k', 'n1m'):
            v = vis('F3', cell, 'g2-%s-%s-ginf-Lnone-S' % (cell, nm), 'first')
            if v is None or 'sc0' not in v.arm_vals:
                continue
            d = v.med('sc0') - v.med('walk')
            tag = '  [LOAD-SUSPECT visit: not used]' if v.n_load_hi else ''
            out('  %-11s %-5s sc0 %10.1f walk %10.1f  charge %+8.1f ns (%+.3f%%), floor %.1f%s' % (cell, nm, v.med('sc0'), v.med('walk'), d, 100 * d / v.med('walk'), floor(v), tag))
    out('  the scaffold costs nothing measurable per call at 64 KiB / 1 MiB (|charge| <= the group floor): M18 is below the floor in the long-N regime, but these are LONG calls;')
    out('  the short-N value of the helper-through-struct cost is not measured by sc0 (it exists only on member-free 64 KiB / 1 MiB groups): M18 for short N is BOUNDED ONLY by tw0 - walk (section 7.1), which also includes the dispatch.')
    ds = []
    for cell in ('f3-hex-run', 'f3-word-eq', 'f3-wcls'):
        v = vis('F3', cell, 'g2-%s-n64k-ginf-Lnone-S' % cell, 'first')
        ds.append((abs(v.med('sc0') - v.med('walk')), floor(v)))
    mx = max(d for d, f in ds)
    key('kit.cscaffold.WALK.DFA_SCAN', 'walkbytes', e6(mx / u), e6(mx), 'null', 'sc0 - walk, member-free single call n64k (hex-run, word-eq, wcls): max |charge|, <= 0.05% of the call; LONG calls only, the short-call/per-use helper cost is NOT measured', 'off',
        e6(max(f for d, f in ds) / u), 'grid2read an. 7.3')


def pay_rule(CALL, summ, SUMU, G):
    hdr('7b. THE PAY RULE T1-T3 EVALUATED ON GRID2\'S OPERANDS (rev 3 §2.5 [C4]; the shipped finder\'s operand spellings, finder.c pay_fill)')
    u = UNIT[0]
    out('Operand keys (kit-grid@2; the finder spells them first, PROVISIONALLY, until the cards fix them): "walkbytes" = ns / u, u = %.4f ns/B.' % u)
    out('  kit.delta.<ALT>.<PICK>.<KIND>.n<N>   = cost(ALT) - cost(PICK) of a single call at N, ALT/PICK in {WALK, V1, W64}                  <- an. 5.4')
    out('  kit.dfloor.<ALT>.<PICK>.<KIND>.n<N>  = the group\'s A/A floor at N (max of the #b and #c copies)                               <- an. 5.4')
    out('  kit.ffloor.<ALT>.<KIND>.n<B>         = the same floor, read at the interval\'s upper bound B for the NEXT form                  <- an. 5.4')
    out('  kit.cdisp_call.<KIND>.<LAYER>.<NFORMS>, kit.cfloor.<...>  = UPPER bound of the dispatch charge per activation + its floor      <- an. 7.1')
    out('  kit.cdisp_use.<KIND>.<LAYER>.<NFORMS>, kit.ufloor.<...>   = UPPER bound of the charge per use + its floor                        <- an. 7.2')
    out('  kit.wfloor.<PICK>.<KIND>             = the floor of the pick\'s per-use cost                                                      <- below')
    out('  LAYER in the finder is OFF / W16 / W32.  The twins cover (OFF, 2 forms: tw0 = WALK path, tw1 = V1 path) and (W32, 3 forms: tw2 = W64 path only).')
    out('  NOT MEASURED: any W16 twin (no S1 twin); the V1 or WALK path through the 3-form chain; DFA_HAT / HYB_PF / VM_ATTEMPT kinds for the single-call charge.')
    out('  The per-use charge was measured on the dig cell (kind DFA_SCAN) only; the dfa-hat and bounded dense groups carry twins as well (5-6 groups each, not reduced here).')
    out()
    c1 = summ['tw1']
    cw = summ['tw0']
    c2 = summ['tw2']
    for n in (8, 32, 48, 63, 64):
        v = G[n]
        out('  floors at N=%-3d: group A/A %.3f ns' % (n, floor(v)))
    out()
    out('T1 (pays where it fires) for R2 (pick V1, unpaid WALK, interval [0, 64) below the W64 block; alt = WALK):')
    out('  holds iff at EVERY measured N in the interval  (walk - V1) - dfloor > C_disp_call(V1 path) + cfloor;  V1-path charge (tw1, OFF, 2 forms): <= %+.3f ns, cfloor %.3f ns:' % (c1['mx'], c1['fl']))
    t1_ok = True
    for n in (8, 32, 48, 63):
        v = G[n]
        sv = v.med('walk') - v.med('V1')
        ok = sv - floor(v) > c1['mx'] + c1['fl']
        t1_ok = t1_ok and ok
        out('    N=%-3d  saving walk-V1 = %+6.2f ns  - dfloor %.3f = %+6.2f  vs  charge+cfloor %+5.2f  : %s' % (n, sv, floor(v), sv - floor(v), c1['mx'] + c1['fl'], 'holds' if ok else 'FAILS'))
    out('  => T1 for R2: %s (the interval is [0, 64) and its first measured point N = 8 fails; N = 32, 48, 63 and every staircase point 33..46 hold).' % ('HOLDS' if t1_ok else 'FAILS'))
    out('  R2 compared against its TERMINAL (W64) instead of the unpaid WALK: A1 - V1 = %s ns at N = 8, 32, 48, 63 (V1 is the better form below the block at SIMD-on; S1 loses by %s).' % (
        '/'.join('%+.2f' % (G[n].med('A1') - G[n].med('V1')) for n in (8, 32, 48, 63)), '/'.join('%+.2f' % (G[n].med('S1') - G[n].med('V1')) for n in (8, 32, 48, 63))))
    out('  R1 (pick WALK below N*, alt = the terminal V1): N* = 8 = the lowest measured point (staircase, an. 5.1): WALK never beats V1 at a measured N, so T1 FAILS (saving walk-V1 is negative at every measured point).')
    out()
    out('T2 (nothing measurable where the row does not fire): C_disp_call + cfloor <= floor(f_next at b), floors at b = 64: %.3f ns.' % floor(G[64]))
    for tw, c in (('tw0', cw), ('tw1', c1), ('tw2', c2)):
        out('    %s (%s path, %s, %d forms): charge upper bound %+.3f + cfloor %.3f = %+.3f ns  => T2 %s' % (
            tw, TWIN[tw][1], TWIN[tw][2], TWIN[tw][3], c['mx'], c['fl'], c['mx'] + c['fl'], 'FAILS' if c['mx'] + c['fl'] > floor(G[64]) else 'holds'))
    d2 = [G[n].med('tw2') - G[n].med('A1') for n in (64, 65, 128, 32, 48, 63)]
    out('  tw2 (the W64 path, N >= 64) is within the floors or faster at N = 64, 65, 128 (%+.2f, %+.2f, %+.2f ns: a layout effect) but is measurable at N = 32, 48, 63 (%+.2f, %+.2f, %+.2f);' % tuple(d2))
    out('  the upper bound over N <= 128 is what the pay rule reads, so T2 fails for it too.')
    out()
    out('T3 (nothing measurable per use): per dense group the twin must read NULL or FASTER than the single form (an. 7.2).')
    for tw in ('tw0', 'tw1', 'tw2'):
        out('    %s: SLOWER beyond the NULL rule in %d of %d dense dig groups (per-use charge up to %+.3f ns; worst group floor %.3f ns/use)  => T3 FAILS' % (
            tw, SUMU[tw]['nR'], SUMU[tw]['n'], SUMU[tw]['mx'], SUMU[tw]['fl']))
    wf = hmed([x for x in [floor(v) / max(own_counts(v, 'walk')['uses'], 1) for v in fa_groups('dig') if facts_of(v) and facts_of(v)['n'] == 65536 and not v.n_load_hi]])
    key('kit.wfloor.WALK.DFA_SCAN', 'walkbytes', e6(wf / u), e6(wf), 'measured', 'median over the dig n=64Ki find-all groups of (A/A floor / uses)', 'off', 0, 'grid2read an. 7b')
    out()
    out('VERDICT (DERIVED): T1 fails for R1 and holds for R2 only above N = 8; T2 FAILS on every twin; T3 FAILS on every twin.  Rev 3 §2.5 / §3.2: "if grid2\'s twins fail T1-T3, no dispatch')
    out('  ships at B4 and B8 waits for [REGIME-TWIN]".  The decision is B4 ships NO dispatch (R1 and R2 stay UNPAID rows).')


# ------------------------------------------------------------------------------------------
# 8. the one-byte arms (item 3, 3v): M19-M22, F1 / F2 / F0
# ------------------------------------------------------------------------------------------
OBKINDS = [('o-fwd', 'DFA_SCAN', 'fwd'), ('o-bnd', 'DFA_SCAN', 'bounded'), ('o-hat', 'DFA_HAT', ''), ('o-hyb', 'HYB_PF', ''),
           ('o-back', 'DFA_ATTEMPT', 'back'), ('o-vm', 'VM_ATTEMPT', '')]
OBARMS = ['walk', 'libc', 'v1', 'loop', 'none']
GAPS = [2, 8, 32, 256, 4096, 0]


def ob_visit(cell, tail, mode):
    return vis('OB', cell, 'ob_%s-%s' % (cell, tail), mode)


def onebyte():
    hdr('8. THE ONE-BYTE ARMS (item 3, 3v, NONE): LIBC / WALK at |S|=1 / V1 one-term / the generic loop / NONE at five DFA kinds and the VM hat (M19-M22, F0-F2)')
    u = UNIT[0]
    out('Arms: walk = the table walk at |S| = 1 (o-back: the hand back-walk); libc = the artifact as the compiler emits it (memchr); v1 = one-term SWAR, STATELESS here (HDR); loop = the generic')
    out('byte loop; none = the use\'s FIND deleted (the consumer walks).  o-vm: walk = the compiler\'s table walk, v1 = the compiler\'s own stateful V1 text, libc = memchr (evidence only).')
    out('ns per call (member-free single calls n = 8, 32, 64, 1 MiB) and ns per 64 KiB pass (find-all over 6 gaps, L = 64 KiB: one planted match per buffer-call).  verdict vs the walk.')
    RES = {}
    for cell, kind, tag in OBKINDS:
        out()
        out('%s  (kind %s%s)' % (cell, kind, (' ' + tag) if tag else ''))
        arms = [a for a in OBARMS if any(a in ob_visit(cell, 'n8-ginf-Lnone-S', 'first').arm_vals for _ in [0])]
        arms = [a for a in OBARMS if a in ob_visit(cell, 'n8-ginf-Lnone-S', 'first').arm_vals or a in ob_visit(cell, 'n64k-g2-L64k-S', 'all').arm_vals]
        out('  single calls (ns):  ' + ' '.join('%9s' % a for a in arms))
        sing = {}
        for n in ('n8', 'n32', 'n64', 'n1m'):
            v = ob_visit(cell, n + '-ginf-Lnone-S', 'first')
            sing[n] = v
            row = '  %-6s floor %7.2f ' % (n, floor(v))
            for a in arms:
                if a in v.arm_vals:
                    d = v.med(a) - v.med('walk')
                    row += ' %9.2f' % v.med(a) if a == 'walk' else ' %9.2f' % v.med(a)
                else:
                    row += ' %9s' % '-'
            out(row)
            row = '         d vs walk       '
            for a in arms:
                if a in v.arm_vals and a != 'walk':
                    row += ' %+8.2f%s' % (v.med(a) - v.med('walk'), verdict(v, a, 'ob_first'))
                else:
                    row += ' %9s' % ''
            out(row)
        # F and beta per arm (beta from n64 -> n1m, F from n8)
        row = '  beta ns/B (n64->n1m): '
        FB = {}
        for a in arms:
            if all(a in sing[n].arm_vals for n in ('n8', 'n64', 'n1m')):
                b = (sing['n1m'].med(a) - sing['n64'].med(a)) / (1048576 - 64)
                Fx = sing['n8'].med(a) - 8 * b
                FB[a] = (Fx, b)
                row += ' %s %.4f' % (a, b)
        out(row)
        out('  F ns (T(8) - 8 beta):  ' + '  '.join('%s %.2f' % (a, FB[a][0]) for a in FB))
        gl = {}
        out('  find-all, ns per 64 KiB pass, by gap g (bytes between landings; 0 = absent):  ' + ' '.join('%9s' % ('g=inf' if g == 0 else 'g=%d' % g) for g in GAPS))
        for g in GAPS:
            nm = 'n64k-%s-L64k-S' % ('ginf' if g == 0 else ('g4k' if g == 4096 else 'g%d' % g))
            gl[g] = ob_visit(cell, nm, 'all')
        for a in arms:
            row = '  %-5s      ' % a
            for g in GAPS:
                v = gl[g]
                if a in v.arm_vals:
                    if a == 'walk':
                        row += ' %9.0f' % v.med(a)
                    else:
                        d = v.med(a) - v.med('walk')
                        row += ' %+7.1f%%%s' % (100 * d / v.med('walk'), verdict(v, a, 'ob_all'))
                else:
                    row += ' %9s' % '-'
            out(row)
        out('  (walk row: absolute ns per pass; other rows: % vs the walk and the NULL-rule verdict W faster / N / R slower)')
        RES[cell] = dict(sing=sing, gl=gl, FB=FB, arms=arms)
    return RES


def onebyte_derived(RES):
    hdr('8b. M19-M22 DERIVED: dominance of a libc-free form over LIBC (F1), NONE\'s gap threshold (F0), the VM hat (F2), D1\'s regret')
    u = UNIT[0]
    out('8b.1 WHICH ARM IS BEST (best-or-tied = within the cell\'s A/A floor of the cell minimum) over the 10 cells of a kind (4 member-free lengths + 6 gaps), and LIBC\'s regret:')
    out('%-7s %-12s | best-or-tied cells: %-6s %-6s %-6s %-6s | LIBC regret vs the cell minimum: worst (cell)' % ('cell', 'kind', 'libc', 'walk', 'v1', 'loop'))
    DOM = {}
    for cell, kind, tag in OBKINDS:
        r = RES[cell]
        cells = []
        names = []
        for n in ('n8', 'n32', 'n64', 'n1m'):
            cells.append(r['sing'][n])
            names.append(n)
        for g in GAPS:
            cells.append(r['gl'][g])
            names.append('g=inf' if g == 0 else 'g=%d' % g)
        best_is = collections.Counter()
        worst = (0.0, '')
        for v, nm in zip(cells, names):
            ts = {a: v.med(a) for a in ('libc', 'walk', 'v1', 'loop') if a in v.arm_vals}
            best = min(ts.values())
            for a in ts:
                if ts[a] <= best + floor(v):
                    best_is[a] += 1
            rg = 100 * (ts['libc'] / best - 1)
            if rg > worst[0]:
                worst = (rg, nm)
        DOM[cell] = worst
        out('%-7s %-12s | %-27s %6d %6d %6d %6d | %+.0f%% (%s)' % (cell, kind, '', best_is['libc'], best_is['walk'], best_is['v1'], best_is['loop'], worst[0], worst[1]))
    out('  => LIBC is best-or-tied on 8-9 of 10 cells of every kind (every cell but the dense g = 2 one and, on o-fwd/o-hyb/o-vm, n = 8), and loses by +%.0f%% to +%.0f%% at g = 2; there the walk, the loop' % (
        min(w[0] for w in DOM.values()), max(w[0] for w in DOM.values())))
    out('     and NONE sit within a few % of each other.  No libc-free form is best-or-tied on more than one cell of any kind (v1, stateless one-term, wins n = 8 on o-fwd, o-hyb and o-vm only).  LIBC\'s own speed at long N is the host libc\'s ifunc-selected SIMD memchr (7.8 us per MiB = 0.0074 ns/B), so the')
    out('     SIMD-OFF label does not describe it: a LIBC row is a SIMD-on-by-the-host form at both kit layers.')
    out()
    out('8b.2 DOMINANCE (M21 = kit.dom.<f>.LIBC.<kind>): f dominates LIBC iff on EVERY measured cell f is not slower than LIBC beyond the group\'s NULL threshold.')
    for cell, kind, tag in OBKINDS:
        r = RES[cell]
        cells = [r['sing'][n] for n in ('n8', 'n32', 'n64', 'n1m')] + [r['gl'][g] for g in GAPS]
        line = []
        for a in ('walk', 'v1', 'loop'):
            if a not in r['arms']:
                continue
            slower = 0
            faster = 0
            for v in cells:
                if a in v.arm_vals and 'libc' in v.arm_vals:
                    d = v.med(a) - v.med('libc')
                    thr = max(floor(v), FRG.get(regime_of(v), 0) * v.med('libc'))
                    if d > thr:
                        slower += 1
                    elif d < -thr:
                        faster += 1
            line.append('%s: slower than LIBC on %d, faster on %d of %d cells -> dom = %d' % (a, slower, faster, len(cells), 1 if slower == 0 else 0))
            tkind = 'DFA_SCAN' if cell in ('o-fwd', 'o-bnd') else kind
            key('kit.dom.%s.LIBC.%s%s' % ({'walk': 'WALK', 'v1': 'V1', 'loop': 'LOOP'}[a], tkind, '.bounded' if cell == 'o-bnd' else ('.back' if cell == 'o-back' else '')), 'bool', 1000000 if slower == 0 else 0, '-', 'derived',
                 'one-byte dominance over LIBC: slower than LIBC beyond the NULL rule on %d of %d measured cells' % (slower, len(cells)), 'off', 0, 'grid2read an. 8b.2')
        out('  %-7s %-12s %s' % (cell, kind, ' | '.join(line)))
    out('  => kit.dom is 0 for every (libc-free form, kind): F1 (a measured libc row may displace D1) has NO form to displace D1 with; F1 does not fire on this data.')
    out()
    out('8b.3 D1\'s regret (D1 = the default libc row, Q-WR-1; UNMEASURED-DEFAULT) per kind: libc vs the best arm per gap cell (find-all, L = 64 KiB):')
    out('%-7s %-12s %s' % ('cell', 'kind', ' '.join('%9s' % ('g=inf' if g == 0 else 'g=%d' % g) for g in GAPS)))
    for cell, kind, tag in OBKINDS:
        r = RES[cell]
        row = ''
        for g in GAPS:
            v = r['gl'][g]
            ts = {a: v.med(a) for a in r['arms'] if a in v.arm_vals}
            best = min(ts.values())
            row += ' %+8.0f%%' % (100 * (v.med('libc') / best - 1))
        out('%-7s %-12s %s' % (cell, kind, row))
    out('  (positive: libc is slower than the best timed arm of that cell; at g = 2 the best is the walk (or none), at g >= 8 libc is best or tied.)')
    out()
    out('8b.4 libc vs the walk: the gap crossover (log2-interpolated zero of libc - walk between consecutive gaps), and F, beta (M19/M20):')
    for cell, kind, tag in OBKINDS:
        r = RES[cell]
        seq = []
        for g in GAPS:
            v = r['gl'][g]
            seq.append((g if g else 8192, v.med('libc') / v.med('walk') - 1.0))
        cr = None
        for (g1, d1), (g2, d2) in zip(seq, seq[1:]):
            if d1 > 0 and d2 <= 0:
                t = d1 / (d1 - d2)
                cr = math.exp(math.log(g1) + t * (math.log(g2) - math.log(g1)))
                break
        fb = r['FB']
        out('  %-7s %-12s libc beats the walk from g* ~ %s B (between the g = %s and g = %s cells; two measured points straddle it);  F(libc) %.2f  beta(libc) %.5f; F(walk) %.2f beta(walk) %.4f; F(v1) %s' % (
            cell, kind, ('%.1f' % cr) if cr else 'n/a', '2', '8', fb['libc'][0], fb['libc'][1], fb['walk'][0], fb['walk'][1], ('%.2f beta %.4f' % fb['v1']) if 'v1' in fb else '-'))
        tkind = 'DFA_SCAN' if cell in ('o-fwd', 'o-bnd') else kind
        suffix = '.bounded' if cell == 'o-bnd' else ('.back' if cell == 'o-back' else '')
        for a, form in (('libc', 'LIBC'), ('walk', 'WALK'), ('v1', 'V1'), ('loop', 'LOOP')):
            if a in fb:
                lay = 'off'
                key('kit.f.%s.%s%s.n8' % (form, tkind, suffix), 'walkbytes', e6(fb[a][0] / u), e6(fb[a][0]), 'measured', 'one-byte stop, streamed single call, T(8)-8*beta (cell %s)' % cell, lay, e6(floor(r['sing']['n8']) / u), 'grid2read an. 8b.4')
                key('kit.beta.%s.%s%s.r0e1c0' % (form, tkind, suffix), 'ratio', e6(fb[a][1] / u), e6(fb[a][1]), 'measured', 'one-byte stop, slope n64->n1m (cell %s)' % cell, lay, e6(floor(r['sing']['n1m']) / r['sing']['n1m'].med('walk')), 'grid2read an. 8b.4')
        if cr:
            key('kit.xover.LIBC.WALK.%s%s' % (tkind, suffix), 'bytes', e6(cr), '-', 'derived', 'gap at which LIBC overtakes the walk (find-all, 2 straddling cells: INTERPOLATED(2, 8))', 'off', 0, 'grid2read an. 8b.4')
    out()
    out('8b.5 NONE (F0; M22): the largest measured gap at which NONE beats the walk (W), NONE vs LIBC, per kind (find-all, L = 64 KiB):')
    for cell, kind, tag in OBKINDS:
        r = RES[cell]
        if 'none' not in r['arms']:
            out('  %-7s %-12s no NONE arm (%s)' % (cell, kind, 'o-back: evidence only, the hand walk is its base' if cell == 'o-back' else 'VM hat: the seek is REQUIRED, NONE is not a form there'))
            continue
        vw = []
        vl = []
        for g in GAPS:
            v = r['gl'][g]
            vw.append('%s %s' % ('inf' if g == 0 else g, verdict(v, 'none', 'ob_all')))
            d = v.med('none') - v.med('libc')
            thr = max(floor(v), FRG['ob_all'] * v.med('libc'))
            vl.append('%s %s' % ('inf' if g == 0 else g, 'N' if abs(d) <= thr else ('W' if d < 0 else 'R')))
        wins = [g for g in GAPS if verdict(r['gl'][g], 'none', 'ob_all') == 'W']
        ties = [g for g in GAPS if verdict(r['gl'][g], 'none', 'ob_all') in ('W', 'N')]
        gnone = max([g for g in wins if g]) if [g for g in wins if g] else None
        gtie = max([g for g in ties if g]) if [g for g in ties if g] else None
        out('  %-7s %-12s none vs walk by g: %s   | none vs libc by g: %s' % (cell, kind, ', '.join(vw), ', '.join(vl)))
        out('       NONE faster than the walk beyond the NULL rule at g in %s (g_none strict = %s); faster-or-NULL at g in %s (tie-inclusive = %s)' % (wins, gnone, ties, gtie))
        tkind = 'DFA_SCAN' if cell in ('o-fwd', 'o-bnd') else kind
        suffix = '.bounded' if cell == 'o-bnd' else ''
        if cell != 'o-back':
            key('kit.gnone.%s%s' % (tkind, suffix), 'bytes', e6(gnone) if gnone else -1, '-', 'derived',
                'NONE vs WALK, find-all L=64Ki: %s; tie-inclusive %s' % ('largest measured gap where NONE is faster beyond the NULL rule' if gnone else 'NONE is never faster than the walk beyond the NULL rule on the six measured gaps', gtie),
                'off', 0, 'grid2read an. 8b.5 (INTERPOLATED on the gap grid {2,8,32,256,4096,inf}; lowest measured gap is 2)')
    out()
    out('8b.6 THE VM HAT AT |S| = 1 (F2 `vm-hat-1b`: kit.saving.V1.WALK.VM_ATTEMPT.(0,1,0) > kit.eps.<regime>):')
    r = RES['o-vm']
    fb = r['FB']
    sv = 1 - fb['v1'][1] / fb['walk'][1]
    out('  single-call slope (n64 -> n1m): walk %.4f ns/B, v1 %.4f ns/B  => saving = 1 - beta_v1/beta_walk = %+.3f;  libc (evidence) %.5f ns/B' % (fb['walk'][1], fb['v1'][1], sv, fb['libc'][1]))
    out('  kit.eps.streamed.slope = %.4f%%: the F2 row\'s test (saving > eps) is MET by %.1f x; as rev 3 §1.3 row 3 is written (a beta saving only), F2 would route the VM hat to V1.' % (
        100 * [k for k in KEYS if k[0] == 'kit.eps.streamed.slope'][0][2] / 1e6, sv / ([k for k in KEYS if k[0] == 'kit.eps.streamed.slope'][0][2] / 1e6)))
    out('  find-all at the VM hat (ns per pass): ')
    for g in GAPS:
        v = r['gl'][g]
        out('    g=%-5s walk %8.0f  v1 %8.0f (%+6.1f%% %s)  libc %8.0f (%+6.1f%% %s)' % ('inf' if g == 0 else g, v.med('walk'), v.med('v1'), 100 * (v.med('v1') / v.med('walk') - 1), verdict(v, 'v1', 'ob_all'),
                                                                                    v.med('libc'), 100 * (v.med('libc') / v.med('walk') - 1), verdict(v, 'libc', 'ob_all')))
    out('  => V1 at the VM hat wins at g >= 8 (-%.0f%% at g = 8) and LOSES at g = 2 (%+.0f%%): a single beta saving prices only the sparse half; the dense-gap loss is the same predictability/state effect as an. 6d.' % (
        100 * (1 - r['gl'][8].med('v1') / r['gl'][8].med('walk')), 100 * (r['gl'][2].med('v1') / r['gl'][2].med('walk') - 1)))
    key('kit.saving.V1.WALK.VM_ATTEMPT.r0e1c0', 'ratio', e6(sv), '-', 'derived', 'derived: 1 - beta_v1/beta_walk, VM hat |S|=1, single-call slope; NOTE g = 2 find-all loses %+.0f%%' % (100 * (r['gl'][2].med('v1') / r['gl'][2].med('walk') - 1)),
        'off', e6(floor(r['sing']['n1m']) / r['sing']['n1m'].med('walk')), 'grid2read an. 8b.6')
    return DOM


# ------------------------------------------------------------------------------------------
# 9. the pre-scan trigger probe (item 8, M23)
# ------------------------------------------------------------------------------------------
def trigger():
    hdr('9. THE PRE-SCAN TRIGGER PROBE (item 8, M23): KEEP the whole-window pre-check vs DROP it (-fno-req-byte -fno-req-run), DFA route, first-mode single calls over 64 KiB')
    u = UNIT[0]
    out('Q-WR-9: P1 (the priced pre-scan) is built only once "a TUG cell is measured LOSING for want of it".  TUG = bytes per landing < 18.5 (g = 8 qualifies, g = 32 does not).')
    out('%-10s %-6s %-7s | %10s | %10s %9s %-3s | %s' % ('cell', 'g', 'byte', 'keep ns', 'drop ns', 'd', 'v', 'reading'))
    TR = []
    for v in VIS['TRIG']:
        m = re.match(r'g2-(trig-\w+)-n64k-g(\d+)-(\w+)-S$', v.key[1])
        g = int(m.group(2))
        pos = m.group(3)
        d = v.med('drop') - v.med('keep')
        vd = verdict(v, 'drop', 'trig')
        if pos == 'absent':
            rd = 'DROP loses x%.0f (the pre-check answers the call: it is the whole point)' % (v.med('drop') / v.med('keep'))
        elif vd == 'W':
            rd = 'DROP wins %.2f ns (%.1f%% of the call): KEEP pays the pre-scan' % (-d, -100 * d / v.med('keep'))
        elif vd == 'R':
            rd = 'DROP loses %.1f ns (%.2f%%)' % (d, 100 * d / v.med('keep'))
        else:
            rd = 'NULL'
        out('%-10s %-6s %-7s | %10.2f | %10.2f %+9.2f %-3s | %s' % (v.key[0], 'TUG g%d' % g if g < 18.5 else 'g%d' % g, pos, v.med('keep'), v.med('drop'), d, vd, rd))
        TR.append((v.key[0], g, pos, d, vd, v.med('keep'), floor(v)))
    ABS = [v.med('drop') / v.med('keep') for v in VIS['TRIG'] if v.key[1].endswith('-absent-S')]
    tug = [t for t in TR if t[1] < 18.5 and t[2] != 'absent']
    fired = [t for t in tug if t[4] == 'W']
    out()
    out('TUG cells with the byte PRESENT (early, late): %d; KEEP measured losing (DROP faster beyond the NULL rule) in %d of them: %s.' % (
        len(tug), len(fired), '; '.join('%s g%d %s %.2f ns' % (t[0], t[1], t[2], -t[3]) for t in fired)))
    out('Q-WR-9\'s trigger, read literally ("a TUG cell measured losing for want of it"): FIRES on these cells, but the loss is %.2f-%.2f ns per call on EARLY cells (%.1f-%.1f%% of a 40-46 ns call)'
        % (min(-t[3] for t in fired if t[2] == 'early'), max(-t[3] for t in fired if t[2] == 'early'),
           min(-100 * t[3] / t[5] for t in fired if t[2] == 'early'), max(-100 * t[3] / t[5] for t in fired if t[2] == 'early')))
    out('  and under 0.7%% on LATE cells (NULL); against it the pre-check wins x%.0f-x%.0f on the ABSENT cells.  Whether the trigger "fires" is therefore a question of the pre-scan\'s PRICE ' % (
        min(ABS), max(ABS)))
    out('  (P1 prices keep vs drop by expected cost): the data give P1 its operands (early cost 1.5-1.8 ns/call, late ~0 within 0.6%, absent -x100) but no rule has been asked of them.')
    for pos in ('early', 'late', 'absent'):
        L = [t for t in TR if t[2] == pos]
        kd = [-t[3] for t in L]                 # KEEP - DROP: positive = the pre-check costs
        key('kit.gate.byte1.DFA_SCAN.%s' % pos, 'walkbytes', e6(hmed(kd) / u), e6(hmed(kd)), 'null' if all(t[4] == 'N' for t in L) else 'measured',
            'KEEP - DROP per call, median over trig-dig/trig-word x g8/g32 (range %+.2f..%+.2f ns); positive = the pre-check costs, negative = it saves' % (min(kd), max(kd)), 'off', e6(max(t[6] for t in L) / u), 'grid2read an. 9 (M23: P1 operand, not a row)')
    return TR




# ------------------------------------------------------------------------------------------
# 10. F2S (real text perf), shape (0,1,1), predictions, rev 3 assumptions, keys
# ------------------------------------------------------------------------------------------
def f2s():
    hdr('6e. F2S (optional, item 7): REAL TEXT, user-space cycles per pass and branch misses (perf; NOT a timed verdict: no A/A, cycles:u only)')
    rows = {}
    for ln in open('%s/f2s.log' % OUT):
        p = ln.split()
        if len(p) == 8 and p[0] != 'cell' and not ln.startswith('#'):
            rows[(p[0], p[1].replace('g2-real-', '').replace('-S', ''), p[2])] = (float(p[3]), float(p[6]), float(p[7]))
    out('cycles/pass of the arm and its change against the walk; branch misses per KiB.  (hex-run = [a-f0-9]+, bounded = [a-z]+\\b, dfa-hat = \\b(true|false|null)\\b over real prose/docs/code, streamed.)')
    out('%-8s %-6s | %12s | %-22s | %-22s | %-22s | %-22s' % ('cell', 'text', 'walk cyc', 'V1 cyc  d%  miss/KiB', 'A1 cyc  d%  miss/KiB', 'A3 cyc  d%  miss/KiB', 'walk miss/KiB'))
    for cell in ('hex-run', 'bounded', 'dfa-hat'):
        for tx in ('prose', 'docs', 'code'):
            w = rows[(cell, tx, 'walk')]
            parts = []
            for a in ('V1', 'A1', 'A3'):
                r = rows[(cell, tx, a)]
                parts.append('%9.0f %+5.1f%% %6.1f' % (r[0], 100 * (r[0] / w[0] - 1), r[2]))
            out('%-8s %-6s | %12.0f | %s | %6.1f' % (cell, tx, w[0], ' | '.join(parts), w[2]))
    out('  Real text puts the forms in the regime the named residual describes: bounded on prose loses +17% (V1) / +19% (A1) in cycles, dfa-hat on prose loses +9% at V1 and wins -14% at A1, hex-run is a wash at V1 and -3% / -20% at A1 / A3.')
    out('  (cycle counts only; the timed ledger of rev 3 §9.3 for these subjects belongs to E4b/E5, not to this slot.)')


def shape011():
    hdr('4c. THE (0,1,1) SHAPE (dfa-hat): beta ratios from the member-free-equivalent group dfa-hat ginf L64k (one find per 64 KiB buffer, no landing)')
    out('grid2 has no member-free dfa-hat cell in F3; the F1 group g2-dfa-hat-n64k-ginf-L64k-S is one call per buffer with nothing to find: T = F + beta*65536.  beta = (T - F_arm)/65536, F_arm from an. 5 (median of n=64,65,128).')
    v = vis('F1', 'dfa-hat', 'g2-dfa-hat-n64k-ginf-L64k-S', 'all')
    G = dig_first_groups()
    Fm = {}
    for a in ('walk', 'V1', 'S1', 'A1'):
        Fm[a] = hmed([G[n].med(a) - BETA['f3-dig'][a] * n for n in (64, 65, 128)])
    r = {a: (v.med(a) - Fm[a]) / 65536 for a in ('walk', 'V1', 'S1', 'A1')}
    out('  T: ' + '  '.join('%s %.0f' % (a, v.med(a)) for a in ('walk', 'V1', 'S1', 'A1')) + ' ns;   beta: ' + '  '.join('%s %.4f' % (a, r[a]) for a in r))
    u = UNIT[0]
    for a in ('V1', 'S1', 'A1'):
        sv = 1 - r[a] / r['walk']
        g1 = 1 - GRID1['beta'][a][(0, 1, 1)] / GRID1['beta']['WALK'][(0, 1, 1)]
        out('  saving %s = %+.3f  (grid1 (0,1,1): %+.3f)' % (a, sv, g1))
        key('kit.saving.%s.WALK.r0e1c1' % a, 'ratio', e6(sv), '-', 'derived', 'dfa-hat ginf-L64k, (T-F)/n; no member-free dfa-hat cell in grid2 (F-corrected one-call group)', 'off' if a == 'V1' else ('w16' if a == 'S1' else 'w32'), e6(floor(v) / v.med('walk')), 'grid2read an. 4c')
        key('kit.beta.%s.DFA_HAT.r0e1c1' % ('WALK' if a == 'walk' else a), 'ratio', e6(r[a] / u), e6(r[a]), 'derived', 'as above', 'off' if a == 'V1' else ('w16' if a == 'S1' else 'w32'), e6(floor(v) / v.med('walk')), 'grid2read an. 4c')


def predictions(G, CROSS, T):
    hdr('10. THE §9.3 PREDICTIONS AND THE rev 3 ASSUMPTIONS AGAINST THIS SLOT')
    eps_slope = [k for k in KEYS if k[0] == 'kit.eps.streamed.slope'][0][2] / 1e6
    eps_fa = [k for k in KEYS if k[0] == 'kit.eps.findall.l64k'][0][2] / 1e6
    out("Each prediction is an inequality on named groups (rev 3 §9.3 [C6]); its NUMBERS are E4b's; below is what THIS slot (streamed, kit-grid@2) says, with the floor and the layer.")
    out()
    out('P1 (R0): "for the hex-run and word-eq find-all groups at OFF, |pick - walk| <= max(A/A, floor)".')
    out('   grid2 times NO hex-run or word-eq find-all group (they are member-free single-call and perf-only groups), so the prediction cannot be scored as written.  What exists:')
    sh = [1 - BETA[c]['V1'] / BETA[c]['walk'] for c in ('f3-hex-run', 'f3-word-eq', 'f3-quad', 'f3-wcls')]
    out(f'   member-free beta savings of V1 over the walk: hex-run {100*sh[0]:+.2f}%, word-eq {100*sh[1]:+.2f}% (provisional), quad {100*sh[2]:+.2f}% (provisional), wcls {100*sh[3]:+.2f}%.')
    out(f'   R0 reads the CLASS key kit.saving.V1.WALK.r2 = max over the measured r2 shapes = {100*sh[0]:+.2f}% (hex-run).  Under kit.eps.streamed.slope = {100*eps_slope:.3f}% R0 does NOT fire ({100*sh[0]:+.2f}% > {100*eps_slope:.3f}%);')
    out(f'   hex-run then goes to R7 (pick V1, a {100*sh[0]:.1f}% member-free GAIN over the walk: not NULL) and word-eq/quad/wcls reach WALK through R7w, not R0.')
    out(f'   Under kit.eps.findall.l64k = {100*eps_fa:.3f}% R0 would fire ({100*sh[0]:+.2f}% <= {100*eps_fa:.3f}%) and hex-run is the walk.  The prediction "R0 turns hex-run NULL" is TRUE only under the find-all token;')
    out('   under the shipped slope token the pick for hex-run is V1 (a WIN, 4.9x the slope-based noise).  word-eq: V1 loses 13%, so the pick is WALK and the prediction holds (trivially).')
    out()
    out('P2 (R7 on measured shapes): "for the (1,0,0) and (0,1,1) groups and item 3a\'s three shapes at OFF, pick - walk <= -floor at every L >= the shape\'s measured crossover".')
    out('   crossover: the V1 crossover is below the lowest measured N (8 B): every L is >= it.')
    bad = collections.defaultdict(list)
    tot = collections.Counter()
    for cell in ('dig', 'bounded', 'dfa-hat'):
        for v in fa_groups(cell):
            if v.n_load_hi:
                continue
            f = facts_of(v)
            if f is None or f['n'] != 65536 or f['U'] == 0:
                continue
            tot[cell] += 1
            vd = verdict(v, 'V1', 'findall')
            if vd != 'W':
                bad[cell].append((f['g'], f['L'], f['shape'], vd, 100 * (v.med('V1') / v.med('walk') - 1)))
    for cell in ('dig', 'bounded', 'dfa-hat'):
        out(f'   {cell:<8} find-all (n=64Ki, U>0) groups: {tot[cell]}; V1 NOT faster than the walk beyond the floor in {len(bad[cell])}:')
        for g, L, shp, vd, d in sorted(bad[cell]):
            out('       g=%-4s L=%-6s %-5s %s %+6.1f%%' % ('inf' if g == 0 else g, L, shp, vd, d))
    out('   Item 3a (c020, c001, c110, member-free): V1 wins by %s (single calls n64k/n1m, NULL floor 0.1%%): HOLDS.' % ', '.join('%.0f%%' % (100 * (1 - BETA[c]['V1'] / BETA[c]['walk'])) for c in ('f3-c020', 'f3-c001', 'f3-c110')))
    nullk = [(c, g, L) for c in ('dig', 'bounded', 'dfa-hat') for (g, L, shp, vd, d) in bad[c] if shp == 'u' and L >= 1024 and g >= 4 and vd == 'N']
    out('   => P2 holds (V1 faster beyond the floor) on the member-free regime the keys were measured in and on every u-shaped group of L >= 1 KiB at g >= 4 EXCEPT %d NULL ties (%s),' % (
        len(nullk), ', '.join('%s g=%d L=%d' % x for x in nullk)))
    out('      and FAILS in a named region: the dense regular groups (g = 2, and reg g = 8) at every L, the L <= 8 groups, and the L = 32 groups at g >= 16.  Those are the "named residual" of')
    out('      §9.2 item 3, now with measured sizes (V1 +15..+46% at g = 2).  It is the shape R5 would route to the walk, but R5 reads E at MEASURED provenance only, so on a default')
    out("      compile it does not fire: the loss SHIPS, bounded by the judge's G2/G3 caps (§9.2 item 3).")
    out()
    out('P3 (R1, if paid): not paid: there is no interval (the crossover is below the staircase) and T1/T2/T3 fail (an. 7b).  The prediction is moot.')
    out('P4 (regret on the grid): "R0 and R7 change find-all grid rows (R0 turns hex-run and word-eq to NULL); R1 and R2 change only single-call rows".  Not scored (no hex-run/word-eq grid rows here).')
    out('P5 (dfa-hat prose contradicts R5; F7): real prose is perf-only here (an. 6e): dfa-hat prose V1 +9% cycles, A1 -14% cycles (SIMD-on gains), consistent with a residual at OFF; NOT timed.')
    out('P6 (no SIMD-on prediction at B4): CONFIRMED vacuous; SIMD-on beta/F/g* are reported for B6: S1/A1 beat the walk at every N >= 64 and every g >= 4; below 64 B S1 loses by up to +13.7 ns (n=63) and A1 by +2.8, V1 is the better form below the block.')
    out()
    out('rev 3 assumptions tested by this slot, with the verdict:')
    out(f' A1  "kit.eps.streamed.slope is gridread F3\'s A/A p90 (0.173%)": the grid2 figure is {100*eps_slope:.3f}% (#b p90, 14 quiet groups; pooled #b+#c 0.126%): same order, lower; CONFIRMED as a regime-split token.')
    out(f'     The regime split itself is CONFIRMED: F3 member-free {100*eps_slope:.3f}% vs F1 find-all {100*eps_fa:.3f}% (11.6x); but the quantity the savings derive from, the SLOPE, has noise 0.25% p90 / 0.32% max (an. 4),')
    out('     2.2x the token: the token under-states the noise of kit.saving.* (no decision flips: the nearest margin is hex-run, 1.21% vs 0.25%).')
    out(" A2  \"M9: V1 crossover 36 B INTERPOLATED(32,48)\": CONTRADICTED.  With the compiler's own V1 text, streamed fresh buffers, V1 beats the walk at EVERY measured N from 8 B (-0.18 ns, 4.5x its floor) to 1 MiB.")
    out("     Rows R1 (interval [0, xover)) and R2's lower end therefore have no interval; M12's +2.3/+0.6 ns at N = 8/32 become -0.18/-2.87 ns.  (Cause not isolated: grid1's V1 arm was the spike/mkvar text, not this compiler's; this slot cannot say which difference matters.)")
    out(' A3  "M15 g*: V1 10.8-16.7 / 3.0-3.3 / 21.5 B; S1 4.3-4.7 ...; A1 4.2-4.4 ...": NOT REPRODUCED as a g threshold.  On the streamed u-shaped series the forms win from g = 4 up (V1 -23.7% at g=4, dig L=64k); the')
    out('     only losses are at g = 2 (a REGULAR landing offset: all forms +0.5..+46%) and at L <= 32.  g* is a function of the landing-offset predictability (an. 6d: reg g8 V1 +34.9%, u g8 V1 -23.6%), not of the gap alone.')
    out(' A4  "M13 c_cold +2.47/+2.90/+2.91 ns; M14 w_use 1.67/2.38/2.22/2.23": CONFIRMED for V1 (+2.45) and w (1.60/2.24/2.15/2.18 on dig); the wide forms\' c_cold is +17-25% higher (S1 +3.64, A1 +3.41 ns).')
    out(' A5  "single-call F ~ 4.2-5.0 ns at n >= 64": CONFIRMED for V1/S1/A1 (4.4/4.6/5.4); the walk is +1.1 ns higher on streamed buffers (5.9 vs 4.74); the sub-block tail (S1 +24.5, A1 +14.7 at n=48) CONFIRMED (21.7/12.9).')
    out(' A6  "beta by shape": CONFIRMED to 0.1-3.3% on all 11 comparable cells (V1, S1, A1 x dig, hex-run, word-eq, quad; A1 word-eq is not usable); word-eq/quad are provisional (load-suspect sources).')
    out(" A7  pay-rule operand spellings (finder.c, provisional): `kit.delta.<alt>.<pick>` orientation is alt - pick; grid1's interim set carries V1.WALK only; R2 needs WALK.V1 and the floors dfloor/ffloor/cfloor/ufloor/wfloor, none of")
    out("     which any earlier set carries.  grid2 supplies them (keys.tsv) in the finder's own spelling, for OFF (tw0/tw1, 2 forms) and W32 (tw2, 3 forms); W16 has no twin (not supplied).")
    out('     The charge is NOT negligible: tw1 (V1 path) +0.2..+0.74 ns per call, tw0 (WALK path) +1.6..+2.4 ns, tw2 (W64 path) -0.3..+0.3 ns; per use up to +0.35 (tw2) / +0.48 (tw1) / +0.59 (tw0) ns.  T2 and T3 FAIL; T1 holds only for R2 above N = 8.')
    out(' A8  "if grid2\'s twins fail T1-T3, no dispatch ships at B4 and B8 waits for [REGIME-TWIN]": that branch is TAKEN.')
    out(' A9  "R2: pick V1, unpaid WALK": the UNPAID pick is the worst form below the block: at N = 48/63 the walk is +4.98/+6.60 ns slower than V1 and S1/A1 lose to V1 by +14.0/+20.3 and +4.6/+9.4 ns.  A row that fails T1 and falls to WALK is a regression against the terminal')
    out("     (W64: -0.35/+2.79 ns vs walk at 48/63).  Finding for B4: R2's `unpaid` should be the terminal pick (drop the row), not WALK.")
    out(' A10 "D1 (one member, not a VM attempt seek) -> LIBC, UNMEASURED-DEFAULT": D1 is measured here: LIBC regret +69..+208% at g = 2, best-or-tied elsewhere; F1 (a libc-free displacement) has no dominant form (kit.dom = 0 everywhere): D1 STANDS as the default; F1 never fires on this data.')
    out(' A11 "F2: the VM hat at |S| = 1 -> V1 where a measured saving exists": saving +0.515 (454x the eps token) BUT V1 at the VM hat loses +38% at g = 2 (find-all): the row as written (beta saving only) would ship that loss.')
    out(' A12 "F0 NONE where E measured and E.g < g_none": NONE never beats the walk beyond the floor except o-bnd at g = 2 (-7.0%); g_none <= 2 B: F0 fires only for g < 2 (a stop on every second byte): effectively never.')
    out(" A13 \"M23: P1 waits for Q-WR-9's trigger\": on the letter the trigger FIRES (KEEP loses 1.47/1.54 ns, 3.4-3.8%, on TUG g8 early cells); the same pre-check wins x49-x112 on absent cells; P1's operands are measured, its rule is a design question.")
    out(' A14 "grid1 prototype figures stop being directly comparable (D167)": CONFIRMED in both directions: the streamed condition moves g* (A3), F_walk (+1.1 ns), the A/A of F1 (3.365% -> 1.316%) and M9.')
    n1 = sum(1 for v in VIS['F1'] if v.launches > 3)
    out(f' A15 launches: rev 3 expects 3.4-5; the slot ran 3 (+2 on {n1} of {len(VIS["F1"])} F1 groups, 26 of 60 OB groups): within the stated band; wall 66.5 min (4 required phases + optional), inside the 91-129 min estimate.')


def confidence(k):
    key_, unit, val, ab, status, regime, layer, floor_, src = k
    nm = key_
    if 'SUSPECT' in regime or 'PROVISIONAL' in src:
        return 'PROVISIONAL'
    if nm.startswith(('kit.beta.', 'kit.saving.', 'kit.block.')):
        return 'HIGH'
    if nm.startswith(('kit.eps.',)):
        return 'MED'
    if nm.startswith(('kit.f.', 'kit.delta.')):
        try:
            return 'HIGH' if abs(float(val)) >= 5 * float(floor_) else ('MED' if abs(float(val)) >= 2 * float(floor_) else 'LOW')
        except ValueError:
            return 'MED'
    if nm.startswith(('kit.dfloor.', 'kit.ffloor.', 'kit.cfloor.', 'kit.ufloor.', 'kit.wfloor.')):
        return 'MED'
    if nm.startswith(('kit.ccold.', 'kit.wuse.')):
        return 'MED'
    if nm.startswith(('kit.cdisp_', 'kit.cscaffold')):
        return 'MED'
    if nm.startswith(('kit.dom.', 'kit.gate.')):
        return 'MED'
    if nm.startswith(('kit.gstar.', 'kit.xover.', 'kit.gnone.')):
        return 'LOW'
    return 'MED'


def write_keys():
    path = os.path.join(HERE, 'keys.tsv')
    seen = {}
    for k in KEYS:
        seen[k[0]] = k              # last writer wins; keys are unique by construction except labelled duplicates
    with open(path, 'w') as f:
        f.write('# kit-grid@2 PROPOSED rows read from the zen4-grid2 slot (lane grid2read); NOT a measurement set: no digest, no deps; a converter (set_to_measures.py, E14) writes the set.\n')
        f.write("# columns: key unit value_e6 abs_ns_e6 status regime layer floor_e6 confidence source.  value_e6 is in the card's unit (ratio: relative to u = beta_walk(dig) = %.4f ns/B; walkbytes: ns / u; bytes; bool 0/1000000).  floor_e6 is in the same unit.\n" % UNIT[0])
        f.write('# value -1 for a bytes key = no threshold exists on the measured grid (see source/regime).  Layer is the SIMD layer of the arm (off = walk/V1; w16 = S1; w32 = A1/W64; iter = A3).  Kind suffix .bounded = the bounded-prefilter variant; .back = DFA_ATTEMPT.\n')
        f.write('# confidence: HIGH (>= 5x the floor or a direct slope), MED, LOW (interpolated on a coarse grid or a shape-confounded crossover), PROVISIONAL (a load-suspect source).\n')
        f.write('key\tunit\tvalue_e6\tabs_ns_e6\tstatus\tregime\tlayer\tfloor_e6\tconfidence\tsource\n')
        for k in sorted(seen):
            row = list(seen[k])
            f.write('\t'.join(str(x) for x in row[:8] + [confidence(seen[k])] + row[8:]) + '\n')
    return len(seen)


if __name__ == '__main__':
    provenance()
    contamination()
    noise()
    EPSB, SUS = beta_table()
    derived_rules(EPSB)
    G, Fv = single_calls()
    shape011()
    alignment(G)
    FIT = findall()
    CROSS = gstar_tables(FIT)
    T = regimes_tally()
    wide_vs_v1()
    predictability()
    f2s()
    CALL, summ = dispatch()
    SUMU = dispatch_use()
    scaffold()
    pay_rule(CALL, summ, SUMU, G)
    RES = onebyte()
    DOM = onebyte_derived(RES)
    TR = trigger()
    predictions(G, CROSS, T)
    n = write_keys()
    hdr('11. KEYS')
    out('%d proposed rows written to keys.tsv (kit-grid@2 spelling; see the file header).' % n)
