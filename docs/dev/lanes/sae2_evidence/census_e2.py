#!/usr/bin/env python3
"""span_arms unit E2's CENSUS (docs/design/span_arms.md §8 row E2, §4.1, §11
point 2): the population's observed movers against an INDEPENDENT MODEL of
T3 rows E-1, E-4 and E-5 (the plain unit), compared two-sided, with the movers
counted per PRODUCER KIND (the two lookaround lowerings apart) and the
window statement's R-span movers counted beside the run movers (r1 F11).

THE MODEL reads no compiler code. T3 says a node that consumes nothing (the
empty string, an assertion, `\\G`, `\\K`, a lookaround of either lowering)
is CAT's width-0 unit. The reference compiler (unit E1, the branch point) already has that
unit for a REPEAT of a width-0 body at m = 0 (T2 row 1), spelled `(?:)?`.
So the walk facts of P under E2 are the reference compiler's walk facts of P's
SPELLING: every zero-width assertion item (with its quantifier) replaced by
`(?:)?`, and `(?:)?` inserted into every empty branch (an `A_EMPTY` node,
the reference's cut). The replacement, not a deletion, never creates an
empty group or branch and moves no capture number. The model's own part is the text
scanner (census_e1.py's, reused, plus the item classes below); a construct it
does not know is CONSUMING, so it predicts no move; a pattern it cannot spell
faithfully (`(?x)`, a callout, a verb, a conditional, a recursion or
subroutine call) is ABSTAINED and listed.

THE WALK FACTS compared (value column, byte and utf8): req_set,
req_set_maxoff, req_whole_run, req_pieces, req_run, req_run_maxoff, req_byte,
req_landmark_maxoff. The others (anchors, k-set, start set, ...) differ
between P and its spelling for reasons outside the walk.

OBSERVED mover: any facts row differs between the reference and the working
compiler (both encodings). PREDICTED mover: the spelling's walk facts differ
from P's (reference compiler). VALUE check, for every mover: the working
walk facts of P equal the reference walk facts of the spelling.

PER PRODUCER KIND: for each predicted mover, the spelling restricted to one
kind's items; the kind is a producer of the move where that alone moves the
walk facts (where no kind does alone, the mover is `joint:` all its kinds). Kinds: empty (an empty branch), wordb (\\b \\B), anchor (^ $ \\A \\Z
\\z), gstart (\\G), kreset (\\K), and the four lookaround forms, each split by its LOWERING:
`look-*:ctx` (lowered to `A_CTX`) or `look-*:look` (an `A_LOOK`), read from
the reference compiler's `kinds` fact on the item compiled ALONE (the
lookaround bit is set iff an `A_LOOK` survives lowering).

R SPAN: the window statement's run span (src/gen/emit_dfa.c `pf_window_of`),
traced by scratch builds of both revisions (mk_rtrace.sh); a mover whose set
of `RSPAN` lines differs (byte or utf8) is an R-span mover.

usage: census_e2.py REF_PCREC WORK_PCREC REF_RTRACE WORK_RTRACE TREE BENCH_DIR OUT_DIR [--jobs N]
"""
import concurrent.futures as cf
import importlib.util
import os
import re
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
spec = importlib.util.spec_from_file_location(
    "census_e1", os.path.join(HERE, "..", "sae1_evidence", "census_e1.py"))
E1 = importlib.util.module_from_spec(spec)
spec.loader.exec_module(E1)

TIMEOUT = 60
UNIT = b"(?:)?"
WALK = ("req_set", "req_set_maxoff", "req_whole_run", "req_pieces", "req_run",
        "req_run_maxoff", "req_byte", "req_landmark_maxoff")
Abstain = E1.Abstain


# ---------------------------------------------------------------- the model

def item_kind(p, s, ae):
    """The zero-width ASSERTION class of item text p[s:ae], or None."""
    t = p[s:ae]
    if t in (b"\\b", b"\\B"):
        return "wordb"
    if t in (b"^", b"$", b"\\A", b"\\Z", b"\\z"):
        return "anchor"
    if t == b"\\G":
        return "gstart"
    if t == b"\\K":
        return "kreset"
    for head, k in ((b"(?<=", "look-behind-pos"), (b"(?<!", "look-behind-neg"),
                    (b"(?=", "look-ahead-pos"), (b"(?!", "look-ahead-neg")):
        if t.startswith(head):
            return k
    return None


