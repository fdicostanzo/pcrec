#!/usr/bin/env python3
# docs/dev/lanes/r17c_nearcap.py (lane r17c, [MEMFN] R-17 step R17-b, review B S9/U4):
# TWO pcrec-side censuses over EMITTED artifacts and refusals. It never calls the
# kit and shares no code with memfn/ or src/: it runs two COMPILERS and reads their
# stdout/stderr text.
#
#   --nearcap     the NEAR-CAP population. R17-b's census (r17b_movers.py) raises
#                 BAD-refusal-moved only over the corpus, which has no artifact near
#                 a cap, yet the kit row adds ~2.2 KB per set site, so a pattern that
#                 was just under max_emit_bytes / max_emit_code_bytes at the BASE
#                 compiler can be refused at the TIP. This mode GENERATES patterns
#                 whose BASE artifact lands within ~10% of a cap (or of a DFA state
#                 cap), compiles each with BASE and TIP under `--features all` on the
#                 arms byte, byte-vm (--engine=vm) and utf8 (-e utf8), and judges
#                   compiles-both | refuses-both | BAD-refusal-moved (one side refuses).
#                 The tip is expected to be 0 BAD once the size-cap ladder rung
#                 (`-fno-kit-size-drop`, denied by --size-cap=refuse) lands: a pattern
#                 that compiled at BASE compiles again at the TIP.
#   --u4 OUT      the PREDICTED-MOVER MANIFEST for emit_sweep's lowered-cap variants
#                 (lowsize, lowboth, lowthr; review B U4). See the OUT header it writes
#                 for what the prediction can and cannot see.
#
# HOW A SHAPE IS SIZED (nearcap). A shape is a pattern template over a count N. The
# figures come from the compiler's own text, never from this script's model:
#   `--warn-emit-bytes=1` makes an ACCEPTED artifact print
#       "N bytes of emitted C source (M of code)"            (total N, code M)
#   a REFUSED one prints "pattern too large: N bytes of emitted C source (limit L"
#   (the total cap) or "... N bytes of emitted code (limit L" (the code cap).
# For each (shape, arm, cap) the count N is solved by bracketed regula falsi / bisection
# on the BASE compiler to land at factor x cap, factor in FACTORS (0.92 .. 1.08), to
# within TOL (3%); a solve that does not converge, or a shape that does not grow the
# metric, is reported (UNREACHED / NOGROW) and dropped, never silently. A refusal by
# the OTHER cap carries no figure for this metric and is read as "over". A shape whose
# code share says the OTHER cap binds first is skipped for this metric (NOMETRIC).
# The population count per arm is read from the BASE artifact's measured ratio, not
# from the target: only candidates whose measured metric sits within +-10% of the cap
# count toward the floor (per arm, pinned below; --floor N overrides; enforced only without --every/--shapes).
#
# CAPS (src/core/limits.def): total 1,000,000 (PCREC_MAX_EMIT_BYTES), code 500,000
# (PCREC_MAX_VM_EMIT_CODE_BYTES); DFA state caps PCREC_MAX_DFA_STATES_GOTO 10,000 /
# _TABLE 32,000 (limits.md 3.3): the `dfa_states` shape `(?:a|b)*a(?:a|b){N}` at a
# fixed N list straddles the goto cap (N=13 is a DFA artifact, N>=14 the VM fallback;
# measured at 010b612c9), and runs also on the arm `byte-dfa` (--engine=dfa, which
# REFUSES past the cap instead of falling back). Counted as `statecap`, not toward the
# size floor.
#
# usage: python3 r17c_nearcap.py --nearcap TREE BASE_PCREC [JOBS] [--every N]
#                                 [--shapes a,b] [--arms byte,byte-vm,utf8] [--floor N]
#        python3 r17c_nearcap.py --u4 OUT TREE BASE_PCREC [JOBS] [--every N]
# TREE is the tip's worktree (TIP = TREE/build/pcrec; TREE/scripts/emit_sweep.py is the
# corpus enumeration). Exit 1 on any BAD (or a missed floor).
import re
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor

