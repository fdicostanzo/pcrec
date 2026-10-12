#!/usr/bin/env python3
"""[COMPOUND] design lane mscomp2: the revision-2 split twin (hand-composed, light).

What changed from twin.py (revision 1), each a panel finding:
  - Q is DERIVED the way the build derives it (chk M3): a small parser turns P
    into a tree, kills every \\G and (outside a lookbehind, and when no (?m)
    occurs) every ^ and \\A to an EMPTY CLASS (the never node; it routes to the
    DFA, where (?!) forced the VM), then prunes bottom-up by compound.md §B.1's
    rules. A pruned arm that holds a capture group is KEPT unpruned: text cannot
    keep a group's number once the group is deleted, which the AST derivation
    does by construction (a twin limitation, logged per case as `keepcap`).
  - F is P's OWN attempt at the floor (sem MF3): P compiled guards-off, its
    <p>_match_caps at f. No \\G(?:P) tree wrap.
  - ONE controller prologue from P (sem MF1/MF2/MF4, arch M5): ctrl2.c.in.
  - Every option arm (sem S2, arch N4): byte, and utf8 x {refuse, none, align}
    x {-futf-check off, on}. Parts are always compiled guards-off.
  - Subjects carry the pattern's witness bytes (chk M4): the pattern's own
    non-ASCII bytes and \\x{...} code points, \\xc3\\xa9, \\x80, a lone \\xc3,
    \\xff; asserted present before the run.
  - Verbs and callouts DECLINE (sem notes): a registry-keyed predicate in the
    build, a token list here.
  - Per case: Q's stamp (must read dfa for an admitted first-build case), the
    match count (must be > 0 somewhere), the decline reason.

  twin2.py PCREC CASES.tsv OUTDIR
CASES.tsv: id <TAB> enc <TAB> pattern_hex <TAB> (ignored: revision 1's q column)
"""
import itertools, os, random, re, subprocess, sys

HERE = os.path.dirname(os.path.abspath(__file__))
GT = "/usr/bin/gnutimeout"
DECLINE_TOKENS = (b"(*COMMIT", b"(*SKIP", b"(*PRUNE", b"(*THEN", b"(*ACCEPT", b"(*FAIL", b"(*F)",
                  b"(?C", b"(*MARK", b"(*:")
NEVER = {"byte": b"[^\\x00-\\xff]", "utf8": b"[^\\x{0}-\\x{10ffff}]"}


# ---- a small regex tree: enough of PCRE's surface for the twin's cases ----
class Item:
    __slots__ = ("kind", "text", "alts", "head", "q", "qmin", "never", "hascap", "flagset")

    def __init__(self, kind, text=b"", alts=None, head=b""):
        self.kind, self.text, self.alts, self.head = kind, text, alts, head
        self.q, self.qmin, self.never, self.hascap, self.flagset = b"", 1, False, False, False


