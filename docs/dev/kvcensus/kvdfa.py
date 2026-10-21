"""kvcensus: read a DFA machine off pcrec's EMITTED C and answer the census's
three machine questions (docs/dev/kvcensus.md §2):

  lang()     on the ANCHORED (match-here) machine: the per-position byte sets
             S_d of every match from the origin, the span length (positions
             every match has), the EXACT prefix length (the largest E such that
             the language's length-E prefixes are the cross product S_0..S_E-1)
             and, past it, a counterexample pair the PCRE2 control re-checks.
  uniform()  on the FORWARD (search) machine: delta_uniform per position (every
             byte of S_d drives the start path to ONE state) and consumable_len
             for a plain unseeded DFA consumer.
  whole()    WHOLE-COVER: the language is exactly the product S_0..S_k-1 of
             fixed width k, with no context (seed), no view and no
             class-indexed accept left to decide.

Only the emitted tables are read (`<prefix>_<m>_byte_class`, `_next_state`,
`_is_accepting`, `_is_accepting_by_class`, `_seed_state`, `_eol_view`,
`_end_view`) and the index expressions of the emitted step/row/accept helpers,
so both table forms (premultiplied, indexed) read the same. A machine whose
scan edges deleted interior states is NOT readable as a table: the census
compiles with -fno-scan-edge for every table it reads.
"""
import re

CAP = 32  # MF_MAX_SPAN_POS's derivation (PCREC_MAX_REQ_RUN_SCAN, window_contract §4.3)
W = frozenset(list(range(48, 58)) + list(range(65, 91)) + list(range(97, 123)) + [95])


def _arr(c, name):
    m = re.search(r"\b%s\[(\d+)\] = \{(.*?)\};" % re.escape(name), c, re.S)
    if not m:
        return None
    return [int(x) for x in re.findall(r"-?\d+", m.group(2))]


def _helper(c, pfx, m, fn):
    """the index expression of an emitted one-line helper, as a lambda."""
    r = re.search(r"%s_%s_%s\([^)]*\)\s*\{\s*return ([^;]*);" % (pfx, m, fn), c)
    if not r:
        return None
    e = r.group(1)
    e = re.sub(r"\((?:unsigned|int|size_t)\)", "", e)
    e = re.sub(r"^[a-z_]+\[(.*)\]$", r"\1", e.strip())
    e = re.sub(r"(\d+)[uU]\b", r"\1", e)
    try:
        return eval("lambda s, cl=0: " + e.replace("/", "//"), {})
    except SyntaxError:
        return None


def _entry(c, m):
    """the EMITTED entry constant X of machine m: `<m>_state = X;` (unseeded)
    or `<m>_state = P ? <seed>[..] : X;` (seeded, P the start position's
    name; X is the absent-predecessor entry). The emitter does not promise X = row 0 (`\\Zx` writes
    2, and row 0 is the eol view's target: kit_proof X0's R1). None if no
    such line is emitted."""
    r = re.search(r"\b%s_state = (?:[a-z_]+ \? [^;:]*: )?(-?\d+);" % m, c)
    return int(r.group(1)) if r else None