def items(p, a, b, out):
    """Every zero-width item of p[a:b] (at any group depth, never inside a
    lookaround, which is replaced whole) as (start, end, kind, text): the
    assertions, and each EMPTY branch (`()`, `(?:|x)`: an `A_EMPTY` node,
    T3 row E-1), whose edit inserts the unit at its position."""
    for sa, sb in E1.alts(p, a, b):
        if sa == sb:
            out.append((sa, sa, "empty", b""))
            continue
        for (s, ae, e, kind, rmin, rmax) in E1.seq_items(p, sa, sb):
            if kind == "zero":
                k = item_kind(p, s, ae)
                if k:
                    out.append((s, e, k, p[s:ae]))
            elif isinstance(kind, tuple):
                items(p, kind[1], kind[2], out)
    return out


def scan(p):
    if b"(?x" in p:
        raise Abstain("(?x)")
    for bad, why in ((b"(?C", "callout"), (b"(*", "verb or (*...)"), (b"(?(", "conditional"),
                     (b"(?R)", "recursion"), (b"(?&", "subroutine call"), (b"(?P>", "subroutine call")):
        if bad in p:
            raise Abstain(why)
    if re.search(rb"\(\?[+-]?\d", p):
        raise Abstain("subroutine call")
    return items(p, 0, len(p), [])


def spell(p, its, kinds=None):
    q = p
    for s, e, k, _ in sorted(its, reverse=True):
        if kinds is None or k in kinds:
            q = q[:s] + UNIT + q[e:]
    return q


# ---------------------------------------------------------------- observation

def facts(pcrec, pat):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--emit-facts=byte,utf8",
                            "--pattern", pat], capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    rows = {}; sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        rows[(x[0], x[1])] = x
    return rows


def walk_of(rows):
    if rows is None:
        return None
    return tuple(rows.get((e, f), [None] * 7)[6] for e in ("byte", "utf8") for f in WALK)


def rspan(pcrec, pat):
    out = set()
    for enc in ([], ["-e", "utf8"]):
        try:
            r = subprocess.run([pcrec, "-p", "rx", "--features", "all", *enc, "-o", "/dev/null",
                                "--pattern", pat], capture_output=True, timeout=TIMEOUT,
                               env=dict(os.environ, PCREC_RSPAN_TRACE="1"))
        except subprocess.TimeoutExpired:
            return None
        for l in r.stderr.decode("latin-1").splitlines():
            if l.startswith("RSPAN\t"):
                out.add(("utf8" if enc else "byte",) + tuple(l.split("\t")[1:]))
    return tuple(sorted(out))


LOWERING = {}


def lowering(ref, text):
    if text not in LOWERING:
        r = facts(ref, text)
        LOWERING[text] = "?" if r is None else (
            "look" if "lookaround" in r.get(("byte", "kinds"), [""] * 7)[6].split(",") else "ctx")
    return LOWERING[text]


def one(args):
    ref, work, rref, rwork, src, pat = args
    rec = {"src": src, "pat": pat}
    r0 = facts(ref, pat); r1 = facts(work, pat)
    rec["compiled"] = r0 is not None and r1 is not None
    if not rec["compiled"]:
        return rec
    rec["moved"] = sorted({k[1] for k in set(r0) | set(r1) if r0.get(k) != r1.get(k)})
    w0 = walk_of(r0)
    rec["ref_walk"] = w0; rec["work_walk"] = walk_of(r1)
    try:
        its = scan(pat)
        rec["nitems"] = len(its)
        rec["predicted"] = False
        if its:
            ws = walk_of(facts(ref, spell(pat, its)))
            rec["spelled_walk"] = ws
            rec["predicted"] = ws is not None and ws != w0
            if rec["predicted"]:
                prod = set()
                for k in sorted({k for _, _, k, _ in its}):
                    wk = walk_of(facts(ref, spell(pat, its, {k})))
                    if wk is not None and wk != w0:
                        if k.startswith("look-"):
                            low = {lowering(ref, t) for _, _, kk, t in its if kk == k}
                            for lw in sorted(low):
                                prod.add(k + ":" + lw)
                        else:
                            prod.add(k)
                # a move no single kind makes alone (`(?:^|\s)foo\b`'s pieces
                # need both cuts gone) is the kinds' JOINT move
                rec["producers"] = sorted(prod) or [
                    "joint:" + "+".join(sorted({k for _, _, k, _ in its}))]
    except Abstain as e:
        rec["abstain"] = str(e)
        rec["predicted"] = None
    if rec["moved"]:
        a, b = rspan(rref, pat), rspan(rwork, pat)
        rec["rspan_moved"] = a != b
        rec["rspan"] = (a, b)
    return rec