def parse(p):
    pos = [0]

    def alts(depth):
        out = [[]]
        while pos[0] < len(p):
            c = p[pos[0]:pos[0] + 1]
            if c == b"|":
                pos[0] += 1; out.append([]); continue
            if c == b")":
                if depth == 0: raise ValueError("unbalanced )")
                return out
            out[-1].append(atom(depth))
        if depth: raise ValueError("unbalanced (")
        return out

    def quant(it):
        m = re.match(rb"(\*|\+|\?|\{(\d*)(,(\d*))?\})([?+]?)", p[pos[0]:])
        if m and not (m.group(0).startswith(b"{") and m.group(2) == b"" and m.group(3) is None):
            it.q = m.group(0); pos[0] += len(it.q)
            if it.q[:1] in (b"*", b"?"): it.qmin = 0
            elif it.q[:1] == b"{": it.qmin = int(m.group(2) or b"0")
        return it

    def atom(depth):
        i = pos[0]; c = p[i:i + 1]
        if c == b"\\":
            if p[i:i + 2] == b"\\Q":
                j = p.find(b"\\E", i + 2); j = len(p) if j < 0 else j + 2
                pos[0] = j; return Item("lit", p[i:j])
            m = re.match(rb"\\(x\{[0-9a-fA-F]+\}|x[0-9a-fA-F]{0,2}|[pP]\{[^}]*\}|[pP].|[gk]\{[^}]*\}|[gk]<[^>]*>|g-?\d+|c.|\d{1,3}|o\{[0-7]+\}|N\{[^}]*\}|.)", p[i:], re.S)
            pos[0] = i + len(m.group(0)); t = m.group(0)
            kind = "gstart" if t == b"\\G" else "astart" if t == b"\\A" else "lit"
            return quant(Item(kind, t))
        if c == b"[":
            j = i + 1
            if p[j:j + 1] == b"^": j += 1
            if p[j:j + 1] == b"]": j += 1
            while j < len(p) and p[j:j + 1] != b"]":
                if p[j:j + 1] == b"\\": j += 2; continue
                if p[j:j + 2] == b"[:":
                    k = p.find(b":]", j + 2); j = k + 2 if k > 0 else j + 1; continue
                j += 1
            pos[0] = j + 1; return quant(Item("lit", p[i:j + 1]))
        if c == b"^":
            pos[0] += 1; return quant(Item("caret", b"^"))
        if c == b"(":
            if p[i:i + 2] == b"(*":
                j = p.find(b")", i); pos[0] = j + 1; return Item("lit", p[i:j + 1])
            m = re.match(rb"\((\?(?:#[^)]*\)|[a-zA-Z^-]*\)|[a-zA-Z^-]*:|=|!|<=|<!|>|\||P?<[A-Za-z_]\w*>|'[A-Za-z_]\w*'|P>[^)]*\)|&[^)]*\)|R\)|[+-]?\d+\)|\())?", p[i:])
            head = m.group(0)
            if head.endswith(b")") and head != b"(":           # comment, flag-only, or a call
                pos[0] = i + len(head)
                it = Item("lit", head)
                it.flagset = re.match(rb"\(\?[a-zA-Z^-]*\)$", head) is not None
                return quant(it)
            pos[0] = i + len(head)
            if head == b"(?(":                                  # conditional: opaque
                d, j = 2, pos[0]                      # the group and its condition
                while j < len(p) and d:
                    if p[j:j + 1] == b"\\": j += 2; continue
                    d += {b"(": 1, b")": -1}.get(p[j:j + 1], 0); j += 1
                pos[0] = j; return quant(Item("lit", p[i:j]))
            a = alts(depth + 1)
            pos[0] += 1                                          # ')'
            it = Item("group", alts=a, head=head)
            it.hascap = head == b"(" or head.startswith(b"(?<") and head[3:4] not in (b"=", b"!") \
                or head.startswith(b"(?P<") or head.startswith(b"(?'")
            return quant(it)
        pos[0] += 1
        return quant(Item("lit", c))

    return alts(0)


def walk_kill(alts, enc, kill_caret, in_lb, st):
    for seq in alts:
        for it in seq:
            if it.kind == "gstart":
                if in_lb: st["unkillable_g"] = True
                else: it.kind, it.text = "never", NEVER[enc]; st["killed"] += 1; st["has_g"] = True
            elif it.kind in ("astart", "caret"):
                if kill_caret and not in_lb:
                    it.kind, it.text = "never", NEVER[enc]; st["killed"] += 1
            elif it.kind == "group":
                lb = in_lb or it.head in (b"(?<=", b"(?<!")
                walk_kill(it.alts, enc, kill_caret, lb, st)


def capped(it):
    if it.kind != "group": return False
    return it.hascap or any(capped(x) for s in it.alts for x in s)


def prune_alts(alts, st):
    """returns (alts, never). Drops never arms unless the arm holds a capture
    group (kept: text cannot preserve the group's number) or a flag setting."""
    keep, nev_all = [], True
    for seq in alts:
        nseq, nev = prune_seq(seq, st)
        if nev:
            if any(capped(x) or x.flagset for x in seq):
                st["keepcap"] += 1; keep.append(seq); continue
            st["pruned_arms"] += 1; continue
        nev_all = False; keep.append(nseq)
    if not keep:
        return alts, True
    return keep, nev_all and all(prune_seq(s, st)[1] for s in keep)


def prune_seq(seq, st):
    out, nev = [], False
    for it in seq:
        if it.kind == "group":
            if it.head in (b"(?=", b"(?!", b"(?<=", b"(?<!"):
                a, n = prune_alts(it.alts, st); it.alts = a
                if n and it.head == b"(?!": continue            # (?!never) = EMPTY
                if n and it.head == b"(?=": it.never = True
            elif it.head != b"(?(":
                a, n = prune_alts(it.alts, st); it.alts = a; it.never = n
        elif it.kind == "never":
            it.never = True
        if it.never:
            if it.qmin == 0: continue                            # REP{0,..} of never = EMPTY
            nev = True
        out.append(it)
    return out, nev


