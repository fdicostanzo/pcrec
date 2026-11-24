#!/usr/bin/env python3
# repoint.py BINDERS_OUT : window_split.md rev 2.1 §8.1's per-unit re-point lists (r98 R5), DERIVED
# from a binders.py run over the assembled tip (never hand-listed): every binder row whose new home
# differs from its B key, grouped by the commit that moves its text. The unit of a destination
# file is the commit that creates it (§8.1); kit_pos.c's binders all lie in the text U3 moves
# (kit_run_member, kit_mass, kit_run_set, kit_run_at), which the script ASSERTS by name.
# Prints `UNIT FILE POP ID` lines, then `repoint: N rows in K units`. Exit 1 on a row whose new
# home has no unit (a file the order does not create) or a kit_pos.c row outside U3's names.
import sys
PEEL = ['vform', 'find', 'floor', 'test', 'text', 'span', 'efind', 'ren', 'frame', 'legacy', 'parts',
        'ask', 'plan', 'check', 'cands', 'verify', 'margin', 'stop']
UNIT = {'kit_kb.c': 'C0b', 'kit_pick.c': 'U3', 'kit_pos.c': 'U3', 'presence.c': 'U3',
        'window.h': 'U4', 'window_decide.c': 'U24'}
for i, p in enumerate(PEEL): UNIT[f'window_{p}.c'] = f'U{6 + i}'
U3_POS = {'kit_run_member', 'S3106'}      # the binders of kit_run_member's text (B :937-962)
rows, bad = [], 0
for l in open(sys.argv[1]):
    c = l.rstrip('\n').split('\t')
    if len(c) < 6 or c[0] not in ('mech', 'g2', 'purity', 'census', 'rows'): continue
    pop, ident, st, new, old = c[0], c[1], c[3], c[4], c[5]
    if not st.startswith('OK') or not new or new == old: continue
    if pop == 'purity': old = 'window.c'
    if new == old: continue
    u = UNIT.get(new)
    if u is None:
        print(f'NO UNIT for {pop} {ident} -> {new}'); bad += 1; continue
    if new == 'kit_pos.c' and not any(ident.startswith(x) for x in U3_POS):
        print(f'kit_pos.c row {pop} {ident} is not in U3\'s moved text'); bad += 1
    rows.append((int(u[1:]) if u[1:].isdigit() else 0, u, new, pop, ident))
for _, u, new, pop, ident in sorted(rows):
    print(f'{u}\t{new}\t{pop}\t{ident}')
print(f'repoint: {len(rows)} rows in {len({r[1] for r in rows})} units')
sys.exit(1 if bad else 0)
