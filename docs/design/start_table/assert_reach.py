#!/usr/bin/env python3
"""docs/design/start_table/assert_reach.py -- [r2.1 sound-S-N5]. The DERIVED
population behind start_table.md §1.3(b): "no newly evaluated predicate
reaches an assertion". Revision 2 stated the obligation with no population;
this prints it.

For every PREDICATE root -- each `inventory.tsv` member classed PRED, WALK or
INLINE (the things the refactor evaluates to select a row) -- it walks
call_graph.py's own edges (imported, not re-parsed) and records every
`pcrec_ctx_fail(` line in a reached definition. The walk does NOT enter:
  - a table (a walk's table holds emit hooks as well as predicates; each
    predicate it holds is its own root, so nothing is lost),
  - the facts layer (src/facts/): a fact ASK is recorded instead, and each
    asked fact's owner file (facts.def's owner column) is listed with its own
    ctx_fail sites -- a fact derives once per compile and caches, so its
    assertion fires on the FIRST ask, whichever predicate makes it,
  - the allocation-failure path (`pcrec_ctx_nomem`, `sb_*`): out-of-memory
    is not an order-sensitive internal assertion.

Output (stdout, TSV):
  pred-assert  ROOT  DEF  FILE:LINE  text   -- an assertion a predicate reaches
  pred-asks    ROOT  FACT                    -- a fact seed the root asks
  fact-assert  FACT  FILE:LINE  text         -- an assertion in an asked fact's owner
and a summary on stderr. Read-only.
Usage: assert_reach.py ROOT inventory.tsv
"""
import collections, contextlib, io, os, re, runpy, sys

root, invp = sys.argv[1], sys.argv[2]
here = os.path.dirname(os.path.abspath(__file__))
sys.argv = [os.path.join(here, "call_graph.py"), root]
with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
    g = runpy.run_path(os.path.join(here, "call_graph.py"))
defs, edges, texts, SEEDS = g["defs"], g["edges"], g["texts"], g["SEEDS"]
code_of = g["code_of"]

roots = []
for l in open(invp):
    if l.startswith("#") or not l.strip():
        continue
    p = l.rstrip("\n").split("\t")
    if len(p) > 1 and p[1] in ("PRED", "WALK", "INLINE"):
        roots.append(p[0])

FAIL = re.compile(r'\bpcrec_ctx_fail\s*\(')


def fails_in(n):
    out = []
    for ln, l in texts.get(n, [])[1:]:
        if FAIL.search(code_of(l)):
            out.append((ln, l.strip()[:90]))
    return out


owner_of_fact = {}
for m in re.finditer(r'^PF_FACT\(\s*([A-Z_]+)\s*,.*?"(src/facts/[^"]+)"',
                     open(os.path.join(root, "src/facts/facts.def")).read(), re.M):
    owner_of_fact[f"pcrec_fact_{m.group(1).lower()}"] = m.group(2)

npa, asked = 0, set()
roots_hit = set()
for r in sorted(roots):
    seen, st = set(), [r]
    while st:
        x = st.pop()
        if x in seen or x not in defs:
            continue
        seen.add(x)
        f, a, b, k = defs[x]
        if x != r and (k in ("table", "data") or f.startswith("src/facts/")):
            if x in SEEDS and x.startswith("pcrec_fact_"):
                asked.add(x)
                print(f"pred-asks\t{r}\t{x}")
            continue
        if x in ("pcrec_ctx_fail", "pcrec_ctx_nomem") or x.startswith("sb_"):
            continue
        for ln, t in fails_in(x):
            print(f"pred-assert\t{r}\t{x}\t{f}:{ln}\t{t}")
            npa += 1
            roots_hit.add(r)
        st.extend(sorted(edges[x], reverse=True))
nfa = 0
for fct in sorted(asked):
    of = owner_of_fact.get(fct)
    for x in sorted(defs):
        if defs[x][0] == of and defs[x][3] == "func":
            for ln, t in fails_in(x):
                print(f"fact-assert\t{fct}\t{of}:{ln}\t{t}")
                nfa += 1
print(f"ROOTS {len(roots)} ROOTS_REACHING_AN_ASSERT {len(roots_hit)} PRED_ASSERT_SITES {npa} "
      f"FACTS_ASKED {len(asked)} FACT_ASSERT_SITES {nfa}", file=sys.stderr)
