#!/usr/bin/env python3
# Lane predspec242b (2026-11-17): the evidence engine of docs/design/predicates_draft.md REVISION 24.2 (the owner's
# rulings of the evening of 2026-11-17 on labels in loops, COND-FAMILY "OWNER RULING — after-loop-read"). DESIGN
# EVIDENCE ONLY; rules nothing.
#
# THE RULE OF REV 24.2 (the settled state): a loop pass has its own labels; a group that took no part in a pass is
# unset in it; a bare condition written after the pattern reads, for a label set inside a loop, THE LAST PASS'S OWN
# value (unset when that pass did not set it); a condition written inside the loop, on the item, is judged in every
# pass and reads that pass's own labels. The CAPTURE stays regex's (PCRE's carried value, read inside rx text).
#
# HOW: lane predspec241's engine (../predspec241_evidence/predspec241_model.py, never edited) is EXECUTED IN MEMORY,
# whole, with five textual patches (each asserted to hit exactly once):
#   P1 its pass-own-labels CANDIDATE becomes the default (`PASSOWN = {"v": PO0}`), so every line it prints is re-run
#      under rev 24.2's rule; P2 its `passown()` context restores the default instead of switching it off;
#   P3-P5 the candidate's three switches act under rev 24's rules only (rev 23.2's BEFORE column is never touched).
# The run under P1 with PO0 = False (the guards only) must reproduce predspec241's committed .out BYTE FOR BYTE: that is
# the SWITCH BACK to rev 24.1's DRAFT READING (PCRE's carry), checked on every run (PART 0).
# A label two loops deep: the engine's pass is the INNERMOST loop's (the owner LEANS to every enclosing loop's: PART N
# runs both, with libpcre2 helper-group models for each).
#
# SWITCHES (W = the worktree; run from $PCREC_TMPDIR/scratch/predspec242b; one process, about 3 minutes):
#   timeout 1800 python3 -I -B W/docs/dev/lanes/predspec242b_evidence/predspec242b_model.py > fwd.out
#   PREDSPEC242B_SABOTAGE=1   after the loop a label reads the FIRST pass's own value (not the last): the owner-shown
#                             tables (PART S) and the pass-own libpcre2 models (PART C2) must fail
#   PREDSPEC242B_RULES=24.1   NOW = rev 24.1's draft reading (PCRE's carry): PART 0's switch is the NOW run; PART A
#                             MOVED 0; PART S prints the STOP lines (the carry answers he was NOT shown)
import os, sys, io, re, contextlib, difflib

HERE = os.path.dirname(os.path.abspath(__file__))
LANES = os.path.dirname(HERE)
F241 = os.path.join(LANES, "predspec241_evidence", "predspec241_model.py")
O241 = os.path.join(LANES, "predspec241_evidence", "predspec241_model.out")
SAB = os.environ.get("PREDSPEC242B_SABOTAGE") == "1"
NOWRULE = os.environ.get("PREDSPEC242B_RULES", "24.2")
if NOWRULE not in ("24.2", "24.1"): sys.exit("PREDSPEC242B_RULES must be 24.2 or 24.1")
for k in ("PREDSPEC241_SABOTAGE", "PREDSPEC241_RULES"): os.environ.pop(k, None)
print("RUN: %s NOW=rev %s" % ("SABOTAGE" if SAB else "forward", NOWRULE))

SRC = open(F241).read()
def patched(po0, sab):
    s = SRC
    def rep(a, b):
        nonlocal s
        assert s.count(a) == 1, (a, s.count(a)); s = s.replace(a, b)
    rep('PASSOWN = {"v": False}', 'PASSOWN = {"v": %s}' % po0)                                         # P1
    rep('        finally: PASSOWN["v"] = False', '        finally: PASSOWN["v"] = %s' % po0)             # P2
    rep('    if PASSOWN["v"]:\n        for l, lp in row.loop.items():', '    if PASSOWN["v"] and RULES["v"] == "24":\n        for l, lp in row.loop.items():')  # P3
    rep('if PASSOWN["v"] and ps: row.last[l] = ps[-1].get(l)', 'if PASSOWN["v"] and RULES["v"] == "24" and ps: row.last[l] = ps[%d].get(l)' % (0 if sab else -1))  # P4
    rep('if not SAB and not PASSOWN["v"]:', 'if not SAB and not (PASSOWN["v"] and RULES["v"] == "24"):')  # P5
    if sab:
        rep('row.last[l] = row.passes[lp][-1].get(l)', 'row.last[l] = row.passes[lp][0].get(l)')
        rep('            return ps[-1].get(l) if ps else None', '            return ps[0].get(l) if ps else None')
    return s
def run241(po0, sab):
    ns = {"__file__": F241, "__name__": "p241"}
    buf = io.StringIO()
    with contextlib.redirect_stdout(buf):
        exec(compile(patched(po0, sab), F241, "exec"), ns)
    return ns, buf.getvalue()

# ================================================================================================= PART 0
print("== PART 0: the premise and the SWITCH BACK (predspec241's engine, patched in memory)")
NS1, OUT1 = run241(False, False)
committed = open(O241).read()
print("0 SWITCH rev 24.1 (PCRE's carry; the patches' guards only) re-run vs predspec241's committed .out: %s (%d lines)" % (
    "BYTE-IDENTICAL" if OUT1 == committed else "DIFFERS", committed.count("\n")))
m = re.search(r"PART A: (\d+) of (\d+) catalogue lines move", OUT1); v7 = re.search(r"PART C V7: libpcre2 \(carry\) vs the engine under pass-own: WHOLE (\d+) .*?SEARCHED (\d+) .*?FIND-ALL (\d+)", OUT1)
print("0 PREMISE rev 24.1's pass-own candidate: PART A %s of %s lines move (rev 24.1 printed 17 of 68); V7 %s / %s / %s of 364 (printed 8 / 33 / 33)" % (
    m.group(1), m.group(2), v7.group(1), v7.group(2), v7.group(3)))
if NOWRULE == "24.2":
    NS, OUT = run241(True, SAB)
else:
    NS, OUT = NS1, OUT1
# the whole of rev 24.1's evidence re-run under the NOW rule: every printed line that changes
a_, b_ = committed.splitlines(), OUT.splitlines()
chg = {}
for op, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a_, b_, autojunk=False).get_opcodes():
    if op == "equal": continue
    for x in a_[i1:i2] + b_[j1:j2]:
        k = x.split(" ")[0] if x[:2] not in ("==",) else "=="
        chg.setdefault(k, set()).add(x)
