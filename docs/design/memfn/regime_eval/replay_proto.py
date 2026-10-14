#!/usr/bin/env python3
"""replay_proto: a PROTOTYPE of [REGIME-EVAL]'s replay on EXISTING data (lane regeval, 2026-10-13).

NO clock, NO build, NO new measurement.  It reads the grid1 slot's finished logs
(worktrees/memfn-slot/grid1/, the run gridread_report.md reads) through grload.py's
LOADERS only.  It does NOT import gridread.py: the replay must not share a source with
the cost model it would otherwise be judging (regime_eval.md §5).

What it shows: the shape of docs/design/memfn/regime_eval.md works.
  - a cell's KNOWLEDGE record (P, N, M, E, H; A = the measurement set below) built
    from compile-time cell facts and the slot's own counters;
  - the regime table's rows (regime_tables.md rev 0.2 + the kit's rev 0.1 check) as
    DECLARED DATA, walked first-match under each filter S0-S3;
  - regret = measured ns of the pick - measured ns of the fastest arm the layer
    offers, per regime, absolute and % of the walk;
  - the failing-direction controls and the A/A control, scored against a
    pre-declared "visibly worse" rule.

IN SAMPLE.  The thresholds were read off this same slot (gridread §4), so this run is a
self-consistency check of the table against its own fit population, NOT the held-out
judgement regime_eval.md §3 pre-registers.  Its numbers must therefore reproduce
regime_tables.md §3's in-sample regret table (where the table claims one); that is the
point of running it.

    python3 -I replay_proto.py [OUT] > proto_out.txt
    python3 -I replay_proto.py --strict [OUT] > proto_out_strict.txt   # gridread §6.2's population
"""
import collections, os, sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.abspath(os.path.join(HERE, '..', '..', '..', '..'))
sys.path.insert(0, os.path.join(ROOT, 'docs', 'dev', 'lanes', 'gridread'))
from grload import load_table, load_counts, load_facts, groups, base_name, TOKC  # loaders only

STRICT = '--strict' in sys.argv            # population = groups timing every form (gridread §6.2's 101)
ARGS = [a for a in sys.argv[1:] if a != '--strict']
OUT = ARGS[0] if ARGS else os.path.join(ROOT, '..', 'memfn-slot', 'grid1')
OUT = os.path.abspath(OUT)
if not os.path.isdir(OUT):
    OUT = '/home/pcrec/projects/pcrec/worktrees/memfn-slot/grid1'

G = groups(load_table(os.path.join(OUT, 'time_F1.log')))
CNT = load_counts(os.path.join(OUT, 'counts.tsv'))
FACT = load_facts(os.path.join(OUT, 'subj_facts.tsv'))

# ---------------------------------------------------------------------------
# P: compile-time cell facts (grid1_report.md §1.1).  site = the g* key.
# ---------------------------------------------------------------------------
CELLP = {'dig': dict(kind='PF', site='pf1', range_terms=1),
         'bounded': dict(kind='PF', site='run', range_terms=1),
         'dfa-hat': dict(kind='HAT', site='hat', range_terms=0)}

# ---------------------------------------------------------------------------
# A = the measurement set.  Zen 4 constants as regime_tables.md rev 0.2 states them
# (midpoints of its ranges; "set v0").  In the real evaluator this is a D166 SET file.
# ---------------------------------------------------------------------------
MS_V0 = dict(id='zen4-grid1-v0',
             n_r1=32, n_r2=64,                     # R1 / R2 one-shot spans
             h_r3a=14, h_r3b=32,                   # R3a / R3b previous-step spans
             gstar_on={'pf1': 4.5, 'run': 2.7, 'hat': 2.2},
             gstar_off={'pf1': 14.0, 'run': 21.5, 'hat': 3.2})

# ---------------------------------------------------------------------------
# The rows: ONE declared table, first-match.  needs = knowledge keys; cond reads the
# knowledge record K and the set MS; pick = a form id.  In the build this is the
# kit's row table itself (regime_eval.md §5.4), read by both.
# ---------------------------------------------------------------------------
def r0(K, MS): return not K['simd'] and K['range_terms'] >= 2
def r1(K, MS): return K['M'] == 'one-shot' and K['N'] < MS['n_r1']
def r2(K, MS): return K['M'] == 'one-shot' and MS['n_r1'] <= K['N'] < MS['n_r2']
def r3a(K, MS): return K['M'] == 'iter' and K['H'] < MS['h_r3a']
def r3b(K, MS): return K['M'] == 'iter' and K['simd'] and MS['h_r3a'] <= K['H'] < MS['h_r3b']
def r5(K, MS): return K['simd'] and K['E'] < MS['gstar_on'][K['site']]
def r6(K, MS): return not K['simd'] and K['E'] < MS['gstar_off'][K['site']]
def r7(K, MS): return True

