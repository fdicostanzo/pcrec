#!/usr/bin/env python3
"""rev22_population.py -- size the REAL J1 population for regime_eval.md rev 2.2.

Lane regeval5, 2026-10-14. No clock, no build, no pcrec: it reads the
[REGIME-CORPUS] manifest and the 177 blinded questions from `main` (git show),
and the corpus BYTES from worktrees/.corpus/ (read only, never executed), and
prints COUNTS:

  1. per subject file: bytes, line-ending class (crlf / lf / mixed / one-line /
     binary), line count, median line length, NUL share, the window budget
     under rev 2.2's buffer-drawing rule (§2.4), and the label (mislabelled);
  2. per question: the first-byte set S of the pattern (zero-width erased,
     from python's own sre parse of the pattern or of rwquest's python
     equivalent; UTF-8 lead bytes for code points), the EXPECTED five-class
     placement (an ESTIMATE: REFUSE / NOSITE / OTHER / UNREACHED / RT need
     pcrec), the call shape, the landing gap g_est = 1 / rate(S) over the
     question's own file sampled by the window rule, the bytes per match from
     rwquest's python count, and the regime under two readings that BRACKET
     the counted placement (lower: one activation per landing, L = g; upper:
     one activation per match, L = bytes per match);
  3. the counts per class x expected class, RT per class x regime, the primed
     split (§5.1), and writes rev22_population.tsv (one row per question).

Every class and regime here is an ESTIMATE (marked `est`); E6's site-mapping
census (no clock) replaces it. Usage:
  python3 -I -B rev22_population.py [CORPUS_DIR]   (default ../../../../../.corpus)
"""
import hashlib
import os
import re._constants as C
import re._parser as P
import subprocess
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
TREE = os.path.normpath(os.path.join(HERE, "..", "..", "..", ".."))
CORPUS = sys.argv[1] if len(sys.argv) > 1 else os.path.normpath(
    os.path.join(TREE, "..", ".corpus"))
OUT_TSV = os.path.join(HERE, "rev22_population.tsv")

B = 65536                    # window (one streamed buffer), rev 2.1 §2.4
M_WANT = 64                  # windows per streamed subject (4 MiB)
M_MIN = 16                   # rev 2.2: fewer than 16 windows (1 MiB) = short-pool
SALT = b"rev2.2-estimate"    # stand-in; the prereg's prereg_salt replaces it at E6
MISLABELLED = {"nonenglish/pg8186.txt", "nonenglish/pg8453.txt",
               "nonenglish/pg20175.txt"}

# Pool families (rev 2.2 §2.4): a question's streamed subject is drawn from its
# own file first, then from files of the SAME family (same format / script /
# language / log source), never across families, never from a mislabelled file.
FAMILY = {}
for n in ("76 84 98 135 345 996 1184 1342 1400 1661 2600 2701").split():
    FAMILY["prose/pg%s.txt" % n] = "prose-en"
for script, ids in (("cjk", "4572 4573 4580 7221 7290 7317"),
                    ("kana", "1982 31617 31757 33307 34013"),
                    ("cyrillic", "2790 2890 11291 14741 15008 30774 37196"),
                    ("greek", "17814 17839 26731"),
                    ("hebrew", "43740 61024"),
                    ("latin-ext", "6696 6698"),
                    ("translit", "9000")):
    for n in ids.split():
        FAMILY["nonenglish/pg%s.txt" % n] = "ne-" + script


def git_show(path):
    return subprocess.run(["git", "-C", TREE, "show", "main:" + path],
                          check=True, capture_output=True).stdout.decode()


def load_manifest():
    rows = []
    for line in git_show("docs/dev/lanes/rwcorpus/manifest.tsv").splitlines()[1:]:
        f = line.split("\t")
        if "/raw/" in f[1]:
            continue                     # raw archives are inputs, not subjects
        rows.append((f[0], f[1], int(f[2])))
    return rows


def load_questions():
    lines = git_show("docs/dev/lanes/rwquest/questions.tsv").splitlines()
    head = lines[0].split("\t")
    out = []
    for line in lines[1:]:
        f = line.split("\t")
        out.append(dict(zip(head, f)))
    return out


