"""X0, kit_proof.md §6.4: conj.py's reading against an INDEPENDENT libpcre2 oracle.

The reading is conj.py's (revision 2.1): the `cover_conj[]` verdict, and on a
`cover` artifact the plan (S_0..S_{k-1}, C_{-1} with absent-before, C_k with
absent-after) read off the emitted anchored machine by kvdfa. The oracle is
x0pcre (x0pcre.c), a libpcre2-8 server that knows no reading. Every set the
oracle produces is grown from PCRE2's own answers: the prefix tree is
explored through the bytes PCRE2 accepts, never through the reading's sets.

PART 1, per-position per-byte SET EQUALITY.
  On every admitted artifact: for d < k, every explored prefix node's next-byte
  set (all 256 bytes asked; under -e utf8 every byte that opens or continues a
  character is completed exhaustively over the code points it can begin) must
  EQUAL the reading's S_d (an under- or over-stated set, or a non-product
  language, fails at a node); no match may end below k (every tail tried);
  at k every full-length prefix x every context x every tail gives the
  anchored length k or no match, and the context / tail answers equal C_{-1}
  with absent-before and C_k with absent-after.
  On every start-origin FIND site of a non-admitted artifact whose reading
  states an exact prefix (the census site `exact` > 0, a machine reading):
  for d < exact, node sets equal the reading's S_d (the hull over contexts).
PART 2, the DIFFERENTIAL (coversim's shape): the cover entry simulated from
  the reading's plan against pcre2_match at EVERY startoffset and through the
  find-all loop, on subjects from the whole alphabet, set-edge-adjacent
  bytes, the pattern's literals and PCRE2's own full-length prefixes, each
  literal path at the subject end alone and after every byte, c = 0,
  c + k = n, two matches, ill-formed utf8.

usage (from the repo root, build/pcrec and build/x0/x0pcre built):
  python3 -I docs/design/kit_proof/x0/x0.py pop OUT.jsonl            # the population
  python3 -I docs/design/kit_proof/x0/x0.py run POP.jsonl RES.jsonl [-j N] [--plant P] [--self P]
  python3 -I docs/design/kit_proof/x0/x0.py summary RES.jsonl
  python3 -I docs/design/kit_proof/x0/x0.py stated STATED.tsv        # S1150: stated sets
  python3 -I docs/design/kit_proof/x0/x0.py plantpop POP.jsonl PREFIX  # each plant's movers
Env: PCREC (build/pcrec), X0PCRE (build/x0/x0pcre), CONJ_PLANT (conj.py's plants).
"""
import collections, gzip, json, os, random, re, subprocess, sys, time

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, os.path.join(HERE, ".."))
sys.path.insert(0, os.path.join(HERE, "..", "..", "..", "dev", "kvcensus"))
import conj   # noqa: E402
import kvdfa  # noqa: E402

ORACLE = os.environ.get("X0PCRE", "build/x0/x0pcre")
KV = os.path.join(HERE, "..", "..", "..", "dev", "kvcensus")
LANGF = ["--engine=dfa", "--no-captures"]

# exploration caps (nodes kept per depth); the oracle's own sets choose them
CAP_NATIVE, CAP_UTF8, CAP_CTX = 64, 16, 6
NW = 12           # full-length prefixes carried into the context/tail grid
SITE_BUDGET = 20000   # per byte on a site, whose witnesses may be long (unknown past it)
NCTX_EXTRA = 6    # further live contexts whose prefix tree is explored


# ---------------------------------------------------------------- the oracle
class Oracle:
    def __init__(self):
        self.p = subprocess.Popen([ORACLE], stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                  text=True, bufsize=1 << 16)
        self.calls = 0

    def q(self, *f):
        self.calls += 1
        self.p.stdin.write("\t".join(f) + "\n")
        self.p.stdin.flush()
        return self.p.stdout.readline().rstrip("\n")

    def version(self):
        return self.q("V")

    def compile(self, fl, pat):
        f = ("i" if "i" in fl else "") + ("u" if "u" in fl else "") or "-"
        return self.q("P", f, pat.hex()) == "ok"

    def nxt(self, ctx, w):
        """hard-partial next set (an over-approximation: kept for the record)"""
        h = bytes.fromhex(self.q("N", (ctx or b"").hex(), w.hex()))
        return frozenset(b for b in range(256) if h[b >> 3] >> (b & 7) & 1)

    def qnext(self, ctx, w, H, open_h=False, budget=200000):
        """the VALIDATED next set: bytes with a complete-match witness covering
        W·b within H more bytes (from w), and the UNKNOWN bytes (budget out; with
        open_h also the horizon reached with no witness)"""
        a, u = self.q("Q", (ctx or b"").hex(), w.hex(), str(max(1, H)), str(budget),
                      "u" if open_h else "-").split()
        a, u = bytes.fromhex(a), bytes.fromhex(u)
        bit = lambda h: frozenset(b for b in range(256) if h[b >> 3] >> (b & 7) & 1)
        return bit(a), bit(u)

    def skips(self):
        return int(self.q("K"))

    def tails(self, ctx, w, tails):
        r = self.q("T", (ctx or b"").hex(), w.hex(), ",".join(t.hex() for t in tails))
        return [int(x) for x in r.split(",")]

    def search(self, s):
        a, b = self.q("F", s.hex()).split("|")
        def one(x):
            if x == "-":
                return None
            if x.startswith("e"):
                return x
            u, v = x.split(":")
            return (int(u), int(v))
        return [one(x) for x in a.split(",")], [one(x) for x in b.split(",") if x]

    def close(self):
        self.p.stdin.close()
        self.p.wait()