ROWS = [
    dict(id='R0', needs={'P'}, cond=r0, pick=lambda K: 'walk'),
    dict(id='R1', needs={'P', 'N', 'M'}, cond=r1, pick=lambda K: 'walk'),
    dict(id='R2', needs={'P', 'N', 'M'}, cond=r2, pick=lambda K: 'V1'),
    dict(id='R3a', needs={'H'}, cond=r3a, pick=lambda K: 'walk'),
    dict(id='R3b', needs={'H'}, cond=r3b, pick=lambda K: 'A3'),
    # R4 (per-block popcount, H) is NOT REPLAYABLE from per-pass medians: it switches
    # form inside a call.  regime_eval.md §1.4 hands it to [REGIME-TWIN].
    dict(id='R5', needs={'E', 'P'}, cond=r5, pick=lambda K: 'walk'),
    dict(id='R6', needs={'E', 'P'}, cond=r6, pick=lambda K: 'walk'),
    dict(id='R7', needs={'P'}, cond=r7, pick=lambda K: 'A1' if K['simd'] else 'V1'),
]
FILTERS = collections.OrderedDict([('S0', {'P', 'N', 'M'}), ('S1', {'P', 'N', 'M', 'E'}),
                                   ('S2', {'P', 'N', 'M', 'H'}), ('S3', {'P', 'N', 'M', 'E', 'H'})])
LAYER_ARMS = {('off', False): ['walk', 'V1'], ('off', True): ['walk', 'V1', 'V3'],
              ('on', False): ['walk', 'V1', 'S1', 'A1', 'Sn', 'An'],
              ('on', True): ['walk', 'V1', 'S1', 'A1', 'Sn', 'An', 'V3', 'S3', 'A3']}


def table_pick(rows, K, have, MS):
    for r in rows:
        if r['needs'] <= have and r['cond'](K, MS):
            return r['id'], r['pick'](K)
    raise AssertionError('no row fired: the table is not total')


# ---------------------------------------------------------------------------
# Knowledge per (cell, subject, mode) from facts + counters (never from timings).
# ---------------------------------------------------------------------------
def site_counts(key):
    c = CNT.get((key[0], 'site(G1)', key[1], key[2]))
    if c is None:
        return None
    nb = c['nbuf']
    return {k: v / nb for k, v in c.items()}


def knowledge(key):
    cell, subj, mode = key
    f = FACT[base_name(subj)]
    c = site_counts(key)
    if c is None or c['uses'] == 0:
        return None                              # unreached: the site never runs (leg U)
    n = f['n']
    m = f['pm'] / f['nbuf']
    adv = n - m * TOKC[cell] if mode == 'all' else n
    K = dict(CELLP[cell])
    K['N'] = n                                   # call entry: n - startpos (first call); find-all's
                                                 # later calls see the REMAINING subject, still >> 64
    K['E'] = adv / c['uses']                     # "exemplar" gap: IN SAMPLE the subject is its own exemplar
    K['H'] = adv / c['cold'] if c['cold'] else float('inf')   # previous step span (activation span)
    K['Lact'] = K['H']
    K['mode'] = mode
    return K


def regime_of(K, l_star=64.0, g_star=18.5):
    """costmodel's placement (the one regime_tables §3 reports in), from counted L and g."""
    if K['Lact'] < l_star:
        return 'DINGHY'
    return 'TUG' if K['E'] < g_star else 'LINER'


def ns(key, arm):
    g = G[key]
    if arm == 'walk':
        return g['walk#b']['base']
    return g[arm]['ns'] if arm in g else None


def aa_floor(key):
    return G[key]['walk#b']['floor']


REGIMES = ['DINGHY', 'TUG', 'LINER']


PICKABLE = {False: ['walk', 'V1', 'A1'], True: ['walk', 'V1', 'A1', 'A3']}


