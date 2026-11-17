#!/usr/bin/env python3
# Lane predspec243 (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 24.3 (review r42's
# fixes, docs/dev/reviews/2026-11-17-r42-predspec242.md, as the manager disposed them). DESIGN EVIDENCE ONLY; rules
# nothing.
#
# HOW: lane predspec242b's engine (../predspec242b_evidence/predspec242b_model.py, never edited; it executes lane
# predspec241's engine, which loads lastpass's, pathimpact's path enumerator and rxmodel's libpcre2 harness) is
# EXECUTED IN MEMORY, whole, with textual patches (each asserted to hit exactly once). The fixes act only under the
# NOW rule (rev 24.2's "24.2" context, which is rev 24.3's rule in this run: PASSOWN and rev 24's rules); rev 24.1's
# carry and rev 23.2's rules run as before. Its whole output is printed first, unchanged in form, so that a diff
# against predspec242b_model.out lists every printed number that moved (PART 0 below prints them, WAS / NOW).
#   FIX-A1 (review r42 A1, disposition: "PCRE's trailing empty iteration IS a pass"): a loop iteration that matches
#          the empty string past the minimum is KEPT as the last pass and ends the loop, as libpcre2 does, in all
#          three loop kinds: the literal's loop (pathimpact's `Rx._rep` dropped it), the hole loop (`Rep` dropped it)
#          and `occurrences` (`OccS` kept an empty HIT, but ended the loop on an empty hit after a non-empty gap,
#          where the one-pattern model's iteration is not empty).
#   FIX-A2 (A2, THE MANAGER'S READING entailed by nested-pass): the pass forms (`some`, `occurs.*`, `h[k]`) over a
#          label inside a literal read the OUTERMOST enclosing loop's passes, each pass's label at its outermost view
#          (the last setting after the last start of every loop enclosing the label within that pass). The literal
#          keyed its pass table on the innermost loop; the hole spelling already read the outer passes.
#   FIX-A4 (A4): FIND-ALL follows PCRE2's global loop: after an empty match, retry at the same place for a
#          NON-EMPTY match anchored there (NOTEMPTY_ATSTART | ANCHORED), and only then advance one character. Applied
#          to the engine (NOW rule) and to every libpcre2 model's FIND-ALL loop (the harness's `Pcre.findall`,
#          predspec241's `SM`, predspec242b's `OwnRx`).
#   A5 (control): the STRUCTURAL-UNROLLING model (review r42 MODECLOSURE's model U: a loop `B*` is written
#          `(?:B'*B)?`, B' being B with the label's group made non-capturing, recursively for enclosing loops; only
#          the last pass's copy names the group, so PCRE2's own capture IS the last pass's own label; no helper group,
#          no position test) is the control of the per-pass label (PART U). The helper-group model stays only where a
#          group's text lies inside its own pass; PART U shows both on the two lookaround witnesses.
#
# SWITCHES (W = the worktree; run from $PCREC_TMPDIR/scratch/predspec243; one process, about 3 minutes):
#   timeout 1800 python3 -I -B W/docs/dev/lanes/predspec243_evidence/predspec243_model.py > fwd.out
#   PREDSPEC243_SABOTAGE=1   FIX-A1, FIX-A2 and FIX-A4 are switched OFF in the engine (the libpcre2 models keep
#                            PCRE2's behaviour): PART X's checks must fail (the switch back to rev 24.2's engine)
import os, sys, io, re, contextlib, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
F242 = os.path.join(LANES, "predspec242b_evidence", "predspec242b_model.py")
O242 = os.path.join(LANES, "predspec242b_evidence", "predspec242b_model.out")
SAB = os.environ.get("PREDSPEC243_SABOTAGE") == "1"
for k in ("PREDSPEC242B_SABOTAGE", "PREDSPEC242B_RULES", "PREDSPEC241_SABOTAGE", "PREDSPEC241_RULES"):
    os.environ.pop(k, None)

def rep(s, a, b):
    assert s.count(a) == 1, (a[:80], s.count(a))
    return s.replace(a, b)

