#!/usr/bin/env python3
"""tests/vm/trail_checkpoints.py -- [K134] every trail-writing cycle of a
VM artifact passes a trail checkpoint, and the stamped margin bounds the trail
writes between two checkpoints.

WHAT IT CHECKS, AND WHY. The VM compacts its trail only at `<PREFIX>_TRAIL_CHECK`
sites (src/gen/emit_vm.c `vm_emit_trail_compact`): on every backward `vm_goto`
that closes a span with a trail write, and on every return. The emitter's
argument is that every cycle of the program then passes one, so between two
checkpoints a run executes each `<PREFIX>_SET` site at most once, and the
floor function's `margin` (the site count) bounds the trail growth there. If an
emitter change adds a backward edge the rule does not see (a hand-written
conditional `goto`, a resume label before its push), compaction silently stops
reaching that loop: no answer changes, but the run gives up where it should
not. This check reads the EMITTED C, not the emitter, so it does not share the
emitter's own idea of which edges go back (learnings §3: a control must not
share a source with what it controls).

A checkpoint inside a conditional block guards only the jump after it.

THE GRAPH, per matcher function (`<p>_match_anchored`, and any other function
with a `_SET(`): one node per statement line. Edges: fallthrough to the next
line unless the line is an unconditional `goto`/`return`; every
`goto <p>_L<n>` on the line; a `_PUSH(` line to its resume label (an unwind
restores the depth that push saw, then continues there); a return
(`goto *...call_ret`) to every `_CALL(` return label. `goto <p>_fail` ends the
path (the unwind is the push edge). A `_TRAIL_CHECK();` line is a path
boundary: no edge leaves it. A `_SET(` is weight 1.

VERDICT per artifact: (1) no strongly connected component that contains a
`_SET(`; (2) the heaviest checkpoint-free path is at most the emitted margin;
(3) no `_SET(` inside a C `for`/`while` body, which the line graph cannot
see.

WHAT (2) CONTROLS, AND WHAT IT CANNOT (review 2026-10-29-r2 F8). The margin
the emitter writes is its count of `_SET` sites (`nset`), and once (1)
holds, a checkpoint-free path is simple and visits each `_SET(` line at most
once, so (2) cannot fail while (1) passes unless the margin is SMALLER than
the number of `_SET(` sites in the text. It is therefore the control
"`nset` equals the `_SET(` count of the emitted text" (a SET written by a
path that does not count it), not an independent bound on the stretch; the
bound is (1)'s argument. The margin is the whole program's site count, not
the heaviest checkpoint-free path this script computes (cscan 255 against
61), which is conservative: the floor sits lower than it needs to. Usage:
    trail_checkpoints.py FILE.c...        check emitted artifacts
    trail_checkpoints.py --corpus PCREC TREE [--limit N]
                                          compile every corpus pattern at
                                          --engine=vm --features all and check
The corpus mode prints the population: artifacts checked, artifacts with a
checkpoint, and the largest heaviest-path/margin pair; it fails on an empty
population (K35).
"""
import os
import re
import subprocess
import sys

sys.setrecursionlimit(100000)


def functions(text):
    """Yield (name, body lines) for every top-level function definition."""
    lines = text.split("\n")
    i = 0
    while i < len(lines):
        m = re.match(r"^static .*?\b(\w+)\(.*", lines[i])
        if m and not lines[i].rstrip().endswith(";"):
            name = m.group(1)
            j = i
            while j < len(lines) and lines[j] != "{":
                j += 1
            k = j + 1
            while k < len(lines) and lines[k] != "}":
                k += 1
            yield name, lines[j + 1:k]
            i = k + 1
        else:
            i += 1