def render(alts):
    def r(it):
        if it.kind == "group":
            return it.head + b"|".join(b"".join(r(x) for x in s) for s in it.alts) + b")" + it.q
        return it.text + it.q
    return b"|".join(b"".join(r(x) for x in s) for s in alts)


def derive(p, enc):
    """P -> (Q text | None for never, has_g, reason): reason != None declines."""
    if any(t in p for t in DECLINE_TOKENS): return None, False, "verb-or-callout"
    if re.search(rb"\(\?[a-z-]*x", p): return None, False, "x-flag (twin parser)"
    kill_caret = re.search(rb"\(\?[a-zA-Z^-]*m", p) is None and b"(*" not in p.replace(b"(*UTF", b"").replace(b"(*UCP", b"")
    try:
        tree = parse(p)
    except Exception as e:
        return None, False, f"twin-parse:{e}"
    st = dict(killed=0, has_g=False, unkillable_g=False, keepcap=0, pruned_arms=0)
    walk_kill(tree, enc, kill_caret, False, st)
    if st["unkillable_g"]: return None, False, "unkillable-\\G"
    if st["killed"] == 0: return None, False, "nothing-killed (A2)"
    a, never = prune_alts(tree, st)
    return (None if never else render(a)), st["has_g"], f"ok killed={st['killed']} pruned={st['pruned_arms']} keepcap={st['keepcap']}"


def witness_bytes(p, enc):
    req = []
    for c in sorted(set(b for b in p if b >= 0x80)): req.append(bytes([c]))
    for m in re.finditer(rb"\\x\{([0-9a-fA-F]+)\}", p):
        cp = int(m.group(1), 16)
        if cp >= 0x80:
            req.append(chr(cp).encode("utf-8") if enc == "utf8" and cp < 0x110000 else bytes([cp & 0xff]))
    if enc == "utf8": req += [b"\xc3\xa9", b"\x80", b"\xc3", b"\xff"]
    out = []
    for r in req:
        if r not in out: out.append(r)
    return out[:5]


def subjects(p, enc):
    req = witness_bytes(p, enc)
    lits = sorted(set(ch for ch in p if 32 <= ch < 127 and chr(ch).isalnum()))[:3]
    alpha = list(req) + [b" ", b"\n"] + [bytes([c]) for c in lits] + [b"x"]
    if b"{" in p or b"\\s" in p: alpha += [b"{", b"}", b"\t"]
    seen = []
    for a in alpha:
        if a not in seen: seen.append(a)
    alpha = seen[:8]
    assert all(r in alpha for r in req), (p, req, alpha)       # chk M4: witness bytes present
    out = [b""]
    for L in range(1, 5):
        out += [b"".join(t) for t in itertools.product(alpha, repeat=L)]
    rnd = random.Random(1)
    for _ in range(300):
        out.append(b"".join(rnd.choice(alpha) for _ in range(rnd.randint(5, 24))))
    # chk M3: matches > 0 per ID needs subjects that reach the pattern's words
    # (concat-sqli's keywords never appear in a 7-letter alphabet)
    words = list(dict.fromkeys(re.findall(rb"[A-Za-z_]{3,}", re.sub(rb"\\[a-zA-Z]", b" ", p))))[:24]
    seps = [b" ", b"(", b";", b"\n", b"x", b"", b"'", b"/"]
    for _ in range(300 if words else 0):
        k = rnd.randint(1, 4)
        out.append(b"".join(rnd.choice(seps) + rnd.choice(words) for _ in range(k)) + rnd.choice(seps))
    for r in req:
        assert any(r in s for s in out), r
    return out


ARMS_BYTE = [("byte", [], 0, 0)]
ARMS_UTF8 = [(f"g{g}{'-uc' if uc else ''}", gf + (["-futf-check"] if uc else []), gi, uc)
             for g, gf, gi in (("refuse", [], 1), ("none", ["-fno-startpos-guard"], 0),
                               ("align", ["-fstartpos-guard=align"], 2))
             for uc in (0, 1)]


