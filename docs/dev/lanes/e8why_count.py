#!/usr/bin/env python3 -I
"""e8why_count.py OUTDIR -- counts only (no clock): per (J1 mover, subject) cell, the member density of the scanned set.
The set is read from the V1 artifact's rx_*_pf__mask (range/eq/cube operands); the cell list and deltas from e8_cells.tsv."""
import re, sys, os, numpy as np
W = "/home/pcrec/projects/pcrec/worktrees/e8min/build/e8slot_r2"
def memberset(art):
    t = open(art).read()
    m = re.search(r"unsigned long long rx_\w*?pf__mask\(const unsigned char \*p\)\s*\{(.*?)\n\}", t, re.S)
    body = m.group(1); s = set()
    for l, w in re.findall(r"range\(v, (0x[0-9a-f]+), (\d+)\)", body): s |= set(range(int(l, 16), int(l, 16) + int(w)))
    for b in re.findall(r"eq\(v, (0x[0-9a-f]+)\)", body): s.add(int(b, 16))
    for mk, val in re.findall(r"cube\(v, (0x[0-9a-f]+|\d+), (0x[0-9a-f]+|\d+)\)", body):
        mk = int(mk, 0); val = int(val, 0); s |= {b for b in range(256) if b & mk == val}
    assert "vor" in body or len(re.findall(r"range|eq|cube", body)) == 1, body
    return frozenset(s)
rows = [l.rstrip("\n").split("\t") for l in open(W + "/e8_cells.tsv")][1:]
out = []
cache = {}
for r in rows:
    if r[0] != "J1": continue
    q = r[2].split("-", 1)[1] if r[2].startswith("j1-") else r[1].split("-", 1)[1]
    cell, subj, n, shape, delta, verdict, matches = r[1], r[3], int(r[4]), r[5], float(r[10]), r[11], int(r[13])
    q = cell.split("-", 1)[1]
    S = memberset(f"{W}/bin/j1-{q}/V1/art.c")
    if subj not in cache: cache[subj] = np.fromfile(f"{W}/subj/{subj}", dtype=np.uint8)
    a = cache[subj]; lut = np.zeros(256, bool); lut[list(S)] = True
    hit = lut[a]; pos = np.flatnonzero(hit); H = len(pos)
    gaps = np.diff(pos) if H > 1 else np.array([1])
    blocks = hit[: len(hit) // 8 * 8].reshape(-1, 8).any(1)
    # stops after a hit: the next hit is within the same 8-byte block as the previous one (cache served)
    out.append(dict(q=q, subj=subj, n=n, shape=shape, delta=delta, v=verdict, matches=matches, members=len(S),
        dens=H / n, meangap=n / max(H, 1), med=float(np.median(gaps)), g1=float((gaps == 1).mean()), g8=float((gaps <= 8).mean()),
        occ=float(blocks.mean()), cv=float(gaps.std() / max(gaps.mean(), 1e-9)), hm=H / max(matches, 1), hits=H))
import json; json.dump(out, open(sys.argv[1] + "/counts.json", "w"))
print("q subj shape delta v | members dens meangap med g1 occ cv hits/match")
for o in sorted(out, key=lambda o: (o["q"], o["subj"])):
    print(f'{o["q"]:4} {o["subj"][:22]:22} {o["shape"]} {o["delta"]:+6.1f} {o["v"]} | {o["members"]:3} {o["dens"]:.3f} {o["meangap"]:8.2f} {o["med"]:5.0f} {o["g1"]:.2f} {o["occ"]:.2f} {o["cv"]:5.2f} {o["hm"]:9.1f}')

# ---- second pass: predictability of the stop pattern (counts only) ----
def ideal_mispred(bits, k):
    """mispredicts of an ideal order-k context predictor (per context, the minority outcome), as a rate per element"""
    b = bits.astype(np.uint32); n = len(b)
    ctx = np.zeros(n, np.uint32)
    for j in range(1, k + 1): ctx[j:] |= b[:-j] << (j - 1)
    c = np.bincount(ctx * 2 + b, minlength=2 << k).reshape(-1, 2)
    return float(np.minimum(c[:, 0], c[:, 1]).sum()) / n
if len(sys.argv) > 2:
    print("q subj delta v | hits/B  walkmisp/B(k6) (k10)  blkmisp/B  walk_misp/hit  d_ns/hit")
    rows2 = []
    for o in sorted(out, key=lambda o: (o["q"], o["subj"])):
        if o["hits"] == 0: continue
        S = memberset(f"{W}/bin/j1-{o['q']}/V1/art.c"); lut = np.zeros(256, bool); lut[list(S)] = True
        a = cache[o["subj"]]; hit = lut[a]
        # cap the subject at 8 MiB for speed (counts are rates)
        hit = hit[: 8 << 20]; nb = len(hit) // 8 * 8
        blk = hit[:nb].reshape(-1, 8).any(1)
        m6, m10 = ideal_mispred(hit, 6), ideal_mispred(hit, 10); mb = ideal_mispred(blk, 6) / 8
        dens = hit.mean(); dns = o["delta"] / 100.0
        rows2.append((o["q"], o["subj"], o["delta"], o["v"], dens, m6, m10, mb))
        print(f'{o["q"]:4} {o["subj"][:22]:22} {o["delta"]:+6.1f} {o["v"]} | {dens:.3f} {m6:.4f} {m10:.4f} {mb:.4f} {m6/dens:6.3f}')
    json.dump(rows2, open(sys.argv[1] + "/pred.json", "w"))