print("0 RE-RUN rev 24.1's evidence (every printed line) under NOW: lines that differ from the committed .out, per part (old + new lines): %s" % (
    ", ".join("%s %d" % (k, len(v)) for k, v in sorted(chg.items())) or "none"))
for x in b_:
    if x.startswith("== SUMMARY") or x.startswith("== PART A SUMMARY") or x.startswith("== PART B SUMMARY") or x.startswith("== PART C SUMMARY") or x.startswith("== ORDER CHECK SUMMARY") or x.startswith("== PRINTED CHECK"):
        print("0 NOW   " + x)

# ------------------------------------------------------------------------------------------------ handles
G = NS
Pat, W, C, NOT, Rep, OCC, D = G["Pat"], G["W"], G["C"], G["NOT"], G["Rep"], G["OCC"], G["D"]
SOME, NONE, Count, ANDC, ORC, Committed, AND = G["SOME"], G["NONE"], G["Count"], G["ANDC"], G["ORC"], G["Committed"], G["AND"]
lt, eq, num, between = G["lt"], G["eq"], G["num"], G["between"]
strings, lists, candf, fmtl, P = G["strings"], G["lists"], G["candf"], G["fmtl"], G["P"]
REJ = G["REJ"]
RG3, DSP, KHPOOL, CLOSEPOOL, TMPOOL, OCCPOOL, XYPOOL, ABP5, SCX5 = (G[k] for k in ("RG3", "DSP", "KHPOOL", "CLOSEPOOL", "TMPOOL", "OCCPOOL", "XYPOOL", "ABP5", "SCX5"))
REPp, REP1p, CLOSEp, KHp, NUMp, ABXYp = (G[k] for k in ("REPp", "REP1p", "CLOSEp", "KHp", "NUMp", "ABXYp"))
ITEM1, ITEMO = G["ITEM1"], G["ITEMO"]
h5 = G["h5"]

@contextlib.contextmanager
def R(rule):
    """rev 24.2 (pass-own, the NOW rule), rev 24.1 (PCRE's carry) or rev 23.2's rules."""
    old = G["PASSOWN"]["v"]
    with G["rules"]("23.2" if rule == "23.2" else "24"):
        G["PASSOWN"]["v"] = (rule == "24.2")
        try: yield
        finally: G["PASSOWN"]["v"] = old
NOW = NOWRULE
def E(rule, mk, labs=()): return candf(lambda: R(rule), mk, labs)
def fq(s, m, k): return k if k == REJ else fmtl(s, m, k)
def ans3(f, texts): return "WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (texts[0], fq(texts[0], "WHOLE", f("WHOLE", texts[0])), texts[1], fq(texts[1], "SEARCHED", f("SEARCHED", texts[1])), texts[2], fq(texts[2], "FIND-ALL", f("FIND-ALL", texts[2])))
def diffn(f1, f2, pool, modes=("WHOLE", "SEARCHED", "FIND-ALL")):
    out, tot = [], 0
    for m in modes:
        d = [s for s in pool if f1(m, s) != f2(m, s)]
        tot += len(d)
        if d:
            w = min(d, key=lambda x: (len(x), x))
            out.append("%s %d (first `%s`: %s vs %s)" % (m, len(d), w, fq(w, m, f1(m, w)), fq(w, m, f2(m, w))))
        else: out.append("%s 0" % m)
    return "; ".join(out) + " of %d (labels compared)" % len(pool), tot
def dn(f1, f2, pool): return diffn(f1, f2, pool)[0]

# ------------------------------------------------------------------------------------------------ libpcre2 models
class OwnRx:
    """A libpcre2 model of a program under rev 24.2's rule: the pattern carries a HELPER GROUP `(?<ps_X>)` at the start
    of each pass of the loop that owns a label; a callout reads a label as THE PASS'S OWN only when its capture starts
    at or after that pass's helper (else it is unset: an earlier pass set it). `own` maps a label to its helper (labels
    not in `own` are read as PCRE holds them). Tests are callouts `(?C"name")`; a final callout records the reported
    labels (the last successful path's). PCRE itself never unsets a group per pass: this is the callout model of the
    rule (an exception the language requests, §R.6), not a plain regex."""
    def __init__(self, pattern, tests, labs, own):
        self.labs, self.own, self.side = labs, own, {}
        cos = {k: (lambda c, f=f: bool(f(self.vals(c)))) for k, f in tests.items()}
        cos["__end"] = self._end
        self.pattern = pattern
        self.rx = P.Pcre(pattern + '(?C"__end")', cos)
    def vals(self, c):
        v = {}
        for l in set(self.labs) | set(self.own):
            if l in self.own:
                sl, sp = c.span(l), c.span(self.own[l])
                v[l] = None if (sl is None or sp is None or sl[0] < sp[0]) else c.subject[sl[0]:sl[1]]
            else: v[l] = c.get(l)
        return v
    def _end(self, c): self.side = self.vals(c); return True
    def m(self, s, pos=0, opts=0):
        self.side = {}
        r = self.rx.match(s, pos, opts)
        return None if r is None else (r[0], r[1], tuple((l, self.side.get(l)) for l in self.labs))
    def key(self, mode, s):
        if mode == "WHOLE":
            r = self.m(s, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED); return None if r is None else r[2]
        if mode == "SEARCHED": return self.m(s)
        out, pos = [], 0
        while pos <= len(s):
            r = self.m(s, pos)
            if r is None: break
            out.append(r); pos = r[1] if r[1] > r[0] else r[1] + 1
        return tuple(out)
def rxk(model): return lambda m, s: model.key(m, s)
def carryrx(pattern, tests, labs): return OwnRx(pattern, tests, labs, {})   # PCRE's capture state (the CAPTURE's reading)

lt5 = lambda v: v is not None and int(v) < 5
def late(h, m): return num(h) and num(m) and (int(h), int(m)) >= (9, 30)
def jeq(h, m): return (h, m) == ("10", "45")
CHECKS = []                                   # (name, ok) -- each can fail; the sabotage must fail some
def check(name, ok): CHECKS.append((name, ok)); return "OK" if ok else "FAILED"

