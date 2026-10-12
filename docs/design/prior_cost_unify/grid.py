#!/usr/bin/env python3
"""docs/design/prior_cost_unify/grid.py -- rev 2 §5.4 control (b')'s
PROTOTYPE ([r3 F3]): the both-formulas disagreement count as an ARITHMETIC
GRID over (mass, K, gap, bar), per formula pair, with a PLANTED off-by-one
per pair that must read > 0. Rev 1's count ran over the corpus only, where
the populated (mass, K, gap) region is sparse and a disagreement count of 0
could not fail; here the grid decides AGREEMENT and the corpus (stamps, at
U1/U2) only says which grid regions are populated. emit_sweep, not this,
decides movers.

Each pair is (today's spelling, the primitive's spelling). A U1 pair must read
0 (the input moved, the formula did not); each pair's plant must read > 0.
Exits 1 if a U1 pair disagrees or a plant reads 0.
"""
import sys
from fractions import Fraction as F
M = 1_000_000

# ---- ladders ----------------------------------------------------------
masses = sorted({2, 3, 7, 255, 256, 1000, 3906, 62_500, 64_000, 99_999,
                 100_000, 333_333, 500_000, 999_999, M} |
                {M // g for g in range(1, 70)} | {M // g + 1 for g in range(1, 70)})
Ks = [0, 1, 2, 3, 7, 31, 100, 101, 1000, 50_000]
gaps = [1, 2, 3, 4, 9, 12, 16, 26, 30]

# ---- pair #3 (R4): `ppm*gap > 10^6` vs adv = 10^6/ppm (rational) < gap ---
def r4_old(ppm, gap): return ppm * gap > M
def r4_new(ppm, gap): return ppm > 0 and F(M, ppm) < gap        # exact
def r4_rev1(ppm, gap): return ppm > 0 and (10**9 // ppm) < 1000 * gap  # rev 1's adv_milli
def r4_plant(ppm, gap): return ppm * gap >= M                    # off by one at equality

# ---- the CUBE_RUN product, one rounding per call site -----------------
def prod(ms, up):
    h = M
    for m in ms:
        h = (h * m + (M - 1 if up else 0)) // M
    return h
def prod_plant(ms, up):            # ceil spelled (x + 10^6) / 10^6: off by one
    h = M
    for m in ms:
        h = (h * m + (M if up else 0)) // M
    return h

# ---- pair #4 (handoff K admission), its formula kept at U1 ------------
def k_admit(h, K, m):
    if h == 0: return True
    if K * h >= M: return False
    return (M - K * h) * m > M * h

def run(name, cells, old, new):
    n = d = 0
    for c in cells:
        n += 1
        d += old(*c) != new(*c)
    return n, d

out, bad = [], False
cells3 = [(p, g) for p in masses for g in gaps]
for nm, f, want0 in (("#3 R4 vs rational adv", r4_new, True),
                     ("#3 R4 vs rev1 adv_milli", r4_rev1, True),
                     ("#3 PLANT >= for >", r4_plant, False)):
    n, d = run(nm, cells3, r4_old, f)
    out.append((nm, n, d)); bad |= (d != 0) if want0 else (d == 0)

runs = [(a, b) for a in masses[::3] for b in masses[::4]] + \
       [(a, b, c) for a in masses[::6] for b in masses[::6] for c in masses[::6]]
for up, who in ((True, "#4 landmark (ceil/step)"), (False, "#7 prefix_k chain (floor/step)")):
    n, d = run(who, [(r,) for r in runs], lambda r: prod(r, up), lambda r: prod(list(r), up))
    out.append((who + " vs primitive(round=" + ("UP" if up else "DOWN") + ")", n, d)); bad |= d != 0
    n, d = run(who, [(r,) for r in runs], lambda r: prod(r, up), lambda r: prod(r, not up))
    out.append((who + " PLANT: the other rounding", n, d)); bad |= d == 0
    if up:   # the ceil spelling's own off-by-one; a floor has no such spelling
        n, d = run(who, [(r,) for r in runs], lambda r: prod(r, up), lambda r: prod_plant(r, up))
        out.append((who + " PLANT: ceil off by one", n, d)); bad |= d == 0

cells4 = [(prod(r, True), K, m) for r in runs[::7] for K in Ks for m in masses[::5]]
n, d = run("#4", cells4, k_admit, lambda h, K, m: k_admit(h, K, m))
out.append(("#4 K admission, formula kept (U1)", n, d)); bad |= d != 0
n, d = run("#4", cells4, k_admit, lambda h, K, m: k_admit(h, K + 1, m))
out.append(("#4 PLANT: K+1", n, d)); bad |= d == 0

# ---- a U2 illustration: R4 against a COST verdict (reseed vs stepping),
# with the two MEASURED Mac cells (hyb_reseed.md §3). Not a prediction of
# U2's movers (cross-box cells; the gap is MEASURED, not derived): it shows
# the grid naming the disagreement BAND a U2 commit would be counted on.
for cls, att, gap in (("frameless", F(16, 10), 16), ("framed", F(86, 10), 4)):
    # closed form: R4 arms (steps first) iff ppm > M/gap; the cost verdict
    # steps first iff adv*attempt < reseed, i.e. ppm > M*attempt/25
    lo, hi = sorted((F(M, gap), F(M) * att / 25))
    out.append((f"U2 illustration {cls}: R4 vs reseed-cost band, ppm in ({float(lo):.0f}, {float(hi):.0f}]", 0, 0))

for nm, n, d in out:
    print(f"{nm}\tcells={n}\tdisagree={d}")
sys.exit(1 if bad else 0)