# ------------------------------------------------------------------------------------------------ patches to 241
FIX243 = {"v": not SAB}
P241_GLOB = r'''
def _FIX(): return FIX243["v"] and PASSOWN["v"] and RULES["v"] == "24"     # rev 24.3's fixes act under the NOW rule only
NOTEMPTY_ATSTART = 0x00000008
def _glob(match, s):
    """PCRE2's global loop (pcre2demo): again from the end; after an EMPTY match retry at the same place with
    NOTEMPTY_ATSTART | ANCHORED, and only when that fails advance one character (FIX-A4)."""
    out, pos, ne = [], 0, False
    while pos <= len(s):
        r = match(s, pos, (NOTEMPTY_ATSTART | P.PCRE2_ANCHORED) if ne else 0)
        if r is None:
            if ne: pos += 1; ne = False; continue
            break
        out.append(r); ne = (r[1] == r[0]); pos = r[1]
    return out
P.Pcre.findall = lambda self, s: _glob(self.match, s)
def _rep243(self, items, lo, hi, greedy, count, s, pos, caps, hist, fl, nid):
    """pathimpact's Rx._rep with FIX-A1: an empty iteration past the minimum is KEPT (it is the last pass; PCRE does
    not loop again after it) instead of dropped."""
    def more():
        if count < hi:
            for p2, c2, h2 in self._seq(items, 0, s, pos, caps, hist + (("it", nid, pos),), fl):
                if p2 == pos and count >= lo:
                    if _FIX(): yield p2, c2, h2
                    continue
                yield from _rep243(self, items, lo, hi, greedy, count + 1, s, p2, c2, h2, fl, nid)
    if greedy:
        yield from more()
        if count >= lo: yield pos, caps, hist
    else:
        if count >= lo: yield pos, caps, hist
        yield from more()
E["Rx"]._rep = _rep243
'''
def fix241(s):
    s = rep(s, 'P = LP["P"]                                           # pcre2h\n',
            'P = LP["P"]                                           # pcre2h\n' + P241_GLOB)
    # FIX-A1, the hole loop
    s = rep(s, "                if e == pos: continue                       # an empty pass ends the loop (PCRE)\n"
               "                own = carry_pass(row, c, carry)\n                if own is None: continue\n",
               "                if e == pos and not _FIX(): continue        # an empty pass ends the loop (PCRE)\n"
               "                own = carry_pass(row, c, carry)\n                if own is None: continue\n"
               "                if e == pos and len(ps) >= self.lo:         # FIX-A1: the empty pass is kept, then the loop ends\n"
               "                    yield pos, passrow(self.key, self.labs, (i, pos), ps + (own,)), (); continue\n")
    # FIX-A1, occurrences: the one-pattern iteration is empty only when the gap AND the hit are empty
    s = rep(s, "                    if e == g:                              # an empty hit ends the loop\n"
               "                        if len(h) >= self.mn: yield from tail(e, h)\n                        continue\n",
               "                    if (e == pos) if _FIX() else (e == g):  # an empty ITERATION ends the loop (FIX-A1: gap + hit)\n"
               "                        if len(h) >= self.mn: yield from tail(e, h)\n"
               "                        elif _FIX(): yield from loop(e, h, dict(carry, **{k: v for k, v in own.items() if k != 'hit'}))\n"
               "                        continue\n")
    # FIX-A4, the engine's FIND-ALL
    s = rep(s, "def findall(Pn, s):\n    out, pos = [], 0\n    while pos <= len(s):\n        r = search(Pn, s, pos)\n"
               "        if r is None: break\n        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1\n    return out\n",
               "def findall(Pn, s):\n    if _FIX():                                           # FIX-A4: PCRE2's global loop\n"
               "        def m(s_, pos, opts):\n"
               "            if opts: return next(((pos, e, row) for e, row in acc_iter(Pn, s_, pos) if e > pos), None)\n"
               "            return search(Pn, s_, pos)\n"
               "        return _glob(m, s)\n"
               "    out, pos = [], 0\n    while pos <= len(s):\n        r = search(Pn, s, pos)\n"
               "        if r is None: break\n        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1\n    return out\n")
    # FIX-A4, predspec241's `&` models
    s = rep(s, "    def findall(self, s):\n        out, pos = [], 0\n        while pos <= len(s):\n            r = self.match(s, pos)\n"
               "            if r is None: break\n            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1\n        return out\n",
               "    def findall(self, s): return _glob(self.match, s)                # FIX-A4\n")
    return s

# ------------------------------------------------------------------------------------------------ patches to 242b
OUTER_ADD = r'''
        if _FIX():                    # FIX-A2: the pass forms read the OUTERMOST loop's passes, each at its outermost view
            outer = {}
            for nm, g in r.names.items():
                ls = enc.get(g)
                if ls: outer.setdefault(ls[0], []).append((nm, g, ls))
            for o, mem in outer.items():
                key = ("L", "outer", id(r), o); ps = []; cur = None
                for ev in hist:
                    if ev[0] == "it" and ev[1] == o:
                        cur = {}; ps.append(cur)
                    elif cur is None: continue
                    elif ev[0] == "it":
                        for nm, g, ls in mem:
                            if ev[1] in ls: cur.pop(nm, None)
                    elif ev[0] == "g":
                        for nm, g, ls in mem:
                            if ev[1] == g: cur[nm] = s[ev[2]:ev[3]]
                for nm, g, ls in mem: row.loop[nm] = key
                row.passes[key] = ps
    return row
LP["row_of"] = _row_of_outer
'''
SRC = open(F242).read()
S = SRC
S = rep(S, "            row.last[nm] = (vs[0] if SAB_OWN else vs[-1]) if vs else None\n    return row\nLP[\"row_of\"] = _row_of_outer\n",
        "            row.last[nm] = (vs[0] if SAB_OWN else vs[-1]) if vs else None\n" + OUTER_ADD)
S = rep(S, "        rep('    if PASSOWN[\"v\"] and view is None and LP[\"MODE\"][\"v\"] == \"R\" and any(', ",
        "        s = FIX241(s)\n        rep('    if PASSOWN[\"v\"] and view is None and LP[\"MODE\"][\"v\"] == \"R\" and any(', ")
S = rep(S, "        out, pos = [], 0\n        while pos <= len(s):\n            r = self.m(s, pos)\n            if r is None: break\n"
           "            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1\n        return tuple(out)\n",
        "        return tuple(G[\"_glob\"](self.m, s))                     # FIX-A4\n")
S = rep(S, "        exec(compile(patched(po0, sab), F241, \"exec\"), ns)",
        "        if po0: ns[\"FIX243\"] = FIX243\n        exec(compile(patched(po0, sab), F241, \"exec\"), ns)")

