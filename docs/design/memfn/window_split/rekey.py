#!/usr/bin/env python3
# rekey.py ROOT BINDERS_OUT > MAP : the decider census map at the unit's tip (window_split.md rev 2
# §7, W23). Reads ROOT's tests/memfn/decider_census.tsv and a `binders.py` run over the assembled
# tip (its `census` rows give each member's defining file there), and prints the map with every
# member keyed by its new file (a header declaration is not a home: the .c that defines it wins;
# a `data` member declared in window.h is keyed window.h), then appends the unit's NEW members
# (NEW below: the O3 predicates (U3) and the accessors (U5)). Run the census against it with
# `decider_census.py --root ROOT --src TIP/memfn/src --map MAP --no-plants` and the tip's pins
# HITS 62 / MEMBER_COUNT 78 (§7 says which commit moves each).
import sys

NEW = [
    ('kit_pick.c', 'kit_tie_exchanges', 'fn', '-', 'TIE', '- (window_split O3: a question over the TIE table)'),
    ('kit_pick.c', 'kit_tie_reseeds', 'fn', '-', 'TIE', '- (window_split O3: a question over the TIE table)'),
    ('window_stop.c', 'wf_a_choose', 'fn', '-', 'KEY', "- (window_split A2: decide's Table A walk)"),
    ('window_margin.c', 'wf_m_choose', 'fn', '-', 'M', "- (window_split A3: decide's Table M walk)"),
    ('window_ren.c', 'wf_ren_pieces', 'fn', '-', 'T-FRAME,T-STREAM', "- (window_split O1: wf_plan_site's pieces)"),
    ('window_ren.c', 'wf_ren_check', 'excluded', '-',
     "the renderer tables' self-check (wf_tables_check's part; it decides nothing)", '-'),
    ('window_ren.c', 'wf_legacy_stream', 'fn', '-', 'T-STREAM', "- (window_split A4: the legacy frames' declared stream)"),
]

# rows whose member ceases to exist: kit.h's prototype of kit_tie_takes (O3 makes it static in
# kit_pick.c, whose own `fn` row stays), so its `excluded` prototype row is deleted in U3.
DROP = {('kit.h', 'kit_tie_takes')}

root, bout = sys.argv[1], sys.argv[2]
home = {}
for l in open(bout):
    c = l.rstrip('\n').split('\t')
    if c[0] == 'census' and len(c) > 5:
        home[(c[5], c[1], c[2])] = c[4]
for l in open(root + '/tests/memfn/decider_census.tsv'):
    if l.startswith('#') or not l.strip():
        sys.stdout.write(l); continue
    c = l.rstrip('\n').split('\t')
    if (c[0], c[1]) in DROP:
        continue
    h = home.get((c[0], c[1], c[2]))
    if h:
        hs = h.split(',')
        cs = [x for x in hs if x.endswith('.c')]
        c[0] = 'window.h' if c[2] == 'data' and 'window.h' in hs else (cs or hs)[0]
    print('\t'.join(c))
for r in NEW:
    print('\t'.join(r))