argv = sys.argv[1:]
VALUE_FLAGS = ('--every', '--shapes', '--arms', '--floor', '--u4')
args = [a for i, a in enumerate(argv) if not a.startswith('--')
        and (i == 0 or argv[i - 1] not in VALUE_FLAGS)]


def opt(name, default=None):
    return argv[argv.index(name) + 1] if name in argv else default


MODE_U4 = '--u4' in argv
MODE_NEAR = '--nearcap' in argv
if MODE_U4 == MODE_NEAR or len(args) < 2:
    sys.exit(__doc__ if False else 'usage: r17c_nearcap.py (--nearcap | --u4 OUT) TREE BASE_PCREC [JOBS] '
             '[--every N] [--shapes a,b] [--arms a,b] [--floor N]')
TREE, BASE = args[0], args[1]
JOBS = int(args[2]) if len(args) > 2 else 4
EVERY = int(opt('--every', 1))
TIP = TREE + '/build/pcrec'

CAP_TOTAL, CAP_CODE, THR_DEFAULT = 1_000_000, 500_000, 120_000
CAPS = {'total': CAP_TOTAL, 'code': CAP_CODE}
WARN = re.compile(rb'(\d+) bytes of emitted C source \((\d+) of code\)')
REF_TOT = re.compile(rb'pattern too large: (\d+) bytes of emitted C source \(limit')
REF_CODE = re.compile(rb'pattern too large: (\d+) bytes of emitted code \(limit')
TIMEOUT = 300


