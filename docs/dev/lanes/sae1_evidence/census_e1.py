#!/usr/bin/env python3
"""span_arms unit E1's CENSUS (docs/design/span_arms.md §8 row E1, §11 point 2):
the population's observed movers against an INDEPENDENT MODEL of T2 row 1,
compared two-sided.

THE MODEL reads no compiler code. T2 row 1 says a repeat whose body consumes
nothing (its widest match is 0 bytes) is CAT's unit for the necessary run, so
the run of a pattern P under E1 is the run TODAY's compiler gives for P with
every such repeat DELETED from the text (the spelling; a deleted item matches
the empty string, which is what the unit is). The model's own part is the
text scanner below: which quantified items are width 0, judged from PCRE
syntax alone (anchors, `\\b`-class assertions, lookarounds, empty groups,
option settings, comments, `{0}` repeats, and groups made only of those).
Anything it does not know is CONSUMING (the model then predicts no move);
a candidate inside a pattern it cannot spell faithfully (a capture group
among the deleted items, or `(?x)`) is ABSTAINED and listed.

THE OBSERVATION: the facts listing (`--emit-facts=byte,utf8`) of the
reference compiler (the branch point) and the working one, row by row.

A pattern is a PREDICTED mover when its spelling's reference run differs
from the original's reference run (either encoding); an OBSERVED mover when
any facts row differs between the two compilers. The two-sided compare lists
predicted-not-observed and observed-not-predicted, and for every mover checks
the value: the working run of P equals the reference run of P's spelling.

usage: census_e1.py REF_PCREC WORK_PCREC TREE BENCH_DIR OUT_DIR [--jobs N]
"""
import concurrent.futures as cf
import os
import re
import subprocess
import sys

TIMEOUT = 60


# ---------------------------------------------------------------- population

def decode_escape(s):
    # --list-source's escape vocabulary: \t \n \r \\ \xNN
    out = bytearray(); b = s.encode("utf-8", "surrogateescape"); i = 0
    while i < len(b):
        c = b[i]
        if c == 0x5C and i + 1 < len(b):
            n = b[i + 1]
            m = {ord('t'): 9, ord('n'): 10, ord('r'): 13, 0x5C: 0x5C}
            if n in m:
                out.append(m[n]); i += 2; continue
            if n == ord('x') and i + 3 < len(b):
                try:
                    out.append(int(bytes(b[i + 2:i + 4]), 16)); i += 4; continue
                except ValueError:
                    pass
        out.append(c); i += 1
    return bytes(out)


def corpus(pcrec, tree):
    pats = []
    for d, _, fs in os.walk(os.path.join(tree, "tests")):
        for f in sorted(fs):
            if not f.endswith(".rxt"):
                continue
            p = os.path.join(d, f)
            r = subprocess.run([pcrec, "--list-source", p], capture_output=True, timeout=TIMEOUT)
            if r.returncode != 0:
                continue
            for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
                if line.startswith("#") or not line.strip():
                    continue
                x = line.split("\t")
                if len(x) >= 5 and x[0] in ("pattern", "pattern-esc"):
                    pats.append(("corpus:" + os.path.relpath(p, tree), decode_escape(x[4])))
    return pats


def bench(bdir):
    pats = []
    for d, _, fs in os.walk(bdir):
        if os.path.basename(d) != "patterns":
            continue
        for f in sorted(fs):
            if f.endswith(".rx"):
                with open(os.path.join(d, f), "rb") as h:
                    t = h.read()
                if t.endswith(b"\n"):
                    t = t[:-1]
                pats.append(("bench:" + os.path.relpath(os.path.join(d, f), bdir), t))
    return pats


# ---------------------------------------------------------------- the model

class Abstain(Exception):
    pass


ZERO_ESC = set(b"bBAzZGK")          # zero-width escapes
QUANT = re.compile(rb"\*|\+|\?|\{(\d*)(,(\d*))?\}")


def parse_quant(p, i):
    """A quantifier at p[i:] -> (end, rmin, rmax or None) or None."""
    if i >= len(p):
        return None
    c = p[i:i + 1]
    if c in (b"*", b"+", b"?"):
        e = i + 1
        rmin, rmax = {b"*": (0, None), b"+": (1, None), b"?": (0, 1)}[c]
    elif c == b"{":
        m = re.match(rb"\{(\d*)(?:(,)(\d*))?\}", p[i:])
        if not m or (m.group(1) == b"" and not m.group(2)) or (m.group(1) == b"" and m.group(3) == b""):
            return None
        rmin = int(m.group(1) or b"0")
        rmax = rmin if not m.group(2) else (int(m.group(3)) if m.group(3) else None)
        e = i + m.end()
    else:
        return None
    if e < len(p) and p[e:e + 1] in (b"+", b"?"):
        e += 1
    return e, rmin, rmax