def run(cmd, **kw):
    return subprocess.run([GT, "300"] + cmd, capture_output=True, **kw)


def bound_floor(path):
    """F = P's attempt loop bounded to one start: the build's part option (a
    BOUND, start_max = search_from), done here by patching the emitted line.
    Returns 1 when patched, 0 when P has no DFA attempt loop (F then uses P's
    anchored entry)."""
    src = open(path, "rb").read()
    line = b"const size_t start_max = subject_length;"
    if src.count(line) != 1:
        return 0
    open(path, "wb").write(src.replace(line, b"const size_t start_max = search_from; /* [twin] F: one attempt */"))
    return 1


def stamp(path, pre, key):
    m = re.search(rb'#define ' + pre.upper().encode() + rb'_' + key.encode() + rb' "([\w-]+)"', open(path, "rb").read())
    return m.group(1).decode() if m else "-"


def case(pcrec, cid, enc, pat, wd):
    q, has_g, why = derive(pat, enc)
    if not why.startswith("ok"):
        return [f"{cid}\t{enc}\t-\tDECLINED\t{why}"]
    os.makedirs(wd, exist_ok=True)
    E = ["-e", "utf8"] if enc == "utf8" else []
    base = [pcrec, "--features", "all"] + E
    guardsoff = ["-fno-startpos-guard"] if enc == "utf8" else []
    for pre, name, text in (("rxf", "floor", pat),) + ((("rxq", "q", q),) if q is not None else ()):
        r = run(base + guardsoff + ["-p", pre, "-o", f"{wd}/{name}.c", "--pattern", text])
        if r.returncode:
            return [f"{cid}\t{enc}\t-\tREFUSED-{name}\t{r.stderr.decode(errors='replace').strip()[:120]}\tq={q!r}"]
    fmode = bound_floor(f"{wd}/floor.c")
    qst = "never" if q is None else stamp(f"{wd}/q.c", "rxq", "ENGINE") + "/" + stamp(f"{wd}/q.c", "rxq", "DFA_SCAN")
    subj = b"\n".join(s.hex().encode() for s in subjects(pat, enc)) + b"\n"
    rows = []
    for arm, aflags, gi, uc in (ARMS_UTF8 if enc == "utf8" else ARMS_BYTE):
        r = run(base + aflags + ["-p", "rxp", "-o", f"{wd}/plain.c", "--pattern", pat])
        if r.returncode:
            rows.append(f"{cid}\t{enc}\t{arm}\tREFUSED-plain\t{r.stderr.decode(errors='replace').strip()[:100]}"); continue
        pst = stamp(f"{wd}/plain.c", "rxp", "ENGINE") + "/" + stamp(f"{wd}/plain.c", "rxp", "DFA_SCAN")
        cc = ["gcc", "-O1", "-std=gnu11", "-w", f"-DUTF={1 if enc == 'utf8' else 0}", f"-DGUARD={gi}",
              f"-DUCHECK={uc}", f"-DHAS_G={1 if has_g else 0}", f"-DQNEVER={1 if q is None else 0}",
              f"-DFMODE={fmode}", "-I", wd, "-x", "c", "-o", f"{wd}/t", f"{HERE}/diff.c", f"{HERE}/ctrl2.c.in", f"{wd}/floor.c",
              f"{wd}/plain.c"] + ([f"{wd}/q.c"] if q is not None else []) + ["-lpcre2-8"]
        b = run(cc)
        if b.returncode:
            rows.append(f"{cid}\t{enc}\t{arm}\tBUILD-FAIL\t{b.stderr.decode(errors='replace').strip()[:200]}"); continue
        o = run([f"{wd}/t", pat.hex()], input=subj)
        rows.append(f"{cid}\t{enc}\t{arm}\tplain={pst}\tq={qst}\tf={'bounded' if fmode else 'anchored'}\t{why}\t{o.stdout.decode().strip()}")
    return rows


def main():
    pcrec, cases, out = sys.argv[1:4]
    for ln in open(cases):
        if not ln.strip() or ln.startswith("#"): continue
        f = ln.rstrip("\n").split("\t")
        cid, enc, pat = f[0], f[1], bytes.fromhex(f[2])
        for row in case(pcrec, cid, enc, pat, os.path.join(out, re.sub(r"[^\w.-]", "_", cid))):
            print(row, flush=True)


if __name__ == "__main__":
    main()
