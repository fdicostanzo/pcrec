#!/usr/bin/env python3
r"""span_arms unit R1's CENSUS (docs/design/span_arms.md §8 row R1, §3.4,
D191): the population's observed movers against an INDEPENDENT MODEL of T2
rows 2-3 (a repeat of a consuming body is its copies), compared two-sided.

THE MODEL reads no compiler code. It SPELLS every quantified item whose body
consumes (the scanner's width-0 test, census_e1.py's, says it is not width 0)
as copies, and asks TODAY's compiler (the branch point, unit E1's build) for
the spelling's run:
  - `X{m}` (m >= 0)          ->  X X ... X  (m copies; `X{0}` is deleted);
  - `X{m,n}`/`X{m,}`, m >= 1 ->  X^m (?:X){0,n-m} X^m  (the head and best
    read X^m then the gap, the tail the gap then X^m; the run never crosses
    the gap, so the doubled copies give exactly T2 row 3's runs, and only
    the run BYTES are compared, never offsets);
  - `X{0,n}`, `X*`, `X?`     ->  unchanged (T2 row 3 at c = 0 is the gap).
Each copy is `(?:X)`. A width-0 body is E1's and already in the reference.
Spelled bottom-up, so nested repeats compose. ABSTAINED (listed): `(?x)`; a
named group inside a copied body (the copies would duplicate the name); a
capture inside a copied body when the pattern refers to groups (a
backreference, a call, a condition, `(?|`); a quantified non-ASCII literal
byte (the byte and utf8 encodings read it as different atoms); a quantifier
after `\Q...\E`; a spelling over 20000 bytes.

THE OBSERVATION and THE COMPARE are census_e1.py's: every `--emit-facts=
byte,utf8` row of the reference vs the working compiler; predicted =
the spelling's reference run differs from the pattern's reference run;
the value check = the working run equals the spelling's reference run,
per encoding. A value difference whose two runs carry the same information
(`popcount` of the masks: a tie the walk breaks by its own order, span_arms
F22) is listed apart as TIE, not as a mismatch.

usage: census_r1.py REF_PCREC WORK_PCREC TREE BENCH_DIR OUT_DIR [--jobs N]
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



REFS = re.compile(rb"\\[1-9]|\\g|\\k|\(\?P[=>]|\(\?&|\(\?R|\(\?[0-9+-]|\(\?\(|\(\?\||\(\*")
MAXLEN = 20000


def named_group(t):
    return re.search(rb"\(\?(?:P?<[A-Za-z_]|')", t) is not None


def quant_parts(q):
    """The quantifier text -> (base, suffix)."""
    if q[:1] == b"{":
        k = q.index(b"}") + 1
        return q[:k], q[k:]
    return q[:1], q[1:]


def spell_seq(p, a, b, refs, cnt):
    out = []
    for sa, sb in alts(p, a, b):
        part = b""
        for (s, ae, e, kind, rmin, rmax) in seq_items(p, sa, sb):
            if isinstance(kind, tuple):
                atom = p[s:kind[1]] + spell_seq(p, kind[1], kind[2], refs, cnt) + p[kind[2]:ae]
                zero = zero_width(p, kind[1], kind[2])
            else:
                atom = p[s:ae]
                zero = kind == "zero"
                if kind == "cons" and e > ae and len(atom) == 1 and atom[0] >= 0x80:
                    raise Abstain("a quantified non-ASCII literal byte")
            if e == ae or zero or (rmin == 0 and rmax != 0):
                part += atom + p[ae:e]
                continue
            if isinstance(kind, tuple) and (rmin >= 2 or rmax != rmin):
                if named_group(atom):
                    raise Abstain("a named group inside a copied body")
                if refs and (kind[3] or has_capture(p, kind[1], kind[2])):
                    raise Abstain("a capture inside a copied body, and the pattern refers to groups")
            c = b"(?:" + atom + b")"
            if rmax == rmin:
                sp = c * rmin
            else:
                _, suf = quant_parts(p[ae:e])
                gap = b"*" if rmax is None else b"{0,%d}" % (rmax - rmin)
                sp = c * rmin + c + gap + suf + c * rmin
            cnt[0] += 1
            if len(sp) > MAXLEN:
                raise Abstain("a spelling over %d bytes" % MAXLEN)
            part += sp
        out.append(part)
    return b"|".join(out)


def spell(p):
    """(spelled pattern, n spelled repeats) or raise Abstain."""
    if b"(?x" in p or b"(?xx" in p:
        raise Abstain("(?x)")
    if re.search(rb"\\E[*+?{]", p):
        raise Abstain("a quantifier after \\Q...\\E")
    cnt = [0]
    q = spell_seq(p, 0, len(p), REFS.search(p) is not None, cnt)
    return q, cnt[0]


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
        # the note's leading provenance label ("core"/"derived": req_whole_run is PF_DERIVED
        # since the rate rule) is a listing label, not a value or a why
        if len(x) > 8 and x[8].split(";", 1)[0] in ("core", "derived"):
            x[8] = x[8].split(";", 1)[1] if ";" in x[8] else ""
        rows[(x[0], x[1])] = x
    return rows


def run_of(rows):
    """The run and the pieces, per encoding: what T2 rows 2-3 can change."""
    if rows is None:
        return None
    return tuple(rows.get((e, f), [None] * 8)[k] for e in ("byte", "utf8")
                 for f, k in (("req_whole_run", 6), ("req_pieces", 6)))


def info(run):
    """A listed run's information: popcount of its masks (8 per exact byte)."""
    if run in (None, "none", ""):
        return 0
    if "/" in run:
        m = bytes.fromhex(run.split("/")[1])
        return sum(bin(x).count("1") for x in m)
    return 4 * len(run)