class Machine:
    """One emitted machine, its states renumbered to ROWS 0..n-1. The entry
    row is `entry`, read from the emitted constant, never assumed to be 0."""

    def __init__(self, c, m, pfx="rx"):
        self.ok = False
        g = lambda n: _arr(c, "%s_%s_%s" % (pfx, m, n))
        bc, ns, acc = g("byte_class"), g("next_state"), g("is_accepting")
        if acc is None and ns:
            # a uniform accept folded into the helper: `{ (void)s; return 1; }`
            u = re.search(r"%s_%s_accepts\(%s_%s_state s\)\s*\{\s*\(void\)s;\s*return ([01]);"
                          % (pfx, m, pfx, m), c)
            if u:
                acc = [int(u.group(1))] * len(ns)
        if not bc or not ns or not acc or len(bc) != 256:
            return
        step = _helper(c, pfx, m, "step")
        if step is None:
            return
        self.ncl = ncl = max(bc) + 1
        premul = step(1, 0) == 1 and len(acc) == len(ns)
        self.premul = premul
        nrow = len(ns) // ncl
        dead_v = 65535 if premul and max(ns) == 65535 else None
        isdead = lambda v: v < 0 or v == dead_v or (premul and v == 65535)
        norm = (lambda v: None if isdead(v) else v // ncl) if premul else \
               (lambda v: None if isdead(v) else v)
        self.norm = norm
        self.bc = bc
        self.nrow = nrow
        self.next = [[norm(ns[step(r * ncl if premul else r, k)]) for k in range(ncl)]
                     for r in range(nrow)]
        av = lambda r: r * ncl if premul else r
        self.acc = [bool(acc[av(r)]) if av(r) < len(acc) else False for r in range(nrow)]
        abc = g("is_accepting_by_class")
        acls = _helper(c, pfx, m, "accepts_class")
        self.by_class = None
        if abc and acls:
            self.by_class = [[bool(abc[acls(av(r), k)]) for k in range(ncl)] for r in range(nrow)]
        seed = g("seed_state")
        self.seed = [norm(v) for v in seed] if seed else None
        self.views = {}
        rowf = _helper(c, pfx, m, "row")
        for vn in ("eol_view", "end_view"):
            v = g(vn)
            if v and rowf:
                self.views[vn] = [norm(v[rowf(av(r))]) if rowf(av(r)) < len(v) else None
                                  for r in range(nrow)]
        self.seeded = self.seed is not None
        # the entry: unseeded, the one entry row; seeded, the ABSENT-
        # predecessor entry (None = dead, or no entry line was emitted)
        x = _entry(c, m)
        self.entry_read = x is not None
        self.entry = norm(x) if x is not None else None
        self.has_views = bool(self.views) or self.by_class is not None
        # liveness: can reach any accept (plain, class-indexed or a view's)
        self.acc_any = [self.acc[r] or (self.by_class and any(self.by_class[r])) or
                        any(vv[r] is not None and self.acc[vv[r]] for vv in self.views.values())
                        for r in range(nrow)]
        # the VIEW-GATED byte (kit_proof X0's R2): the emitted loop takes the
        # eol view at a subject-final '\n' and steps the VIEW state on it, so
        # a row q consumes that '\n' to t = step(eol[q], '\n'), and the match
        # ends at the subject end, accepted there as the emitted end test does
        # (end view if live, else eol view, else plain). The plain table does
        # not carry this edge (`(a$\n)|ab`: S_1 = {b, \n}, not {b}).
        eol = self.views.get("eol_view")
        self.vnl = [False] * nrow
        if eol:
            for r in range(nrow):
                if eol[r] is not None:
                    t = self.next[eol[r]][bc[10]]
                    self.vnl[r] = t is not None and self.acc_end(t)
        self.live = self.liveness()
        self.ok = True

    def liveness(self):
        """the rows that can reach an accept: plain, class-indexed or a view's,
        or the view-gated final '\n' (vnl); recomputed by a plant that edits
        the table"""
        live = set(r for r in range(self.nrow) if self.acc_any[r] or self.vnl[r])
        pred = {}
        for r in range(self.nrow):
            for t in self.next[r]:
                if t is not None:
                    pred.setdefault(t, set()).add(r)
        todo = list(live)
        while todo:
            t = todo.pop()
            for r in pred.get(t, ()):
                if r not in live:
                    live.add(r); todo.append(r)
        return live

    def step(self, r, b):
        return self.next[r][self.bc[b]]

    def acc_end(self, t):
        """row t accepts at the subject end (p == n): the end view when live,
        else the eol view when live, else the plain accept (the emitted
        end test's order)"""
        for vn in ("end_view", "eol_view"):
            v = self.views.get(vn)
            if v and v[t] is not None:
                return self.acc[v[t]]
        return self.acc[t]

    def starts(self, ctx=None, absent=True):
        """the entry rows. Unseeded: {entry}. Seeded: under a context SET `ctx`
        (bytes the predecessor may be) plus the absent-predecessor entry when
        `absent`; ctx None = every context (the union over all). The entry is
        the EMITTED constant (`entry`), not row 0."""
        if not self.entry_read:
            raise ValueError("kvdfa: no emitted entry constant for this machine")
        if not self.seeded:
            return {self.entry} if self.entry is not None else set()
        bs = range(256) if ctx is None else ctx
        s = {self.seed[self.bc[b]] for b in bs}
        if absent:
            s.add(self.entry)
        return {r for r in s if r is not None}


def lang(M, starts, cap=CAP):
    """-> dict(S, span, exact, cex, Qk). The walk is over SUBSETS of rows: a
    string u reaches T(u) = {delta*(s, u) : s in starts}, so a seeded machine
    (one start per predecessor class) reads the language over every context.
    Q maps a subset -> one witness string. Position d EXISTS while no subset
    can accept (no match ends before it); it is EXACT while every subset
    reached allows the same next-byte set."""
    st = frozenset(r for r in starts if r in M.live)
    Q = {st: b""} if st else {}
    S, exact, cex = [], None, None
    span = cap
    ended = False   # a view-gated '\n' ended a match at this depth
    view_d = []     # depths whose set gained a byte only through the eol view
    for j in range(cap):
        if not Q or ended:
            span = j; break
        if any(M.acc_any[q] for T in Q for q in T):
            span = j; break
        B = {}
        for T in Q:
            B[T] = frozenset(b for b in range(256)
                             if any(M.step(q, b) is not None and M.step(q, b) in M.live for q in T))
            if any(M.vnl[q] for q in T):
                # the TRUE set (manager ruling, X0 R2): a byte reached through
                # the eol view is a byte some match carries at depth j
                if 10 not in B[T] and j not in view_d:
                    view_d.append(j)
                B[T] = B[T] | {10}
                ended = True
        union = frozenset().union(*B.values())
        if exact is None and len(set(B.values())) > 1:
            exact = j
            for T1 in B:
                for T2 in B:
                    d = B[T1] - B[T2]
                    if d and cex is None:
                        b = min(d)
                        cex = (Q[T1] + bytes([b]), Q[T2] + bytes([b]))
        S.append(union)
        Qn = {}
        for T, w in Q.items():
            for b in sorted(B[T]):
                Tn = frozenset(t for t in (M.step(q, b) for q in T) if t is not None and t in M.live)
                if Tn not in Qn:
                    Qn[Tn] = w + bytes([b])
        Q = Qn
    if exact is None:
        exact = span
    return dict(S=S, span=span, exact=exact, cex=cex, Qk=Q, view_d=view_d)


def uniform(F, S, exact, starts=None):
    """-> (contig_len, best_len, per-position flags). The DFA consumer may enter
    at the state after N proven bytes iff that state is ONE row for every
    string of S_0 x .. x S_N-1, no row on the way is dead, and no row BEFORE
    the entry accepts (the entry row itself may: its accept is a constant)."""
    Q = set(starts if starts is not None else F.starts())
    if len(Q) != 1:
        return 0, 0, []
    flags, contig, best = [], 0, 0
    run = True
    for j in range(exact):
        Qn = {F.step(q, b) for q in Q for b in S[j]}
        if None in Qn:
            break
        u = len(Qn) == 1
        flags.append(u)
        if u:
            best = j + 1
            if run:
                contig = j + 1
        else:
            run = False
        if any(F.acc_any[t] for t in Qn):
            break   # an accept inside the skipped bytes: entry must stop here
        Q = Qn
    return contig, best, flags


def whole(M, L, starts):
    """the language is exactly S_0 x .. x S_k-1, fixed width k, decided."""
    k = L["span"]
    if starts != {M.entry} or M.seeded or M.has_views or k == 0 or k >= CAP:
        return 0
    if L["exact"] != k or not L["Qk"]:
        return 0
    for T in L["Qk"]:
        for q in T:
            if not M.acc[q]:
                return 0
            if any(t is not None and t in M.live for t in M.next[q]):
                return 0
    return k


def setstr(s):
    """compact rendering of a byte set: ranges in hex, `*` for all 256."""
    s = sorted(s)
    if len(s) == 256:
        return "*"
    out, i = [], 0
    while i < len(s):
        j = i
        while j + 1 < len(s) and s[j + 1] == s[j] + 1:
            j += 1
        out.append("%02x" % s[i] if i == j else "%02x-%02x" % (s[i], s[j]))
        i = j + 1
    return ",".join(out)


def hexset(h):
    bs = bytes.fromhex(h)
    return frozenset(b for b in range(256) if (bs[b >> 3] >> (b & 7)) & 1)


def forward_path(F, S0, cap=CAP):
    """A SCAN-RESTART site (span 0's set narrower than the language's S_0: the
    forward scan restarts where its start row stops self-looping, and the
    reverse pass recovers the start): the per-position ENGAGED sets of the
    forward machine from its emitted entry row (S_0 = the site's set; then
    every byte that keeps some reached row live and off the start row), with
    the same entry rule as uniform(). -> (best, contig, sets)."""
    e0 = F.entry   # the emitted entry row (the start row), never assumed 0
    Q, S, best, contig, run = {e0}, [frozenset(S0)], 0, 0, True
    for j in range(cap):
        Qn = {F.step(q, b) for q in Q for b in S[j]}
        Qn.discard(None)
        if not Qn:
            break
        if len(Qn) == 1:
            best = j + 1
            if run:
                contig = j + 1
        else:
            run = False
        if any(F.acc_any[t] for t in Qn):
            break
        Q = Qn
        nxt = frozenset(b for b in range(256) for q in Q
                        if F.step(q, b) is not None and F.step(q, b) != e0 and F.step(q, b) in F.live)
        if not nxt:
            break
        S.append(nxt)
    return best, contig, S
