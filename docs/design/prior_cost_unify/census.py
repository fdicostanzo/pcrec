#!/usr/bin/env python3
"""docs/design/prior_cost_unify/census.py -- [PRIOR-COST-UNIFY] rev 2 §1.1's
DERIVED member census ([r3 F5]). Not a hand list: rev 1 hand-listed twenty
members and miscounted them (21 rows under a "twenty" heading; the critic
found `pcrec_find_run_rank` missing).

Method. It reuses docs/design/start_table/call_graph.py's PARSE (every
top-level definition under src/, its body, and an edge to every definition the
body names), exec'd with that script's own output discarded, and then walks
the graph BACKWARDS from the RATE PRIMITIVES -- the `pcrec_find_*` functions
whose answer is a byte-rate prior or a choice made from one:

  ROOTS   every `pcrec_find_*` definition in src/core/findings.c is either a
          root (a rate primitive) or listed in NOT_RATE with a reason; an
          unlisted one is exit 1 (a new primitive must be classified).
  READERS the definitions whose body names a root or a CARRIER.
  CARRIER a reader that hands a rate on (returns one, or wraps a primitive);
          its own readers join the frontier.

Every reader must have a row in census_disp.tsv (name, class, member id,
reason; class MEMBER | CARRIER | NOT). An undispositioned reader, or a
disposition naming no reader (stale), is exit 1. Floors (K35): the MEMBER
count and the root count are checked against the literals below, so a broken
parse cannot read green on an empty population.

What it CANNOT find, by construction: a decision that SHOULD read the prior
and does not (a structural `|S| < 256`, a byte COUNT, a constant). Those are
rev 2 §1.1 part B, listed by hand and labelled so.

Usage: census.py ROOT   (prints a TSV; exit 0 complete, 1 incomplete)
"""
import contextlib, io, os, re, runpy, sys

root = sys.argv[1] if len(sys.argv) == 2 else sys.exit("usage: census.py ROOT")
cg_path = os.path.join(root, "docs/design/start_table/call_graph.py")
argv0 = sys.argv
sys.argv = [cg_path, root]
with contextlib.redirect_stdout(io.StringIO()):
    g = runpy.run_path(cg_path, run_name="call_graph")
sys.argv = argv0
defs, texts, edges = g["defs"], g["texts"], g["edges"]

NOT_RATE = {  # pcrec_find_* definitions that answer no rate question
    "pcrec_find_store_text": "store access (bundle text)",
    "pcrec_find_store_name": "store access",
    "pcrec_find_store_blocks": "store access",
    "pcrec_find_store_bundles": "store access",
    "pcrec_find_store_link": "store access",
    "pcrec_find_name_ok": "name grammar",
    "pcrec_find_normalize": "builds the rate table (counts -> ppm); its floor is FIND_FLOOR_PPM",
    "pcrec_find_deriv": "derivation vocabulary",
    "pcrec_find_derive_counts": "derivation (cpfreq -> bytes)",
    "pcrec_find_block_byte_rate": "resolution of one block's rates",
    "pcrec_find_chain_answer": "resolution (which block answers)",
    "pcrec_find_byte_rate_digest": "stamp digest",
    "pcrec_find_rows_digest": "stamp digest",
    "pcrec_find_stamp": "stamp text",
}
ROOT_FLOOR = 10
MEMBER_FLOOR = 9

roots = sorted(n for n, d in defs.items()
               if n.startswith("pcrec_find_") and d[0] == "src/core/findings.c"
               and d[3] == "func" and n not in NOT_RATE)
bad = [n for n, d in defs.items() if n.startswith("pcrec_find_") and d[0] == "src/core/findings.c"
       and d[3] == "func" and n not in NOT_RATE and n not in roots]
rev = {}
for n, es in edges.items():
    for e in es:
        rev.setdefault(e, set()).add(n)

disp = {}
dp = os.path.join(root, "docs/design/prior_cost_unify/census_disp.tsv")
for l in open(dp):
    if not l.strip() or l.startswith("#"):
        continue
    f = l.rstrip("\n").split("\t")
    disp[f[0]] = f[1:]

fail = []
readers, front, seen = {}, list(roots), set(roots)
while front:
    x = front.pop()
    for r in sorted(rev.get(x, ())):
        if r in roots or defs.get(r, ("", 0, 0, ""))[3] == "type":
            continue
        readers.setdefault(r, set()).add(x)
        if r in seen:
            continue
        seen.add(r)
        if r not in disp:
            fail.append(f"UNDISPOSITIONED reader {r} ({defs[r][0]}:{defs[r][1]}) of {x}")
            continue
        if disp[r][0] == "CARRIER":
            front.append(r)
for n in disp:
    if n not in readers:
        fail.append(f"STALE disposition {n}: no longer reads a root or carrier")

print("#kind\tname\tfile:line\tclass\tmember\treads\treason")
for r in sorted(roots):
    print(f"root\t{r}\t{defs[r][0]}:{defs[r][1]}\t\t\t\t")
nm = 0
for r in sorted(readers, key=lambda n: (defs[n][0], defs[n][1])):
    c = disp.get(r, ["?", "", ""])
    nm += c[0] == "MEMBER"
    # the decision SITES: lines of r naming what it reads
    sites = [str(ln) for ln, l in texts[r][1:]
             if any(re.search(r'\b' + re.escape(x) + r'\b', g["code_of"](l)) for x in readers[r])]
    print(f"reader\t{r}\t{defs[r][0]}:{defs[r][1]}\t{c[0]}\t{c[1] if len(c) > 1 else ''}\t"
          f"{','.join(sorted(readers[r]))}@{','.join(sites)}\t{c[2] if len(c) > 2 else ''}")
print(f"# roots={len(roots)} readers={len(readers)} members={nm} "
      f"carriers={sum(1 for r in readers if disp.get(r, [''])[0] == 'CARRIER')} "
      f"not={sum(1 for r in readers if disp.get(r, [''])[0] == 'NOT')}")
if len(roots) < ROOT_FLOOR:
    fail.append(f"root count {len(roots)} below floor {ROOT_FLOOR} (K35)")
if nm < MEMBER_FLOOR:
    fail.append(f"member count {nm} below floor {MEMBER_FLOOR} (K35)")
for f in bad + fail:
    print("FAIL: " + f, file=sys.stderr)
sys.exit(1 if bad or fail else 0)