def skip_class(p, i):
    """p[i] == '[': the index after the class."""
    j = i + 1
    if j < len(p) and p[j:j + 1] == b"^":
        j += 1
    if j < len(p) and p[j:j + 1] == b"]":
        j += 1
    while j < len(p):
        c = p[j:j + 1]
        if c == b"\\":
            j += 2; continue
        if c == b"[" and p[j:j + 2] in (b"[:", b"[=", b"[."):
            k = p.find(p[j + 1:j + 2] + b"]", j + 2)
            if k < 0:
                raise Abstain("posix class")
            j = k + 2; continue
        if c == b"]":
            return j + 1
        j += 1
    raise Abstain("unterminated class")


def group_end(p, i):
    """p[i] == '(': index after the matching ')'."""
    depth = 0; j = i
    while j < len(p):
        c = p[j:j + 1]
        if c == b"\\":
            if p[j + 1:j + 2] == b"Q":
                k = p.find(b"\\E", j + 2)
                j = len(p) if k < 0 else k + 2; continue
            j += 2; continue
        if c == b"[":
            j = skip_class(p, j); continue
        if c == b"(":
            if p[j:j + 3] == b"(?#":
                k = p.find(b")", j)
                if k < 0:
                    raise Abstain("comment")
                j = k + 1; continue
            depth += 1
        elif c == b")":
            depth -= 1
            if depth == 0:
                return j + 1
        j += 1
    raise Abstain("unbalanced")


def seq_items(p, a, b):
    """Split p[a:b] (no top-level '|') into items: (start, atom_end, end,
    kind, rmin, rmax). kind: 'zero', 'cons', or ('group', inner_a, inner_b, capture)."""
    items = []; i = a
    while i < b:
        c = p[i:i + 1]; s = i
        kind = "cons"
        if c == b"\\":
            n = p[i + 1:i + 2]
            if n == b"Q":
                k = p.find(b"\\E", i + 2)
                k = b if k < 0 or k > b else k
                kind = "zero" if k == i + 2 else "cons"
                i = k + 2 if k < b else b
                items.append((s, i, i, "quote" if kind == "cons" else "zero", 1, 1)); continue
            if n and n[0] in ZERO_ESC:
                kind = "zero"
            elif n in (b"x", b"o", b"N", b"p", b"P", b"g", b"k", b"c") and p[i + 2:i + 3] in (b"{", b"<", b"'"):
                close = {b"{": b"}", b"<": b">", b"'": b"'"}[p[i + 2:i + 3]]
                k = p.find(close, i + 3)
                if k < 0:
                    raise Abstain("escape")
                i = k + 1
                q = parse_quant(p, i)
                e = q[0] if q else i
                items.append((s, i, e, kind, *(q[1:] if q else (1, 1)))); i = e; continue
            elif n == b"x":
                i += 2
                while i < b and i < s + 4 and p[i:i + 1] in b"0123456789abcdefABCDEF":
                    i += 1
                q = parse_quant(p, i); e = q[0] if q else i
                items.append((s, i, e, kind, *(q[1:] if q else (1, 1)))); i = e; continue
            elif n == b"c":
                i += 3
                q = parse_quant(p, i); e = q[0] if q else i
                items.append((s, i, e, kind, *(q[1:] if q else (1, 1)))); i = e; continue
            i += 2
        elif c in (b"^", b"$"):
            kind = "zero"; i += 1
        elif c == b"[":
            i = skip_class(p, i)
        elif c == b"(":
            e = group_end(p, i)
            h = p[i:i + 3]
            if p[i:i + 2] == b"(*":
                raise Abstain("verb or (*...) group")
            if h == b"(?#":
                items.append((s, e, e, "zero", 1, 1)); i = e; continue
            if h in (b"(?=", b"(?!") or p[i:i + 4] in (b"(?<=", b"(?<!"):
                kind = "zero"
            elif h == b"(?:" or h == b"(?>" or h == b"(?|":
                kind = ("group", i + 3, e - 1, False)
            elif h in (b"(?<", b"(?P", b"(?'"):
                m = re.match(rb"\(\?(?:P?<|')[A-Za-z_]\w*[>']", p[i:])
                if not m:
                    raise Abstain("group head")
                kind = ("group", i + m.end(), e - 1, True)
            elif h[:2] == b"(?":
                m = re.match(rb"\(\?[a-zA-Z^-]*(\)|:)", p[i:])
                if not m:
                    raise Abstain("group head " + h.decode("latin-1"))
                if m.group(1) == b")":
                    if b"x" in m.group(0):
                        raise Abstain("(?x)")
                    items.append((s, i + m.end(), i + m.end(), "zero", 1, 1)); i = i + m.end(); continue
                if b"x" in m.group(0):
                    raise Abstain("(?x:)")
                kind = ("group", i + m.end(), e - 1, False)
            else:
                kind = ("group", i + 1, e - 1, True)
            i = e
        else:
            i += 1
        q = parse_quant(p, i)
        e = q[0] if q else i
        items.append((s, i, e, kind, *(q[1:] if q else (1, 1))))
        i = e
    return items