# ================================================================================================= PART S
# The answers the owner was SHOWN tonight (COND-FAMILY "after-loop-read" and the brief's STOP RULE), recomputed under
# NOW. A difference is a STOP line (the settled state answers otherwise than he was shown).
print("== PART S: the tables the owner was shown (STOP RULE), NOW = rev %s" % NOW)
ALTp = r"(?:(?P<a>\d)|(?P<b>[a-z]))*xx"
ALTx = r"(?:(?<a>\d)|(?<b>[a-z]))*xx"
ALTo = r"(?:(?<ps>)(?:(?<a>\d)|(?<b>[a-z])))*xx"
SHOWN = []
def shown(tag, desc, mk, labs, texts, want):
    f = E(NOW, mk, labs); fc = E("24.1", mk, labs)
    got = tuple(G["fmtk"](t, "WHOLE", f("WHOLE", t) is not None) for t in texts)
    for t, g, w in zip(texts, got, want):
        print("S %s %s on `%s`: NOW %s ; rev 24.1's carry %s ; SHOWN %s%s" % (tag, desc, t, fq(t, "WHOLE", f("WHOLE", t)), fq(t, "WHOLE", fc("WHOLE", t)), w, "" if g == w else "   STOP: differs from what he was shown"))
    SHOWN.append(got == tuple(want))
