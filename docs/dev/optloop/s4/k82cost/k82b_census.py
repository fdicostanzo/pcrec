#!/usr/bin/env python3
"""k82cost: the (B) cost row's verdict on every bench export whose emitted
pre-check carries a RUN, under the BUILTIN rates (no exemplar: byte-rate = the
builtin prior under -e byte, NONE under -e utf8; run-rarity = NONE =
cardinality), W = 64 KiB, M = 0, Linux cost row (litscan_k82b.md §3.2).

Scope (litscan_k82b.md §1.5): only a run block is ever declined, and only
against its FALLBACK (the set pick's one-byte check, or nothing when the set
is empty: the pre-C3 program); routes whose pre-check is the no-match proof
(VM with no DFA prefilter, K65/K66) are excluded by construction.  E* is the
engine ns/B ABOVE which the run block beats its fallback; the cost row
declines the run iff the artifact's E < E*.  E is NOT computed here (it is
the one term with no calibration yet, §1.3); the verdict column applies the
form row E_form (§1.3 table) to show the mover set it would give.  PCREC, BENCH, FINDB4 from the environment."""
import math, os, re, subprocess, glob, sys
sys.argv = ['x', os.environ['FINDB4'], '/dev/null', 'linux']
src = open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'k82b_model.py')).read()
g = {}; exec(compile(src.replace('\nmain()\n', '\n'), 'm', 'exec'), g)
SRC = os.environ.get('SRC', 'builtin')      # builtin | weblog | log (an --analysis bundle)
d1, _ = g['bundle'](os.path.join(os.environ['FINDB4'], 'src/findings/default.rxt'))
if SRC != 'builtin':
    b1, b2 = g['bundle'](os.path.join(os.environ['FINDB4'], 'src/findings/%s.rxt' % SRC))
else:
    b1, b2 = None, None
P = os.environ['PCREC']; W = int(os.environ.get('W', 65536))
# E_form: the engine's per-byte cost by its scan form, Linux, the measured
# DENY medians of r1read §3 (byte-class: mod-i .96, ci-* .68-.70, union .75;
# memchr: cls-* .59; offset-set: slack .24; memchr-bounded/offset-set-
# bounded: http-5xx/stack-frame log fail .02-.35).  ILLUSTRATIVE, not a
# calibration: §1.3 names the per-form calibration that replaces it.
E_FORM = {'byte-class': .75, 'byte-class-bounded': .75, 'memchr': .59, 'offset-set': .24,
          'memchr-bounded': .05, 'offset-set-bounded': .35, 'run-pinned': .10}
rows = []
for f in sorted(glob.glob(os.environ['BENCH'] + '/bench/*/patterns/*.rx')):
    setn = f.split('/bench/')[1].split('/')[0]
    enc = ['-e', 'utf8'] if setn == 'utf8' else []
    pat = open(f, 'rb').read().rstrip(b'\n')
    try:
        o = subprocess.run([x.encode() for x in [P, '--features', 'all', '-p', 'rx', *enc, '--emit-facts', '--pattern']] + [pat],
                           capture_output=True, text=True, timeout=60).stdout
    except subprocess.TimeoutExpired:
        continue
    get = lambda k: (re.search(r'\t%s\t"?([^"\t\n]*)' % k, o) or [None, ''])[1]
    why = get('RX_REQ_WHY')
    if why != 'emitted': continue
    rr = re.search(r'\treq_run\t.*?\t(yes|no)\t(\S*)\t', o)
    rs = re.search(r'\treq_set\t.*?\t(yes|no)\t(\S*)', o)
    c1 = b1 if SRC != 'builtin' else (None if enc else d1)
    setm = [int(x) for x in rs.group(2).split(',')] if rs and rs.group(2) not in ('none', '') else []
    vmpf = get('RX_VM_PREFILTER'); eng = get('RX_ENGINE')
    if eng == 'vm' and vmpf != 'hybrid': continue          # the pre-check is the proof
    if rr and rr.group(2) not in ('', 'none'):
        h, _, mk = rr.group(2).partition('/'); hb, _, idx = h.partition('@')
        T = bytes.fromhex(hb); K = bytes.fromhex(mk) if mk else b'\xff' * len(T)
        sets = [g['cube'](t, k) for t, k in zip(T, K)]
        rho = 2.0 ** -g['markov1'](b2, sets)
        ss = [g['rate'](c1, [m]) for m in sets[g['pick'](c1, sets, int(idx))]]
        kind = 'masked' if mk else 'exact'
    else:
        continue                                            # byte-only: not (B)'s question
    # run guard vs fallback, per subject: cost_run - E*W*R_run  vs  cost_fb - E*W*R_fb
    # => the run wins iff E*W*(R_run - R_fb) > cost_run - cost_fb, i.e. E > E*
    R_run = math.exp(-rho * W); cost_run = g['gate_cost'](rho, ss, W, 0)
    if setm:
        pb = min(setm, key=lambda b: (g['rate'](c1, [b]), -b)); p = g['rate'](c1, [pb])
        R_fb = math.exp(-p * W); cost_fb = g['gate_cost'](p, [p], W, 0)
    else:
        R_fb = 1.0 if False else 0.0; cost_fb = 0.0              # no gate: rejects nothing, costs nothing
    gain = W * (R_run - R_fb)
    Estar = (cost_run - cost_fb) / gain if gain > 0 else float('inf')
    pf = get('RX_DFA_PREFILTER') if eng == 'dfa' else 'hybrid:' + get('RX_DFA_PREFILTER')
    Ef = E_FORM.get(pf.split(':')[-1], None)
    verdict = '?' if Ef is None else ('DECLINE' if Ef < Estar else 'keep')
    rows.append((Estar, os.path.basename(f)[:-3], setn, kind, eng, pf, -math.log2(rho), sum(ss), Ef or 0, verdict))
rows.sort()
print('# rates: %s, W = %d' % (SRC, W))
print('# %d run-bearing emitted pre-checks on proof-free routes; E* ns/B, name, set, kind, engine, prefilter, run bits, stop rate, E_form, verdict' % len(rows))
for r in rows:
    print('%8.3f  %-44s %-10s %-6s %-4s %-26s %5.1f %.4f %.2f %s' % r)