def analyse(body, p):
    lab = {}
    for i, ln in enumerate(body):
        m = re.match(r"^%s_L(\d+):" % re.escape(p), ln)
        if m:
            lab[int(m.group(1))] = i
    rets = [int(x) for ln in body for x in re.findall(r"_CALL\(&&%s_L(\d+)" % re.escape(p), ln)]
    n = len(body)
    w = [ln.count("_SET(") for ln in body]
    # a whole-line checkpoint ends every path through it; one inside a
    # conditional block (`if (c) { X_TRAIL_CHECK(); goto L; }`) ends the
    # jump it guards and leaves the fallthrough
    chk = [re.match(r"^\s*\w+_TRAIL_CHECK\(\);\s*$", ln) is not None for ln in body]
    nchk = sum("_TRAIL_CHECK();" in ln for ln in body)
    succ = [[] for _ in range(n)]
    for i, ln in enumerate(body):
        if chk[i]:
            continue
        s = ln.strip()
        unguarded = ln.split("_TRAIL_CHECK();")[0]
        for x in re.findall(r"goto %s_L(\d+)" % re.escape(p), unguarded):
            succ[i].append(lab[int(x)])
        if "_PUSH(" in ln:
            for x in re.findall(r"&&%s_L(\d+)" % re.escape(p), ln):
                succ[i].append(lab[int(x)])
        if re.search(r"goto \*run->resume_stack\[\w+\]\.call_ret", ln):
            succ[i].extend(lab[r] for r in rets)
            continue
        if s.startswith("goto ") or s.startswith("return ") or s.startswith("return;"):
            continue
        if i + 1 < n:
            succ[i].append(i + 1)
    # Tarjan, iterative
    index = [None] * n
    low = [0] * n
    onst = [False] * n
    st = []
    comp = [None] * n
    ncomp = 0
    counter = 0
    for root in range(n):
        if index[root] is not None:
            continue
        work = [(root, 0)]
        while work:
            v, pi = work.pop()
            if pi == 0:
                index[v] = low[v] = counter
                counter += 1
                st.append(v)
                onst[v] = True
            recurse = False
            for k in range(pi, len(succ[v])):
                u = succ[v][k]
                if index[u] is None:
                    work.append((v, k + 1))
                    work.append((u, 0))
                    recurse = True
                    break
                elif onst[u]:
                    low[v] = min(low[v], index[u])
            if recurse:
                continue
            if low[v] == index[v]:
                while True:
                    u = st.pop()
                    onst[u] = False
                    comp[u] = ncomp
                    if u == v:
                        break
                ncomp += 1
            if work:
                parent = work[-1][0]
                low[parent] = min(low[parent], low[v])
    members = [[] for _ in range(ncomp)]
    for v in range(n):
        members[comp[v]].append(v)
    bad = []
    cw = [0] * ncomp
    for c, vs in enumerate(members):
        cw[c] = sum(w[v] for v in vs)
        cyc = len(vs) > 1 or vs[0] in succ[vs[0]]
        if cyc and cw[c] > 0:
            bad.append(min(vs))
    # heaviest path over the condensation (Tarjan numbers SCCs in reverse
    # topological order: successors first)
    csucc = [set() for _ in range(ncomp)]
    for v in range(n):
        for u in succ[v]:
            if comp[u] != comp[v]:
                csucc[comp[v]].add(comp[u])
    best = [0] * ncomp
    for c in range(ncomp):
        best[c] = cw[c] + max((best[d] for d in csucc[c]), default=0)
    heaviest = max(best, default=0)
    # (3) a SET inside a C loop body
    inloop = []
    depth_loop = []
    for i, ln in enumerate(body):
        s = ln.strip()
        if re.match(r"^(for|while)\b", s) and s.endswith("{"):
            depth_loop.append(ln.count("{") - ln.count("}"))
        elif depth_loop:
            depth_loop[-1] += ln.count("{") - ln.count("}")
            if "_SET(" in ln:
                inloop.append(i)
            if depth_loop[-1] <= 0:
                depth_loop.pop()
    return bad, heaviest, inloop, nchk


def check_text(text, label):
    m = re.search(r"static .*?size_t (\w+)_trail_gc_floor\(", text)
    p = m.group(1) if m else None
    margin = None
    mm = re.search(r"const size_t margin = (\d+);", text)
    if mm:
        margin = int(mm.group(1))
    errs = []
    worst = 0
    nchk = 0
    for name, body in functions(text):
        if not any("_SET(" in ln for ln in body):
            continue
        pp = p or name.rsplit("_match_anchored", 1)[0]
        bad, heaviest, inloop, c = analyse(body, pp)
        nchk += c
        worst = max(worst, heaviest)
        for i in bad:
            errs.append("%s: %s: a cycle writes the trail and passes no checkpoint (line %d of the body: %s)"
                        % (label, name, i + 1, body[i].strip()))
        for i in inloop:
            errs.append("%s: %s: a _SET( inside a C loop body (body line %d)" % (label, name, i + 1))
    if nchk and margin is None:
        errs.append("%s: checkpoints but no margin in the floor function" % label)
    if margin is not None and worst > margin:
        errs.append("%s: heaviest checkpoint-free path %d exceeds the margin %d: the margin "
                    "undercounts the artifact's _SET sites" % (label, worst, margin))
    return errs, worst, margin, nchk


def corpus(pcrec, tree, limit):
    pats = []
    for root, _, files in os.walk(os.path.join(tree, "tests")):
        for f in sorted(files):
            if not f.endswith(".rxt"):
                continue
            r = subprocess.run([pcrec, "--list-source", os.path.join(root, f)],
                               capture_output=True, timeout=60)
            for ln in r.stdout.split(b"\n"):
                fl = ln.split(b"\t")
                if len(fl) >= 5 and fl[0] in (b"pattern", b"pattern-esc"):
                    pats.append(fl[4])
    seen = set()
    uniq = [x for x in pats if not (x in seen or seen.add(x))]
    if limit:
        uniq = uniq[:limit]
    return uniq


def main(argv):
    errs = []
    if argv[:1] == ["--corpus"]:
        pcrec, tree = argv[1], argv[2]
        limit = int(argv[4]) if argv[3:4] == ["--limit"] else 0
        pats = corpus(pcrec, tree, limit)
        checked = with_chk = 0
        top = (0, 0, b"")
        for pat in pats:
            r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--engine=vm",
                                "--pattern-esc", "--pattern", "\"" + pat.decode("latin-1").replace('"', '\\"') + "\"", "-o", "-"],
                               capture_output=True, timeout=60)
            if r.returncode != 0:
                continue
            checked += 1
            e, worst, margin, nchk = check_text(r.stdout.decode("latin-1"), pat.decode("latin-1")[:60])
            errs += e
            if nchk:
                with_chk += 1
                if worst > top[0]:
                    top = (worst, margin, pat)
        print("trail_checkpoints: %d corpus patterns, %d VM artifacts checked, %d with a checkpoint; "
              "heaviest checkpoint-free path %d (margin %s) on %r"
              % (len(pats), checked, with_chk, top[0], top[1], top[2][:60]))
        if checked == 0 or with_chk == 0:
            errs.append("empty population (K35)")
    else:
        for f in argv:
            with open(f, encoding="latin-1") as fh:
                e, worst, margin, nchk = check_text(fh.read(), f)
            errs += e
            print("%s: %d checkpoints, heaviest checkpoint-free path %d, margin %s" % (f, nchk, worst, margin))
    for e in errs:
        print("FAIL: " + e)
    return 1 if errs else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