NS = {"__file__": F242, "__name__": "p242b", "FIX241": fix241, "FIX243": FIX243}
buf = io.StringIO()
with contextlib.redirect_stdout(buf):
    exec(compile(S, F242, "exec"), NS)
OUT = buf.getvalue()
print("RUN: predspec243 %s (rev 24.3 = predspec242b's engine + FIX-A1, FIX-A2, FIX-A4)" % ("SABOTAGE (the fixes OFF)" if SAB else "forward"))
sys.stdout.write(OUT)

# ================================================================================================= PART 0
print("== PART 0 (rev 24.3): predspec242b's whole output re-run under rev 24.3 vs its committed .out: every changed line, WAS (rev 24.2) then NOW (rev 24.3)")
a_, b_ = open(O242).read().splitlines(), OUT.splitlines()
nchg = 0
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a_, b_, autojunk=False).get_opcodes():
    if op == "equal": continue
    nchg += 1
    for x in a_[i1:i2]: print("0 WAS  " + x)
    for x in b_[j1:j2]: print("0 NOW  " + x)
print("0 changed hunks: %d (every line of predspec242b_model.out not listed is printed identically under rev 24.3)" % nchg)

# ------------------------------------------------------------------------------------------------ handles
G = NS["G"]; P = G["P"]
Pat, W, C, NOT, Rep, OCC, AND, ANDC, Atom = (G[k] for k in ("Pat", "W", "C", "NOT", "Rep", "OCC", "AND", "ANDC", "Atom"))
SOME, NONE, Count, Idx, Committed = G["SOME"], G["NONE"], G["Count"], G["Idx"], G["Committed"]
lt, eq, num, strings, lists = G["lt"], G["eq"], G["num"], G["strings"], G["lists"]
E, R, diffn, dn, ans3, fq, rxk, OwnRx, h5 = (NS[k] for k in ("E", "R", "diffn", "dn", "ans3", "fq", "rxk", "OwnRx", "h5"))
Seq = NS["Seq"]
REJ = G["REJ"]
NOW = "24.2"                                  # the NOW context of predspec242b = rev 24.3's rule in this run
lt5 = lambda v: v is not None and num(v) and int(v) < 5
CHK = []
def check(name, ok): CHK.append((name, ok)); return "OK" if ok else "FAILED"
def safe(f):
    def g(m, s):
        try: return f(m, s)
        except ValueError: return REJ
    return g
class URx:
    """MODEL U (structural unrolling): plain libpcre2 callouts reading PCRE2's capture; only the last pass's copy of
    each loop body names the group, so the capture IS the last pass's own label at the outermost view."""
    def __init__(self, pattern, tests, labs):
        self.labs, self.side, self.pattern = tuple(labs), {}, pattern
        cos = {k: (lambda c, f=f: bool(f({l: c.get(l) for l in self.rx.names}))) for k, f in tests.items()}
        cos["__end"] = self._end
        self.rx = P.Pcre(pattern + '(?C"__end")', cos)
    def _end(self, c): self.side = {l: c.get(l) for l in self.labs}; return True
    def m(self, s, pos=0, opts=0):
        self.side = {}
        r = self.rx.match(s, pos, opts)
        return None if r is None else (r[0], r[1], tuple((l, self.side.get(l)) for l in self.labs))
    def key(self, mode, s):
        if mode == "WHOLE":
            r = self.m(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED); return None if r is None else r[2]
        if mode == "SEARCHED": return self.m(s)
        return tuple(G["_glob"](self.m, s))
def E242(mk, labs=()):
    """rev 24.2's engine: the NOW rule with FIX-A1, FIX-A2, FIX-A4 OFF (the before column of every rev 24.3 count)."""
    f = E(NOW, mk, labs)
    def g(m, s):
        old = FIX243["v"]; FIX243["v"] = False
        try: return f(m, s)
        finally: FIX243["v"] = old
    return g
def uk(pattern, tests, labs): x = URx(pattern, tests, labs); return lambda m, s: x.key(m, s)
def stepone(mo, s):
    out, pos = [], 0
    while pos <= len(s):
        r = mo.m(s, pos)
        if r is None: break
        out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
    return tuple(out)
R4 = strings("37;", 4); A4 = strings("37a", 4); RG3 = G["RG3"]; NP = strings("37;,", 5)