def measure(binary, pat, extra):
    """(status, total, code): status ok | refused-total | refused-code | refused-other
    | timeout. Figures are None where the text carries none."""
    if len(pat) > 120_000:      # one argv string is capped near 128 KB by the kernel (E2BIG): read as over
        return ('refused-other', None, None)
    cmd = [binary, '-p', 'rx', '--features', 'all'] + extra + ['--warn-emit-bytes=1', '-o', '-',
                                                                 '--pattern', pat]
    try:
        r = subprocess.run(cmd, stdout=subprocess.DEVNULL, stderr=subprocess.PIPE, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return ('timeout', None, None)
    m = WARN.search(r.stderr)
    if r.returncode == 0:
        return ('ok', int(m.group(1)), int(m.group(2))) if m else ('ok', None, None)
    m = REF_TOT.search(r.stderr)
    if m:
        return ('refused-total', int(m.group(1)), None)
    m = REF_CODE.search(r.stderr)
    if m:
        return ('refused-code', None, int(m.group(1)))
    return ('refused-other', None, None)


def accepted(res):
    return res[0] == 'ok'


def fmt(res):
    s, t, c = res
    return '%s %s/%s' % (s, t if t is not None else '-', c if c is not None else '-')


# ---- mode --u4 ---------------------------------------------------------------------
def run_u4():
    out = opt('--u4')
    sys.path.insert(0, TREE + '/scripts')
    import emit_sweep as es

    def caps_of(vflags):
        c = {'total': CAP_TOTAL, 'code': CAP_CODE, 'thr': THR_DEFAULT}
        for name, key in (('PCREC_MAX_EMIT_BYTES', 'total'), ('PCREC_MAX_VM_EMIT_CODE_BYTES', 'code'),
                          ('PCREC_SIZE_TERM_THRESHOLD', 'thr')):
            m = re.search(r'-D%s=(\d+)' % name, vflags)
            if m:
                c[key] = int(m.group(1))
        return c

    variants = {}
    for v, fl in es.VARIANTS.items():
        c = caps_of(fl)
        if c != caps_of(''):
            variants[v] = c
    bases = {'byte': [], 'utf8': ['-e', 'utf8']}
    engines = {'auto': [], 'vm': ['--engine=vm']}
    pats = es.distinct_patterns(es.enumerate_corpus(TIP, TREE, 30), every=EVERY)

    def task(item):
        p, bname, ename = item
        ex = bases[bname] + engines[ename]
        return item, measure(BASE, p, ex), measure(TIP, p, ex)

    items = [(p, b, e) for p in pats for b in bases for e in engines]
    with ThreadPoolExecutor(JOBS) as ex:
        res = list(ex.map(task, items))
    rows, plain_moved, counts = [], [], {}
    for (p, bname, ename), a, b in res:
        if a[0] == 'timeout' or b[0] == 'timeout':
            plain_moved.append((bname, ename, p, 'timeout'))
            continue
        if accepted(a) != accepted(b):
            plain_moved.append((bname, ename, p, 'plain-refusal-moved base=%s tip=%s' % (a[0], b[0])))
            for v in variants:
                rows.append((v, bname, p, a[1], b[1], ename, 'plain-refusal-moved', a[2], b[2]))
            continue
        if not accepted(a) or a[1] is None or b[1] is None:
            continue    # refused by both at the shipped caps: refused at every lowered cap too
        if (a[1], a[2]) == (b[1], b[2]):
            continue
        for v, c in variants.items():
            why = []
            if (a[1] <= c['total']) != (b[1] <= c['total']):
                why.append('cross-total')
            if (a[2] <= c['code']) != (b[2] <= c['code']):
                why.append('cross-code')
            if (a[2] > c['thr']) != (b[2] > c['thr']):
                why.append('cross-sizeterm')
            if not why and max(a[2], b[2]) > c['thr']:
                why.append('ladder-both-ran')   # the size term ran on both; its input moved
            if why:
                rows.append((v, bname, p, a[1], b[1], ename, '+'.join(why), a[2], b[2]))
    rows.sort(key=lambda r: (r[0], r[1], r[2], r[5]))
    with open(out, 'w') as fh:
        fh.write('# r17c_nearcap.py --u4: predicted movers for emit_sweep\'s lowered-cap variants.\n')
        fh.write('# base=%s tip=%s patterns=%d every=%d; variants (caps total/code/size-term threshold):\n'
                 % (BASE, TIP, len(pats), EVERY))
        for v, c in variants.items():
            fh.write('#   %s: %d / %d / %d\n' % (v, c['total'], c['code'], c['thr']))
        fh.write('# Columns: variant, base, repr(pattern), base_bytes, tip_bytes (TOTAL emitted bytes, normal\n'
                 '#   builds, --warn-emit-bytes=1), engine (auto|vm), class, base_code, tip_code.\n'
                 '# A pattern is predicted iff its (total, code) bytes differ BASE vs TIP and a variant limit lies\n'
                 '#   between them: class cross-total (base<=cap<tip or the reverse), cross-code, cross-sizeterm\n'
                 '#   (code > threshold on one side only: the unroll-K size term, compile.c SIZE_TERM, runs on one\n'
                 '#   side only; compile.c tests EMIT CODE bytes against PCREC_SIZE_TERM_THRESHOLD). The class\n'
                 '#   ladder-both-ran (no limit crossed, bytes differ, code > threshold on both) is the size term\n'
                 '#   REACTING to moved bytes; it is listed because it can move, and the judge counts it apart.\n'
                 '#   plain-refusal-moved: one side refuses at the SHIPPED caps (a mover in every variant).\n'
                 '# WHAT THIS PREDICTION CANNOT SEE: (1) the variant compile itself: a variant build takes the\n'
                 '#   ladder/cap-rescue paths on artifacts whose plain bytes were measured with different K and\n'
                 '#   routes, so a variant artifact is NOT its plain artifact once any limit is crossed; (2) which\n'
                 '#   emit_sweep STREAM shows the move (emit-ir, emit-ir-auto, stderr each show a different\n'
                 '#   subset: a refusal moves stderr, a K/route change moves the listing); (3) the VM entry-shape\n'
                 '#   knee (tuning.md 2.21) and every other bytes-reactive selection that is not a cap or the\n'
                 '#   size-term trigger; (4) the new size-cap ladder rung (-fno-kit-size-drop) reacting to a\n'
                 '#   crossing: it can turn a predicted refusal into an acceptance whose bytes differ again;\n'
                 '#   (5) options other than the base (-e utf8) x engine (auto, vm) the stream flags add.\n'
                 '#   A MANIFEST ENTRY THAT DOES NOT MOVE is therefore not an error: the judge counts and prints it.\n')
        for r in rows:
            fh.write('%s\t%s\t%r\t%s\t%s\t%s\t%s\t%s\t%s\n' % r)
        for bname, ename, p, why in plain_moved:
            fh.write('# PLAIN-MOVED %s %s %r %s\n' % (bname, ename, p, why))
    tally = {}
    for r in rows:
        for cl in r[6].split('+'):
            tally.setdefault((r[0], r[1]), {}).setdefault(cl, set()).add(r[2])
    print('patterns', len(pats), 'every', EVERY, 'rows', len(rows), 'plain-moved', len(plain_moved))
    for k in sorted(tally):
        print('U4 %-8s %-5s ' % k + ' '.join('%s=%d' % (c, len(s)) for c, s in sorted(tally[k].items())))
    print('manifest', out)
    return 0


# ---- mode --nearcap ----------------------------------------------------------------
def shape_fns():
    def alt_cls(n):
        return '(?:' + '|'.join('[%s-%s]%d' % (chr(97 + i % 20), chr(98 + i % 20), i) for i in range(n)) + ')'

    def cat_cls(n):
        return ''.join('[a-%s]x' % chr(98 + i % 20) for i in range(n))

    def alt_lit(n):
        return '(?:' + '|'.join('w%d' % i for i in range(n)) + ')'
    return {
        'rep_cd': lambda n: '(?:[a-z][0-9]){1,%d}' % n,
        'rep_w': lambda n: '(?:\\w+@){1,%d}' % n,
        'rep_nx': lambda n: '(?:[^x]y){1,%d}' % n,          # [^x]y repeats
        'alt_cls': alt_cls,                                  # alternation of classes
        'cat_cls': cat_cls,                                  # concatenated classes (grows the VM program)
        'alt_lit': alt_lit,
        'backref': lambda n: '(\\w)\\1' * n,                 # VM-route shapes
        'bref_rep': lambda n: '(?:(\\w)\\1){1,%d}' % n,
    }


ARMS_ALL = {'byte': [], 'byte-vm': ['--engine=vm'], 'utf8': ['-e', 'utf8'], 'byte-dfa': ['--engine=dfa']}
SIZE_ARMS = ['byte', 'byte-vm', 'utf8']
FACTORS = (0.92, 0.96, 1.0, 1.04, 1.08)
TOL = 0.03
NMAX = 400_000
STATE_NS = (10, 11, 12, 13, 14, 15)


def metric_of(res, metric):
    """The metric's figure from a base measurement, or None (unknown: read as over)."""
    s, t, c = res
    if metric == 'total':
        return t if s in ('ok', 'refused-total') else None
    return c if s in ('ok', 'refused-code') else None


def solve(unit_pts, mk, extra, metric, target):
    """Find N with metric(N) ~ target (within TOL) on the BASE compiler. unit_pts caches
    {N: measurement} for this (shape, arm). Returns (N, measurement) or (None, reason)."""
    def get(n):
        if n not in unit_pts:
            unit_pts[n] = measure(BASE, mk(n), extra)
        return unit_pts[n]

    n = 64
    for _ in range(14):
        res = get(n)
        if res[0] in ('refused-other', 'timeout') and metric_of(res, metric) is None \
                and res[0] != 'refused-total' and res[0] != 'refused-code':
            # the shape stops compiling for a reason that is neither cap: treat as over
            pass
        v = metric_of(res, metric)
        if v is not None and abs(v / target - 1) <= TOL:
            return n, res
        lows = [(k, metric_of(r, metric)) for k, r in unit_pts.items()
                if metric_of(r, metric) is not None and metric_of(r, metric) < target]
        highs = [(k, metric_of(r, metric)) for k, r in unit_pts.items()
                 if metric_of(r, metric) is None or metric_of(r, metric) >= target]
        lo = max(lows) if lows else None
        hi = min(highs, key=lambda kv: kv[0]) if highs else None
        if lo and hi:
            if hi[0] - lo[0] <= 1:
                return None, 'UNREACHED (bracket closed at N=%d..%d)' % (lo[0], hi[0])
            if hi[1] is not None and hi[1] > lo[1]:
                nn = lo[0] + int((hi[0] - lo[0]) * (target - lo[1]) / (hi[1] - lo[1]))
            else:
                nn = (lo[0] + hi[0]) // 2
            n = min(max(nn, lo[0] + 1), hi[0] - 1)
        elif lo:
            if lo[0] >= NMAX:
                return None, 'UNREACHED (N>%d)' % NMAX
            pts = sorted(lows)
            if len(pts) >= 2 and pts[-1][1] > pts[-2][1]:
                slope = (pts[-1][1] - pts[-2][1]) / (pts[-1][0] - pts[-2][0])
                nn = pts[-1][0] + int((target - pts[-1][1]) / slope)
            else:
                nn = lo[0] * 2
            n = min(max(nn, lo[0] + 1), lo[0] * 16, NMAX)
        else:
            if hi[0] <= 1:
                return None, 'UNREACHED (N=1 already over)'
            n = max(1, hi[0] // 2)
    return None, 'UNREACHED (no convergence)'


def unit_task(unit):
    """One (shape, arm): probe growth, then solve each (metric, factor). Returns candidates:
    dicts {arm, shape, kind, metric, factor, n, pat, base} and notes."""
    shape, mk, arm = unit
    extra = ARMS_ALL[arm]
    pts, cands, notes = {}, [], []
    if shape == 'dfa_states':
        for n in STATE_NS:
            p = '(?:a|b)*a(?:a|b){%d}' % n
            cands.append(dict(arm=arm, shape=shape, kind='statecap', metric='states', factor=None,
                              n=n, pat=p, base=measure(BASE, p, extra)))
        return cands, notes
    r0, r1 = measure(BASE, mk(64), extra), measure(BASE, mk(256), extra)
    pts[64], pts[256] = r0, r1
    if not (accepted(r0) and accepted(r1)):
        notes.append('%s/%s NOGROW probe refused (%s | %s)' % (arm, shape, fmt(r0), fmt(r1)))
        return cands, notes
    for metric in ('total', 'code'):
        i = 1 if metric == 'total' else 2
        v0, v1 = r0[i], r1[i]
        if v1 < 1.5 * v0:
            notes.append('%s/%s/%s NOGROW (%d -> %d bytes for N 64 -> 256)' % (arm, shape, metric, v0, v1))
            continue
        share = r1[2] / r1[1]
        if (metric == 'total' and share >= 0.5) or (metric == 'code' and share < 0.5):
            notes.append('%s/%s/%s NOMETRIC (code share %.2f: the other cap binds first)' % (arm, shape, metric, share))
            continue
        for f in FACTORS[::EVERY]:
            target = int(CAPS[metric] * f)
            n, res = solve(pts, mk, extra, metric, target)
            if n is None:
                notes.append('%s/%s/%s x%.2f %s' % (arm, shape, metric, f, res))
                continue
            cands.append(dict(arm=arm, shape=shape, kind='size', metric=metric, factor=f, n=n,
                              pat=mk(n), base=res))
    return cands, notes


def judge_task(c):
    extra = ARMS_ALL[c['arm']]
    c['tip'] = measure(TIP, c['pat'], extra)
    a, b = c['base'], c['tip']
    if 'timeout' in (a[0], b[0]):
        c['verdict'] = 'BAD-timeout'
    elif accepted(a) and accepted(b):
        c['verdict'] = 'compiles-both'
    elif not accepted(a) and not accepted(b):
        c['verdict'] = 'refuses-both'
    else:
        c['verdict'] = 'BAD-refusal-moved'
    return c


def run_near():
    shapes = shape_fns()
    want = opt('--shapes')
    names = list(shapes) if not want else want.split(',')
    arms = opt('--arms', ','.join(SIZE_ARMS)).split(',')
    units = [(s, shapes[s], a) for s in names if s in shapes for a in arms if a in SIZE_ARMS]
    if not want or 'dfa_states' in names:
        units += [('dfa_states', None, a) for a in ('byte', 'utf8', 'byte-dfa') if a in arms or a == 'byte-dfa']
    with ThreadPoolExecutor(JOBS) as ex:
        solved = list(ex.map(unit_task, units))
        cands = [c for cs, _ in solved for c in cs]
        for _, ns in solved:
            for n in ns:
                print('NOTE', n)
        cands = list(ex.map(judge_task, cands))
    bads = 0
    stats = {}
    for c in cands:
        s = stats.setdefault(c['arm'], dict(cand=0, near=0, near_total=0, near_code=0, statecap=0, both=0,
                                            refboth=0, bad=0))
        s['cand'] += 1
        ratio = ''
        if c['kind'] == 'statecap':
            s['statecap'] += 1
        else:
            v = metric_of(c['base'], c['metric'])
            r = v / CAPS[c['metric']]
            ratio = '%.3f' % r
            if 0.9 <= r <= 1.1:
                s['near'] += 1
                s['near_' + c['metric']] += 1
        s['both'] += c['verdict'] == 'compiles-both'
        s['refboth'] += c['verdict'] == 'refuses-both'
        if c['verdict'].startswith('BAD'):
            s['bad'] += 1
            bads += 1
        print('%-8s %-10s %-6s x%-5s N=%-7s base[%s] tip[%s] %s%s' % (
            c['arm'], c['shape'], c['metric'], ratio or '-', c['n'], fmt(c['base']), fmt(c['tip']),
            c['verdict'], '' if c['verdict'][0] != 'B' else '   %r' % c['pat'][:120]))
    # Per-arm floors (K35): floor(0.9 x measured) on the first full run (lane
    # r17c, 2026-10-12, at 2fdc4215b vs 010b612c9: byte 25, byte-vm 20, utf8 25
    # within 10% of a cap; the shape families reach no more, see the NOGROW and
    # UNREACHED notes). `--floor N` replaces all three.
    floors = dict(byte=22, **{'byte-vm': 18}, utf8=22)
    if '--floor' in argv:
        floors = {a: int(opt('--floor')) for a in arms}
    enforce = EVERY == 1 and not want
    missed = 0
    for arm in arms:
        s = stats.get(arm, dict(cand=0, near=0, near_total=0, near_code=0, statecap=0, both=0, refboth=0, bad=0))
        print('ARM %-8s candidates=%d within10%%=%d (total=%d code=%d) statecap=%d compiles-both=%d '
              'refuses-both=%d BAD=%d' % (arm, s['cand'], s['near'], s['near_total'], s['near_code'],
                                          s['statecap'], s['both'], s['refboth'], s['bad']))
        floor = floors.get(arm, 1)
        if s['near'] < floor:
            if enforce:
                missed += 1
                print('FLOOR-FAIL %s: %d patterns within 10%% of a cap < floor %d' % (arm, s['near'], floor))
            else:
                print('FLOOR-NOT-ENFORCED %s: %d < %d (a subsample, --every/--shapes)' % (arm, s['near'], floor))
    if 'byte-dfa' in stats:
        s = stats['byte-dfa']
        print('ARM byte-dfa  (statecap shapes only) candidates=%d compiles-both=%d refuses-both=%d BAD=%d'
              % (s['cand'], s['both'], s['refboth'], s['bad']))
    print('BAD', bads)
    return 1 if bads or missed else 0


if __name__ == '__main__':
    sys.exit(run_u4() if MODE_U4 else run_near())
