#!/usr/bin/env python3
"""docs/design/start_table/call_graph.py -- the CALL-GRAPH half of the
derived start-decision inventory ([r2 sound-M2/M3/M6, checks-M1];
start_table.md §2.1 method 1).

Not a hand list. It parses every top-level C definition under src/ (functions
and `static const ... NAME[] = {` tables), draws an edge from each definition
to every other definition its body names (a call, a function pointer stored in
a table, a table walked), and then:

  1. R = everything reachable from the two emitters (pcrec_emit_dfa,
     pcrec_emit_vm); each member is tagged by whether the SEARCH-BODY WRITERS (the three emitters
     that write a search loop: emit_unanchored, emit_attempt,
     vm_emit_search_body) reach it, the STAMP WRITERS
     (pcrec_emit_dfa_scan_stamps, vm_emit_stamps) reach it, or only the
     emitter's PLAN (e.g. vm_plan_reseed, decided before either).
  2. SEEDS = the landmark-fact accessors facts.def declares (every
     pcrec_fact_<name> except the E1 shape facts `kinds`/`nullable`) plus
     `pcrec_artifact_has_dfa_scan` (the route read) -- the question "where can
     a match begin" is by definition a read of a landmark or of the route.
  3. FAMILY = the members of R that reach a SEED (the functions on a path from
     a search-body writer to a landmark read), plus the tables they walk.
  4. SITES = every `if (`/`while (`/`?`/`return` line inside a FAMILY body
     whose text names a SEED or another FAMILY member. Each is a candidate
     start decision; start_table.md §2.2 accounts for every one (a row, a
     reader of a row, a projection, or "not a start decision" with a reason).

Output (stdout, TSV): kind, name, file:line, detail. Read-only.
Usage: call_graph.py ROOT
"""
import os, re, sys, collections

root = sys.argv[1]
SRC = ["src"]
DEF_RX = re.compile(r'^(?:static\s+)?(?:inline\s+)?(?:const\s+)?[A-Za-z_][\w\s\*]*?\b([A-Za-z_]\w*)\s*\(([^;]*)$')
TAB_RX = re.compile(r'^(?:static\s+)?const\s+[\w\s\*]+?\b([A-Za-z_]\w*)\s*\[\s*\]\s*=\s*\{')
IDENT = re.compile(r'\b[A-Za-z_]\w*\b')

defs = {}   # name -> (file, start_line, end_line, kind)
texts = {}  # name -> body text (list of (lineno, line))
for d in SRC:
    for dp, _, fs in os.walk(os.path.join(root, d)):
        for f in sorted(fs):
            if not f.endswith(".c"):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, root)
            L = open(path, encoding="utf-8", errors="replace").read().split("\n")
            i = 0
            while i < len(L):
                l = L[i]
                m = TAB_RX.match(l)
                kind = None
                if m:
                    kind = "table"
                else:
                    m = DEF_RX.match(l)
                    if m and not l.startswith((" ", "\t", "#", "/", "*")):
                        # find the opening brace at column 0 within 8 lines
                        j = i
                        while j < len(L) and j < i + 8 and not L[j].startswith("{"):
                            if L[j].rstrip().endswith(";"):
                                j = -1
                                break
                            j += 1
                        if j >= 0 and j < len(L) and L[j].startswith("{"):
                            kind = "func"
                            brace = j
                if kind:
                    name = m.group(1)
                    k = i + 1
                    if kind == "func" and L[brace].count("{") == L[brace].count("}"):
                        k = brace            # a one-line body: `{ ... }`
                    else:
                        while k < len(L) and not L[k].startswith("}"):
                            k += 1
                    defs.setdefault(name, (rel, i + 1, k + 1, kind))
                    texts.setdefault(name, [(n + 1, L[n]) for n in range(i, k + 1)])
                    i = k + 1
                    continue
                i += 1

# function-like MACROS are definitions too: a table walk is spelled
# DFA_SELECT(...), which expands to dfa_select(); without the macro edge the
# walk would be invisible to the graph.
for d in SRC:
    for dp, _, fs in os.walk(os.path.join(root, d)):
        for f in sorted(fs):
            if not f.endswith((".c", ".h")):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, root)
            L = open(path, encoding="utf-8", errors="replace").read().split("\n")
            for i, l in enumerate(L):
                m = re.match(r'^#define\s+([A-Za-z_]\w*)\(', l)
                if not m:
                    continue
                k = i
                while L[k].rstrip().endswith("\\") and k + 1 < len(L):
                    k += 1
                defs.setdefault(m.group(1), (rel, i + 1, k + 1, "macro"))
                texts.setdefault(m.group(1), [(n + 1, L[n]) for n in range(i, k + 1)])
names = set(defs)
edges = collections.defaultdict(set)
for n, body in texts.items():
    for ln, l in body[1:]:
        code = re.sub(r'"(\\.|[^"\\])*"', '""', l)   # strings out
        code = re.sub(r'/\*.*?\*/|//.*$', '', code)
        if code.lstrip().startswith(("*", "/*")):
            continue
        for t in IDENT.findall(code):
            if t in names and t != n:
                edges[n].add(t)


def reach(roots):
    seen, st = set(), list(roots)
    while st:
        x = st.pop()
        if x in seen or x not in names:
            continue
        seen.add(x)
        st.extend(edges[x])
    return seen