# ================================================================================================= PART X1: FIX-A1
print("== PART X1 (review r42 A1): PCRE's trailing EMPTY iteration is a pass (the default is regex)")
for pat, t in ((r"(?:(?<h>\d)?)*", "3"), (r"(?:a|(?<e>))*", "a"), (r"(?:a|(?<e>))*", "")):
    r = P.Pcre(pat).match(t, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    print("X1 libpcre2 `/%s/` WHOLE on `%s`: match %s, groups %s" % (pat, t, r[:2], r[2]))
NLp, NLu = r"(?:(?P<h>\d)?)*", r"(?:(?:(?:\d)?)*(?<h>\d)?)?"
NL2p, NL2u = r"(?:(?P<h>\d)|;?)*", r"(?:(?:\d|;?)*(?:(?<h>\d)|;?))?"
for nm, ep, up in (("NL nullable body `(?:(?<h>\\d)?)*`", NLp, NLu), ("NL2 nullable body `(?:(?<h>\\d)|;?)*`", NL2p, NL2u)):
    for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
        fe = E(NOW, lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",))
        d = diffn(fe, uk(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",)), R4)
        print("X1 %s `& %s`: the engine NOW vs MODEL U `/%s/`: %s ; CHECK %s" % (nm, cn, up + uc, d[0], check("X1 %s %s engine = model U" % (nm[:3], cn), d[1] == 0)))
        print("X1   BEFORE: rev 24.2's engine vs MODEL U: %s" % dn(E242(lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",)), uk(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",)), R4))
f = E(NOW, lambda: W(Pat(NLp), NOT(h5())), ("h",))
print("X1 WITNESS `/(?:(?<h>\\d)?)*/ & NOT (h: <5)`: NOW %s" % ans3(f, ("3", "3", "3")))
print("X1   rev 24.2's engine (the empty pass dropped) %s" % ans3(E242(lambda: W(Pat(NLp), NOT(h5())), ("h",)), ("3", "3", "3")))
f = E(NOW, lambda: W(Pat(NLp), h5()), ("h",))
print("X1 the positive `/(?:(?<h>\\d)?)*/ & (h: <5)`: NOW %s (the condition fails on the empty pass; PCRE backtracks to the path without it)" % ans3(f, ("3", "3", "3")))
# the three loop kinds agree: the literal's loop, the hole loop, occurrences' iteration (pass table and labels)
for cn, ec in (("(h: <5)", lambda: h5()), ("NOT (h: <5)", lambda: NOT(h5())), ("some((h: <5))", lambda: SOME(h5())),
               ("occurs.none(NOT (h: <5))", lambda: NONE(NOT(h5()))), ("(h[2]: <5)", lambda: Idx("h", 2, lt(5)))):
    fl = safe(E(NOW, lambda ec=ec: W(Pat(NLp), ec()), ("h",)))
    fh = safe(E(NOW, lambda ec=ec: W(Rep(Pat(r"(?P<h>\d)?"), 0), ec()), ("h",)))
    d = diffn(fl, fh, R4)
    print("X1 THE LOOP KINDS `& %s`: the literal `/(?:(?<h>\\d)?)*/` vs the hole loop `/(?:${x})*/`, x := `/(?<h>\\d)?/`: %s ; CHECK %s" % (cn, d[0], check("X1 literal = hole loop %s" % cn, d[1] == 0)))
    print("X1   BEFORE (rev 24.2's engine, both loops dropping the empty pass): %s" % dn(safe(E242(lambda ec=ec: W(Pat(NLp), ec()), ("h",))), safe(E242(lambda ec=ec: W(Rep(Pat(r"(?P<h>\d)?"), 0), ec()), ("h",))), R4))
OCCu = r"(?:(?:[\s\S]*?(?:\d)?)*[\s\S]*?(?<h>\d)?)?[\s\S]*"
for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
    fe = E(NOW, lambda ec=ec: W(OCC(Pat(r"(?P<h>\d)?")), ec()), ("h",))
    d = diffn(fe, uk(OCCu + uc, {"t": lambda v: lt5(v["h"])}, ("h",)), strings("3a", 5))
    print("X1 OCCURRENCES `occurrences(/(?<h>\\d)?/) & %s` (a nullable argument) vs its one-pattern MODEL U `/%s/`: %s ; CHECK %s" % (cn, OCCu + uc, d[0], check("X1 occurrences nullable = model U %s" % cn, d[1] == 0)))
f = E(NOW, lambda: W(OCC(Pat(r"(?P<h>\d)?")), NOT(h5())), ("h", "#hits"))
print("X1   `occurrences(/(?<h>\\d)?/) & NOT (h: <5)` NOW %s" % ans3(f, ("3", "a3", "3 a")))
print("X1 rev 24.2's pools: every loop body consumes a character (review r42 V1), so no line of PARTS 0-Q can move by FIX-A1")

# ================================================================================================= PART X2: FIX-A2
print("== PART X2 (review r42 A2): the PASS FORMS over a label two loops deep read the OUTER passes at their outermost view (THE MANAGER'S READING, entailed by nested-pass)")
NEST, INNER = r"(?:(?:(?P<h>\d)?;)*,)*", r"(?:(?P<h>\d)?;)*"
def nest_direct(form, t):
    """An independent WHOLE evaluator of NEST's pass forms from the text alone: outer passes end at `,`, inner at `;`;
    an outer pass's h is its LAST inner pass's own digit (unset when it set none or ran none)."""
    if not re.fullmatch(r"(?:(?:\d?;)*,)*", t): return None
    outs = []
    for seg in t.split(",")[:-1]:
        inn = seg.split(";")[:-1]
        outs.append(inn[-1] if inn and inn[-1] else None)
    ok = lambda v: v is not None and int(v) < 5
    if form == "some": return any(ok(v) for v in outs)
    if form == "none-not": return not any(not ok(v) for v in outs)
    return len(outs) >= 2 and ok(outs[1])
for cn, ec, form in (("some((h: <5))", lambda: SOME(h5()), "some"), ("occurs.none(NOT (h: <5))", lambda: NONE(NOT(h5())), "none-not"),
                     ("(h[2]: <5)", lambda: Idx("h", 2, lt(5)), "idx")):
    fl = safe(E(NOW, lambda ec=ec: W(Pat(NEST), ec()), ("h",)))
    fh = safe(E(NOW, lambda ec=ec: W(Rep(Seq(Pat(INNER), Pat(",")), 0), ec()), ("h",)))
    d = diffn(fl, fh, NP)
    dd = sum(1 for t in NP if (fl("WHOLE", t) not in (None, REJ)) != bool(nest_direct(form, t)))
    print("X2 `& %s`: the literal NEST `/(?:(?:(?<h>\\d)?;)*,)*/` vs its hole spelling `/(?:${inner},)*/`: %s ; CHECK %s" % (cn, d[0], check("X2 literal = holes %s" % cn, d[1] == 0)))
    print("X2   BEFORE: rev 24.2's engine, literal vs holes: %s" % dn(safe(E242(lambda ec=ec: W(Pat(NEST), ec()), ("h",))), safe(E242(lambda ec=ec: W(Rep(Seq(Pat(INNER), Pat(",")), 0), ec()), ("h",))), NP))
    print("X2   the literal vs an independent direct evaluator (outer passes from the text, WHOLE, holds): %d of %d differ ; CHECK %s" % (dd, len(NP), check("X2 literal = direct %s" % cn, dd == 0)))
    print("X2   WITNESSES (WHOLE): " + " ; ".join("`%s` literal %s, holes %s" % (t, fq(t, "WHOLE", fl("WHOLE", t)), fq(t, "WHOLE", fh("WHOLE", t))) for t in ("3;7;,", ",", ",3;,", "3;;,7;,", "7;3;,")))
    print("X2   NOW %s" % ans3(fl, ("3;,7;,", "7;,3;, 3;,", "3;, ,7;, 7;3;,")))
# A3: a joint across depths and across sibling loops
print("== PART X3 (review r42 A3): a joint whose labels sit at two depths or in SIBLING loops")
hk = lambda: C(("h", "k"), lambda h, k: num(h) and num(k) and int(h) > int(k))
TWO, SIB = r"(?:(?P<k>\d)(?:(?P<h>\d);)*,)*", r"(?:(?P<k>\d);)*(?:(?P<h>\d),)*"
for nm, pat, texts in (("two depths `/(?:(?<k>\\d)(?:(?<h>\\d);)*,)*/`", TWO, ("37;,", "37;,51;,", "37;, 73;, 37;,51;,")),
                       ("siblings `/(?:(?<k>\\d);)*(?:(?<h>\\d),)*/`", SIB, ("3;7,", "7;3, 3;7,", "3;7, 7;3, 3;9;7,"))):
    for cn, ec in (("((h, k): h > k) (bare)", lambda: hk()), ("some(J)", lambda: SOME(hk())), ("occurs.none(NOT J)", lambda: NONE(NOT(hk())))):
        f = safe(E(NOW, lambda pat=pat, ec=ec: W(Pat(pat), ec()), ("h", "k")))
        print("X3 %s `& %s`: %s" % (nm, cn, ans3(f, texts)))

# ================================================================================================= PART X4: FIX-A4
print("== PART X4 (review r42 A4): FIND-ALL is PCRE2's global loop (retry NOT-EMPTY at the same place after an empty match)")
b = lambda n: ("(?<h>\\d)?;" if n else "(?:\\d)?;")
for nm, ep, up in (("greedy REP", r"(?:(?P<h>\d)?;)*", "(?:(?:%s)*%s)?" % (b(0), b(1))), ("lazy REP `*?`", r"(?:(?P<h>\d)?;)*?", "(?:(?:%s)*?%s)??" % (b(0), b(1)))):
    for cn, ec, uc in (("(h: <5)", lambda: h5(), '(?C"t")'), ("NOT (h: <5)", lambda: NOT(h5()), '(?!(?C"t"))')):
        mo = URx(up + uc, {"t": lambda v: lt5(v["h"])}, ("h",))
        fe = E(NOW, lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",))
        d1 = [t for t in RG3 if stepone(mo, t) != mo.key("FIND-ALL", t)]
        d2 = [t for t in RG3 if fe("FIND-ALL", t) != mo.key("FIND-ALL", t)]
        w = min(d1, key=lambda x: (len(x), x)) if d1 else None
        print("X4 %s `& %s`: model U step-one vs PCRE2's loop %d of %d%s ; the engine NOW vs PCRE2's loop %d ; CHECK %s" % (
            nm, cn, len(d1), len(RG3), "" if w is None else " (first `%s`: step-one %s vs PCRE2 %s)" % (w, fq(w, "FIND-ALL", stepone(mo, w)), fq(w, "FIND-ALL", mo.key("FIND-ALL", w))),
            len(d2), check("X4 %s %s engine = PCRE2 loop" % (nm, cn), len(d2) == 0)))
        fb = E242(lambda ep=ep, ec=ec: W(Pat(ep), ec()), ("h",))
        print("X4   BEFORE: rev 24.2's engine vs PCRE2's loop %d of %d" % (sum(1 for t in RG3 if fb("FIND-ALL", t) != mo.key("FIND-ALL", t)), len(RG3)))
f = E(NOW, lambda: W(Pat(r"(?:(?P<h>\d)?;)*?"), NOT(h5())), ("h",))
print("X4   rev 24.2's engine %s" % ans3(E242(lambda: W(Pat(r"(?:(?P<h>\d)?;)*?"), NOT(h5())), ("h",)), (";", ";", ";")))
print("X4 WITNESS lazy `/(?:(?<h>\\d)?;)*?/ & NOT (h: <5)` NOW %s" % ans3(f, (";", ";", ";")))

# ================================================================================================= PART U: model U
print("== PART U (review r42 A5): the STRUCTURAL-UNROLLING model (U) as the control of the per-pass label; the helper-group model only where a group's text lies inside its own pass")
CLOSEp, ITEMO = G["CLOSEp"], G["ITEMO"]
ALTp = NS["ALTp"]; SCX5, ABP5, CLOSEPOOL, A37 = G["SCX5"], G["ABP5"], G["CLOSEPOOL"], NS["A37"]
GAP = r"[\s\S]*?"
def dflt(h, m): return (lambda h, m: num(h) and num(m) and int(h) < 10 and int(m) < 30)(h if h is not None else "0", m if m is not None else "0")
UROWS = [
 ("V7", "REP & `(h: <5)`", r'(?:(?:(?:\d)?;)*(?<h>\d)?;)?(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), lambda: W(Pat(G["REPp"]), h5()), RG3),
 ("V8", "REP & `(h: !<5)`", r'(?:(?:(?:\d)?;)*(?<h>\d)?;)?(?C"t")', {"t": lambda v: v["h"] is not None and not lt5(v["h"])}, ("h",), lambda: W(Pat(G["REPp"]), C("h", lambda x: not lt(5)(x))), RG3),
 ("V9", "REP & `NOT (h: <5)`", r'(?:(?:(?:\d)?;)*(?<h>\d)?;)?(?!(?C"t"))', {"t": lambda v: lt5(v["h"])}, ("h",), lambda: W(Pat(G["REPp"]), NOT(h5())), RG3),
 ("V29", "CLOSE & `((h = 0, m = 0): (<10, <30))`", r'(?:(?:\d+(?::\d\d)?,)*(?<h>\d+)(?::(?<m>\d\d))?,)?(?C"t")', {"t": lambda v: dflt(v["h"], v["m"])}, ("h", "m"),
  lambda: W(Pat(CLOSEp), G["close_R"](h="0", m="0")), CLOSEPOOL),
 ("S4", "CLOSE & `((h, m = 00): == (10, 00))` (the shown hour table)", r'(?:(?:\d+(?::\d\d)?,)*(?<h>\d+)(?::(?<m>\d\d))?,)?(?C"t")',
  {"t": lambda v: v["h"] is not None and (v["h"], v["m"] if v["m"] is not None else "00") == ("10", "00")}, ("h", "m"),
  lambda: W(Pat(CLOSEp), C(("h", "m"), lambda h, m: (h, m) == ("10", "00"), m="00")), lists(["9:45,", "10,", "10:45,", "9,"], 3)),
 ("G3", "`/(?:${item})+/ & (h: <5)` (outside)", r'(?:(?:\d)?;)*(?<h>\d)?;(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), lambda: W(Rep(Pat(ITEMO), 1), h5()), RG3),
 ("G4", "`occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: \"a\")` (outside)", r'(?:[\s\S]*?(?:a)?b)*[\s\S]*?(?<x>(?<g>a)?b)[\s\S]*(?C"t")', {"t": lambda v: v["g"] == "a"}, ("x", "g"),
  lambda: W(OCC(Pat(r"(?P<x>(?P<g>a)?b)"), 1), C("g", eq("a"))), ABP5),
 ("G5e", "two depths, outside (the outermost view)", r'(?:(?:\d;)+x)*(?:\d;)*(?<h>\d);x(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), lambda: W(Rep(Pat(r"(?:(?P<h>\d);)+x"), 1), h5()), SCX5),
 ("G6", "`occurrences(/(?:(?<h>\\d);)+/, min = 1) & (h: <5)`", r'(?:[\s\S]*?(?:\d;)+)*[\s\S]*?(?:\d;)*(?<h>\d);[\s\S]*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",),
  lambda: W(OCC(Pat(r"(?:(?P<h>\d);)+"), 1), h5()), SCX5),
 ("G10e", "`occurrences(/(?:(?<h>\\d)?;)+/, min = 1) & (h: <5)`", r'(?:[\s\S]*?(?:\d?;)+)*[\s\S]*?(?:\d?;)*(?<h>\d)?;[\s\S]*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",),
  lambda: W(OCC(Pat(r"(?:(?P<h>\d)?;)+"), 1), h5()), SCX5),
 ("S1", "the alternation `/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)`", r'(?:(?:\d|[a-z])*(?:(?<a>\d)|(?<b>[a-z])))?xx(?C"t")', {"t": lambda v: lt5(v["a"])}, ("a", "b"),
  lambda: W(Pat(ALTp), C("a", lt(5))), A37),
 ("N1", "NEST `/(?:(?:(?<h>\\d)?;)*,)*/ & (h: <5)` (the outermost view)", r'(?:(?:(?:(?:\d)?;)*,)*(?:(?:(?:\d)?;)*(?<h>\d)?;)?,)?(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",),
  lambda: W(Pat(NEST), h5()), NP),
 ("NL", "a nullable body `/(?:(?<h>\\d)?)*/ & NOT (h: <5)`", NLu + '(?!(?C"t"))', {"t": lambda v: lt5(v["h"])}, ("h",), lambda: W(Pat(NLp), NOT(h5())), R4),
 ("LB", "a lookbehind sets h in its pass `/(?:\\d|(?<=(?<h>\\d))[a-z])*/ & (h: <5)`", r'(?:(?:\d|(?<=\d)[a-z])*(?:\d|(?<=(?<h>\d))[a-z]))?(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",),
  lambda: W(Pat(r"(?:\d|(?<=(?P<h>\d))[a-z])*"), h5()), A4),
 ("LA", "a lookahead sets h `/(?:(?=.(?<h>\\d))[a-z]|\\d)*/ & (h: <5)`", r'(?:(?:(?=.\d)[a-z]|\d)*(?:(?=.(?<h>\d))[a-z]|\d))?(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",),
  lambda: W(Pat(r"(?:(?=.(?P<h>\d))[a-z]|\d)*"), h5()), A4),
]
ueq = 0
for tag, nm, pat, tests, labs, mk, pool in UROWS:
    d = diffn(uk(pat, tests, labs), E(NOW, mk, labs), pool)
    dc = diffn(uk(pat, tests, labs), E("24.1", mk, labs), pool)
    ueq += (d[1] == 0)
    print("U %s %s  /%s/" % (tag, nm, pat))
    print("U %s   MODEL U vs the engine NOW: %s ; CHECK %s ; CONTROL vs the engine under rev 24.1's carry: %s" % (tag, d[0], check("U %s model U = engine" % tag, d[1] == 0), "DIFFERS" if dc[1] else "EQUAL (cannot tell the readings apart here)"))
for tag, ep, hp, pool in (("LB", r"(?:\d|(?<=(?P<h>\d))[a-z])*", r"(?:(?<ps>)(?:\d|(?<=(?<h>\d))[a-z]))*", A4), ("LA", r"(?:(?=.(?P<h>\d))[a-z]|\d)*", r"(?:(?<ps>)(?:(?=.(?<h>\d))[a-z]|\d))*", A4)):
    mo = OwnRx(hp + '(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), {"h": "ps"})
    d = diffn(rxk(mo), E(NOW, lambda ep=ep: W(Pat(ep), h5()), ("h",)), pool)
    print("U %s   the HELPER-GROUP model `/%s(?C)/` vs the engine NOW: %s (the group's text lies OUTSIDE its pass: the helper model does not apply)" % (tag, hp, d[0]))
print("U the helper-group models of PART C2 stay for G1, G2, G9e (a condition INSIDE the pass; every group's text inside its own pass, no lookaround in their pools)")
print("== PART U SUMMARY: %d of %d model U rows equal to the engine NOW" % (ueq, len(UROWS)))

# ================================================================================================= PART K: operand-context narrowed
print("== PART K (C5): which constructs \"certain contextual rx\" covers (the owner, 2026-11-15: anchors in a filter operand mean the stretch; contextual rx that would look past it are DISALLOWED)")
class SubjRx:
    """`A & B` with B's context the SUBJECT: B must match exactly the stretch A reports, its lookarounds, `\\b`, `\\G`
    reading the subject around it (B run in the subject from the stretch's start, anchored, its end tied)."""
    def __init__(self, outer, inner):
        self.inner, self._end = P.Pcre(inner + '(?C"__e")', {"__e": lambda c: c.pos == self._tgt}), None
        self.outer = P.Pcre(outer + '(?C"__op")', {"__op": self._op})
    def _op(self, c):
        self._tgt = c.pos
        return self.inner.match(c.subject, c.start, P.PCRE2_ANCHORED) is not None
    def m(self, s, pos=0, opts=0):
        r = self.outer.match(s, pos, opts); return None if r is None else (r[0], r[1], ())
SM = G["SM"]
class StrRx:
    def __init__(self, outer, inner): self.sm = SM(outer, inner, "and")
    def m(self, s, pos=0, opts=0):
        r = self.sm.match(s, pos, opts); return None if r is None else (r[0], r[1], ())
def kk(mo):
    def f(mode, s):
        if mode == "WHOLE": return mo.m(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED) is not None
        if mode == "SEARCHED": r = mo.m(s); return None if r is None else r[:2]
        return tuple(r[:2] for r in G["_glob"](mo.m, s))
    return f
def kf(s, m, k):
    if m == "WHOLE": return "HOLDS" if k else "FAILS"
    if m == "SEARCHED": return "FAILS" if k is None else "`%s`@%d" % (s[k[0]:k[1]], k[0])
    return "[" + ", ".join("`%s`@%d" % (s[a:b], a) for a, b in k) + "]"
CTXP = strings("1a ", 4)
for nm, inner, texts in (("`\\b` at the operand's start", r"\b\d+", ("1", "a1", "a11 1a1")),
                         ("`\\B` at the operand's start", r"\B\d+", ("1", "a1", "a11 1a1")),
                         ("a lookbehind at the start `(?<=a)`", r"(?<=a)\d+", ("1", "a1", "a11 1a1")),
                         ("a lookahead at the end `(?![a-z])`", r"\d+(?![a-z])", ("1", "1a", "11a 1a1")),
                         ("`\\G` at the operand's start", r"\G\d+", ("1", "a1", "a11 1a1")),
                         ("`\\K` (resets the reported start)", r"\d\K\d*", ("1", "a1", "a11 1a1"))):
    fs, fj = kk(StrRx(r"\d+", inner)), kk(SubjRx(r"\d+", inner))
    d = sum(1 for m in ("WHOLE", "SEARCHED", "FIND-ALL") for t in CTXP if fs(m, t) != fj(m, t))
    per = " / ".join(str(sum(1 for t in CTXP if fs(m, t) != fj(m, t))) for m in ("WHOLE", "SEARCHED", "FIND-ALL"))
    print("K %s, `/\\d+/ & /%s/`: COVERED: the program is REJECTED (the edge-assertion error) ; NOT COVERED, read on the stretch: WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s ; (the subject reading, which the ruling excludes: %s ; %s ; %s) ; stretch vs subject %s of %d" % (
        nm, inner, texts[0], kf(texts[0], "WHOLE", fs("WHOLE", texts[0])), texts[1], kf(texts[1], "SEARCHED", fs("SEARCHED", texts[1])), texts[2], kf(texts[2], "FIND-ALL", fs("FIND-ALL", texts[2])),
        kf(texts[0], "WHOLE", fj("WHOLE", texts[0])), kf(texts[1], "SEARCHED", fj("SEARCHED", texts[1])), kf(texts[2], "FIND-ALL", fj("FIND-ALL", texts[2])), per, len(CTXP)))
fe = E(NOW, lambda: AND(Pat(r"\d+"), Pat(r"\b\d+")), ())
fs = kk(StrRx(r"\d+", r"\b\d+"))
d = sum(1 for m in ("WHOLE", "SEARCHED", "FIND-ALL") for t in CTXP if (fe(m, t) is not None) != bool(fs(m, t)) if m == "WHOLE") + \
    sum(1 for t in CTXP if (lambda k: None if k is None else k[:2])(fe("SEARCHED", t)) != fs("SEARCHED", t)) + sum(1 for t in CTXP if tuple(x[:2] for x in fe("FIND-ALL", t)) != fs("FIND-ALL", t))
print("K the engine NOW (the operand on the stretch) vs the libpcre2 stretch model on `\\b`: %d of %d texts x modes differ ; CHECK %s" % (d, 3 * len(CTXP), check("K engine = stretch model", d == 0)))

# ================================================================================================= PART Y: the R5 candidates
print("== PART Y (§R.2): the other \"probably a mistake\" errors, each candidate's answers (ERROR = REJECTED in every mode)")
for slug, nm, mk, labs, texts in (
        ("label-twice-warn", "`/(?<h>\\d+)/ & (h: >2, h: <5)` (the `&` of the two tests)", lambda: W(Pat(r"(?P<h>\d+)"), ANDC(C("h", lambda v: num(v) and int(v) > 2), h5())), ("h",), ("3", "x7 3", "3 4 7")),
        ("empty-search-error", "`/(?<h>\\d*)/ & NOT (h: <5)` (a nullable final pattern, PCRE's empty matches)", lambda: W(Pat(r"(?P<h>\d*)"), NOT(h5())), ("h",), ("", "a7", "7a3")),
        ("min-values", "`occurrences(/\\d/, min = 2)` (at least two hits)", lambda: OCC(Pat(r"\d"), 2), ("#hits",), ("1a2", "1 a2 3", "12 3 45")),
        ("dollar-condition", "`/(?<x>\\d+)/ & ($x & <5)` read as `(x: <5)`", lambda: W(Pat(r"(?P<x>\d+)"), C("x", lt(5))), ("x",), ("3", "7 3", "3 9 4"))):
    print("Y %s %s: THE MEANING %s ; THE ERROR: REJECTED / REJECTED / REJECTED" % (slug, nm, ans3(E(NOW, mk, labs), texts)))

# ================================================================================================= PART Z: re-runs the text names
print("== PART Z: lines the revision quotes that predspec242b did not print as such")
f = E(NOW, lambda: W(OCC(Pat(r"(?P<g>a)?b")), C("g", eq("a"))), ("g", "#hits"))
print("Z RULING-12 §2.6's kept example `(m: occurrences(/(?<g>a)?b/) & (g: \"a\"))` on `abb` (WHOLE on m's text): NOW %s" % ans3(f, ("abb", "abb", "abb b")))
f1 = E(NOW, lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), ("#hits",))
f2 = E(NOW, lambda: G["OccG0"](Pat(r"\d+"), Pat(r"1\d*"), 1), ("#hits",))
f1n, f2n = E(NOW, lambda: OCC(AND(Pat(r"\d+"), Pat(r"1\d*")), 1), ()), E(NOW, lambda: G["OccG0"](Pat(r"\d+"), Pat(r"1\d*"), 1), ())
print("Z D1 zero-place: the group-0 candidate vs THE LAW's twin, hit lists compared: %s" % dn(f1, f2, G["DSP"]))
print("Z D1 zero-place: the same, holds and stretch only (hit lists NOT compared): %s" % dn(f1n, f2n, G["DSP"]).replace(" (labels compared)", ""))
r = P.Pcre(r"(?J)(?:(?P<x>a)|(?P<x>b))+\k<x>").match("abba", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
r2 = P.Pcre(r"(?J)(?:(?P<x>a)|(?P<x>b))+\k<x>").match("abbb", 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
print("Z A6 duplicate names in a loop, libpcre2: `/(?J)(?:(?<x>a)|(?<x>b))+\\k<x>/` WHOLE on `abba` %s, on `abbb` %s (the capture `\\k<x>` reads the FIRST SET group of the name, `a`; the label x, the last pass's own, is `b`)" % (
    "MATCHES" if r else "FAILS", "MATCHES" if r2 else "FAILS"))

# ================================================================================================= summary
print("== CHECKS (rev 24.3's own): " + "; ".join("%s %s" % (n, "OK" if ok else "FAILED") for n, ok in CHK))
print("== SUMMARY (rev 24.3): predspec242b's output re-run, %d changed hunks (PART 0); rev 24.3 checks %d of %d OK; model U rows %d of %d equal" % (
    nchg, sum(1 for _, ok in CHK if ok), len(CHK), ueq, len(UROWS)))