def population(iterator):
    """groups on which every form the TABLE can pick was timed (all mode for iterator).
    The measured best is the min over the layer's arms that WERE timed; a group missing
    a non-pickable arm is kept and counted as partial (regime_eval.md §2.6: a population
    restricted to fully-timed groups dropped the very L = 8 cells the R3 correction rests on)."""
    keys = []
    for key in G:
        if iterator and key[2] != 'all':
            continue
        need = LAYER_ARMS[('on', True)] if STRICT else PICKABLE[iterator]
        if any(ns(key, a) is None for a in need):
            continue
        if base_name(key[1]).startswith('g1-f3-') or '@' in key[1]:
            continue
        if knowledge(key) is None:
            continue
        keys.append(key)
    return keys


def score(rows, MS, fil, simd, keys, iterator, policy=None):
    """regret per regime; policy overrides the table with a fixed arm."""
    have = FILTERS[fil]
    arms = LAYER_ARMS[('on' if simd else 'off', iterator)]
    reg = collections.Counter(); walk = collections.Counter(); aa = collections.Counter()
    fired = collections.Counter(); cells = []
    for key in keys:
        K = dict(knowledge(key)); K['simd'] = simd
        K['M'] = 'iter' if (iterator and key[2] == 'all') else 'one-shot'
        if policy:
            rid, pick = 'fixed', policy
        else:
            rid, pick = table_pick(rows, K, have, MS)
        if pick not in arms:
            pick = 'walk' if pick != 'A3' else 'A1'     # an unavailable form reads its layer's fallback
        best = min((a for a in arms if ns(key, a) is not None), key=lambda a: ns(key, a))
        rg = regime_of(K)
        r = ns(key, pick) - ns(key, best)
        reg[rg] += r; walk[rg] += ns(key, 'walk'); aa[rg] += aa_floor(key); fired[rid] += 1
        cells.append((key, rg, rid, pick, best, r))
    return reg, walk, aa, fired, cells


def fmt(reg, walk):
    return '  '.join('%s %8.1f us (%5.1f%%)' % (rg[0], reg[rg] / 1e3, 100 * reg[rg] / walk[rg] if walk[rg] else 0)
                     for rg in REGIMES)


def visibly_worse(cc, bc, walk, regimes):
    """PRE-DECLARED (regime_eval.md §4.2): over the cells whose pick the control MOVED, in at
    least one target regime, the summed regret increase exceeds max(2 x the moved cells'
    summed NULL thresholds, 1.0 point of the regime's walk).  A cell's NULL threshold is
    gridread's: max(its A/A floor, 3.09% of its walk)."""
    d = collections.Counter(); nul = collections.Counter()
    for x, y in zip(bc, cc):
        if x[3] == y[3]:
            continue
        rg = x[1]
        d[rg] += y[5] - x[5]
        nul[rg] += max(aa_floor(x[0]), 0.0309 * ns(x[0], 'walk'))
    for rg in regimes:
        if walk[rg] and d[rg] > max(2 * nul[rg], 0.01 * walk[rg]):
            return True
    return False


