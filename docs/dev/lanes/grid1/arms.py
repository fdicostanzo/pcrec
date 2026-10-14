#!/usr/bin/env python3
"""grid1: read, VALIDATE and expand the arm tables (README.md "The arm contract").

  arms.py OUT validate [SET]             problems on stdout, exit 1 if any
  arms.py OUT items  [SET] [PHASE]       cell arm role subject mode  (one per timed item)
  arms.py OUT groups [SET] [PHASE]       cell subject mode arms      (base first, comma list)
  arms.py OUT cells  [SET] [PHASE]       one cell per line

SET   timed (default) = $OUT/arms.tsv + every $OUT/ext/*/arms.tsv, merged;
      f2              = $OUT/arms_f2.tsv (F2's perf cells; never timed);
      all             = timed + f2 (check.sh's population).
PHASE F1 = own cells (not f3-*), F3 = f3-* cells, EXT = cells whose base an
      ext set declares, any (default) = every cell.

Rows are additive: a (cell, arm) may appear on several rows (each a cross
product of its subjects x modes); its role must be the same on every row.
Each cell has exactly ONE base arm and the base must cover every (subject,
mode) any arm of its cell lists. A subject token is NAME or NAME@OFF (OFF =
the start offset past a 64-aligned block, GRID_OFF); NAME must exist as
$OUT/subj/NAME (a file, a directory, or a *.list manifest). Every (cell, arm)
needs an executable $OUT/bin/<cell>/<arm>/run.
"""
import glob, os, sys

def sources(out, which):
    own = [os.path.join(out, "arms.tsv")]
    ext = sorted(glob.glob(os.path.join(out, "ext", "*", "arms.tsv")))
    f2 = [os.path.join(out, "arms_f2.tsv")]
    return {"timed": [("own", p) for p in own] + [("ext", p) for p in ext],
            "f2": [("f2", p) for p in f2],
            "all": [("own", p) for p in own] + [("ext", p) for p in ext]}[which]

def load(out, which):
    rows, probs = [], []
    for origin, p in sources(out, which):
        if not os.path.exists(p):
            if origin != "ext": probs.append(f"missing {p}")
            continue
        for ln, line in enumerate(open(p), 1):
            line = line.rstrip("\n")
            if not line or line.startswith("#"): continue
            f = line.split("\t")
            if len(f) != 5: probs.append(f"{p}:{ln}: {len(f)} columns, want 5 (cell arm role subjects modes)"); continue
            cell, arm, role, subs, modes = f
            if role not in ("base", "arm"): probs.append(f"{p}:{ln}: role {role!r} (base|arm)")
            sl = [s for s in subs.split(",") if s]
            ml = [m for m in modes.split(",") if m]
            for m in ml:
                if m not in ("first", "all"): probs.append(f"{p}:{ln}: mode {m!r} (first|all)")
            if not sl or not ml: probs.append(f"{p}:{ln}: empty subjects or modes")
            rows.append((origin, p, ln, cell, arm, role, sl, ml))
    return rows, probs

def model(out, which):
    rows, probs = load(out, which)
    if which == "all":       # f2 is its own namespace: validate it apart, merge the items
        r2, p2 = load(out, "f2")
        return build(out, rows, probs) , build(out, r2, p2)
    return build(out, rows, probs), None

def build(out, rows, probs):
    role, origin, items, order = {}, {}, {}, []
    for o, p, ln, cell, arm, r, sl, ml in rows:
        k = (cell, arm)
        if k in role and role[k] != r: probs.append(f"{p}:{ln}: {cell}/{arm} role {r} here, {role[k]} elsewhere")
        role.setdefault(k, r)
        if r == "base": origin.setdefault(cell, o)
        for s in sl:
            for m in ml:
                key = (cell, s, m)
                if key not in items: items[key] = []; order.append(key)
                if arm not in items[key]: items[key].append(arm)
    cells = sorted({c for c, _ in role})
    base = {}
    for c in cells:
        b = [a for (cc, a), r in role.items() if cc == c and r == "base"]
        if len(b) != 1: probs.append(f"cell {c}: {len(b)} base arms {b}, want exactly 1"); continue
        base[c] = b[0]
    for (c, s, m), arms in items.items():
        if c in base and base[c] not in arms: probs.append(f"cell {c}: base {base[c]} does not cover {s} {m} (arms {','.join(arms)})")
        nm = s.split("@")[0]
        if not os.path.exists(os.path.join(out, "subj", nm)): probs.append(f"subject {nm} ({c}) not in {out}/subj")
        if "@" in s and not s.split("@")[1].isdigit(): probs.append(f"subject token {s}: offset not a number")
    for (c, a) in role:
        if not os.access(os.path.join(out, "bin", c, a, "run"), os.X_OK): probs.append(f"no executable bin/{c}/{a}/run")
    return dict(role=role, origin=origin, items=items, order=order, base=base, probs=sorted(set(probs)))

def phase_of(m, cell):
    if cell.startswith("f3-"): return "F3"
    return "EXT" if m["origin"].get(cell) == "ext" else "F1"

def main():
    out, cmd = sys.argv[1], sys.argv[2]
    which = sys.argv[3] if len(sys.argv) > 3 else "timed"
    phase = sys.argv[4] if len(sys.argv) > 4 else "any"
    m, m2 = model(out, which)
    ms = [m] + ([m2] if m2 else [])
    if cmd == "validate":
        probs = [p for x in ms for p in x["probs"]]
        for p in probs: print(p)
        n = sum(len(x["items"]) for x in ms)
        print(f"arms: {sum(len(x['role']) for x in ms)} (cell, arm) pairs, {n} groups, "
              f"{sum(len(v) for x in ms for v in x['items'].values())} items, {len(probs)} problems")
        sys.exit(1 if probs else 0)
    for x in ms:
        for (c, s, mo) in x["order"]:
            if phase != "any" and phase_of(x, c) != phase: continue
            arms = x["items"][(c, s, mo)]
            b = x["base"].get(c)
            arms = ([b] if b in arms else []) + [a for a in arms if a != b]
            if cmd == "items":
                for a in arms: print(f"{c}\t{a}\t{'base' if a == b else 'arm'}\t{s}\t{mo}")
            elif cmd == "groups":
                print(f"{c}\t{s}\t{mo}\t{','.join(arms)}")
        if cmd == "cells":
            for c in sorted({c for c, _, _ in x["order"] if phase == "any" or phase_of(x, c) == phase}): print(c)

if __name__ == "__main__":
    main()
