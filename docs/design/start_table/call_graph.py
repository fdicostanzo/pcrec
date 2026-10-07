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
# [r2.1 C-N1] a top-level DATA definition: an array of any size (`[]`,
# `[N]`, `[A][B]`), a struct initializer (`const PcrecEnc x = {`), a string
# constant (`static const char x[] =` then string lines) or a scalar. Revision
# 2 matched `NAME[] = {` only, which left sized tables (tune.c's
# TUNE_TABLE[5], clskit.c's DENY_FLAG[CLSD_NDENY]) and every string-emitter
# constant (enc_utf8.c) without an owner.
DATA_RX = re.compile(r'^(?:static\s+)?(?:const\s+)?((?:[A-Za-z_]\w*\s+(?:const\s+)?)+?)\**\s*'
                     r'(?:const\s+)?\**\s*([A-Za-z_]\w*)\s*((?:\[[^\]]*\]\s*)*)=\s*(.*)$')
# [r2.1 C-N1] a TYPE definition: `typedef struct X {`, `struct X {`,
# `typedef enum {`, `enum {` (one-line or multi-line). A row struct
# (`DfaCand`, the common leading member of every start table's row) is
# where a row's deny/applies/name fields are declared, and revision 2 had no
# owner for an anchor there (S282).
TYPE_RX = re.compile(r'^(typedef\s+)?(struct|union|enum)\b\s*([A-Za-z_]\w*)?\s*\{')
IDENT = re.compile(r'\b[A-Za-z_]\w*\b')
QUAL = {"static", "const", "inline", "extern", "volatile", "unsigned", "signed",
        "struct", "union", "enum"}

defs = {}   # name -> (file, start_line, end_line, kind)
texts = {}  # name -> body text (list of (lineno, line))
elem = {}   # table name -> its element type name (for the row-type closure)


def code_of(l):
    l = re.sub(r'"(\\.|[^"\\])*"', '""', l)
    return re.sub(r'/\*.*?\*/|//.*$', '', l)


def add(name, rel, a, b, kind, L):
    defs.setdefault(name, (rel, a + 1, b + 1, kind))
    texts.setdefault(name, [(n + 1, L[n]) for n in range(a, b + 1)])


def to_closing_brace(L, i):
    """Index of the line that closes a top-level `{` opened on line i."""
    c = code_of(L[i])
    if c.count("{") and c.count("{") == c.count("}"):
        return i
    k = i + 1
    while k < len(L) and not L[k].startswith("}"):
        k += 1
    return min(k, len(L) - 1)


def to_semicolon(L, i):
    k = i
    while k < len(L) and not code_of(L[k]).rstrip().endswith(";"):
        k += 1
    return min(k, len(L) - 1)


for d in SRC:
    for dp, _, fs in os.walk(os.path.join(root, d)):
        for f in sorted(fs):
            # [r2.1 C-N1] headers too: a `static inline` in internal.h is a
            # definition (S236's anchor sits in one); revision 2 parsed
            # headers for macros only.
            if not f.endswith((".c", ".h")):
                continue
            path = os.path.join(dp, f)
            rel = os.path.relpath(path, root)
            L = open(path, encoding="utf-8", errors="replace").read().split("\n")
            i = 0
            while i < len(L):
                l = L[i]
                # [START-TABLE] C2: the trace build's own code (`#ifdef
                # PCREC_CAND_TRACE` up to its `#else`/`#endif`: the both-walks
                # oracle, its hooks' trace spellings, the quiet depth) is not
                # in the default build, decides nothing and is no definition
                # of the census; the `#else` branch is parsed as usual.
                if re.match(r'^#\s*ifdef\s+PCREC_CAND_TRACE\b', l):
                    depth, i = 0, i + 1
                    while i < len(L):
                        if re.match(r'^#\s*if', L[i]):
                            depth += 1
                        elif re.match(r'^#\s*endif\b', L[i]):
                            if depth == 0:
                                break
                            depth -= 1
                        elif re.match(r'^#\s*else\b', L[i]) and depth == 0:
                            break
                        i += 1
                    i += 1
                    continue
                m = re.match(r'^#\s*define\s+([A-Za-z_]\w*)(\()?', l)
                if m:
                    # function-like MACROS are definitions (a table walk is
                    # spelled DFA_SELECT(...)); [r2.1] object-like ones too
                    # (S209's anchor is `#define VM_MAX_BODY_CAPS ...`).
                    k = i
                    while L[k].rstrip().endswith("\\") and k + 1 < len(L):
                        k += 1
                    add(m.group(1), rel, i, k, "macro" if m.group(2) else "const", L)
                    i = k + 1
                    continue
                if not l or l.startswith((" ", "\t", "#", "/", "*", "}")):
                    i += 1
                    continue
                m = TYPE_RX.match(l)
                if m:
                    k = to_closing_brace(L, i)
                    tm = re.match(r'^\}?\s*.*?\}\s*([A-Za-z_]\w*)\s*;', L[k]) if m.group(1) else None
                    name = (tm.group(1) if tm else None) or m.group(3) or f"{m.group(2)}@{rel}:{i + 1}"
                    add(name, rel, i, k, "type", L)
                    i = k + 1
                    continue
                m = DEF_RX.match(l)
                if m:
                    # a function: the opening brace at column 0 within 8 lines
                    j = i
                    while j < len(L) and j < i + 8 and not L[j].startswith("{"):
                        if L[j].rstrip().endswith(";"):
                            j = -1
                            break
                        j += 1
                    if j >= 0 and j < len(L) and L[j].startswith("{"):
                        k = j if code_of(L[j]).count("{") == code_of(L[j]).count("}") \
                            else to_closing_brace(L, j)
                        add(m.group(1), rel, i, k, "func", L)
                        i = k + 1
                        continue
                m = DATA_RX.match(l)
                if m and not l.startswith(("typedef", "return", "else")):
                    rest = m.group(4).strip()
                    k = to_closing_brace(L, i) if rest.startswith("{") else to_semicolon(L, i)
                    # revision 2 called an array a "table"; a struct
                    # initializer or a string constant is "data"
                    kind = "table" if m.group(3) and rest.startswith("{") else "data"
                    add(m.group(2), rel, i, k, kind, L)
                    tw = [t for t in m.group(1).split() if t not in QUAL]
                    if tw:
                        elem[m.group(2)] = tw[-1]
                    i = k + 1
                    continue
                i += 1

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
    if defs[n][3] == "type":
        continue
    if any(re.search(r'(->|\.)' + f + r'\b', l) for _, l in body for f in SEED_FIELDS):
        edges[n].add("@field")