# ------------------------------------------------------------ the alphabets
def enc(c):
    return chr(c).encode("utf-8", "surrogatepass")


LEADS = {}
for _L in range(0xC2, 0xF5):
    if _L < 0xE0:
        _lo = (_L & 0x1F) << 6; _hi = _lo + 63
    elif _L < 0xF0:
        _lo = max(0x800, (_L & 0x0F) << 12); _hi = ((_L & 0x0F) << 12) + 0xFFF
    else:
        _lo = max(0x10000, (_L & 0x07) << 18); _hi = min(0x10FFFF, ((_L & 0x07) << 18) + 0x3FFFF)
    LEADS[_L] = (_lo, _hi)


def contexts(utf):
    """None = the subject starts at the origin (absent-before)."""
    if not utf:
        return [None] + [bytes([b]) for b in range(256)]
    out = [None] + [bytes([b]) for b in range(128)]
    for b in range(0x80, 0xC0):
        out += [bytes([0xC3, b]), bytes([0xE2, 0x80, b]), bytes([0xF0, 0x9F, 0x98, b]), bytes([b])]
    out += [bytes([b]) for b in range(0xC0, 0x100)]
    return out


def tails(utf):
    """b"" = the subject ends at the end (absent-after)."""
    t = [b""] + [bytes([b]) for b in range(256)]
    if utf:
        for L, (lo, hi) in LEADS.items():
            mid = (lo + hi) // 2
            if 0xD800 <= mid <= 0xDFFF:
                mid = 0xE000
            t += [enc(lo), enc(mid), enc(hi)]
    return t


def last(ctx):
    return "absent" if ctx is None else ctx[-1]


def edges(S):
    """bytes adjacent to each edge of the set S (both sides)"""
    out = set()
    for b in S:
        for x in (b - 1, b + 1):
            if 0 <= x < 256 and x not in S:
                out.add(x)
                out.add(b)
    return out


def pick(S, n, rnd, extra=()):
    """a sample of the set S: its edges, min, max, extra members, then random"""
    S = sorted(S)
    if len(S) <= n:
        return S
    keep = {S[0], S[-1]} | (set(extra) & set(S)) | (edges(set(S)) & set(S))
    keep = sorted(keep)
    if len(keep) > n:
        keep = [keep[0], keep[-1]] + rnd.sample(keep[1:-1], n - 2)
    rest = [b for b in S if b not in keep]
    return sorted(set(keep) | set(rnd.sample(rest, min(len(rest), max(0, n - len(keep))))))


# ---------------------------------------------------------- the reading
def reading(pat, fl):
    """conj.py's verdict; on cover, its plan. Also the census-site reading: the
    hull over contexts off A (A.starts()), its exact prefix and span."""
    why, st = conj.verdict(pat.decode("latin-1"), fl)
    out = dict(why=why)
    if why == "cover":
        out["plan"] = dict(S=[sorted(x) for x in st["L"]["S"]], k=st["k"], Cm1=sorted(st["Cm1"]),
                           absB=st["absB"], Ck=sorted(st["Ck"]), absA=st["absA"])
    return out, st


def site_reading(pat, fl):
    """the machine reading a non-cover start-origin site states: kvdfa.lang over
    A.starts() (every context), as kvcensus read it; the compile the census used
    (default, else --engine=dfa --no-captures)"""
    for extra in ([], LANGF):
        a = [conj.PCREC, "-p", "rx", "--features", "all", "-fno-scan-edge"] + extra
        if "i" in fl: a.append("-i")
        if "u" in fl: a += ["-e", "utf8"]
        if "R" in fl: a.append("-fno-rev-end")
        argv = [os.fsencode(x) for x in ["nice", "-n", "19", "gnutimeout", "30"] + a + ["-o", "-", "--pattern"]] + [pat]
        p = subprocess.run(argv, capture_output=True)
        if p.returncode != 0:
            continue
        A = conj.machine(p.stdout.decode("latin-1"))
        if A.ok:
            L = kvdfa.lang(A, A.starts())
            return dict(S=[sorted(x) for x in L["S"]], exact=L["exact"], span=L["span"],
                        seeded=A.seeded, src="N" if not extra else "D")
    return None


# ------------------------------------------------------------ part 1
class P1:
    def __init__(self):
        self.nodes = 0
        self.cells = 0
        self.unknown = 0
        self.bad = []

    def miss(self, kind, **kw):
        if len(self.bad) < 40:
            kw = {k: (v.hex() if isinstance(v, bytes) else sorted(v) if isinstance(v, (set, frozenset)) else v)
                  for k, v in kw.items()}
            self.bad.append(dict(kind=kind, **kw))
        else:
            self.bad.append(dict(kind=kind))