# ------------------------------------------------------------ windows (§2.4)
def h(*parts):
    return int.from_bytes(hashlib.sha256(b"|".join(parts)).digest()[:8], "big")


def reserve(path, size):
    """The exemplar reserve: R = size // 8 (at least 64 KiB when size >= 128 KiB),
    at a salt-derived offset. Returns (lo, hi)."""
    r = size // 8
    if size >= 2 * B:
        r = max(r, B)
    lo = h(SALT, path.encode(), b"E") % max(1, size - r + 1)
    return lo, lo + r


def usable(path, size):
    lo, hi = reserve(path, size)
    return [(0, lo), (hi, size)]


def windows(path, size):
    """rev 2.2's rule for one file: the file minus its exemplar reserve is one
    USABLE stream; cut it into M equal strata, M = min(64, floor(usable / B)),
    and take one B-byte window per stratum at a salt-derived offset. A window
    that crosses the reserve continues after it (it never reads reserved
    bytes). Returns, per window, a list of (file offset, length) pieces.
    (A pool concatenates its files' usable streams the same way.)"""
    segs = usable(path, size)
    total = sum(b - a for a, b in segs)
    m = min(M_WANT, total // B)
    out = []
    if m == 0:
        return out
    span = total // m
    for j in range(m):
        u = j * span + h(SALT, path.encode(), b"W", str(j).encode()) % max(1, span - B + 1)
        pieces, need = [], B
        for a, b in segs:
            seglen = b - a
            if u >= seglen:
                u -= seglen
                continue
            take = min(need, seglen - u)
            pieces.append((a + u, take))
            need -= take
            u = 0
            if need == 0:
                break
        out.append(pieces)
    return out


# ------------------------------------------------------------ file facts
def file_facts(rel):
    path = os.path.join(CORPUS, rel)
    with open(path, "rb") as f:
        data = f.read()
    size = len(data)
    lf = data.count(b"\n")
    crlf = data.count(b"\r\n")
    cls = rel.split("/")[0]
    if cls == "binary":
        eol = "binary"
    elif lf <= 1:
        eol = "one-line"
    elif crlf >= 0.99 * lf:
        eol = "crlf"
    elif crlf <= 0.01 * lf:
        eol = "lf"
    else:
        eol = "mixed"
    hist = [0] * 256
    wins = windows(rel, size)
    if wins:
        sample = b"".join(data[o:o + n] for w in wins for o, n in w)
    else:
        lo, hi = reserve(rel, size)
        sample = data[:lo] + data[hi:]          # under one window: the usable bytes
    use = sum(b - a for a, b in usable(rel, size))
    for b in range(256):
        hist[b] = sample.count(bytes([b]))
    lens = sorted(len(x) for x in data.split(b"\n")[:200000]) if lf else [size]
    med = lens[len(lens) // 2]
    return {"size": size, "eol": eol, "lines": lf, "med_line": med,
            "nul": data.count(b"\x00") / max(1, size), "hist": hist,
            "nsamp": len(sample), "nwin": len(wins), "usable": use,
            "buckets": bucket_bytes(data), "med_long": med_long(data)}


EDGES = (14, 32, 64)            # rev 2.1 §1.3's lines bucket edges


def bucket_bytes(data):
    """bytes in lines whose length (LF-split, CR kept) falls in each bucket"""
    out = [0, 0, 0, 0]
    for ln in data.split(b"\n"):
        n = len(ln)
        k = sum(n >= e for e in EDGES)
        out[k] += n + 1
    return out


def med_long(data):
    ls = sorted(len(x) for x in data.split(b"\n") if len(x) >= 64)
    return ls[len(ls) // 2] if ls else 0


# ------------------------------------------------------------ first-byte set
def lead(cp):
    if cp < 0x80:
        return cp
    if cp < 0x800:
        return 0xC0 | (cp >> 6)
    if cp < 0x10000:
        return 0xE0 | (cp >> 12)
    return 0xF0 | (cp >> 18)


def leads_of_ranges(ranges):
    out = set()
    for a, b in ranges:
        for lo_, hi_ in ((0, 0x7F), (0x80, 0x7FF), (0x800, 0xFFFF), (0x10000, 0x10FFFF)):
            x, y = max(a, lo_), min(b, hi_)
            if x <= y:
                out.update(range(lead(x), lead(y) + 1))
    return out


def complement(ranges, top):
    ranges = sorted(ranges)
    out, cur = [], 0
    for a, b in ranges:
        if a > cur:
            out.append((cur, a - 1))
        cur = max(cur, b + 1)
    if cur <= top:
        out.append((cur, top))
    return out


ASCII_WORD = [(48, 57), (65, 90), (95, 95), (97, 122)]
ASCII_DIGIT = [(48, 57)]
ASCII_SPACE = [(9, 13), (32, 32)]
UCP_EXTRA = [(0x80, 0x10FFFF)]          # under ucp: approximate \w/\d/\s as "any non-ASCII"


def cat_ranges(cat, ucp):
    base = {C.CATEGORY_DIGIT: ASCII_DIGIT, C.CATEGORY_WORD: ASCII_WORD,
            C.CATEGORY_SPACE: ASCII_SPACE}
    neg = {C.CATEGORY_NOT_DIGIT: C.CATEGORY_DIGIT, C.CATEGORY_NOT_WORD: C.CATEGORY_WORD,
           C.CATEGORY_NOT_SPACE: C.CATEGORY_SPACE}
    if cat in base:
        return base[cat] + (UCP_EXTRA if ucp else []), False
    return base[neg[cat]], True


def casefold_ranges(ranges):
    extra = []
    for a, b in ranges:
        for cp in range(a, min(b, 0x24F) + 1):
            ch = chr(cp)
            for v in (ch.lower(), ch.upper()):
                if len(v) == 1 and ord(v) != cp:
                    extra.append((ord(v), ord(v)))
    return ranges + extra


class Walk:
    def __init__(self, text, ucp):
        self.text, self.ucp = text, ucp
        self.top = 0x10FFFF if text else 0xFF

    def univ(self):
        return [(0, self.top)]

    def item(self, op, av, fl):
        """-> (ranges, nullable)"""
        ci = fl & 2
        if op is C.LITERAL:
            r = [(av, av)]
            return (casefold_ranges(r) if ci else r), False
        if op is C.NOT_LITERAL:
            return complement([(av, av)], self.top), False
        if op is C.ANY:
            return (self.univ() if fl & 16 else complement([(10, 10)], self.top)), False
        if op is C.IN:
            rs, neg = [], False
            for o, a in av:
                if o is C.NEGATE:
                    neg = True
                elif o is C.LITERAL:
                    rs.append((a, a))
                elif o is C.RANGE:
                    rs.append(a)
                elif o is C.CATEGORY:
                    cr, cneg = cat_ranges(a, self.ucp)
                    rs.extend(complement(cr, self.top) if cneg else cr)
            if ci:
                rs = casefold_ranges(rs)
            return (complement(rs, self.top) if neg else rs), False
        if op is C.BRANCH:
            rs, nul = [], False
            for s in av[1]:
                r, n = self.seq(s, fl)
                rs += r
                nul |= n
            return rs, nul
        if op is C.SUBPATTERN:
            add, dele = av[1], av[2]
            return self.seq(av[3], (fl | add) & ~dele)
        if op in (C.MAX_REPEAT, C.MIN_REPEAT, C.POSSESSIVE_REPEAT):
            r, n = self.seq(av[2], fl)
            return r, (n or av[0] == 0)
        if op is C.ATOMIC_GROUP:
            return self.seq(av, fl)
        if op in (C.AT, C.ASSERT, C.ASSERT_NOT):
            return [], True
        if op is C.GROUPREF:
            return self.univ(), True
        raise ValueError("unhandled %s" % op)

    def seq(self, items, fl):
        rs = []
        for op, av in items:
            r, n = self.item(op, av, fl)
            rs += r
            if not n:
                return rs, False
        return rs, True


def first_set(q):
    flags = q["flags"].split(",") if q["flags"] != "-" else []
    utf = "utf" in flags
    ucp = "ucp" in flags
    pat = q["py_equiv_pattern"] or q["pattern"]
    pf = 0
    if "i" in flags:
        pf |= 2
    if "m" in flags:
        pf |= 8
    if "s" in flags:
        pf |= 16
    if utf:
        tree = P.parse(pat, pf)
        w = Walk(True, ucp)
    else:
        tree = P.parse(pat.encode("latin-1"), pf)
        w = Walk(False, ucp)
    fl = tree.state.flags
    rs, nul = w.seq(list(tree), fl)
    lead_set = leads_of_ranges(rs) if utf else set(
        b for a, c in rs for b in range(a, c + 1))
    first = list(tree)
    anch = mline = False
    if first and first[0][0] is C.AT:
        kind = first[0][1]
        if kind in (C.AT_BEGINNING, C.AT_BEGINNING_STRING):
            if fl & 8 and kind is C.AT_BEGINNING:
                mline = True
            else:
                anch = True
    return lead_set, nul, anch, mline


# ------------------------------------------------------------ placement (est)
UNREACHED_EST = {"L25", "N11"}   # zero python hits AND the required run absent: the pre-check answers
UCP_RISK = set()                 # filled below: questions needing (*UCP)


def place(q, S, nul, anch, mline):
    """Expected class (ESTIMATE). First match, in order:"""
    flags = q["flags"]
    if anch or (q["mode"] == "line" and q["pattern"].startswith("^")):
        return "NOSITE", "anchored at the subject (or line) start"
    if mline:
        return "OTHER", "MLINE ((?m)^ line-start site)"
    if nul or len(S) >= 250:
        return "NOSITE", "no narrowing first-byte set (|S| = %d%s)" % (
            len(S), ", nullable" if nul else "")
    if len(S) == 1:
        return "OTHER", "pf_memchr (one first byte)"
    if q["id"] in UNREACHED_EST:
        return "UNREACHED", "required run absent: the pre-check answers"
    return "RT", "set FIND, |S| = %d" % len(S)


def shape(mode):
    return {"find-all": "all", "count": "all", "first": "first", "line": "lines"}[mode]


def primed(q):
    """§5.1's disclosure split: the intents the injected digest could have
    primed (rare literals, anchors, back-references, many-keyword alternations)."""
    p = q["pattern"]
    lit = re_literal_run(p)
    tags = []
    if q["guess_frequency"] == "rare" and lit >= 3:
        tags.append("rare-literal")
    if "$" in p.replace("\\$", "") or p.startswith("^") or "\\A" in p or "\\z" in p:
        tags.append("anchor")
    if "\\1" in p:
        tags.append("backref")
    if p.count("|") >= 3:
        tags.append("keyword-alt")
    return ",".join(tags) or "-"


def re_literal_run(p):
    best = cur = 0
    i = 0
    while i < len(p):
        ch = p[i]
        if ch == "\\" and i + 1 < len(p):
            if p[i + 1] in ".\\-/\"'[](){}*+?|^$":
                cur += 1
                i += 2
                continue
            cur = 0
            i += 2
            continue
        if ch.isalnum() or ch in " _-:/@<>=\",'":
            cur += 1
        else:
            cur = 0
        best = max(best, cur)
        i += 1
    return best


def w_ok(rel, ff):
    """(W): one contiguous >= 1 MiB slice of the file outside its reserve"""
    return max(b - a for a, b in usable(rel, ff["size"])) >= 1 << 20


def runs(S):
    """the RANGE-term count proxy: maximal runs of consecutive byte values in S"""
    s = sorted(S)
    return sum(1 for i, b in enumerate(s) if i == 0 or s[i - 1] != b - 1)


def regime(L, g):
    if L < 64:
        return "DINGHY"
    return "TUG" if g < 18.5 else "LINER"


def main():
    man = load_manifest()
    qs = load_questions()
    files = sorted({q["files"].split(";")[0] for q in qs} |
                   {r[1] for r in man})
    facts = {}
    print("== 1. subject files (derived rows of manifest.tsv; raw archives excluded)")
    print("%-44s %10s %-8s %8s %6s %5s %4s %-2s %-19s %s" % (
        "file", "bytes", "eol", "lines", "medln", "NUL%", "win", "W", "lines % <14/<32/<64/64+", "label"))
    for rel in files:
        if not os.path.exists(os.path.join(CORPUS, rel)):
            continue
        ff = file_facts(rel)
        facts[rel] = ff
        lab = "MISLABELLED" if rel in MISLABELLED else ""
        bt = ff["buckets"]
        tb = max(1, sum(bt))
        print("%-44s %10d %-8s %8d %6d %5.1f %4d %-2s %-19s %s" % (
            rel, ff["size"], ff["eol"], ff["lines"], ff["med_line"],
            100 * ff["nul"], ff["nwin"], "y" if w_ok(rel, ff) else "-",
            "/".join("%d" % round(100 * x / tb) for x in bt), lab))
    eolc = {}
    for rel, ff in facts.items():
        eolc.setdefault((rel.split("/")[0], ff["eol"]), []).append(rel)
    print("  line-ending classes per corpus class:")
    for (c, e), v in sorted(eolc.items()):
        print("    %-11s %-8s %3d files" % (c, e, len(v)))
    print()

    # pool budget per question family
    def pool_windows(rel):
        fam = FAMILY.get(rel, rel)
        pool = [rel] + sorted(r for r in facts if FAMILY.get(r, r) == fam and r != rel
                              and r not in MISLABELLED)
        tot = sum(facts[r]["size"] for r in pool)
        r_pool = max(B, tot // 8) if tot >= 2 * B else tot // 8   # ONE exemplar reserve per pool
        return fam, min(M_WANT, (tot - r_pool) // B), len(pool)

    print("== 2. questions: expected class (ESTIMATE), shape, g_est, regime brackets")
    rows = []
    for q in qs:
        rel = q["files"].split(";")[0]
        S, nul, anch, mline = first_set(q)
        cls, why = place(q, S, nul, anch, mline)
        flags = q["flags"]
        if "ucp" in flags:
            UCP_RISK.add(q["id"])
        ff = facts[rel]
        fam, pw, pn = pool_windows(rel)
        rate = sum(ff["hist"][b] for b in S) / max(1, ff["nsamp"])
        g = 1 / rate if rate > 0 else float("inf")
        cnt = int(q["py_count_full"] or 0)
        bpm = ff["size"] / cnt if cnt else float("inf")
        L_lo, L_up = g, max(g, bpm)
        sh = shape(q["mode"])
        if sh == "lines":
            L_lo, L_up = min(L_lo, ff["med_line"]), min(L_up, ff["med_line"])
        rlo, rup = regime(L_lo, g), regime(L_up, g)
        excl = ""
        if cls == "RT":
            if rel in MISLABELLED:
                excl = "mislabelled"
            elif pw < M_MIN:
                excl = "short-pool"
        if excl:
            cls = "GATE-EXCLUDED"
            why = excl
        row = dict(id=q["id"], cls=q["class"], file=rel, fam=fam, eol=ff["eol"],
                   flags=flags, mode=q["mode"], shape=sh, S=len(S), est=cls, why=why,
                   g=g, bpm=bpm, rlo=rlo, rup=rup, pool=pw, pooln=pn,
                   primed=primed(q), ucp=("ucp" if "ucp" in flags else "-"),
                   runs=runs(S), w=("y" if w_ok(rel, ff) else "-"),
                   b0=ff["buckets"][0], b1=ff["buckets"][1], b2=ff["buckets"][2],
                   b3=ff["buckets"][3], medlong=ff["med_long"],
                   eolsens=("eol-sensitive" if ff["eol"] == "crlf" and
                            ("$" in q["pattern"] or "(?m)" in q["pattern"] or "m" in flags.split(","))
                            else "-"))
        rows.append(row)
    with open(OUT_TSV, "w") as f:
        cols = ["id", "cls", "file", "fam", "eol", "flags", "mode", "shape", "S",
                "est", "why", "g", "bpm", "rlo", "rup", "pool", "pooln", "primed",
                "ucp", "eolsens", "runs", "w", "b0", "b1", "b2", "b3", "medlong"]
        f.write("# rev22_population.py output: one row per question; est / rlo / rup are ESTIMATES\n")
        f.write("\t".join(cols) + "\n")
        for r in rows:
            f.write("\t".join(("%.1f" % r[c]) if isinstance(r[c], float) else str(r[c])
                              for c in cols) + "\n")
    print("%-4s %-10s %-6s %-5s %4s %-13s %8s %9s %-6s %-6s %5s %s" % (
        "id", "class", "shape", "eol", "|S|", "est", "g_est", "B/match", "rlo", "rup",
        "pool", "why"))
    for r in rows:
        print("%-4s %-10s %-6s %-5s %4d %-13s %8.1f %9.0f %-6s %-6s %5d %s" % (
            r["id"], r["cls"], r["shape"], r["eol"][:5], r["S"], r["est"], r["g"],
            min(r["bpm"], 1e9), r["rlo"], r["rup"], r["pool"], r["why"]))
    print()

    classes = ["logs", "code", "prose", "structured", "markup", "nonenglish", "binary"]
    kinds = ["REFUSE", "NOSITE", "OTHER", "UNREACHED", "GATE-EXCLUDED", "RT"]
    print("== 3. expected class per corpus class (ESTIMATE; REFUSE needs pcrec: see ucp risk)")
    print("%-11s %4s " % ("class", "n") + " ".join("%13s" % k for k in kinds))
    tot = {k: 0 for k in kinds}
    for c in classes:
        sub = [r for r in rows if r["cls"] == c]
        line = "%-11s %4d " % (c, len(sub))
        for k in kinds:
            n = sum(r["est"] == k for r in sub)
            tot[k] += n
            line += "%13d " % n
        print(line)
    print("%-11s %4d " % ("ALL", len(rows)) + " ".join("%13d" % tot[k] for k in kinds))
    print("  ucp (REFUSE risk until [UCP] ships its route): %s" % " ".join(sorted(UCP_RISK)))
    print("  GATE-EXCLUDED reasons: %s" % ", ".join(
        "%s %s" % (r["id"], r["why"]) for r in rows if r["est"] == "GATE-EXCLUDED"))
    print()

    rt = [r for r in rows if r["est"] == "RT"]
    print("== 4. RT patterns per class x regime, own call shape (lower: L = g / upper: L = bytes per match)")
    regs = ["DINGHY", "TUG", "LINER"]
    print("%-11s %4s  %s" % ("class", "RT", "  ".join("%-13s" % x for x in regs)))
    for c in classes + ["ALL"]:
        sub = [r for r in rt if c == "ALL" or r["cls"] == c]
        cells = []
        for x in regs:
            cells.append("%3d / %3d    " % (sum(r["rlo"] == x for r in sub),
                                            sum(r["rup"] == x for r in sub)))
        print("%-11s %4d  %s" % (c, len(sub), "  ".join(cells)))
    print("  RT by own shape: " + ", ".join(
        "%s %d" % (s, sum(r["shape"] == s for r in rt)) for s in ("all", "first", "lines")))
    print("  RT by eol: " + ", ".join(
        "%s %d" % (e, sum(r["eol"] == e for r in rt)) for e in ("lf", "crlf", "one-line", "binary", "mixed")))
    print("  RT eol-sensitive (CRLF file and a line anchor): %s" % " ".join(
        r["id"] for r in rt if r["eolsens"] != "-"))
    pr = [r for r in rt if r["primed"] != "-"]
    print("  RT primed-intent split (§5.1): %d primed, %d not; primed ids: %s" % (
        len(pr), len(rt) - len(pr), " ".join(r["id"] for r in pr)))
    allp = [r for r in rows if r["primed"] != "-"]
    print("  all questions primed-intent: %d of %d" % (len(allp), len(rows)))
    # patterns per regime (G0 needs >= 5 patterns per layer x regime x filter)
    print()
    print("== 5. RT per class (own shape) with g_est bands (B per landing)")
    for c in classes:
        sub = [r for r in rt if r["cls"] == c]
        bands = [sum(r["g"] < 18.5 for r in sub), sum(18.5 <= r["g"] < 64 for r in sub),
                 sum(r["g"] >= 64 for r in sub)]
        print("  %-11s g<18.5 %3d  18.5..64 %3d  >=64 %3d" % (c, *bands))


if __name__ == "__main__":
    main()