facts = [m.group(1).lower() for m in re.finditer(
    r'^PF_FACT\(\s*([A-Z_]+)', open(os.path.join(root, "src/facts/facts.def")).read(), re.M)]
SEEDS = {f"pcrec_fact_{f}" for f in facts if f not in ("kinds", "nullable")}
SEEDS.add("pcrec_artifact_has_dfa_scan")
# The MACHINE landmarks (the row contract's `landmark` column, §1.1: s0
# escapes, seed liveness, interior deadness, the scanned set's density) have
# no facts.def row; their producers are the one hand input to this census and
# are named here so a reviewer can contest them.
SEEDS |= {"unanch_start", "dfa_interior_dead", "cand_from_live_seeds",
          "pcrec_dfa_cand_ppm"}
# ... and the VM program properties rows read as FIELDS (no function to call).
SEED_FIELDS = {"root_minw", "mrl_win", "nclamp", "prefilter_collapsed"}
EMIT_ROOTS = ["pcrec_emit_dfa", "pcrec_emit_vm"]
BODY_ROOTS = ["emit_unanchored", "emit_attempt", "vm_emit_search_body"]
STAMP_ROOTS = ["pcrec_emit_dfa_scan_stamps", "vm_emit_stamps"]
for n, body in texts.items():
    if any(re.search(r'(->|\.)' + f + r'\b', l) for _, l in body for f in SEED_FIELDS):
        edges[n].add("@field")

R_body = reach(BODY_ROOTS)
R_stamp = reach(STAMP_ROOTS)
R = reach(EMIT_ROOTS)
# FAMILY: members of R from which a SEED is reachable (and the seeds' owners
# are excluded: the facts layer is core, its derivations are not start rows)
reaches_seed = {}


def rs(x, stack=()):
    if x in reaches_seed:
        return reaches_seed[x]
    if x in SEEDS or x == "@field":
        reaches_seed[x] = True
        return True
    if x in stack:
        return False
    v = any(rs(y, stack + (x,)) for y in edges[x])
    reaches_seed[x] = v
    return v


FAMILY = {x for x in R if x not in SEEDS and rs(x)
          and not defs[x][0].startswith("src/facts/")}
# a FAMILY table's rows are FAMILY: every predicate and hook a start table
# stores is a member even where it reads only the selection struct.
grew = True
while grew:
    grew = False
    for t in [x for x in FAMILY if defs[x][3] == "table"]:
        for y in edges[t]:
            if y not in FAMILY and y in names and defs[y][3] == "func":
                FAMILY.add(y)
                grew = True
COND = re.compile(r'^\s*(if|else if|while|return|for)\b|\?|&&|\|\|')
print("# call_graph.py: roots", ",".join(BODY_ROOTS), "| stamps", ",".join(STAMP_ROOTS))
print(f"# definitions {len(defs)}; reachable from bodies {len(R_body)}, from stamp writers {len(R_stamp)}; "
      f"seeds {len(SEEDS)}; family {len(FAMILY)}")
print("kind\tname\tsite\tdetail")
for x in sorted(defs, key=lambda n: (defs[n][0], defs[n][1])):
    f, a, b, k = defs[x]
    print(f"def-{k}\t{x}\t{f}:{a}-{b}\t")
for s in sorted(SEEDS):
    print(f"seed\t{s}\t{defs.get(s, ('?', 0))[0]}:{defs.get(s, ('?', 0))[1]}\t")
for x in sorted(FAMILY, key=lambda n: (defs[n][0], defs[n][1])):
    f, a, b, k = defs[x]
    reads = sorted((edges[x] & (SEEDS | FAMILY)))
    who = "+".join(w for w, r in (("body", R_body), ("stamp", R_stamp)) if x in r) or "plan"
    if "@field" in edges[x]:
        reads = reads + ["@field"]
    print(f"family-{k}\t{x}\t{f}:{a}\t{who}; names {','.join(reads)}")
nsite = 0
CALLS = SEEDS | FAMILY
for x in sorted(FAMILY, key=lambda n: (defs[n][0], defs[n][1])):
    f = defs[x][0]
    body = []
    for ln, l in texts[x][1:]:
        code = re.sub(r'"(\\.|[^"\\])*"', '""', l)
        code = re.sub(r'/\*.*?\*/|//.*$', '', code)
        if not code.lstrip().startswith(("*", "/*")):
            body.append((ln, code))
    # locals bound from a seed/family call (or a seed field): a condition on
    # such a local is a decision on the landmark through one indirection.
    bound = set()
    for _, code in body:
        for m in re.finditer(r'\b([A-Za-z_]\w*)\s*=\s*([^;=][^;]*)', code):
            rhs = set(IDENT.findall(m.group(2)))
            if rhs & CALLS or rhs & SEED_FIELDS:
                bound.add(m.group(1))
    for ln, code in body:
        if not COND.search(code):
            continue
        ids = set(IDENT.findall(code))
        hit = sorted(ids & (CALLS | SEED_FIELDS))
        via = sorted(ids & bound - set(hit))
        if hit or via:
            nsite += 1
            tag = ",".join(hit) + ((" via " + ",".join(via)) if via else "")
            print(f"site\t{x}\t{f}:{ln}\t{tag} | {code.strip()[:100]}")
print(f"# sites {nsite}", file=sys.stderr)