def explore(O, ctxs, depth, cap, rnd, utf, want=None, r1=None, tl=None, kmin=None, extra=(), horizon=None,
            open_h=False, budget=200000):
    """the PCRE2 prefix tree from the origin, grown through PCRE2's own VALIDATED
    next sets (the union over `ctxs`), `depth` levels; a byte's witness may end
    within `horizon` bytes of the origin (default `depth`). `want[d]` is the
    reading's S_d: every node at depth d must have exactly that next set (r1
    records misses; a budget-out byte is INCONCLUSIVE, compared on neither side).
    With `tl`/`kmin`: no match may end below kmin at any node (every tail tried).
    -> (levels: [[(w, set)]], full: the depth-`depth` strings)"""
    level = [b""]
    levels = []
    hz = depth if horizon is None else horizon
    for d in range(depth):
        row = []
        for w in level:
            N, U = frozenset(), frozenset()
            for c in ctxs:
                a, u = O.qnext(c, w, hz - d, open_h, budget)
                N, U = N | a, U | u
            U = U - N
            row.append((w, N))
            if r1 is not None:
                r1.nodes += 1
                r1.unknown += len(U)
                if want is not None and (N - U) != (want[d] - U):
                    # under: bytes PCRE2 allows that the reading lacks (a lost
                    # match); over: bytes the reading states that PCRE2 refuses
                    r1.miss("S_d", d=d, ctx=None if len(ctxs) != 1 else ctxs[0], node=w,
                            under=sorted(N - want[d] - U), over=sorted(want[d] - N - U))
                if tl is not None:
                    for c in ctxs:
                        ls = O.tails(c, w, tl)
                        r1.cells += len(ls)
                        if any(0 <= L < kmin for L in ls):
                            t = tl[next(i for i, L in enumerate(ls) if 0 <= L < kmin)]
                            r1.miss("accept<k", d=d, ctx=c, node=w, tail=t,
                                    len=min(L for L in ls if 0 <= L < kmin))
        levels.append(row)
        kids = []
        per = max(1, cap // max(1, len(row)))
        for w, N in row:
            for b in pick(N, per + 2, rnd, extra):
                kids.append(w + bytes([b]))
        if len(kids) > cap:
            keep = set(kids[:1] + kids[-1:])
            kids = sorted(keep | set(rnd.sample(kids, cap - len(keep))))
        level = kids
        if not level:
            break
    return levels, level


def part1_cover(O, plan, utf, rnd, lits):
    r1 = P1()
    k, S = plan["k"], [frozenset(x) for x in plan["S"]]
    Cm1, Ck = frozenset(plan["Cm1"]), frozenset(plan["Ck"])
    CT, TL = contexts(utf), tails(utf)
    cap = CAP_UTF8 if utf else CAP_NATIVE
    # ctx0: absent if PCRE2 lets a match begin there, else the first context
    # that does (PCRE2's own answer, not the reading's C_{-1})
    ctx0 = None
    for c in CT:
        if O.qnext(c, b"", k)[0]:
            ctx0 = c
            break
    else:
        r1.miss("no-match-anywhere")
        return r1, [], []
    levels, full = explore(O, [ctx0], k, cap, rnd, utf, want=S, r1=r1, tl=TL, kmin=k, extra=lits)
    if len(levels) < k:
        r1.miss("tree-ends", depth=len(levels))
    W = sorted(set(full))
    if len(W) > NW:
        W = sorted(set([W[0], W[-1]] + rnd.sample(W[1:-1], NW - 2)))
    if not W:
        r1.miss("no-full-prefix")
        return r1, levels, W
    # C10's libpcre2 side: no match runs past k. After a full-length prefix
    # PCRE2's VALIDATED next set must be empty (a byte with a witness is a
    # longer match; a context byte after k is not covered, so it is not one)
    for w in W:
        a, u = O.qnext(ctx0, w, 6, True, SITE_BUDGET)
        r1.nodes += 1
        if a:
            r1.miss("longer-than-k", ctx=ctx0, node=w, bytes=sorted(a)[:8])
    # the context x tail grid at k
    live = {}
    for c in CT:
        seen = None
        for w in W:
            ls = O.tails(c, w, TL)
            r1.cells += len(ls)
            bad = [(TL[i], L) for i, L in enumerate(ls) if L not in (-1, k)]
            if bad:
                r1.miss("end-not-k", ctx=c, node=w, tail=bad[0][0], len=bad[0][1])
            byfirst = collections.defaultdict(set)
            for i, L in enumerate(ls[1:], 1):
                byfirst[TL[i][0]].add(L == k)
            ck = frozenset(b for b, v in byfirst.items() if True in v)
            mixed = sorted(b for b, v in byfirst.items() if len(v) > 1)
            if mixed:
                r1.miss("C_k-not-byte", ctx=c, node=w, bytes=mixed[:8])
            sig = (ck, ls[0] == k)
            if seen is None:
                seen = sig
            elif sig != seen:
                r1.miss("context-x-prefix", ctx=c, node=w)
        islive = bool(seen[0]) or seen[1]
        live[c] = islive
        want_live = plan["absB"] if c is None else c[-1] in Cm1
        if islive != want_live:
            r1.miss("C_-1" if c is not None else "absent-before", ctx=c, pcre=islive, reading=want_live)
        elif islive:
            if seen[0] != Ck:
                r1.miss("C_k", ctx=c, pcre=seen[0], reading=Ck)
            if seen[1] != plan["absA"]:
                r1.miss("absent-after", ctx=c, pcre=seen[1], reading=plan["absA"])
    # last bytes reached by several contexts (utf8) must agree
    bylast = collections.defaultdict(set)
    for c, v in live.items():
        bylast[last(c)].add(v)
    for b, v in bylast.items():
        if len(v) > 1:
            r1.miss("C_-1-not-byte", byte=b)
    # the prefix tree again under further live contexts (PCRE2-live)
    others = [c for c in CT if live.get(c) and c != ctx0]
    for c in sorted(set(([others[0], others[-1]] if others else []) +
                        rnd.sample(others, min(len(others), NCTX_EXTRA - 2))), key=lambda x: (x is not None, x or b"")):
        explore(O, [c], k, CAP_CTX, rnd, utf, want=S, r1=r1)
    return r1, levels, W


def part1_site(O, rd, utf, rnd, absent=True):
    """d < exact on a non-cover site: node sets equal the reading's hull S_d.
    absent=False leaves the subject start out of the contexts (a statement made
    only past the floor, z2's split-part statements)"""
    r1 = P1()
    ex = min(rd["exact"], len(rd["S"]))
    S = [frozenset(x) for x in rd["S"]]
    CT = contexts(utf) if absent else contexts(utf)[1:]
    if rd["seeded"]:
        if utf:
            ctxs = [None] * absent + [bytes([b]) for b in range(128)] + \
                   [b"\xc3\xa9", b"\xe2\x80\x94", b"\xf0\x9f\x98\x80", b"\x80", b"\xff"]
            cap = 2
        else:
            ctxs, cap = CT, 8
        explore(O, ctxs, ex, cap, rnd, utf, want=S, r1=r1, horizon=ex + 8, open_h=True, budget=SITE_BUDGET)
    else:
        # the reading claims a context-free language: the same sets under each
        # of several contexts, one at a time
        cap = CAP_UTF8 if utf else CAP_NATIVE
        if absent:
            explore(O, [None], ex, cap, rnd, utf, want=S, r1=r1, horizon=ex + 8, open_h=True, budget=SITE_BUDGET)
        for c in rnd.sample(contexts(utf)[1:], 4):
            explore(O, [c], ex, CAP_CTX, rnd, utf, want=S, r1=r1, horizon=ex + 8, open_h=True, budget=SITE_BUDGET)
    return r1


# ------------------------------------------------------------ part 2
def cover_search(plan, s, sf, kplus=0):
    S, k, n = plan["_S"], plan["k"], len(s)
    for c in range(sf, n - k + 1):
        if all(s[c + i] in S[i] for i in range(k)):
            if c == 0:
                if not plan["absB"]:
                    continue
            elif s[c - 1] not in plan["_Cm1"]:
                continue
            if c + k == n:
                if not plan["absA"]:
                    continue
            elif s[c + k] not in plan["_Ck"]:
                continue
            return (c, c + k + kplus)
    return None


ILL = [b"\xff", b"\xc0", b"\x80", b"\xe2\x82", b"\xed\xa0\x80", b"\xf4\x90\x80\x80", b"\xc3",
       b"\xc0\xaf", b"\xf8\x88\x80\x80\x80"]
MB = [b"\xc3\xa9", b"\xe2\x82\xac", b"\xf0\x9f\x98\x80", b"\xc2\xa0", b"\xe2\x80\x8b"]


def text_literals(pat):
    """literal paths of the pattern text: each top-level branch with its
    zero-width items dropped and simple escapes decoded, when what is left is
    a plain literal; plus coversim's literal runs"""
    out = set()
    for br in re.split(rb"(?<!\\)\|", pat):
        b = re.sub(rb"\(\?<?[=!][^)]*\)|\\[bBzZAG]|[$^]|\(\?[a-z]+\)", b"", br)
        b = b.replace(b"(?:", b"").replace(b"(", b"").replace(b")", b"")
        dec, i, ok = bytearray(), 0, True
        while i < len(b):
            ch = b[i:i + 1]
            if ch == b"\\" and i + 1 < len(b):
                e = b[i + 1:i + 2]
                m = {b"n": 10, b"t": 9, b"r": 13, b"f": 12, b"e": 27, b"a": 7}
                if e in m:
                    dec.append(m[e]); i += 2; continue
                if e == b"x" and re.match(rb"[0-9a-fA-F]{2}", b[i + 2:i + 4]):
                    dec.append(int(b[i + 2:i + 4], 16)); i += 4; continue
                if not e.isalnum():
                    dec += e; i += 2; continue
                ok = False; break
            if ch in b"[]{}*+?.":
                ok = False; break
            dec += ch; i += 1
        if ok and dec:
            out.add(bytes(dec))
    out |= set(re.findall(rb"[A-Za-z0-9/._ -]+", pat))
    return sorted(out)[:12]


def subjects(plan, utf, rnd, W, levels, lits, pat):
    k, S = plan["k"], plan["_S"]
    sub = []
    allb = [bytes([b]) for b in range(256)]
    W = W or []
    for j, w in enumerate(W):
        sub.append(w)
        for t in (allb if j < 2 else rnd.sample(allb, 24)):
            sub.append(w + t)
            sub.append(t + w)
        for _ in range(12):
            sub.append(rnd.choice(allb) + w + rnd.choice(allb))
        sub += [w + w, w + rnd.choice(allb) + w, w[:-1] + w, w + w[1:]]
        if j < 2:
            # a match running past k: every byte after w, then an after-context byte
            for c in sorted(set(plan["Ck"][:2]) | {plan["Ck"][-1]} if plan["Ck"] else set()):
                for t in allb:
                    sub.append(w + t + bytes([c]))
    # each literal path at the subject end, alone and after every byte
    paths = sorted(set(lits) | set(W[:4]))
    for j, p in enumerate(paths):
        sub.append(p)
        for t in (allb if j < 6 else rnd.sample(allb, 32)):
            sub.append(t + p)
        sub.append(p + b"\n")
    # set-edge-adjacent bytes at every position of a full prefix (PCRE2's sets)
    if W:
        w0 = W[0]
        for d, row in enumerate(levels[:k]):
            Nd = frozenset().union(*(N for _, N in row)) if row else frozenset()
            for x in sorted(edges(set(Nd)) | {0, 255, 0x7F, 0x80}):
                v = w0[:d] + bytes([x]) + w0[d + 1:]
                sub += [v, b"x" + v, v + b"x"]
    # random (coversim's shape) with whole-alphabet noise
    al = set(pat) | {ord(x) for x in "a_ Z9-\n."}
    for st in S:
        al |= set(st) if len(st) < 12 else set(rnd.sample(sorted(st), 12))
    al |= set(rnd.sample(range(256), 12))
    al = sorted(al)
    for _ in range(150):
        n = rnd.randrange(0, 10)
        s = bytearray(rnd.choice(al) for _ in range(n))
        if W and rnd.random() < 0.7:
            p = rnd.randrange(n + 1)
            s[p:p] = rnd.choice(W)
        if rnd.random() < 0.5:
            s = bytearray(rnd.randrange(256) for _ in range(rnd.randrange(4))) + s
        sub.append(bytes(s))
    if utf and W:
        for w in W[:3]:
            for x in ILL + MB:
                sub += [x + w, w + x, x + w + x, w[:1] + x + w[1:]]
    seen, out = set(), []
    for s in sub:
        if s not in seen:
            seen.add(s)
            out.append(s)
    return out


def part2(O, plan, utf, subj, kplus=0):
    cells = bad = 0
    first = []
    for s in subj:
        ps, fa_p = O.search(s)
        for sf in range(len(s) + 1):
            if utf and sf < len(s) and 0x80 <= s[sf] < 0xC0:
                continue   # the K50 guard refuses a mid-character startoffset first
            a = cover_search(plan, s, sf, kplus)
            b = ps[sf]
            cells += 1
            if a != b:
                bad += 1
                if len(first) < 6:
                    first.append(dict(s=s.hex(), sf=sf, cover=a, pcre=b))
        pos, fa = 0, []
        while pos <= len(s):
            m = cover_search(plan, s, pos, kplus)
            if not m:
                break
            fa.append(m)
            pos = m[1] if m[1] > m[0] else m[1] + 1
        cells += 1
        if fa != fa_p:
            bad += 1
            if len(first) < 6:
                first.append(dict(s=s.hex(), sf="findall", cover=fa, pcre=fa_p))
    return cells, bad, first


# ------------------------------------------------------------ one item
SELF_PLANTS = ("under-S", "over-S", "drop-Ck", "flip-absA", "k-plus-1", "add-Cm1")


def apply_self(plan, sp, rnd):
    """X0-side plants: mutate the reading's plan so X0 must go red"""
    plan = json.loads(json.dumps(plan))
    k = plan["k"]
    if sp == "under-S":
        d = k - 1
        if plan["S"][d]:
            plan["S"][d] = plan["S"][d][:-1]
    elif sp == "over-S":
        out = [b for b in range(256) if b not in plan["S"][0]]
        if out:
            plan["S"][0] = sorted(plan["S"][0] + [out[len(out) // 2]])
    elif sp == "drop-Ck":
        if plan["Ck"]:
            plan["Ck"] = plan["Ck"][1:]
    elif sp == "flip-absA":
        plan["absA"] = not plan["absA"]
    elif sp == "add-Cm1":
        out = [b for b in range(256) if b not in plan["Cm1"]]
        if out:
            plan["Cm1"] = sorted(plan["Cm1"] + [out[len(out) // 2]])
    return plan


def run_item(it, O, selfp=None):
    t0 = time.time()
    pat, fl = bytes.fromhex(it["pat"]), it["fl"]
    utf = "u" in fl
    rnd = random.Random(hash((it["pat"], fl)) & 0xffffffff)
    res = dict(fl=fl, pat=it["pat"], role=it["role"])
    if not O.compile(fl, pat):
        res["why"] = "pcre-refused"
        return res
    lits = text_literals(pat)
    litb = set(b for l in lits for b in l)
    if it["role"] == "site":
        rd = site_reading(pat, fl)
        if rd is None or rd["exact"] == 0:
            res["why"] = "no-exact-now"
            return res
        r1 = part1_site(O, rd, utf, rnd)
        res.update(why="site", exact=rd["exact"], seeded=rd["seeded"], src=rd["src"],
                   p1=dict(nodes=r1.nodes, cells=r1.cells, unk=r1.unknown, bad=len(r1.bad), e=r1.bad[:8]))
    else:
        rd, st = reading(pat, fl)
        res["why"] = rd["why"]
        if rd["why"] != "cover":
            # the set equality reads a witness whatever cover decides: d < the
            # machine's exact prefix, when A is built
            A = st.get("A") if st else None
            if it["role"] == "witness" and A is not None and A.ok:
                L = kvdfa.lang(A, A.starts())
                if L["exact"] > 0:
                    r1 = part1_site(O, dict(S=[sorted(x) for x in L["S"]], exact=L["exact"],
                                            span=L["span"], seeded=A.seeded), utf, rnd)
                    res.update(exact=L["exact"], p1=dict(nodes=r1.nodes, cells=r1.cells, unk=r1.unknown,
                                                         bad=len(r1.bad), e=r1.bad[:8]))
            return res
        plan = rd["plan"]
        if selfp:
            plan = apply_self(plan, selfp, rnd)
        res["k"] = plan["k"]
        r1, levels, W = part1_cover(O, plan, utf, rnd, litb)
        res["p1"] = dict(nodes=r1.nodes, cells=r1.cells, unk=r1.unknown, bad=len(r1.bad), e=r1.bad[:8])
        plan["_S"] = [frozenset(x) for x in plan["S"]]
        plan["_Cm1"], plan["_Ck"] = frozenset(plan["Cm1"]), frozenset(plan["Ck"])
        subj = subjects(plan, utf, rnd, W, levels, lits, pat)
        cells, bad, first = part2(O, plan, utf, subj, 1 if selfp == "k-plus-1" else 0)
        res["p2"] = dict(subjects=len(subj), cells=cells, bad=bad, e=first)
    res["sec"] = round(time.time() - t0, 2)
    res["skips"] = O.skips()
    return res


# ------------------------------------------------------------ the population
def population(out_path):
    """B: every census whole-cover / context-join pattern (conj.py census B), at
    its flags and again under -fno-rev-end where the verdict or the plan moves;
    out: every other census DFA pattern the table admits at its own flags;
    R: every census DFA pattern whose -fno-rev-end verdict is cover; sites:
    every start-origin FIND site with a machine-read exact prefix whose pattern
    is not admitted; witnesses: witnesses.txt."""
    pats = [json.loads(l) for l in gzip.open(os.path.join(KV, "patterns.tsv.gz"), "rt")]
    sites = [json.loads(l) for l in gzip.open(os.path.join(KV, "sites.tsv.gz"), "rt")]
    byk = {(p["pop"], p["id"], p["cfg"]): p for p in pats}
    flags = lambda p: ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
    items = {}

    def add(fl, pat, role):
        key = (fl, pat)
        if key not in items:
            items[key] = dict(fl=fl, pat=pat, role=role)
    jobs = []
    for p in pats:
        src = p.get("whole") or (p.get("ctx_whole") and p.get("ctx_expr") == 1)
        if src:
            jobs.append((flags(p) or "-", p["pat"], "B"))
        if p.get("engine") == "dfa":
            jobs.append((flags(p) + "R", p["pat"], "R"))
            jobs.append((flags(p) or "-", p["pat"], "A"))
    for s in sites:
        if s.get("origin") == "start" and s.get("op") == "FIND" and s.get("exact", 0) > 0:
            p = byk[(s["pop"], s["id"], s["cfg"])]
            if p.get("lang_src") in ("N", "D"):
                jobs.append((flags(p) or "-", p["pat"], "site"))
    jobs = sorted(set(jobs))
    from multiprocessing import Pool
    with Pool(int(os.environ.get("X0J", "8"))) as pool:
        verd = pool.map(_verdict, [(fl, pat) for fl, pat, _ in jobs], chunksize=8)
    v = dict(zip([(fl, pat) for fl, pat, _ in jobs], verd))
    admitted = set()
    for (fl, pat, role) in jobs:
        if role == "B" and v[(fl, pat)][0] == "cover":
            add(fl, pat, "admitted"); admitted.add((fl.replace("R", ""), pat))
    for (fl, pat, role) in jobs:
        if role == "R" and v[(fl, pat)][0] == "cover":
            base = fl.replace("R", "") or "-"
            if (base, pat) not in admitted or v.get((base, pat), (None, None))[1] != v[(fl, pat)][1]:
                if (base, pat) in admitted:
                    # admitted both ways: the R arm only where the plan moves
                    b = _verdict((base, pat))
                    if b[1] == v[(fl, pat)][1]:
                        continue
                add(fl, pat, "admitted-R")
    # K35: what the table admits OUTSIDE the census whole-cover / context-join
    # population (kit_proof §1.2 counts only inside it)
    for (fl, pat, role) in jobs:
        if role == "A" and v[(fl, pat)][0] == "cover" and (fl, pat) not in admitted:
            add(fl, pat, "admitted-out"); admitted.add((fl, pat))
    for (fl, pat, role) in jobs:
        if role == "site" and (fl, pat) not in admitted:
            add(fl, pat, "site")
    for ln in open(os.path.join(HERE, "..", "witnesses.txt")):
        ln = ln.rstrip("\n")
        if ln and not ln.startswith("#"):
            fl, pat = ln.split("\t", 1)
            items[(fl, "W" + pat)] = dict(fl=fl, pat=pat.encode("latin-1").hex(), role="witness")
    with open(out_path, "w") as f:
        for it in items.values():
            f.write(json.dumps(it) + "\n")
    c = collections.Counter((it["role"], "u" in it["fl"]) for it in items.values())
    for k2, n in sorted(c.items(), key=str):
        print("pop", k2[0], "utf8" if k2[1] else "native", n)


def _verdict(a):
    fl, pat = a
    rd, _ = reading(bytes.fromhex(pat), fl)
    return rd["why"], json.dumps(rd.get("plan"), sort_keys=True)


PLANTS = ("cm1-all", "c8-skip", "c9-depth-k", "c9-eol-as-end", "e0-row0", "c10-drop", "absb-flip", "absa-flip")
# conj.py's `plain-walk` (X0's R2) moves no verdict, only a site's sets: it is
# run on the site role directly, not through plantpop


def _plant_verdicts(a):
    """one compile, the table walked under no plant and under each plant"""
    fl, pat = a
    c = conj.compile_c(bytes.fromhex(pat).decode("latin-1"), fl)
    out = {}
    for P in ("",) + PLANTS:
        conj.PLANT = P
        why, st = "refused", None
        if c is not None:
            st = dict(c=c, fl=fl)
            why = "cover"
            for cid, _, fn in conj.COVER_CONJ:
                if not fn(st):
                    why = cid
                    break
        plan = None
        if why == "cover":
            plan = json.dumps([[sorted(x) for x in st["L"]["S"]], sorted(st["Cm1"]), st["absB"],
                               sorted(st["Ck"]), st["absA"]])
        out[P] = (why, plan)
    conj.PLANT = ""
    return out


def plantpop(pop_path, prefix):
    """per plant: every population pattern (admitted, admitted-R, and every
    census B / R-arm pattern) whose verdict or plan MOVES under the plant, plus
    the witnesses; written to PREFIX<plant>.jsonl"""
    pats = [json.loads(l) for l in gzip.open(os.path.join(KV, "patterns.tsv.gz"), "rt")]
    flags = lambda p: ("i" if p.get("icase") else "") + ("u" if p.get("enc") == "utf8" else "")
    jobs = set()
    for p in pats:
        if p.get("whole") or (p.get("ctx_whole") and p.get("ctx_expr") == 1):
            jobs.add((flags(p) or "-", p["pat"]))
        if p.get("engine") == "dfa":
            jobs.add((flags(p) + "R", p["pat"]))
    wit = [json.loads(l) for l in open(pop_path) if '"witness"' in l]
    jobs = sorted(jobs)
    from multiprocessing import Pool
    with Pool(int(os.environ.get("X0J", "8"))) as pool:
        vs = pool.map(_plant_verdicts, jobs, chunksize=16)
    for P in PLANTS:
        n = 0
        with open(prefix + P + ".jsonl", "w") as f:
            for (fl, pat), v in zip(jobs, vs):
                if v[P] != v[""] and v[P][0] == "cover":
                    f.write(json.dumps(dict(fl=fl, pat=pat, role="mover")) + "\n")
                    n += 1
            for it in wit:
                f.write(json.dumps(it) + "\n")
        print("plantpop", P, "movers", n, "witnesses", len(wit))


# ------------------------------------------------------------ driver
_O = None


def _init():
    global _O
    _O = Oracle()
    conj.PLANT = os.environ.get("CONJ_PLANT", "")


def _work(a):
    it, selfp = a
    try:
        return run_item(it, _O, selfp)
    except Exception as e:  # an instrument failure is a result, never silence
        return dict(fl=it["fl"], pat=it["pat"], role=it["role"], why="X0-ERROR", err=repr(e)[:300])


def run(pop_path, res_path, j, selfp=None, only=None):
    items = [json.loads(l) for l in open(pop_path)]
    if only:
        items = [it for it in items if it["role"] in only]
    O = Oracle()
    ver = O.version()
    O.close()
    from multiprocessing import Pool
    t0 = time.time()
    with Pool(j, initializer=_init) as pool, open(res_path, "w") as f:
        f.write(json.dumps(dict(header=True, pcre2=ver, plant=conj.PLANT, self=selfp, n=len(items),
                                pcrec=conj.PCREC)) + "\n")
        for i, r in enumerate(pool.imap_unordered(_work, [(it, selfp) for it in items], chunksize=1)):
            f.write(json.dumps(r) + "\n")
            f.flush()
    with open(res_path, "a") as f:
        f.write(json.dumps(dict(trailer=True, n=len(items), sec=round(time.time() - t0, 1))) + "\n")
    summary(res_path)


def u1_shape(pat):
    return re.search(rb"\{0(,0)?\}", pat) is not None


def summary(res_path):
    rows = [json.loads(l) for l in open(res_path)]
    hdr = rows[0]
    tr = rows[-1] if rows[-1].get("trailer") else None
    rows = [r for r in rows if "fl" in r]
    print("## X0 %s  pcre2=%s plant=%r self=%r items=%d%s" % (
        res_path, hdr.get("pcre2"), hdr.get("plant"), hdr.get("self"), hdr.get("n"),
        "" if tr else "  (NO TRAILER: incomplete)"))
    agg = collections.defaultdict(collections.Counter)
    red = collections.defaultdict(list)
    for r in rows:
        key = (r["role"], "utf8" if "u" in r["fl"] else "native")
        a = agg[key]
        a["items"] += 1
        a["why:" + r.get("why", "?")] += 1
        if "p1" in r:
            a["p1_nodes"] += r["p1"]["nodes"]; a["p1_cells"] += r["p1"]["cells"]
            a["p1_unknown"] += r["p1"].get("unk", 0)
            if r["p1"]["bad"]:
                a["p1_red"] += 1
                for e in r["p1"]["e"]:
                    a["p1:" + e["kind"]] += 1
        if "p2" in r:
            a["p2_subjects"] += r["p2"]["subjects"]; a["p2_cells"] += r["p2"]["cells"]
            a["p2_diff"] += r["p2"]["bad"]
            if r["p2"]["bad"]:
                a["p2_red"] += 1
        if (r.get("p1", {}).get("bad") or r.get("p2", {}).get("bad")):
            u1 = u1_shape(bytes.fromhex(r["pat"]))
            a["red_u1shape" if u1 else "red_other"] += 1
            red[key].append(r)
        if r.get("why") == "X0-ERROR":
            red[key].append(r)
    for key in sorted(agg):
        print("agg", *key, " ".join("%s=%d" % kv for kv in sorted(agg[key].items())))
    for key in sorted(red):
        for r in red[key][:30]:
            pat = bytes.fromhex(r["pat"])
            print("red", *key, r["fl"], repr(pat)[:60], r.get("why"), "p1=%s" % r.get("p1", {}).get("bad"),
                  "p2=%s" % r.get("p2", {}).get("bad"), "u1shape" if u1_shape(pat) else "",
                  json.dumps((r.get("p1", {}).get("e") or [None])[0])[:300],
                  json.dumps((r.get("p2", {}).get("e") or [None])[0])[:300], r.get("err", ""))
    if tr:
        print("== X0 run COMPLETE: items=%d sec=%s" % (tr["n"], tr["sec"]))


def stated(path):
    """S1150's check: STATED sets (a producer's statement, here the union-
    narrowing plant's and the correct per-thread slice's, ctx_span.md §3.8)
    against libpcre2. Each line: FLAGS TAB PATTERN TAB EXACT_LEN TAB S_0;S_1;..
    (sets as hex byte lists, comma-separated). HULL: PCRE2's set at every stated
    position must lie inside the stated set (an under-stated SENT set lets a
    filter skip a match); EXACT: d < exact_len, every node set equals it."""
    O = Oracle()
    print("## stated sets against %s" % O.version())
    for ln in open(path):
        ln = ln.rstrip("\n")
        if not ln or ln.startswith("#"):
            continue
        fl, pat, ex, sets, label = ln.split("\t")
        S = [frozenset(int(x, 16) for x in s.split(",") if x) for s in sets.split(";")]
        ex = int(ex)
        O.compile(fl, pat.encode("latin-1"))
        rnd = random.Random(7)
        r1 = P1()
        levels, _ = explore(O, contexts("u" in fl), len(S), 64, rnd, "u" in fl)
        for d, row in enumerate(levels):
            for w, N in row:
                r1.nodes += 1
                if not N <= S[d]:
                    r1.miss("hull-under", d=d, node=w, pcre=N, stated=S[d])
                if d < ex and N != S[d]:
                    r1.miss("exact", d=d, node=w, pcre=N, stated=S[d])
        print("%-10s %-3s %-22s exact_len=%d  %s  nodes=%d  %s" % (
            label, fl, pat, ex, "RED" if r1.bad else "green", r1.nodes,
            json.dumps(r1.bad[0]) if r1.bad else ""))
    O.close()


if __name__ == "__main__":
    a = sys.argv[1:]
    if a[0] == "pop":
        population(a[1])
    elif a[0] == "run":
        j = int(a[a.index("-j") + 1]) if "-j" in a else 8
        selfp = a[a.index("--self") + 1] if "--self" in a else None
        if "--plant" in a:
            # through the environment: the workers are forkserver children that
            # import conj.py afresh (a parent-side assignment never reached them)
            conj.PLANT = os.environ["CONJ_PLANT"] = a[a.index("--plant") + 1]
        only = a[a.index("--only") + 1].split(",") if "--only" in a else None
        run(a[1], a[2], j, selfp, only)
    elif a[0] == "summary":
        summary(a[1])
    elif a[0] == "stated":
        stated(a[1])
    elif a[0] == "plantpop":
        plantpop(a[1], a[2])