# [r2.1] a TYPE is not a call: naming `Ctx` reaches nothing. Types enter the
# family only through the row-type closure below, never through reach().
for n in list(edges):
    edges[n] = {y for y in edges[n] if y not in defs or defs[y][3] != "type"}

R_body = reach(BODY_ROOTS)
R_stamp = reach(STAMP_ROOTS)
# [START-TABLE] C2: the one start table's walk is a root too. No emitter
# reaches `cand_select` until C3 switches the first reader (implement, then
# replace), yet `cand_rows[]` and every predicate it stores are start-family
# by construction, so they join the family the commit that builds them.
TABLE_ROOTS = ["cand_select"]
R = reach(EMIT_ROOTS + TABLE_ROOTS)
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
    for t in [x for x in FAMILY if defs[x][3] in ("table", "data")]:
        for y in edges[t]:
            if y not in FAMILY and y in names and defs[y][3] == "func":
                FAMILY.add(y)
                grew = True
# [r2.1 C-N1] THE ROW TYPES: the element type of every FAMILY table, and
# every type such a type EMBEDS BY VALUE (a member line `T name;` with no `*`),
# transitively. This is how `DfaCand` (the common leading member of every
# start table's row, where `deny`/`applies`/`name` are declared) is a member:
# DfaPf embeds it. A type named only through a pointer (`const DfaSel *`) is
# not pulled in, so `Ctx`/`Dfa`/`Job` stay out.
ROWTYPES = set()
st = [elem[t] for t in FAMILY if t in elem]
while st:
    ty = st.pop()
    if ty in ROWTYPES or ty not in defs or defs[ty][3] != "type" \
            or not defs[ty][0].startswith("src/"):
        continue
    ROWTYPES.add(ty)
    for _, l in texts[ty][1:]:
        mm = re.match(r'^\s*(?:const\s+)?([A-Za-z_]\w*)\s+[A-Za-z_]\w*\s*(?:\[[^\]]*\])?\s*;', code_of(l))
        if mm and "*" not in code_of(l):
            st.append(mm.group(1))
FAMILY |= ROWTYPES
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
    trace_depth = 0
    for ln, l in texts[x][1:]:
        code = re.sub(r'"(\\.|[^"\\])*"', '""', l)
        code = re.sub(r'/\*.*?\*/|//.*$', '', code)
        # [START-TABLE] C1: a selection-trace record (`PCREC_CAND_TRACE_REC*`,
        # possibly continued over lines) PRINTS a decision made elsewhere and
        # decides nothing, so its ternaries are not sites. C2's both-walks
        # oracle hooks (`CAND_ORACLE_*`, `VM_CAND_*`) CHECK one and decide
        # nothing either.
        if trace_depth or re.search(r'\b(PCREC_CAND_TRACE_REC|CAND_ORACLE_|VM_CAND_)', code):
            trace_depth += code.count("(") - code.count(")")
            continue
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