shown("S1", "`/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)` WHOLE", lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b"), ("3qxx", "q3xx", "7q3xx"), ("FAILS", "HOLDS", "HOLDS"))
f = E(NOW, lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b")); print("S S1   %s" % ans3(f, ("3qxx", "3qxx", "3qxx q3xx 7q3xx")))
mo = OwnRx(ALTo, {"t": lambda v: lt5(v["a"])}, ("a", "b"), {"a": "ps", "b": "ps"})
ALTo2 = ALTo + '(?C"t")'; mo = OwnRx(ALTo2, {"t": lambda v: lt5(v["a"])}, ("a", "b"), {"a": "ps", "b": "ps"})
mc = carryrx(ALTx + '(?C"t")', {"t": lambda v: lt5(v["a"])}, ("a", "b"))
A37 = strings("37qx", 5)
print("S S1   libpcre2 helper-group model `/%s/` vs the engine NOW: %s ; CHECK %s" % (ALTo2, dn(rxk(mo), E(NOW, lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b")), A37),
      check("S1 pass-own model = engine", diffn(rxk(mo), E(NOW, lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b")), A37)[1] == 0)))
print("S S1   plain libpcre2 (the capture's carry) `/%s(?C)/` vs the engine NOW: %s" % (ALTx, dn(rxk(mc), E(NOW, lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b")), A37)))
JJ = lambda **d: C(("h", "m"), jeq, **d)
PO = ("9:45,10,", "10,9:45,", "10:45,10,")
shown("S2", "`CLOSE & ((h, m): == (10, 45))`, CLOSE := /(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*/, WHOLE", lambda: W(Pat(CLOSEp), JJ()), ("h", "m"), PO, ("FAILS", "FAILS", "FAILS"))
shown("S3", "`CLOSE & ((h, m = 00): == (10, 45))` (the default m = 00), WHOLE", lambda: W(Pat(CLOSEp), JJ(m="00")), ("h", "m"), PO, ("FAILS", "FAILS", "FAILS"))
shown("S4", "`CLOSE & ((h, m = 00): == (10, 00))` (the default m = 00, the hour alone), WHOLE", lambda: W(Pat(CLOSEp), C(("h", "m"), lambda h, m: (h, m) == ("10", "00"), m="00")), ("h", "m"), PO, ("HOLDS", "FAILS", "HOLDS"))
for tag, mk in (("S2", lambda: W(Pat(CLOSEp), JJ())), ("S3", lambda: W(Pat(CLOSEp), JJ(m="00")))):
    print("S %s   %s" % (tag, ans3(E(NOW, mk, ("h", "m")), ("9:45,10,", "10,9:45, 10:45,", "9:45,10, 10:45, 10,9:45,"))))
CLo = r"(?:(?<ps>)(?<h>\d+)(?::(?<m>\d\d))?,)*"
JP = lists(["9:45,", "10,", "10:45,", "9,"], 3)
for tag, tf, mk in (("S2", lambda v: jeq(v["h"], v["m"]), lambda: W(Pat(CLOSEp), JJ())),
                    ("S3", lambda v: jeq(v["h"], v["m"] if v["m"] is not None else "00") and v["h"] is not None, lambda: W(Pat(CLOSEp), JJ(m="00")))):
    mo = OwnRx(CLo + '(?C"t")', {"t": tf}, ("h", "m"), {"h": "ps", "m": "ps"})
    d = diffn(rxk(mo), E(NOW, mk, ("h", "m")), JP)
    print("S %s   libpcre2 helper-group model `/%s(?C)/` vs the engine NOW: %s ; CHECK %s" % (tag, CLo, d[0], check("%s pass-own model = engine" % tag, d[1] == 0)))
# the late loop: a condition on the item, inside the loop, judged in every pass
T2C = r"(?P<h>\d{1,2})(?::(?P<m>\d\d))?,"
LATE = lambda: Rep(W(Pat(T2C), C(("h", "m"), late)), 0)
LT = "10:00,9:00,11:00,"
f = E(NOW, LATE, ("h", "m"))
w_, s_ = fq(LT, "WHOLE", f("WHOLE", LT)), fq(LT, "SEARCHED", f("SEARCHED", LT))
print("S S5 `late := time & ((h, m): >= (9, 30))`, `/(?:${late},)*/` on `%s`: WHOLE %s ; SEARCHED %s ; SHOWN WHOLE FAILS, SEARCHED `10:00,`@0%s" % (LT, w_, s_,
      "" if (w_ == "FAILS" and s_.startswith("`10:00,`@0")) else "   STOP: differs from what he was shown"))
SHOWN.append(w_ == "FAILS" and s_.startswith("`10:00,`@0"))
print("S S5   FIND-ALL `%s`: %s" % (LT, fq(LT, "FIND-ALL", f("FIND-ALL", LT))))
print("S S5   %s" % ans3(f, ("10:00,9:45,", "9:00,10:00,", "9:00,10:00, 9:45,9:15,")))
LP3 = lists(["10:00,", "9:00,", "11:00,", "9:45,", "10,"], 3)
mo = OwnRx(r'(?:(?<ps>)(?<h>\d{1,2})(?::(?<m>\d\d))?,(?C"t"))*', {"t": lambda v: late(v["h"], v["m"])}, ("h", "m"), {"h": "ps", "m": "ps"})
mc = carryrx(r'(?:(?<h>\d{1,2})(?::(?<m>\d\d))?,(?C"t"))*', {"t": lambda v: late(v["h"], v["m"])}, ("h", "m"))
d = diffn(rxk(mo), f, LP3)
print("S S5   libpcre2 helper-group model `/%s/` vs the engine NOW: %s ; CHECK %s" % (mo.pattern, d[0], check("S5 pass-own model = engine", d[1] == 0)))
print("S S5   plain libpcre2 (a pass reads the carried m) vs the engine NOW: %s" % dn(rxk(mc), f, LP3))
print("S S5   the same item under rev 24.1's carry vs NOW: %s" % dn(E("24.1", LATE, ("h", "m")), f, LP3))
print("== PART S SUMMARY: %d of %d shown tables reproduced" % (sum(SHOWN), len(SHOWN)))

# ================================================================================================= PART A
print("== PART A: rev 24.1's catalogue (68 lines) under NOW (rev %s) vs rev 24.1 (carry): every moved line, before and after" % NOW)
CAT = G["CAT"]; aW, aS, aF = G["aW"], G["aS"], G["aF"]
mv = []
for tag, site, desc, mk, labs, texts, printed in CAT:
    res = {}
    for r in ("24.1", NOW):
        with R(r):
            Pn = mk(); res[r] = (aW(Pn, texts[0]), aS(Pn, texts[1], labs), aF(Pn, texts[2], labs))
    if res["24.1"] != res[NOW]:
        mv.append(tag)
        print("A %s [%s] %s" % (tag, site, desc))
        print("A %s   BEFORE (rev 24.1) WHOLE `%s` %s ; SEARCHED `%s` %s ; FIND-ALL `%s` %s" % (tag, texts[0], res["24.1"][0], texts[1], res["24.1"][1], texts[2], res["24.1"][2]))
        print("A %s   AFTER  (rev %s) WHOLE %s ; SEARCHED %s ; FIND-ALL %s" % (tag, NOW, res[NOW][0], res[NOW][1], res[NOW][2]))
print("== PART A SUMMARY: %d lines; MOVED %d (%s)" % (len(CAT), len(mv), ", ".join(mv)))

# ================================================================================================= PART B
print("== PART B: §R.4, every way to write an old meaning, OLD (rev 23.2's program and rules) vs NEW (the spelling under rev %s)" % NOW)
WAYS = G["WAYS"]; under = G["under"]
def u(rule, mk):
    cache = {}
    def f(m, s):
        with R(rule):
            if "p" not in cache: cache["p"] = mk()
            return G["KEYS"][m](cache["p"], s)
    return f
zero = 0
for tag, what, old, new, mko, mkn, pool in WAYS:
    d, n = diffn(u("23.2", mko), u(NOW, mkn), pool)
    zero += (n == 0)
    print("B %s %s: OLD %s ; NEW %s" % (tag, what, old, new))
    print("B %s   texts that differ: %s" % (tag, d.replace(" (labels compared)", " (reported row, labels not compared)")))
W1CO = lambda: Rep(W(Pat(ITEMO), h5()), 1)
d, w1cn = diffn(u("23.2", lambda: W(Pat(REPp), h5())), u(NOW, W1CO), RG3)
print("B W1c-restored rev 24's FIRST spelling, item := `/(?<h>\\d)?;/ & (h: <5)` (the OPTIONAL item), vs W1c's old meaning: %s" % d.replace(" (labels compared)", ""))
d2, _ = diffn(u("23.2", lambda: W(Pat(REPp), h5())), u("24.1", W1CO), RG3)
print("B W1c-restored   the same under rev 24.1's carry (rev 24.1's CONTROL): %s" % d2.replace(" (labels compared)", ""))
print("== PART B SUMMARY: %d rows; %d at 0 differences in every mode; W1c's optional item %s" % (len(WAYS), zero, "at 0" if w1cn == 0 else "NOT at 0"))
for t, desc, mo_, mn_, pool in G["CTRL"][1:]:
    print("B %s CONTROL (the comparison can fail) rev 23.2's meaning vs %s, under NOW: %s" % (t, desc.replace("under rev 24", "read under NOW"), dn(u("23.2", mo_), u(NOW, mn_), pool).replace(" (labels compared)", "")))

# ================================================================================================= PART C
print("== PART C: rev 24.1's 38 libpcre2 models against the engine NOW; for each that reads a label across passes, a helper-group model of the rule")
PC = G["PCASES"]; CO = G["CO"]; SM = G["SM"]
eqc, neq = 0, []
for tag, nm, pat, mk, labs, pool in PC:
    rx = pat if isinstance(pat, SM) else P.Pcre(pat, CO)
    d = diffn(G["rxkey"](rx, labs), G["sortk"](E(NOW, mk, labs)), pool)
    if d[1] == 0: eqc += 1
    else: neq.append(tag); print("C %s %s: plain libpcre2 (PCRE's carry) vs the engine NOW: %s" % (tag, nm, d[0]))
print("== PART C SUMMARY (plain PCRE2, the CAPTURE's reading): %d of %d equal to the engine NOW (%s differ)" % (eqc, len(PC), ", ".join(neq) or "none"))
# C2: the helper-group models (the rule's callout model) for the cases that read a label across passes
h_own = {"h": "ps"}
C2 = [
 ("V7", "REP & `(h: <5)`", r'(?:(?<ps>)(?<h>\d)?;)*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: W(Pat(REPp), h5()), RG3),
 ("V8", "REP & `(h: !<5)`", r'(?:(?<ps>)(?<h>\d)?;)*(?C"t")', {"t": lambda v: v["h"] is not None and not lt5(v["h"])}, ("h",), h_own, lambda: W(Pat(REPp), C("h", lambda x: not lt(5)(x))), RG3),
 ("V9", "REP & `NOT (h: <5)`", r'(?:(?<ps>)(?<h>\d)?;)*(?!(?C"t"))', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: W(Pat(REPp), NOT(h5())), RG3),
 ("V29", "CLOSE & `((h = 0, m = 0): (<10, <30))`", r'(?:(?<ps>)(?<h>\d+)(?::(?<m>\d\d))?,)*(?C"t")',
  {"t": lambda v: int(v["h"] or "0") < 10 and int(v["m"] or "0") < 30}, ("h", "m"), {"h": "ps", "m": "ps"},
  lambda: W(Pat(CLOSEp), G["close_R"](h="0", m="0")), CLOSEPOOL),
 ("G1", "item := `/(?<h>\\d)?;/ & (h: <5)`, `/(?:${item})+/` (inside)", r'(?:(?<ps>)(?<h>\d)?;(?C"t"))+', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: Rep(W(Pat(ITEMO), h5()), 1), RG3),
 ("G2", "`occurrences(/(?<x>(?<g>a)?b)/ & (g: \"a\"), min = 1)` (inside)", r'(?:[\s\S]*?(?<ps>)(?<x>(?<g>a)?b)(?C"t"))+[\s\S]*', {"t": lambda v: v["g"] == "a"}, ("x", "g"), {"x": "ps", "g": "ps"},
  lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1), ABP5),
 ("G3", "`/(?:${item})+/ & (h: <5)`, item := `/(?<h>\\d)?;/` (outside)", r'(?:(?<ps>)(?<h>\d)?;)+(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: W(Rep(Pat(ITEMO), 1), h5()), RG3),
 ("G4", "`occurrences(/(?<x>(?<g>a)?b)/, min = 1) & (g: \"a\")` (outside)", r'(?:[\s\S]*?(?<ps>)(?<x>(?<g>a)?b))+[\s\S]*(?C"t")', {"t": lambda v: v["g"] == "a"}, ("x", "g"), {"x": "ps", "g": "ps"},
  lambda: W(OCC(Pat(r"(?P<x>(?P<g>a)?b)"), 1), C("g", eq("a"))), ABP5),
 ("G5i", "two depths, outside, item := `/(?:(?<h>\\d);)+x/` (INNERMOST pass)", r'(?:(?:(?<ps>)(?<h>\d);)+x)+(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: W(Rep(Pat(r"(?:(?P<h>\d);)+x"), 1), h5()), SCX5),
 ("G5e", "the same (EVERY ENCLOSING pass)", r'(?:(?<ps>)(?:(?<h>\d);)+x)+(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: W(Rep(Pat(r"(?:(?P<h>\d);)+x"), 1), h5()), SCX5),
 ("G9i", "two depths, inside, item := `/(?:(?<h>\\d);)+x/ & (h: <5)` (INNERMOST)", r'(?:(?:(?<ps>)(?<h>\d);)+x(?C"t"))+', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: Rep(W(Pat(r"(?:(?P<h>\d);)+x"), h5()), 1), SCX5),
 ("G9e", "the same (EVERY ENCLOSING)", r'(?:(?<ps>)(?:(?<h>\d);)+x(?C"t"))+', {"t": lambda v: lt5(v["h"])}, ("h",), h_own, lambda: Rep(W(Pat(r"(?:(?P<h>\d);)+x"), h5()), 1), SCX5),
 ("G6", "a place inside a place: `occurrences(/(?:(?<h>\\d);)+/, min = 1) & (h: <5)`", r'(?:[\s\S]*?(?<ps>)(?:(?<h>\d);)+)+[\s\S]*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own,
  lambda: W(OCC(Pat(r"(?:(?P<h>\d);)+"), 1), h5()), SCX5),
 ("G10", "a place inside a place, OPTIONAL: `occurrences(/(?:(?<h>\\d)?;)+/, min = 1) & (h: <5)` (INNERMOST)", r'(?:[\s\S]*?(?:(?<ps>)(?<h>\d)?;)+)+[\s\S]*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own,
  lambda: W(OCC(Pat(r"(?:(?P<h>\d)?;)+"), 1), h5()), SCX5),
 ("G10e", "the same (EVERY ENCLOSING: the hit is the outer pass)", r'(?:[\s\S]*?(?<ps>)(?:(?<h>\d)?;)+)+[\s\S]*(?C"t")', {"t": lambda v: lt5(v["h"])}, ("h",), h_own,
  lambda: W(OCC(Pat(r"(?:(?P<h>\d)?;)+"), 1), h5()), SCX5),
 ("S1", "the alternation `/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)`", ALTo2, {"t": lambda v: lt5(v["a"])}, ("a", "b"), {"a": "ps", "b": "ps"}, lambda: W(Pat(ALTp), C("a", lt(5))), A37),
]
c2eq, c2ne, c2ctl = 0, [], 0
for tag, nm, pat, tests, labs, own, mk, pool in C2:
    mo = OwnRx(pat, tests, labs, own)
    d = diffn(rxk(mo), E(NOW, mk, labs), pool)
    dc = diffn(rxk(mo), E("24.1", mk, labs), pool)
    c2eq += (d[1] == 0); c2ctl += (dc[1] > 0)
    if d[1]: c2ne.append(tag)
    print("C2 %s %s  /%s/" % (tag, nm, pat))
    print("C2 %s   vs the engine NOW: %s ; CONTROL vs the engine under rev 24.1's carry: %s" % (tag, d[0], "DIFFERS" if dc[1] else "EQUAL (this model cannot tell the readings apart here)"))
check("C2 helper-group models (the innermost-pass ones) equal the engine", all(t in ("G5e", "G9e", "G10e") or t not in c2ne for t, *_ in C2))
print("== PART C2 SUMMARY: %d of %d helper-group models equal to the engine NOW (%s differ); %d of %d differ from the carry engine (the control)" % (c2eq, len(C2), ", ".join(c2ne) or "none", c2ctl, len(C2)))
# THE ORDER CHECK, re-run under NOW
oc = []
for tag, mksw in (("V19", lambda: W(AND(Pat(G["PCDp"]), Pat(G["PABp"])), ORC(C("a", eq("1")), C("c", eq("1"))))),
                  ("V21", lambda: AND(Pat(r"(?P<c>\d+?)"), Pat(r"(?P<a>\d+)"))), ("V22", lambda: AND(Pat(r"(?P<a>\d+)"), Pat(r"(?P<c>\d+?)")))):
    rx, labs, pool = G["PBY"][tag]
    n = sum(1 for m in ("WHOLE", "SEARCHED", "FIND-ALL") for s in pool if G["rxkey"](rx, labs)(m, s) != G["enkey"](mksw, labs)(m, s))
    oc.append(n > 0)
    print("C ORDER %s the model vs the engine with the operands swapped: %d texts x modes differ: %s" % (tag, n, "DIFFERS (the check can fail)" if n else "EQUAL: GUARDS NOTHING"))
check("ORDER CHECK differs", all(oc))
print("== ORDER CHECK SUMMARY: %d of %d" % (sum(oc), len(oc)))

# ================================================================================================= PART L
print("== PART L: a LABEL is not a CAPTURE (the owner: \"that logic might be justified if you differentiate between a label and a capture\")")
LCAP = r'(?:(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>'
LCo = r'(?:(?<ps>)(?<h>\d+)(?::(?<m>\d\d))?,)*\k<m>'
for t in ("9:45,10,45", "9:45,10:45,45", "10,45"):
    rc = P.Pcre(LCAP).match(t, 0, P.PCRE2_ANCHORED | P.PCRE2_ENDANCHORED)
    mo = OwnRx(LCo + '(?C"t")', {"t": lambda v: v["m"] == "45"}, ("h", "m"), {"h": "ps", "m": "ps"})
    mc = carryrx(LCAP + '(?C"t")', {"t": lambda v: v["m"] == "45"}, ("h", "m"))
    print("L `/(?:(?<h>\\d+)(?::(?<m>\\d\\d))?,)*\\k<m>/ & (m: \"45\")` WHOLE on `%s`: the rx alone (libpcre2; `\\k<m>` reads the CAPTURE) %s%s ; the program, the LABEL m (rev 24.2, helper-group model) %s ; under rev 24.1's carry (the label = the capture) %s" % (
        t, "MATCHES" if rc else "FAILS", (" m = `%s`" % rc[2]["m"]) if rc else "", fq(t, "WHOLE", mo.key("WHOLE", t)), fq(t, "WHOLE", mc.key("WHOLE", t))))
print("L the engine has no backreference node (Python's GROUPREF is not enumerated): this line is libpcre2 only; its label side is the helper-group model PART C2 checks")

# ================================================================================================= PART R
print("== PART R: the constructs rev 24.1's RAMIFICATIONS listed, re-run (rev 24.1's carry vs NOW)")
def both(nm, mk, labs, texts, pool):
    a, b = E("24.1", mk, labs), E(NOW, mk, labs)
    print("R %s: rev 24.1 %s ; NOW %s ; differ: %s" % (nm, "; ".join("`%s` %s" % (t, fq(t, "WHOLE", a("WHOLE", t))) for t in texts), "; ".join("`%s` %s" % (t, fq(t, "WHOLE", b("WHOLE", t))) for t in texts), dn(a, b, pool)))
both("last-pass-default, `REP & (h: <5)`", lambda: W(Pat(REPp), h5()), ("h",), ("3;;", "7;3;", "3;"), RG3)
both("last-pass-default, a mandatory label `/(?:(?<h>\\d);)*/ & (h: <5)`", lambda: W(Pat(REP1p), h5()), ("h",), ("7;3;", "3;7;"), RG3)
both("a per-test default after the loop, `REP & (h = 0: <5)`", lambda: W(Pat(REPp), C("h", lt(5), h="0")), ("h",), ("7;;", "3;;", "7;3;"), RG3)
both("a default after the loop, outside the set, `REP & (h = 9: <5)`", lambda: W(Pat(REPp), C("h", lt(5), h="9")), ("h",), ("3;;", "3;"), RG3)
both("a default inside, item := `/(?<h>\\d)?;/ & (h = 9: <5)`, `/(?:${item})+/`", lambda: Rep(W(Pat(ITEMO), C("h", lt(5), h="9")), 1), ("h",), ("3;;", "3;"), RG3)
both("`REP & some((h: <5)) & occurs.none(NOT (h: <5))` (W1d)", lambda: W(Pat(REPp), SOME(h5()), NONE(NOT(h5()))), ("h",), ("3;;", "3;"), RG3)
both("`REP & occurs.exactly(2, (h: <5))`", lambda: W(Pat(REPp), Count(h5(), lambda n: n == 2)), ("h",), ("3;;3;", "3;3;"), RG3)
both("an alternation in the body, `/(?:(?<a>\\d)|(?<b>[a-z]))*/ & (a: <5)`", lambda: W(Pat(r"(?:(?P<a>\d)|(?P<b>[a-z]))*"), C("a", lt(5))), ("a", "b"), ("3x", "x3", "3"), strings("37x", 5))
both("the same with a terminal, `/(?:(?<a>\\d)|(?<b>[a-z]))*xx/ & (a: <5)`", lambda: W(Pat(ALTp), C("a", lt(5))), ("a", "b"), ("3qxx", "q3xx", "7q3xx"), A37)
both("a bare joint, `CLOSE & ((h, m): == (10, 45))`", lambda: W(Pat(CLOSEp), JJ()), ("h", "m"), PO, JP)
both("a joint on the item, `/(?:${item})*/`, item := `/(?<h>\\d+)(?::(?<m>\\d\\d))?,/ & ((h, m): == (10, 45))`", lambda: Rep(W(Pat(G["ITEMC"]), JJ()), 0), ("h", "m"), PO, JP)
both("`occurrences`, a condition inside (G2)", lambda: OCC(W(Pat(r"(?P<x>(?P<g>a)?b)"), C("g", eq("a"))), 1), ("x", "g"), ("abb", "ab"), ABP5)
both("`occurrences`, bare after (G4)", lambda: W(OCC(Pat(r"(?P<x>(?P<g>a)?b)"), 1), C("g", eq("a"))), ("x", "g"), ("abb", "ab", "abab"), ABP5)
both("a hit of `hits` (committed) and a group question, `hits(/ab(?<g>[xy])?/) & some((g: \"x\"))`", lambda: W(Committed(Pat(r"ab(?P<g>[xy])?")), SOME(C("g", eq("x")))), ("g",), ("abxab", "abab"), strings("abx", 5))

# ================================================================================================= PART J: joint-last-pass dissolves
print("== PART J: joint-last-pass under the rule (a bare joint reads the last pass's own tuple; a per-item joint is written on the item)")
LPT = G["LastPassTest"]
d = diffn(E(NOW, lambda: W(Pat(CLOSEp), JJ()), ("h", "m")), E("24.1", lambda: W(Pat(CLOSEp), LPT(("h", "m"), jeq)), ("h", "m")), JP)
print("J the bare joint NOW vs rev 24.1's candidate 'the last pass's own tuple' (computed by its own node under the carry): %s" % d[0])
for nm, mk in (("bare, after the loop", lambda: W(Pat(CLOSEp), JJ())), ("on the item (every pass)", lambda: Rep(W(Pat(G["ITEMC"]), JJ()), 0)),
               ("`some(J)` (some pass)", lambda: W(Pat(CLOSEp), SOME(JJ())))):
    print("J %s: %s" % (nm, ans3(E(NOW, mk, ("h", "m")), ("9:45,10,", "10,9:45,", "9:45,10, 10:45, 10:45,10,"))))
print("J under rev 24.1's carry, the bare joint (each label's last setting, a tuple no pass held): %s" % ans3(E("24.1", lambda: W(Pat(CLOSEp), JJ()), ("h", "m")), ("9:45,10,", "10,9:45,", "9:45,10, 10:45,")))

# ================================================================================================= PART N: nested-pass
print("== PART N: nested-pass, a label two loops deep: the INNERMOST loop's pass unsets it, or EVERY ENCLOSING loop's pass")
NEST = r"(?:(?:(?P<h>\d)?;)*,)*"
NI = r'(?:(?:(?<ps>)(?<h>\d)?;)*,)*(?C"t")'
NE = r'(?:(?<ps>)(?:(?<h>\d)?;)*,)*(?C"t")'
NC = r'(?:(?:(?<h>\d)?;)*,)*(?C"t")'
NP = strings("37;,", 5)
mi, me, mcar = OwnRx(NI, {"t": lambda v: lt5(v["h"])}, ("h",), h_own), OwnRx(NE, {"t": lambda v: lt5(v["h"])}, ("h",), h_own), carryrx(NC, {"t": lambda v: lt5(v["h"])}, ("h",))
eng = E(NOW, lambda: W(Pat(NEST), h5()), ("h",))
TX = ("3;,,", "3;;,", "3;,7;,", "7;,3;,")
for t in TX:
    print("N `/(?:(?:(?<h>\\d)?;)*,)*/ & (h: <5)` WHOLE `%s`: INNERMOST %s ; EVERY ENCLOSING (the owner's lean) %s ; PCRE's carry (rev 24.1) %s ; the engine NOW %s" % (
        t, fq(t, "WHOLE", mi.key("WHOLE", t)), fq(t, "WHOLE", me.key("WHOLE", t)), fq(t, "WHOLE", mcar.key("WHOLE", t)), fq(t, "WHOLE", eng("WHOLE", t))))
for nm, mod in (("INNERMOST", mi), ("EVERY ENCLOSING", me)):
    print("N %s: %s" % (nm, ans3(rxk(mod), ("3;,,", "3;,, 7;,", "3;,, 3;;, 3;,7;,"))))
print("N INNERMOST vs EVERY ENCLOSING: %s" % dn(rxk(mi), rxk(me), NP))
print("N INNERMOST vs PCRE's carry: %s" % dn(rxk(mi), rxk(mcar), NP))
d = diffn(rxk(mi), eng, NP)
print("N the engine NOW (its pass is the innermost loop's) vs the INNERMOST helper model: %s ; CHECK %s" % (d[0], check("N innermost model = engine", d[1] == 0 or NOW != "24.2")))
# rev 24.1's direct evaluator (WHOLE) for the every-enclosing reading, against the helper model
ev = sum(1 for t in NP if G["nest_ans"]("every", t).startswith("HOLDS") != (me.key("WHOLE", t) is not None))
print("N rev 24.1's direct WHOLE evaluator 'every enclosing' vs the EVERY ENCLOSING helper model: %d of %d differ (holds)" % (ev, len(NP)))
print("N the catalogue: no line of PART A, B or C sets an OPTIONAL label two loops deep; G5, G9 (a mandatory label two deep) and G6 (a loop inside `occurrences`) answer alike under both (PART C2 G5i/G5e, G9i/G9e); G10/G10e (an optional label inside a loop inside `occurrences`) part them")

# ================================================================================================= PART Q
print("== PART Q: what the rule leaves undetermined, and rev 24.1's other questions re-run (NOW vs rev 24.1)")
# value-point: when a label takes its value
print("Q value-point the DRAFT'S READING: a label takes its value when its group closes, visible to the rest of the pass and, if the pass is the last, after the loop. Candidate: at the end of each pass (a condition inside the pass, before the pass ends, sees it unset)")
HH = lambda: Rep(Pat(r"(?P<h>\d);"), 1)
ITEMH = lambda: Rep(W(Pat(ITEM1), h5()), 1)
f1 = E(NOW, ITEMH, ("h",))
f2 = E(NOW, lambda: Rep(W(Pat(ITEM1), C("h", lambda v: False)), 1), ("h",))     # the pass-end candidate: inside the pass h reads unset, the test fails
print("Q value-point   W1a's item `/(?<h>\\d);/ & (h: <5)`, `/(?:${item})+/`: GROUP CLOSE %s ; PASS END %s" % (ans3(f1, ("3;", "3;7;", "3;1; 7;")), ans3(f2, ("3;", "3;7;", "3;1; 7;"))))
print("Q value-point   GROUP CLOSE vs PASS END: %s" % dn(f1, f2, RG3))
print("Q value-point   after the loop the two agree on every catalogue line (a reader after the loop sees the pass ended)")
# before-and-inside
def pre_keep(t):
    if not re.fullmatch(r"\d?(?:;\d?)*", t): return "FAILS"
    segs = t.split(";"); before, passes = segs[0] or None, [x or None for x in segs[1:]]
    v = passes[-1] if (passes and passes[-1]) else before
    return "HOLDS" if (v is not None and int(v) < 5) else "FAILS"
print("Q before-and-inside `/(?<h>\\d)?(?:;(?<h>\\d)?)*/ & (h: <5)` (duplicate names; WHOLE, rev 24.1's direct evaluator): " + " ; ".join(
    "`%s`: carry %s, last pass's own (the pass unsets the outside setting too) %s, the outside setting kept when the last pass set none %s" % (t, G["pre_ans"]("carry", t), G["pre_ans"]("own", t), pre_keep(t))
    for t in ("3", "3;", "3;7", "7;3;", ";3;")))
PP = strings("37;", 5)
print("Q before-and-inside   counts of %d (holds): last pass's own vs keep-outside %d; carry vs last pass's own %d; carry vs keep-outside %d" % (len(PP),
      sum(1 for t in PP if G["pre_ans"]("own", t)[:5] != pre_keep(t)[:5]), sum(1 for t in PP if G["pre_ans"]("carry", t)[:5] != G["pre_ans"]("own", t)[:5]), sum(1 for t in PP if G["pre_ans"]("carry", t)[:5] != pre_keep(t)[:5])))
PRE = r'(?<h0>\d)?(?:;(?<ps>)(?<h>\d)?)*(?C"t")'
def pre_model(keep):
    def t(v): x = v["h"] if v["h"] is not None else (v["h0"] if (keep or v["ps"] is None) else None); return lt5(x)
    return OwnRx(PRE.replace('(?<ps>)', '(?<ps>)'), {"t": t}, ("h", "h0", "ps"), {"h": "ps"})
for nm, keep in (("last pass's own", False), ("keep-outside", True)):
    mo = pre_model(keep)
    dd = sum(1 for t in PP if (mo.key("WHOLE", t) is not None) != ((G["pre_ans"]("own", t) if not keep else pre_keep(t)).startswith("HOLDS")))
    print("Q before-and-inside   libpcre2 model (the outside group renamed h0, the two read as one label) for '%s' vs the direct evaluator: %d of %d differ (holds)" % (nm, dd, len(PP)))
# hits as passes
print("Q hits-pass: a hit of `occurrences` / `contains` as a pass: a bare condition after it reads the LAST HIT's own labels (the engine NOW): G4 above; `hits` (committed) hits are fresh matches under both readings")
H3P = lambda: W(Committed(Pat(NUMp)), NONE(NOT(C("n", lt(100)))))
for slug, nm, mk, labs, texts, pool in (
        ("hits-text", "H3 `hits(/(?<n>\\d+)/) & occurs.none(NOT (n: <100))` (stretch)", H3P, ("#hits",), ("1234", "x300 12", "1234 5 300"), OCCPOOL),
        ("hits-text", "the subject candidate", lambda: W(Committed(Pat(NUMp), 0, True), NONE(NOT(C("n", lt(100))))), ("#hits",), ("1234", "x300 12", "1234 5 300"), OCCPOOL),
        ("hits-committed", "the one-pattern hits `occurrences(/(?<n>\\d+)/) & occurs.none(NOT (n: <100))`", lambda: W(OCC(Pat(NUMp)), NONE(NOT(C("n", lt(100))))), ("#hits",), ("1234", "x300 12", "1234 5"), OCCPOOL),
        ("hits-committed", "an optional label over the one-pattern hits, `occurrences(/a(?<g>x)?/) & (g: \"x\")` (the last hit's own)", lambda: W(OCC(Pat(r"a(?P<g>x)?")), C("g", eq("x"))), ("g", "#hits"), ("axa", "axa", "axa ax"), strings("ax ", 5)),
        ("hits-committed", "the same over the committed list, `hits(/a(?<g>x)?/) & (g: \"x\")`", lambda: W(Committed(Pat(r"a(?P<g>x)?")), C("g", eq("x"))), ("g", "#hits"), ("axa", "axa", "axa ax"), strings("ax ", 5)),
        ("atomic-search", "`atomic(t2) & !q`", lambda: D(G["Atom"](G["mk_t2"]()), G["mk_q"]()), ("h", "m"), ("9:30", "9:30", "9:30 9:15"), G["TP5"]),
        ("join-order", "`G & L` (left outer)", lambda: AND(Pat(r"(?P<a>\d+)"), Pat(r"(?P<c>\d+?)")), ("a", "c"), ("11", "11", "11 123"), DSP),
        ("polarity-rule", "`t2 & NOT (h: <0)`", lambda: W(G["mk_t2"](), NOT(C("h", lt(0)))), ("h",), ("9:30", "x9:30", "9:30 1"), G["TP5"]),
        ("pass-list-read", "last pass: `/(?:(?<h>\\d);)*(?<k>\\d)/ & (k: == $h)`", lambda: W(Pat(G["PLp"]), C(("k", "h"), lambda k, h: k == h)), ("h", "k"), ("3;7;7", "3;7;3", "3;7;7 7;3;3"), RG3),
        ("pass-list-read", "last pass, an OPTIONAL h: `/(?:(?<h>\\d)?;)*(?<k>\\d)/ & (k: == $h)`", lambda: W(Pat(r"(?:(?P<h>\d)?;)*(?P<k>\d)"), C(("k", "h"), lambda k, h: k == h)), ("h", "k"), ("7;;7", "7;;7", "7;;7 3;3"), RG3),
        ("zero-place", "`occurrences(/\\d+/ & (0: /1\\d*/), min = 1)` (innermost)", lambda: OCC(G["ZERO"](Pat(r"\d+"), Pat(r"1\d*")), 1), ("#hits",), (" 1", " 1", " 1 12"), DSP),
        ("operand-context", "`/\\d+/ & /\\b\\d+/` (the stretch)", lambda: AND(Pat(r"\d+"), Pat(r"\b\d+")), (), ("1", "a1 1", "a11 1a1"), G["CTXPOOL"]),
        ("when", "`KH & when((h: <5), (k: between(3, 7)))`", lambda: G["WHEN"](G["KH"](), h5(), G["pk"]()), ("k", "h"), ("5;1;9", "5;1;9", "3;0;5 5;1;9"), KHPOOL)):
    a, b = E("24.1", mk, labs), E(NOW, mk, labs)
    d = diffn(a, b, pool)
    print("Q %s %s: NOW %s ; rev 24.1 vs NOW %s -> %s" % (slug, nm, ans3(b, texts), d[0], "UNCHANGED" if d[1] == 0 else "MOVES"))
# some / occurs read each pass's own labels: equal under both (they read the pass table)
for nm, mk in (("`REP & some((h: <5))`", lambda: W(Pat(REPp), SOME(h5()))), ("`REP & occurs.none(NOT (h: <5))`", lambda: W(Pat(REPp), NONE(NOT(h5())))),
               ("`REP & occurs.exactly(2, (h: <5))`", lambda: W(Pat(REPp), Count(h5(), lambda n: n == 2))), ("`CLOSE & some(((h, m = 00): == (10, 00)))`", lambda: W(Pat(CLOSEp), SOME(C(("h", "m"), lambda h, m: (h, m) == ("10", "00"), m="00"))))):
    a, b = u("24.1", mk), u(NOW, mk)
    print("Q some-own %s: rev 24.1 vs NOW (holds and stretch): %s" % (nm, dn(a, b, RG3 if "REP" in nm else JP).replace(" (labels compared)", "")))
# looped-warning: which programs would warn; answers unchanged
print("Q looped-warning (the manager's proposal): a WARNING when a bare condition after a pattern reads a label set inside a loop; it moves no answer. Programs of this file it would flag: " +
      ", ".join(t for t, _, d_, *__ in CAT if any(k in d_ for k in ("REP", "(?:(?<h>\\d);)*", "occurrences(/\\d+/) &", "KH &"))) )
print("Q looped-warning   the bare form vs the item form it would point at: `/(?:(?<h>\\d);)*/ & (h: <5)` vs `/(?:${item})*/`, item := `/(?<h>\\d);/ & (h: <5)`: %s" % dn(
    u(NOW, lambda: W(Pat(REP1p), h5())), u(NOW, lambda: Rep(W(Pat(ITEM1), h5()), 0)), RG3).replace(" (labels compared)", ""))

# ================================================================================================= summary
print("== CHECKS: " + "; ".join("%s %s" % (n, "OK" if ok else "FAILED") for n, ok in CHECKS))
print("== SUMMARY: switch rev 24.1 %s; shown tables %d of %d; catalogue %d lines, MOVED %d; old meanings %d rows, %d at 0, W1c optional %s; plain libpcre2 %d of %d equal; helper-group models %d of %d equal; order check %d of %d; checks %d of %d OK" % (
    "BYTE-IDENTICAL" if OUT1 == committed else "DIFFERS", sum(SHOWN), len(SHOWN), len(CAT), len(mv), len(WAYS), zero, "at 0" if w1cn == 0 else "NOT at 0",
    eqc, len(PC), c2eq, len(C2), sum(oc), len(oc), sum(1 for _, ok in CHECKS if ok), len(CHECKS)))