def alts(p, a, b):
    out = []; i = a; s = a
    while i < b:
        c = p[i:i + 1]
        if c == b"\\":
            if p[i + 1:i + 2] == b"Q":
                k = p.find(b"\\E", i + 2); i = b if k < 0 else k + 2; continue
            i += 2; continue
        if c == b"[":
            i = skip_class(p, i); continue
        if c == b"(":
            i = group_end(p, i); continue
        if c == b"|":
            out.append((s, i)); s = i + 1
        i += 1
    out.append((s, b))
    return out


def zero_width(p, a, b):
    """Is every path through p[a:b] zero bytes wide?"""
    for sa, sb in alts(p, a, b):
        for (s, ae, e, kind, rmin, rmax) in seq_items(p, sa, sb):
            if rmax == 0:
                continue
            if kind == "zero":
                continue
            if isinstance(kind, tuple) and zero_width(p, kind[1], kind[2]):
                continue
            return False
    return True


def has_capture(p, a, b):
    for sa, sb in alts(p, a, b):
        for (s, ae, e, kind, rmin, rmax) in seq_items(p, sa, sb):
            if isinstance(kind, tuple) and (kind[3] or has_capture(p, kind[1], kind[2])):
                return True
    return False


def candidates(p, a=0, b=None):
    """The QUANTIFIED width-0 items (T2 row 1's repeats) as (start, end)."""
    b = len(p) if b is None else b
    out = []
    for sa, sb in alts(p, a, b):
        for (s, ae, e, kind, rmin, rmax) in seq_items(p, sa, sb):
            quantified = e > ae
            if isinstance(kind, tuple):
                body_zero = zero_width(p, kind[1], kind[2])
                if quantified and body_zero:
                    out.append((s, e, kind[3] or has_capture(p, kind[1], kind[2])))
                    continue
                out += candidates(p, kind[1], kind[2])
            elif quantified and kind == "zero":
                out.append((s, e, False))
    return out


def spell(p):
    """(spelled pattern, n candidates) or raise Abstain."""
    if b"(?x" in p or b"(?xx" in p:
        raise Abstain("(?x)")
    c = candidates(p)
    if any(cap for _, _, cap in c):
        raise Abstain("a capture among the deleted items (group numbers would move)")
    q = p
    for s, e, _ in sorted(c, reverse=True):
        q = q[:s] + q[e:]
    return q, len(c)


# ---------------------------------------------------------------- observation

def facts(pcrec, pat):
    try:
        r = subprocess.run([pcrec, "-p", "rx", "--features", "all", "--emit-facts=byte,utf8",
                            "--pattern", pat], capture_output=True, timeout=TIMEOUT)
    except subprocess.TimeoutExpired:
        return None
    if r.returncode != 0:
        return None
    rows = {}
    sec = None
    for line in r.stdout.decode("utf-8", "surrogateescape").splitlines():
        if line.startswith("#section "):
            sec = line.split()[1]; continue
        if line.startswith("#") or sec != "facts":
            continue
        x = line.split("\t")
        rows[(x[0], x[1])] = x
    return rows


def run_of(rows):
    if rows is None:
        return None
    return tuple(rows.get((e, "req_whole_run"), [None] * 7)[6] for e in ("byte", "utf8"))