def one(args):
    ref, work, src, pat = args
    rec = {"src": src, "pat": pat}
    r0 = facts(ref, pat); r1 = facts(work, pat)
    rec["compiled"] = r0 is not None and r1 is not None
    if not rec["compiled"]:
        return rec
    rec["moved"] = sorted({k[1] for k in set(r0) | set(r1) if r0.get(k) != r1.get(k)})
    rec["moved_value"] = sorted({k[1] for k in set(r0) | set(r1)
                                 if (r0.get(k) or [None] * 8)[6:8] != (r1.get(k) or [None] * 8)[6:8]})
    # a description dropped on both sides, for another first reason (the
    # power is described before its right neighbour's wall is met; the
    # spelling meets the wall first): the listing's why alone moves
    rec["why_only"] = rec["moved_value"] == ["req_pieces"] and all(
        (r0.get((e, "req_pieces")) or [None] * 8)[6] == "none" ==
        (r1.get((e, "req_pieces")) or [None] * 8)[6] for e in ("byte", "utf8"))
    try:
        q, n = spell(pat)
        rec["ncand"] = n
        if n:
            rs = facts(ref, q)
            rec["spelled_run"] = run_of(rs)
            rec["predicted"] = rs is not None and run_of(rs) != run_of(r0)
            if rs is None:
                rec["abstain"] = "the spelling does not compile"
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
    whyonly = {r["pat"] for r in comp if r["moved"] and r.get("why_only")}
    obs = {r["pat"] for r in comp if r["moved"]} - whyonly
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
    diff = [p for p in obs & pred if by[p]["work_run"] != by[p]["spelled_run"]]
    def tie(p):
        w, s = by[p]["work_run"], by[p]["spelled_run"]
        return (s is not None and all(info(w[i]) == info(s[i]) for i in (0, 2))
                and (w[1], w[3]) == (s[1], s[3]))
    ties = [p for p in diff if tie(p)]
    valbad = [p for p in diff if not tie(p)]
    lines = [
        "population: %d rows (%d corpus, %d bench), %d distinct texts, %d compiled on both sides"
        % (len(pop), sum(1 for s, _ in pop if s.startswith("corpus:")),
           sum(1 for s, _ in pop if s.startswith("bench:")), len(seen), len(comp)),
        "candidates (texts with a spelled repeat): %d; abstained: %d (of them movers: %d)"
        % (sum(1 for r in comp if r.get("ncand")), sum(1 for r in comp if r.get("abstain")), len(absn)),
        "observed movers: %d (corpus %d, bench %d)" % (len(obs),
            sum(1 for p in obs if by[p]["src"].startswith("corpus:")),
            sum(1 for p in obs if by[p]["src"].startswith("bench:"))),
        "predicted movers: %d" % len(pred),
        "predicted and observed: %d; value mismatches (work run != reference run of the spelling): %d; ties (equal information, other bytes): %d"
        % (len(obs & pred), len(valbad), len(ties)),
        "observed, not predicted: %d" % len(obs - pred),
        "predicted, not observed: %d" % len(pred - obs),
        "facts that moved (union): %s" % ",".join(sorted({f for p in obs for f in by[p]["moved"]})),
        "facts whose VALUE or WHY moved (union; the rest moved only their `used` column): %s"
        % ",".join(sorted({f for p in obs for f in by[p]["moved_value"]})),
        "pieces WHY-only movers (both `none`, another drop reason; not counted as movers): %d" % len(whyonly),
        "pieces movers: %d (every one an exact repeat's: listed as PIECES below)" % sum(1 for p in obs if "req_pieces" in by[p]["moved"]),
    ]
    for p in sorted(obs - pred):
        lines.append("  OBS-NOT-PRED %s %s moved=%s abstain=%s" % (by[p]["src"], esc(p), ",".join(by[p]["moved"]), by[p].get("abstain", "")))
    for p in sorted(pred - obs):
        lines.append("  PRED-NOT-OBS %s %s" % (by[p]["src"], esc(p)))
    for p in sorted(ties):
        lines.append("  TIE %s %s work=%s spelled=%s" % (by[p]["src"], esc(p), by[p]["work_run"], by[p]["spelled_run"]))
    for p in sorted(valbad):
        lines.append("  VALUE %s %s work=%s spelled=%s" % (by[p]["src"], esc(p), by[p]["work_run"], by[p]["spelled_run"]))
    for p in sorted(whyonly):
        lines.append("  PIECES-WHY %s %s" % (by[p]["src"], esc(p)))
    for p in sorted(p for p in obs if "req_pieces" in by[p]["moved"]):
        lines.append("  PIECES %s %s" % (by[p]["src"], esc(p)))
    for r in sorted((r for r in comp if r.get("abstain")), key=lambda r: r["src"]):
        lines.append("  ABSTAIN %s %s: %s%s" % (r["src"], esc(r["pat"]), r["abstain"], " (MOVER)" if r["moved"] else ""))
    lines.append("== census COMPLETE: %d movers, %d two-sided differences" % (len(obs), len((obs - pred) | (pred - obs)) + len(valbad)))
    with open(os.path.join(out, "summary.txt"), "w") as h:
        h.write("\n".join(lines) + "\n")
    print("\n".join(lines))
    return 0


if __name__ == "__main__":
    sys.exit(main())
