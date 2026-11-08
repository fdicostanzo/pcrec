"""p2_model.py PCREC CASEFOLDING BENCH_UTF8_DIR -- Stage 2p's gate
(docs/design/alt_normal_form.md §5 stage 2p "Gate"; lane altbuild,
2026-11-06): pcrec's `req_pieces` fact equals an INDEPENDENT model's on
  (1) the 37 mixed-width simple-fold classes X in `(?i)abcd<X>efgh` -e utf8,
  (2) every bench/utf8 pattern the model can read (the rest are listed
      UNPREDICTED and counted, K35).

THE MODEL shares no code with pcrec. A pattern it reads is a top-level
alternation of sequences of ITEMS: a literal character, `\\x{..}`, a
bracket class of characters/ranges (negated or not), `.`, or ASCII
`\\d \\s \\w`; `(?i)` folds each literal and class member to its simple-fold
orbit (CaseFolding.txt C+S). Each item is a finite string set; its UTF-8
encodings grouped by byte length give per-length position sets. The
description of a sequence is the product (widths add, positions
concatenate), of an alternation the union, and any two groups of one total
width are the position-wise union -- which equals the position-wise union
over ALL the language's strings of that length, however early it is taken
(every string of one length aligns at both ends). Anything with an anchor,
`\\b`, a quantifier or a lookaround is a WALL (pcrec cuts there until stage
2a, §3.4), predicted `decline:not-fixed-width`. One group predicts
`decline:one-group`. Rendering: facts_listing.md §4.1.2's `req_pieces`
spelling (groups ascending, `W:` or `W@o:`, the last 32 positions stored).
Exit 1 on any difference, or if the readable population is under its floor."""
import collections, os, re, subprocess, sys

MAX_POS = 32

def orbits(path):
    g = collections.defaultdict(set)
    for line in open(path, encoding="utf-8"):
        line = line.split("#")[0].strip()
        if not line: continue
        f = [x.strip() for x in line.split(";")]
        if f[1] not in ("C", "S"): continue
        s, d = int(f[0], 16), int(f[2], 16)
        g[d] |= {s, d}
    orb = {}
    for d, m in g.items():
        for c in m: orb[c] = m
    return orb

def fold(cps, orb, ci):
    if not ci: return set(cps)
    out = set()
    for c in cps: out |= orb.get(c, {c})
    return out

def valid(c): return not (0xD800 <= c <= 0xDFFF)

ALL = [c for c in range(0x110000) if valid(c)]

def groups_of(cps):
    """Code point set -> {width: [byte set per position]}."""
    d = {}
    for c in cps:
        b = chr(c).encode("utf-8")
        g = d.setdefault(len(b), [set() for _ in b])
        for i, x in enumerate(b): g[i].add(x)
    return d

def cat(a, b):
    o = {}
    for wa, ga in a.items():
        for wb, gb in b.items():
            g = ga + gb
            if wa + wb in o: o[wa + wb] = [x | y for x, y in zip(o[wa + wb], g)]
            else: o[wa + wb] = [set(x) for x in g]
    return o

def alt(a, b):
    o = {w: [set(x) for x in g] for w, g in a.items()}
    for w, g in b.items():
        if w in o: o[w] = [x | y for x, y in zip(o[w], g)]
        else: o[w] = [set(x) for x in g]
    return o

class Wall(Exception): pass
class Unread(Exception): pass

def parse_class(p, i, orb, ci):
    neg = p[i] == "^"
    if neg: i += 1
    cps, first = set(), True
    while i < len(p) and (p[i] != "]" or first):
        first = False
        if p.startswith("[:", i): raise Unread("posix class")
        c, i = char_at(p, i)
        if i + 1 < len(p) and p[i] == "-" and p[i + 1] != "]":
            d, i = char_at(p, i + 1)
            cps |= set(range(c, d + 1))
        else:
            cps.add(c)
    if i >= len(p): raise Unread("unterminated class")
    cps = {c for c in fold(cps, orb, ci) if valid(c)}
    if neg: cps = set(ALL) - cps
    return cps, i + 1

def char_at(p, i):
    if p[i] == "\\":
        if p.startswith("\\x{", i):
            j = p.index("}", i)
            return int(p[i + 3:j], 16), j + 1
        if p[i + 1] in "\\.^$|?*+()[]{}/-@~": return ord(p[i + 1]), i + 2
        raise Unread("escape " + p[i:i + 2])
    return ord(p[i]), i + 1