def esc(b):
    return b.decode("latin-1").encode("unicode_escape").decode()


def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    ref, work, rref, rwork, tree, bdir, out = a
    os.makedirs(out, exist_ok=True)
    pop = E1.corpus(work, tree) + E1.bench(bdir)
    seen = {}
    for src, pat in pop:
        seen.setdefault(pat, src)
    recs = []
    with cf.ThreadPoolExecutor(jobs) as ex:
        for r in ex.map(one, [(ref, work, rref, rwork, src, pat) for pat, src in seen.items()]):
            recs.append(r)
    comp = [r for r in recs if r["compiled"]]
    by = {r["pat"]: r for r in comp}
    obs = {r["pat"] for r in comp if r["moved"]}
    pred = {r["pat"] for r in comp if r.get("predicted")}
    absn = [r for r in comp if r.get("abstain") and r["moved"]]
    valbad = [p for p in obs & pred if by[p]["work_walk"] != by[p]["spelled_walk"]]
    rsp = {p for p in obs if by[p].get("rspan_moved")}
    bench_obs = sorted(p for p in obs if by[p]["src"].startswith("bench:"))
    kinds = {}
    for p in obs & pred:
        for k in by[p].get("producers", []):
            kinds.setdefault(k, set()).add(p)
    with open(os.path.join(out, "census.tsv"), "w") as h:
        h.write("#src\tpattern\tmoved_facts\tpredicted\tnitems\tproducers\trspan_moved\tref_run\twork_run\tabstain\n")
        for r in sorted(comp, key=lambda r: r["src"]):
            if not (r["moved"] or r.get("predicted") or r.get("nitems") or r.get("abstain")):
                continue
            run = lambda w: "-" if w is None else "%s|%s" % (w[2], w[2 + len(WALK)])
            h.write("\t".join([r["src"], esc(r["pat"]), ",".join(r["moved"]), str(r.get("predicted")),
                               str(r.get("nitems", "")), ",".join(r.get("producers", [])),
                               str(r.get("rspan_moved", "")), run(r["ref_walk"]), run(r["work_walk"]),
                               r.get("abstain", "")]) + "\n")
    lines = [
        "population: %d rows (%d corpus, %d bench), %d distinct texts, %d compiled on both sides"
        % (len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")),
           sum(1 for s, _ in pop if s.startswith("bench:")), len(seen), len(comp)),
        "texts with a zero-width item: %d; abstained: %d (of them movers: %d)"
        % (sum(1 for r in comp if r.get("nitems")), sum(1 for r in comp if r.get("abstain")), len(absn)),
        "observed movers: %d (corpus %d, bench %d)" % (len(obs), len(obs) - len(bench_obs), len(bench_obs)),
        "predicted movers: %d" % len(pred),
        "predicted and observed: %d; value mismatches (work walk facts != reference walk facts of the spelling): %d"
        % (len(obs & pred), len(valbad)),
        "observed, not predicted: %d" % len(obs - pred),
        "predicted, not observed: %d" % len(pred - obs),
        "R-span movers (the window statement's R span moved, byte or utf8): %d (bench %d)"
        % (len(rsp), sum(1 for p in rsp if by[p]["src"].startswith("bench:"))),
        "facts that moved (union): %s" % ",".join(sorted({f for p in obs for f in by[p]["moved"]})),
        "movers per producer kind (a mover may count under several):",
    ]
    for k in sorted(kinds):
        lines.append("  %-24s %d (bench %d)" % (k, len(kinds[k]), sum(1 for p in kinds[k] if by[p]["src"].startswith("bench:"))))
    for p in bench_obs:
        lines.append("  BENCH-MOVER %s %s producers=%s rspan=%s" % (by[p]["src"], esc(p), ",".join(by[p].get("producers", [])), by[p].get("rspan_moved")))
    for p in sorted(obs - pred):
        lines.append("  OBS-NOT-PRED %s %s moved=%s abstain=%s" % (by[p]["src"], esc(p), ",".join(by[p]["moved"]), by[p].get("abstain", "")))
    for p in sorted(pred - obs):
        lines.append("  PRED-NOT-OBS %s %s" % (by[p]["src"], esc(p)))
    for p in sorted(valbad):
        lines.append("  VALUE %s %s work=%s spelled=%s" % (by[p]["src"], esc(p), by[p]["work_walk"], by[p]["spelled_walk"]))
    lines.append("== census COMPLETE: %d movers, %d two-sided differences" % (len(obs), len((obs - pred) | (pred - obs)) + len(valbad)))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