def one(args):
    ref, work, src, pat = args
    rec = {"src": src, "pat": pat}
    r0 = facts(ref, pat); r1 = facts(work, pat)
    rec["compiled"] = r0 is not None and r1 is not None
    if not rec["compiled"]:
        return rec
    rec["moved"] = sorted({k[1] for k in set(r0) | set(r1) if r0.get(k) != r1.get(k)})
    try:
        q, n = spell(pat)
        rec["ncand"] = n
        if n:
            rs = facts(ref, q)
            rec["spelled_run"] = run_of(rs)
            rec["predicted"] = rs is not None and run_of(rs) != run_of(r0)
        else:
            rec["predicted"] = False
    except Abstain as e:
        rec["abstain"] = str(e)
        rec["predicted"] = None
    rec["ref_run"] = run_of(r0); rec["work_run"] = run_of(r1)
    return rec


def main():
    a = sys.argv[1:]
    jobs = 8
    if "--jobs" in a:
        k = a.index("--jobs"); jobs = int(a[k + 1]); del a[k:k + 2]
    ref, work, tree, bdir, out = a
    os.makedirs(out, exist_ok=True)
    pop = corpus(work, tree) + bench(bdir)
    # distinct pattern texts (the facts of a text do not depend on its file)
    seen = {}
    for src, pat in pop:
        seen.setdefault(pat, src)
    work_items = [(ref, work, src, pat) for pat, src in seen.items()]
    recs = []
    with cf.ThreadPoolExecutor(jobs) as ex:
        for r in ex.map(one, work_items):
            recs.append(r)
    comp = [r for r in recs if r["compiled"]]
    obs = {r["pat"] for r in comp if r["moved"]}
    pred = {r["pat"] for r in comp if r.get("predicted")}
    absn = [r for r in comp if r.get("abstain") and r["moved"]]
    by = {r["pat"]: r for r in comp}
    def esc(b):
        return b.decode("latin-1").encode("unicode_escape").decode()
    with open(os.path.join(out, "census.tsv"), "w") as h:
        h.write("#src\tpattern\tmoved_facts\tpredicted\tncand\tref_run\twork_run\tspelled_run\tabstain\n")
        for r in sorted(comp, key=lambda r: r["src"]):
            if not (r["moved"] or r.get("predicted") or r.get("ncand") or r.get("abstain")):
                continue
            h.write("\t".join([r["src"], esc(r["pat"]), ",".join(r["moved"]), str(r.get("predicted")),
                               str(r.get("ncand", "")), str(r["ref_run"]), str(r["work_run"]),
                               str(r.get("spelled_run", "")), r.get("abstain", "")]) + "\n")
    valbad = [p for p in obs & pred if by[p]["work_run"] != by[p]["spelled_run"]]
    lines = [
        "population: %d rows (%d corpus, %d bench), %d distinct texts, %d compiled on both sides"
        % (len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")),
           sum(1 for s, _ in pop if s.startswith("bench:")), len(seen), len(comp)),
        "candidates (texts with a width-0 quantified item): %d; abstained: %d (of them movers: %d)"
        % (sum(1 for r in comp if r.get("ncand")), sum(1 for r in comp if r.get("abstain")), len(absn)),
        "observed movers: %d (corpus %d, bench %d)" % (len(obs),
            sum(1 for p in obs if by[p]["src"].startswith("corpus:")),
            sum(1 for p in obs if by[p]["src"].startswith("bench:"))),
        "predicted movers: %d" % len(pred),
        "predicted and observed: %d; value mismatches (work run != reference run of the spelling): %d"
        % (len(obs & pred), len(valbad)),
        "observed, not predicted: %d" % len(obs - pred),
        "predicted, not observed: %d" % len(pred - obs),
        "facts that moved (union): %s" % ",".join(sorted({f for p in obs for f in by[p]["moved"]})),
    ]
    for p in sorted(obs - pred):
        lines.append("  OBS-NOT-PRED %s %s moved=%s abstain=%s" % (by[p]["src"], esc(p), ",".join(by[p]["moved"]), by[p].get("abstain", "")))
    for p in sorted(pred - obs):
        lines.append("  PRED-NOT-OBS %s %s" % (by[p]["src"], esc(p)))
    for p in sorted(valbad):
        lines.append("  VALUE %s %s work=%s spelled=%s" % (by[p]["src"], esc(p), by[p]["work_run"], by[p]["spelled_run"]))
    lines.append("== census COMPLETE: %d movers, %d two-sided differences" % (len(obs), len((obs - pred) | (pred - obs)) + len(valbad)))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