def describe(p, orb):
    ci = ucp = False
    while True:
        if p.startswith("(?i)"): ci, p = True, p[4:]
        elif p.startswith("(*UCP)"): ucp, p = True, p[6:]
        elif p.startswith("(?m)"): p = p[4:]
        else: break
    if re.search(r"\(\?<?[=!]", p): raise Wall()
    if any(t in p for t in ("\\b", "\\B", "\\A", "\\z", "\\Z")): raise Wall()
    desc, seq, i = None, {0: []}, 0
    while i <= len(p):
        if i == len(p) or p[i] == "|":
            desc = seq if desc is None else alt(desc, seq)
            seq, i = {0: []}, i + 1
            if i > len(p): break
            continue
        ch = p[i]
        if ch in "^$": raise Wall()
        if ch in "+*?{": raise Wall()
        if ch in "()": raise Unread("group")
        if ch == "[":
            cps, i = parse_class(p, i + 1, orb, ci)
        elif ch == ".":
            cps, i = {c for c in ALL if c != 0x0A}, i + 1
        elif p.startswith(("\\d", "\\s", "\\w"), i):
            if ucp: raise Unread("UCP class")
            cps = {"d": set(range(0x30, 0x3A)), "s": {9, 10, 11, 12, 13, 32},
                   "w": set(range(0x30, 0x3A)) | set(range(0x41, 0x5B)) |
                        set(range(0x61, 0x7B)) | {0x5F}}[p[i + 1]]
            i += 2
        elif p.startswith(("\\p", "\\P"), i):
            raise Unread("property")
        else:
            c, i = char_at(p, i)
            cps = fold({c}, orb, ci)
        seq = cat(seq, groups_of(cps))
    return desc

def render(d):
    if len(d) < 2: return "none", "decline:one-group"
    out = []
    for w in sorted(d):
        g = d[w]
        keep = g[-MAX_POS:]
        head = "%d" % w if len(keep) == w else "%d@%d" % (w, w - len(keep))
        out.append(head + ":" + "".join("[" + ",".join(str(b) for b in sorted(s)) + "]" for s in keep))
    return "|".join(out), ""

def pcrec_pieces(pcrec, pat):
    r = subprocess.run([pcrec, "-p", "rx", "-e", "utf8", "--features", "all",
                        "--emit-facts=utf8", "--pattern", pat],
                       capture_output=True, timeout=120)
    if r.returncode: return None
    for line in r.stdout.decode("utf-8", "replace").splitlines():
        c = line.split("\t")
        if len(c) > 7 and c[1] == "req_pieces": return c[6], c[7]
    return None

def main():
    pcrec, cf, bdir = sys.argv[1:4]
    orb = orbits(cf)
    cells = []
    seen = set()
    for c, m in sorted(orb.items()):
        k = min(m)
        if k in seen: continue
        seen.add(k)
        if len({len(chr(x).encode()) for x in m}) > 1:
            cells.append(("fold-mixed U+%04X" % k, "(?i)abcd%sefgh" % chr(k)))
    nmixed = len(cells)
    for f in sorted(os.listdir(bdir)):
        if f.endswith(".rx"):
            pat = open(os.path.join(bdir, f), encoding="utf-8").read().split("\n")[0]
            cells.append(("bench/utf8/" + f, pat))
    bad = unread = agree = refused = 0
    for name, pat in cells:
        try:
            want = render(describe(pat, orb))
        except Wall:
            want = ("none", "decline:not-fixed-width")
        except Unread as e:
            unread += 1
            got = pcrec_pieces(pcrec, pat)
            print("UNPREDICTED\t%s\t%s\t(%s)\tpcrec: %s" % (name, pat[:60], e, got and got[1]))
            continue
        got = pcrec_pieces(pcrec, pat)
        if got is None:
            refused += 1
            print("REFUSED\t%s\t%s\t(pcrec refuses the compile)" % (name, pat[:60]))
            continue
        if got == want:
            agree += 1
            print("OK\t%s\t%s\t%s" % (name, pat[:60], (want[1] or "%d pieces" % (want[0].count("|") + 1))))
        else:
            bad += 1
            print("DIFF\t%s\t%s\n  model: %s %s\n  pcrec: %s" % (name, pat[:60], want[0][:300], want[1], got))
    print("mixed-width fold classes: %d (design: 37)" % nmixed)
    print("cells: %d agree, %d differ, %d unpredicted, %d refused" % (agree, bad, unread, refused))
    if nmixed != 37: bad += 1; print("FLOOR: the fold population is not 37")
    if agree < 37 + 40: bad += 1; print("FLOOR: fewer than 77 cells agree")
    print("p2 model: %s" % ("FAIL" if bad else "PASS"))
    sys.exit(1 if bad else 0)

main()