def main():
    print('population rule:', 'STRICT (every form timed, all mode)' if STRICT else 'PICKABLE (every form the table can pick timed)')
    print('replay_proto: IN-SAMPLE replay of regime_tables rev 0.2 on the grid1 slot', OUT)
    print('measurement set:', MS_V0['id'])
    for iterator in (False, True):
        keys = population(iterator)
        print()
        print('=' * 78)
        print('population: %s, %d groups (%s)' % ('iterator (all mode, keep arms timed)' if iterator else 'no iterator',
                                                  len(keys), ', '.join('%s %d' % (rg, sum(1 for k in keys if regime_of(knowledge(k)) == rg)) for rg in REGIMES)))
        for simd in (True, False):
            print('-- SIMD %s' % ('on' if simd else 'off'))
            fils = ['S2', 'S3'] if iterator else ['S0', 'S1']
            for fil in fils:
                reg, walk, aa, fired, _ = score(ROWS, MS_V0, fil, simd, keys, iterator)
                print('   table %s  %s   rows fired: %s' % (fil, fmt(reg, walk), dict(fired)))
            for pol in (['walk', 'V1'] + (['A1'] + (['A3'] if iterator else []) if simd else [])):
                reg, walk, aa, _, _ = score(ROWS, MS_V0, fils[0], simd, keys, iterator, policy=pol)
                print('   always %-4s %s' % (pol, fmt(reg, walk)))
            print('   A/A floor  ' + '  '.join('%s %8.1f us' % (rg[0], aa[rg] / 1e3) for rg in REGIMES))

    # ------------------------------------------------------------------
    # failing-direction controls (regime_eval.md §4): each must score visibly worse
    # ------------------------------------------------------------------
    print()
    print('=' * 78)
    print('CONTROLS (pre-declared "visibly worse": on the MOVED cells, summed regret increase > max(2 x their summed NULL thresholds, 1 pt of the regime walk) in a target regime)')
    swapped = dict(MS_V0, gstar_on=MS_V0['gstar_off'], gstar_off=MS_V0['gstar_on'])
    pf_only = dict(MS_V0, gstar_on={k: MS_V0['gstar_on']['pf1'] for k in MS_V0['gstar_on']},
                   gstar_off={k: MS_V0['gstar_off']['pf1'] for k in MS_V0['gstar_off']})
    old_r3 = [r for r in ROWS if r['id'] != 'R3a']      # R3b then catches span < 14 too
    old_r3 = [dict(r, cond=(lambda K, MS: K['M'] == 'iter' and K['simd'] and K['H'] < MS['h_r3b']))
              if r['id'] == 'R3b' else r for r in old_r3]
    ctrls = [('swapped g* (on<->off)', ROWS, swapped, [('S1', True, False), ('S1', False, False), ('S3', True, True)], REGIMES),
             ('g* per site -> PF figure', ROWS, pf_only, [('S1', True, False), ('S1', False, False)], REGIMES),
             ('old R3 (A3 at span < 14 B)', old_r3, MS_V0, [('S2', True, True), ('S3', True, True)], ['DINGHY'])]
    for r in ROWS:
        if r['id'] == 'R7':
            continue
        ctrls.append(('delete %s' % r['id'], [x for x in ROWS if x is not r], MS_V0,
                      [('S0', True, False), ('S0', False, False), ('S1', True, False), ('S1', False, False),
                       ('S2', True, True), ('S3', True, True), ('S3', False, True)], REGIMES))
    for name, rows, ms, cfgs, target in ctrls:
        verdicts = []
        for fil, simd, iterator in cfgs:
            keys = population(iterator)
            b, walk, aa, bf, bc = score(ROWS, MS_V0, fil, simd, keys, iterator)
            c, _, _, cf, cc = score(rows, ms, fil, simd, keys, iterator)
            moved = sum(1 for x, y in zip(bc, cc) if x[3] != y[3])
            if moved == 0:
                v = 'UNREACHED'
            else:
                v = 'WORSE' if visibly_worse(cc, bc, walk, target) else 'NOT-WORSE'
            d = '/'.join('%+.1f' % ((c[rg] - b[rg]) / 1e3) for rg in REGIMES)
            verdicts.append('%s/%s%s: %s (moved %d, d us %s)' % (fil, 'on' if simd else 'off', '+it' if iterator else '', v, moved, d))
        print('  %-28s %s' % (name, '; '.join(verdicts)))

    # A/A: the same arm twice must read ~0
    keys = population(False)
    tot = sum(abs(G[k]['walk#b']['ns'] - G[k]['walk#b']['base']) for k in keys)
    w = sum(ns(k, 'walk') for k in keys)
    print('  %-28s regret(walk#b vs walk) summed %.1f us = %.2f%% of the walk (must sit inside the floor: it IS the floor)'
          % ('A/A', tot / 1e3, 100 * tot / w))

    # per-cell listing (S1, SIMD on), diffable
    print()
    print('=' * 78)
    print('PER-CELL (filter S1, SIMD on, no iterator): cell subject mode regime row pick best regret_ns')
    _, _, _, _, cells = score(ROWS, MS_V0, 'S1', True, population(False), False)
    for key, rg, rid, pick, best, r in sorted(cells, key=lambda x: -x[5])[:25]:
        print('  %-8s %-30s %-5s %-6s %-4s %-4s %-4s %10.1f' % (key[0], key[1], key[2], rg, rid, pick, best, r))
    print('  ... (%d cells; top 25 by regret)' % len(cells))


if __name__ == '__main__':
    main()
