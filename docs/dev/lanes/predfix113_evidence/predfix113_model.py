#!/usr/bin/env python3
"""predfix113_model.py: lane predfix113's evidence, the successor of predfold1128_model.py.

Review r113 (of the fold predfold1128) applied to the predicate documents as RULED by the predicate manager
(the dispositions filed with docs/dev/reviews/2026-11-27-r113-predfold1128.md). DESIGN evidence only: nothing here
rules; no check under `make` reads it.

It LOADS predfold1128's model unchanged up to its checks (`# ==== CHECKS128`; the older models load through it), then
puts, switched by X113[0] (off: predfold1128's walker, front ends and engine as merged, the control):
  LIT113      EXAMPLES-1: the strong lean read literally. A label the SENDER writes in an argument is reached across
              the place only from a binding that USES the sender (a `use` node above the call: `Y.a.h`, `X.a.h`,
              caller-label-export), never from a label in the sender's own text above the call
              (`k.a.h` over `[k = [c = B([a = A])]]`, an error). LIT113[0] off is predfold1128's PLACE128 boundary
              ("a label directly on the call"), the other reading, RUN.
  EXP113      `_exports128` also hides a group inside an underscore group (`/(?<_g>(?<h>\\d))/` exports no `h`,
              core/labels/export statement 3): RULING-6's underscore line.
  ROWS113     RULING-6 rows 1 and 8, each a switch between its two readings (printed reading first):
              ROW1_113 "error" (nested-scope: a body reading its named list's label bare is refused at its
              definition) / "legal" (the body reads what its list names: the call inlined as `[(=h) = A] & cond`);
              ROW8_113 "one-path" (an argument holding `h` in two labelled parts: the use error naming both) /
              "last" (the ruled edge read for parts: the last part's label, `b.h`).
  CHECKED113  RULING-3: "error" (the fold's reading; the loaded engine refuses `checked`) / "new" (line 4's second
              sentence a NEW rule: the call replaced by its body with the parameter's name put for the argument's).
Every switch is RUN both ways by OPEN113; the other readings' answers are compared with regexes written by hand.
The verdict is the last line, `predfix113_model: N checks, F failed`; it exits non-zero iff that line reports a
failure.
PINNED COMMITS: this model reads git ONLY by commit id (START113). The older models it re-runs read by commit id too,
but for predfold1123_model.py (`lane/pred-rev28:`), a historical lane file not edited here.
`PREDFIX113_LIGHT=1` skips SUCCESSOR113; `PREDFIX113_SUCCDIR=DIR` an existing EMPTY scratch directory for the
successor outputs; `PREDFIX113_READDUMP=1` reads DIR instead of re-running; `PREDFIX113_WRITEDECL=F` writes the seen
reds as a declaration draft; `PREDFIX113_SABOTAGE=sN` plants one wrong rule, fact or text per check (PLANTS113);
`=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfix113_model.py` from the worktree root.
"""
import builtins
import os
import re
import subprocess
import sys

MY113 = os.path.abspath(__file__)
HERE113 = os.path.dirname(MY113)
LANES113 = os.path.normpath(os.path.join(HERE113, ".."))
P128 = os.path.join(LANES113, "predfold1128_evidence", "predfold1128_model.py")
START113 = "8fa0108f9"                                       # this lane's starting commit (lane/predfix113), PINNED
SAB113 = os.environ.get("PREDFIX113_SABOTAGE", "")
LIGHT113 = os.environ.get("PREDFIX113_LIGHT") == "1"
_src128 = builtins.open(P128, encoding="utf-8").read()
_a113 = _src128.index("\n# ==== CHECKS128 (a probe loads the model up to this line)") + 1
_sav113 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFOLD1128_", "PREDFIX112_", "PREDFOLD1127_", "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P128
exec(compile(_src128[:_a113], P128, "exec"), globals())      # noqa: S102  predfold1128's engines, unchanged
__file__ = MY113
os.environ.update(_sav113)
X113 = [True]
LIT113 = [True]
ROW1_113 = ["error"]
ROW8_113 = ["one-path"]
CHECKED113 = ["error"]
MARK113 = "(the owner's strong lean, entailed by carve-out-reading and caller-label-export; to be confirmed)"


def s113(q):
    return SAB113 == q


# ================================================================== LIT113: the lean read literally (EXAMPLES-1)
def _between(start, x, P):                                   # noqa: F811
    """predfold1128's PLACE128 with one boundary changed: a sender's label across the place is kept only where a
    binding's USE lies above the call on the chain (the path enters the sender's text from outside)."""
    out = _BETWEEN112(start, x, P)                           # noqa: F821
    if not X128[0]:                                          # noqa: F821
        return out
    res = []
    for node, betw, gates, walls, chain in out:
        bad = [n for n in chain[1:] if n.k == "arg" and not _listed128(n)]   # noqa: F821
        if bad:
            last = bad[-1]
            below = chain[chain.index(last) + 1:]
            sender = (len(bad) == 1 and node.k == "label" and not node.name.startswith("_")
                      and not any(n.k in ("call", "arg") for n in below[:-1]))
            c = _call_of128(last)                            # noqa: F821
            j = next((i for i, n in enumerate(chain) if n is c), -1)
            if X113[0] and LIT113[0]:
                outside = j >= 0 and any(n.k == "use" for n in chain[:j])
                if s113("s1"):
                    outside = True
                ok = sender and outside
            else:
                on_call = j < 0 or not any(_named(n) for n in chain[1:j])   # noqa: F821
                ok = sender and not on_call
            if not ok:
                DROP128[-1].append((last, c))                # noqa: F821
                continue
        if CROSS128 and any(n.k == "arg" for n in chain[1:]):   # noqa: F821
            CROSS128[-1] = True                              # noqa: F821
        res.append((node, betw, gates, walls, chain))
    return res


# ================================================================== EXP113: an underscore group hides its groups
_EXP128 = _exports128                                        # noqa: F821


def _under_underscore113(body):
    out = set()
    for m in re.finditer(r"\(\?<_\w*>", body):
        depth, j = 1, m.end()
        while j < len(body) and depth:
            depth += {"(": 1, ")": -1}.get(body[j], 0)
            j += 1
        out |= set(re.findall(r"\(\?<(\w+)>", body[m.end():j]))
    return out


def _exports128(name, defs, seen=()):                         # noqa: F811
    out = _EXP128(name, defs, seen)
    if not X113[0] or name not in defs or s113("s2"):
        return out
    return out - _under_underscore113(defs[name][1])


# ================================================================== ROWS113 and CHECKED113: the front end
_PROG128 = prog                                              # noqa: F821


def _row1_113(e, binds, defs):
    for n, (head, body, _) in defs.items():
        ps = _params128(head) if head else []                # noqa: F821
        if len(ps) != 1 or ps[0][0] is None:
            continue
        m = re.fullmatch(r"/\$\{\[\s*\(=(\w+)\)\s*=\s*%s\s*\]\}/\s*&\s*(\(\s*(\w+)\s*:.*\))" % re.escape(ps[0][0]), body)
        if not m or m.group(3) != m.group(1):
            continue
        if ROW1_113[0] == "error":
            raise CompileError("at %s's definition: `%s` is a label its parameter holds, not its to name "   # noqa: F821
                               "(core/holes/bare-condition/nested-scope; a marked reading)" % (n, m.group(1)))
        for a, b, args in reversed(_calls128(e, n)):         # noqa: F821
            e = e[:a] + "[(=%s) = %s] & %s" % (m.group(1), args[0], m.group(2)) + e[b:]
        binds = [x for x in binds if n not in _defs128([x])]   # noqa: F821
    return e, binds


def _row8_113(e, binds, defs):
    for g in defs:
        if not defs[g][0]:
            continue
        for a, b, args in _calls128(e, g):                   # noqa: F821
            for k, arg in enumerate(args):
                m = re.fullmatch(r"\[\s*\w+\s*=\s*\w+\s*\](?:\s*SEQ\s*\[\s*\w+\s*=\s*\w+\s*\])+", arg.strip())
                if not m:
                    continue
                parts = re.findall(r"\[\s*(\w+)\s*=\s*(\w+)\s*\]", arg)
                for lab, by, lst in _demands128(defs, g, k):   # noqa: F821
                    holders = [p for p, src in parts if lab in _exports128(src, defs)]
                    if len(holders) < 2:
                        continue
                    if ROW8_113[0] == "one-path":
                        raise CompileError("at `%s`: two labels `%s` in the argument, %s, which %s's list `%s` cannot "   # noqa: F821
                                           "pick between (core/labels/rule/one-path; a marked reading)" % (
                                               e[a:b], lab, " and ".join("`%s.%s`" % (h_, lab) for h_ in holders), by, lst))
                    last = holders[-1] if not s113("s4") else holders[0]
                    e = e[:a] + "(" + arg + ")" + e[b:]
                    e = re.sub(r"(?<![\w.])%s\.%s(?!\w)" % (re.escape(g), lab), "%s.%s" % (last, lab), e)
                    return e, [x for x in binds if g not in _defs128([x])]   # noqa: F821
    return e, binds


def _checked113(e, binds, defs):
    if CHECKED113[0] != "new":
        return e, binds
    for n, (head, body, _) in defs.items():
        ps = _params128(head) if head else []                # noqa: F821
        if len(ps) != 1 or ps[0][0] is None:
            continue
        p = ps[0][0]
        if not re.fullmatch(r"%s\s*&\s*\(\s*%s\.\w+\s*:.*\)" % (re.escape(p), re.escape(p)), body):
            continue
        for a, b, args in reversed(_calls128(e, n)):         # noqa: F821
            e = e[:a] + re.sub(r"(?<![\w.])%s(?![\w(])" % re.escape(p), args[0], body) + e[b:]
        binds = [x for x in binds if n not in _defs128([x])]   # noqa: F821
    return e, binds


def prog(expr, binds=(), **opts):                            # noqa: F811
    if X113[0] and X128[0]:                                  # noqa: F821
        binds = list(binds)
        defs = _defs128(binds)                               # noqa: F821
        expr, binds = _row1_113(expr, binds, defs)
        if not s113("s3"):
            expr, binds = _row8_113(expr, binds, _defs128(binds))   # noqa: F821
        expr, binds = _checked113(expr, binds, _defs128(binds))     # noqa: F821
    return _PROG128(expr, binds, **opts)


# ==== CHECKS113 (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821
AH = "A := /(?<h>\\d)/"
BP = "B(rx) := /${[p = rx]}xx/"
YB = 'Y := [c = B([a = A])] SEQ "!"'
NB = "N(rx) := /${[(=h) = rx]}/"
ISO = 'isodate := [year = /\\d{4}/] SEQ "-" SEQ [month = /\\d\\d/] SEQ "-" SEQ [day = /\\d\\d/]'
TX = ["3xx", "7xx", "4xx", "x3xx", "3xxx"]
TXB = ["3xx!", "7xx!", "4xx!", "x3xx!"]


def unit113(name, what):
    print("== %s: %s" % (name, what))


_ANS113, _RE113 = ans11, RePg                                # noqa: F821  bound here: a later sliced-in reader rebinds a name


def same_as(P, rx_, texts):
    """the program's answers (whole, searched, find-all) against a regex written by hand from the reading."""
    return P is not None and _ANS113(P, texts) == _ANS113(_RE113(rx_), texts)


D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
JOIN113 = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in DOCF}   # noqa: F821
OLD113 = {f_: _git8("docs/design/predicates/" + f_, START113) for f_ in DOCF}   # noqa: F821

unit113("CANARY113", "LIT113 off is predfold1128's boundary (the control): `k.a.h` over `[k = [c = B([a = A])]]` "
        "legal; on refused naming the place; `Y.a.h` and `X.a.h` (caller-label-export) legal both ways")
KAH = ("[k = [c = B([a = A])]] & (k.a.h: <5)", [AH, BP])
LIT113[0] = False
c0 = run11(*KAH)                                             # noqa: F821
LIT113[0] = True
c1 = run11(*KAH)                                             # noqa: F821
ya = run11("Y & (Y.a.h: <5)", [AH, BP, YB])                  # noqa: F821
xa = run11("X & (X.a.h: <5)", [AH, BP, YB, 'X := [y = Y] SEQ ";"'])   # noqa: F821
check("CANARY113", c0[0] is not None and c1[0] is None and "argument place" in (c1[1] or "")   # noqa: F821
      and same_as(ya[0], r"[0-4]xx!", TXB) and same_as(xa[0], r"[0-4]xx!;", [t_ + ";" for t_ in TXB]),
      "off: %s; on: %s; Y.a.h %s; X.a.h %s" % ("legal" if c0[0] else c0[1], (c1[1] or "LEGAL")[:110],
                                              "legal" if ya[0] else ya[1], "legal" if xa[0] else xa[1]))

unit113("OPEN113", "each marked cell this lane prints, BOTH readings RUN: the printed reading refused as its line "
        "says; the other reading legal, its answers equal to a regex written by hand AND printed verbatim in the "
        "documents (continuation lines joined)")
OPEN = [  # name, program, binds, switch, printed value, other value, hand regex, (wholes, searched, find-all), refusal word
    ("EXAMPLES-1 k.a.h", KAH[0], KAH[1], LIT113, True, False, r"[0-4]xx", (["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx"),
     "argument place"),
    ("RULING-6 row 1 N2", "N2(A)", [AH, "N2(rx) := /${[(=h) = rx]}/ & (h: <5)"], ROW1_113, "error", "legal", r"[0-4]",
     (["3", "7"], "7 3", "3 7 4"), "not its to name"),
    ("RULING-6 row 8", "N([a = P] SEQ [b = Q]) & (N.h: <5)", ["P := /(?<h>\\d)/", "Q := /,(?<h>\\d)/", NB], ROW8_113,
     "one-path", "last", r"\d,[0-4]", (["7,3", "3,7"], "3,7 7,3", "7,3 3,7 1,2"), "`a.h` and `b.h`"),
    ("RULING-3 checked", "checked(isodate)", ["checked(B) := B & (B.year: < 2100)", ISO], CHECKED113, "error", "new",
     r"(?:20\d\d|1\d\d\d|0\d\d\d)-\d\d-\d\d",
     (["2024-02-29", "2150-01-01"], "x 2150-01-01 1999-12-31", "2024-02-29 2150-01-01 1999-12-31"), "does not hold"),
]
op_bad, OPENTXT113 = [], []
_FMT113 = fmt                                                # noqa: F821
ALLJ = " ".join(JOIN113[f_] for f_ in BASES11)               # noqa: F821
for nm_, e_, b_, sw_, pv_, ov_, rx_, (wh_, se_, fa_), word_ in OPEN:
    sw_[0] = pv_
    P0, e0 = run11(e_, b_)                                   # noqa: F821
    sw_[0] = ov_
    P1, e1 = run11(e_, b_)                                   # noqa: F821
    sw_[0] = pv_
    txt = _FMT113(P1, wh_, se_, fa_) if P1 is not None else ""
    OPENTXT113.append(txt)
    if s113("s5") and nm_.startswith("RULING-3"):
        txt = txt.replace("HOLDS", "FAILS", 1)
    printed = bool(txt) and txt in ALLJ
    ok_ = P0 is None and word_ in (e0 or "") and same_as(P1, rx_, wh_ + [se_]) and printed
    print("   %-20s printed reading: %s | other: %s; hand regex %s; printed in the documents: %s" % (
        nm_, (e0 or "LEGAL")[:90], txt[:90] or (e1 or "")[:90], same_as(P1, rx_, wh_ + [se_]), printed))
    if not ok_:
        op_bad.append(nm_)
check("OPEN113", not op_bad, "%d cells, both readings run; not as printed: %s" % (len(OPEN), op_bad or "none"))   # noqa: F821

unit113("SWEEP113", "every printed three-mode line RUN under this model; the starting commit %s's lines under the "
        "control (X113 off: predfold1128 as merged) against these, keyed by the program; every key gone or moved "
        "DECLARED" % START113)
_sw113a = _src128.index('exec(compile(_src11[_src11.index("def sw11(docs):")')
_sw113b = _src128.index("OLD128 = {f_: _git8(")
exec(compile(_src128[_sw113a:_sw113b], P128, "exec"), globals())     # noqa: S102  the sweep and error-line readers, verbatim
X113[0] = False
OLD_T113 = sw11(OLD113)                                      # noqa: F821
X113[0] = True
NOWS113 = dict(NOWS)                                         # noqa: F821
if s113("s6"):
    NOWS["core.md"] = NOWS["core.md"].replace("His remedy: WHOLE `3-7` HOLDS", "His remedy: WHOLE `3-7` FAILS", 1)   # noqa: F821
NEW_T113 = sw11(NOWS)                                        # noqa: F821
NOWS.update(NOWS113)                                         # noqa: F821
GONE113 = {   # a printed line whose program this lane moved: key -> why
    "Bo(Ad) & (Bo.d: <5)": "EXAMPLES-2: \"His remedy\" re-written with the body's `d` under `q` (the separating "
                           "witness); the old program, the same answers as the line before it, is gone",
}
MOVED113 = {}
inh = set((k_, f_, st_) for k_, vs in OLD_T113.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt, used = [], [], [], [], [], {}, set()
for k_, vs in NEW_T113.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            (sw_inh if (k_, f_, st_) in inh else sw_bad).append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T113.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T113.get(k_, []) if v_[0] == f0]
        if nk:
            po, pn = sorted(set(v_[4] for v_ in vs)), sorted(set(v_[4] for v_ in nk))
            if po != pn:
                if k_[0] in MOVED113:
                    used.add(k_[0])
                    print("   MOVED BY A RULING %s `%s`: %s" % (f0, k_[0], MOVED113[k_[0]]))
                else:
                    sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE113:
            used.add(k_[0])
            print("   DROPPED OR MOVED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE113[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale = sorted(k_ for k_ in list(GONE113) + list(MOVED113) if k_ not in used)
for k_, vs in NEW_T113.items():
    if k_ not in OLD_T113:
        sw_new.append((vs[0][0], vs[0][1], k_[0], vs[0][3][:150]))
for x_ in sw_new:
    print("   ADDED %s:%d `%s`: %s" % x_)
for x_ in sw_gone:
    print("   GONE %s:%d %r (was %s)" % x_)
for x_ in sw_moved:
    print("   MOVED %s %r\n      old: %s\n      now: %s" % x_)
for x_ in sw_bad:
    print("   BAD %s:%d %s `%s`: %s" % x_)
for x_ in stale:
    print("   STALE DECLARATION %s" % x_)
check("SWEEP113", OLD_T113 and not sw_bad and not sw_moved and not sw_gone and not stale and len(sw_new) >= 3,   # noqa: F821
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T113.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T113), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE113) + len(MOVED113),
          len(sw_new), len(stale)))

unit113("ERRSWEEP113", "every printed compile-error line of the base files refused under this model, no crash; each "
        "named form in the refusal's message (predfold1128's rows, and this lane's)")
_mg113a = _src128.index("MSG128 = dict(MSG112)")
_mg113b = _src128.index("es_bad, es_msg = [], []", _mg113a)
exec(compile(_src128[_mg113a:_mg113b], P128, "exec"), globals())     # noqa: S102  predfold1128's message rows, verbatim
MSG113 = dict(MSG128)                                        # noqa: F821
MSG113.update({
    KAH[0]: "argument place",
    "N(Au) & (N.h: <5)": "(=h)",
    "N(As) & (N.h: <5)": "(=h)",
    "N(Aw) & (N.h: <5)": "(=h)",
    "N2(A)": "not its to name",
    "N([a = P] SEQ [b = Q]) & (N.h: <5)": "`a.h` and `b.h`",
    "checked(isodate)": "does not hold",
    "Bo(Ad) & (Bo.d: <5)": "`Bo.q.d`",
})
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s113("s7"):
    D8["core.md"] = D8["core.md"].replace("Lacking it, behind an underscore group: modes: a compile error (`N(Au) & (N.h: <5)`, Au := `/(?<_g>(?<h>\\d))/`",
                                          "Lacking it, behind an underscore group: modes: a compile error (`N(Au) & (N.h: <5)`, Au := `/(?<g>(?<h>\\d))/`", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines({f_: _enc_ref128(v_) for f_, v_ in D8.items()}) if not x_[0].endswith("_details.md")]   # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG113 and MSG113[e_] not in err:
        es_msg.append((f_, ln_, e_, MSG113[e_], err[:140]))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
for x_ in es_msg:
    print("   MESSAGE %s:%d `%s` lacks %s: %s" % x_)
msg_unseen = sorted(set(MSG113) - set(e_ for _, _, e_, _ in es_now))
check("ERRSWEEP113", es_now and not es_bad and not es_msg and not msg_unseen,   # noqa: F821
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s" % (len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none"))

unit113("SPECLINES113", "every printed line new in this lane (not in its file at the starting commit) is RUN: a "
        "three-mode line SAME as run, a compile-error line refused")
newset = {f_: set(NOWS[f_].split("\n")) - set(OLD113[f_].split("\n")) for f_ in BASES11}   # noqa: F821
nl3, nle, nl_bad, nl_names = 0, 0, [], []
for k_, vs in NEW_T113.items():
    for f_, ln_, st_, got_, pr_ in vs:
        if f_ in newset and NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:   # noqa: F821
            nl3 += 1
            nl_names.append(NOWS[f_].split("\n")[ln_ - 1].split(":")[0])   # noqa: F821
            if st_ != "same":
                nl_bad.append((f_, ln_, st_))
for f_, ln_, e_, b_ in es_now:
    if NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:           # noqa: F821
        nle += 1
        nl_names.append(NOWS[f_].split("\n")[ln_ - 1].split(":")[0])   # noqa: F821
        if run11(e_, b_)[0] is not None:                      # noqa: F821
            nl_bad.append((f_, ln_, "legal"))
nl_lines = [(f_, L_) for f_ in BASES11 for L_ in newset[f_] if re.search(r"WHOLE `|modes: a compile error", L_)
            and not L_.startswith(("-", " "))]               # noqa: F821
nl_bul = [(f_, L_) for f_ in BASES11 for L_ in newset[f_] if "WHOLE `" in L_ and L_.startswith(("-", " "))]   # noqa: F821
bul_bad = [L_[:80] for f_, L_ in nl_bul                     # a bullet's answers are an OPEN113 run, printed verbatim
           if not any(t_.startswith(" ".join(L_.split("WHOLE ", 1)[1].split())) for t_ in [x_[6:] for x_ in OPENTXT113])]
nl_all = len(nl_lines) + (1 if s113("s8") else 0)
for n_ in sorted(nl_names):
    print("   RUN %s" % n_)
check("SPECLINES113", not nl_bad and not bul_bad and nl3 + nle == nl_all and nl_all >= 12, "%d new printed lines: "   # noqa: F821
      "three-mode %d, compile-error %d, unread %d; not as printed: %s; %d bullets carrying a reading's answers, not an "
      "OPEN113 run: %s" % (nl_all, nl3, nle, nl_all - nl3 - nle, nl_bad or "none", len(nl_bul), bul_bad or "none"))

unit113("HAND113", "the new legal lines' answers against regexes written by hand (a second source beside the sweep): "
        "the remedy (the body's `d`), `hits.g` and `occurrences.n` against the printed `.hit` lines of their piece")
hd_bad = []
rm_ = run11("Bo(Ad) & (Bo.d: <5)", ["Ad := /(?<d>\\d)/", "Bo(rx) := /${[q = /(?<d>\\d)/]}-${[(=, _ = d) = rx]}/"])[0]   # noqa: F821
if not same_as(rm_, r"[0-4]-\d" if not s113("s9") else r"\d-[0-4]", ["3-7", "7-3", "3-3", "7-7", "7-7 3-7"]):
    hd_bad.append("His remedy")
LIBJ = JOIN113["library.md"]
for new_, old_ in [('(`hits(/a(?<g>x)?/) & (hits.g: "x")`', '(`hits(/a(?<g>x)?/) & (hits.hit.g: "x")`'),
                   ('(`occurrences(/(?<n>\\d+)/) & (occurrences.n: "3")`', '(`occurrences(/(?<n>\\d+)/) & (occurrences.hit.n: "3")`')]:
    ln_new = next((L_ for L_ in NOWS["library.md"].split("\n") if new_ in L_), "")   # noqa: F821
    ln_old = next((L_ for L_ in OLD113["library.md"].split("\n") if old_ in L_), "")
    a_new = re.search(r"WHOLE .*? / FIND-ALL [^(]*\]", ln_new)
    a_old = re.search(r"WHOLE .*? / FIND-ALL [^(]*\]", ln_old)
    ok_ = a_new and a_old and a_new.group(0) == a_old.group(0)
    print("   %-60s answers equal to the printed `%s` line at %s: %s" % (new_[2:62], old_[2:40], START113, bool(ok_)))
    if not ok_:
        hd_bad.append(new_)
check("HAND113", not hd_bad, "3 lines; differing: %s" % (hd_bad or "none"))   # noqa: F821

unit113("MARK113", "the strong lean's mark: the exact phrase counted (the start's count, less the two RULING-4 drops, "
        "plus its four adds); dropped and added at the named sites; the re-worded site; no variant phrase")
mk_old = sum(OLD113[f_].count(MARK113) for f_ in BASES11)   # noqa: F821
mk_now = {f_: NOWS[f_].count(MARK113) for f_ in BASES11}    # noqa: F821
DROP_SITES = ["Two binding levels, the sender's label: WHOLE", "Through a call, the sender's name: WHOLE"]
ADD_SITES = ["In the sender's own text the call's label and the macro's name are paths through the place alike",
             "A label above the call's label: modes: a compile error",
             "a read through the call reaches the argument only through a list on its place (argument-place)",
             "never through the call's label or the macro's name (`Y.c.a.h` caller-label-export; `B.a.h` a reading"]
if s113("s10"):
    ADD_SITES.append("Through a call, the body's label itself: WHOLE")


def _site113(start):
    i = JOIN113["core.md"].find(start)
    if i < 0:
        return None
    j = JOIN113["core.md"].find("\n", i)
    return JOIN113["core.md"][i:j]


mk_bad = []
for s_ in DROP_SITES:
    t_ = _site113(s_)
    if t_ is None or MARK113 in t_:
        mk_bad.append(("drop", s_))
for s_ in ADD_SITES:
    t_ = _site113(s_)
    if t_ is None or MARK113 not in t_:
        mk_bad.append(("add", s_))
rw_ = _site113("Through the call's label: modes: a compile error")
if not rw_ or "read `Y.a.h` (ruled, caller-label-export; its ground the strong lean, to be confirmed); `Y.c.h` alike " + MARK113 not in rw_:
    mk_bad.append(("re-worded", "Through the call's label"))
bad_phr = [f_ for f_ in BASES11 if re.search(r"the owner's strong lean(?!, entailed by carve-out-reading and caller-label-export; to be confirmed)", NOWS[f_])]   # noqa: F821
want_ = mk_old - len(DROP_SITES) + len(ADD_SITES)
check("MARK113", not mk_bad and not bad_phr and sum(mk_now.values()) == want_,   # noqa: F821
      "%d marked sites now (%s); at %s %d; expected %d; sites not as ruled: %s; a variant phrase: %s" % (
          sum(mk_now.values()), ", ".join("%s %d" % kv for kv in sorted(mk_now.items())), START113, mk_old, want_,
          mk_bad or "none", bad_phr or "none"))

unit113("QUOTES113", "RULING-1: param-reference's lines as printed, each a verbatim substring of the record at the "
        "PINNED start commit (line 3 with \"own\"; lines 1-2 and 4 quoted apart, no splice)")
REC113 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START113)   # noqa: F821
RW = ws(REC113)                                              # noqa: F821
ref_ = ws(piece8("core/operators/bindings/reference"))      # noqa: F821
call_ = ws(piece8("core/operators/bindings/reference-call"))   # noqa: F821
if s113("s11"):
    call_ = call_.replace("by the caller's own path rules", "by the caller's path rules")
q1 = re.search(r'lines 1, 2 and 4 as asked \(line 3: core/operators/bindings/reference-call\): "(1\. .*?did not list\.)"; line 4: "(4\. .*?as today\.)"', ref_)
q3 = re.search(r'line 3 as asked: "(3\. .*?error at the call\.)"', call_)
qs = ([q1.group(1), q1.group(2)] if q1 else []) + ([q3.group(1)] if q3 else [])
q_bad = [q_[:60] for q_ in qs if q_ not in RW]
stmt_ok = "each listed label is read there by the caller's own path rules" in call_.split("needs:")[0]
check("QUOTES113", len(qs) == 3 and not q_bad and stmt_ok and "by the caller's own path rules" in (qs[2] if len(qs) == 3 else ""),   # noqa: F821
      "%d quotes found (lines 1-2, 4, 3); not in the record at %s: %s; the statement carries \"own\": %s" % (
          len(qs), START113, q_bad or "none", stmt_ok))

unit113("STALE113", "the texts this lane retires, searched with continuation lines joined: none printed")
STALE113 = [
    ("core.md", r"takes the named label as the body's own", "RULING-2: named-list's withdrawn meaning"),
    ("library.md", r"takes every label the argument exports as the body's own", "RULING-2: argument-labels"),
    ("core.md", r"by the caller's path rules", "RULING-1: \"own\" dropped"),
    ("core.md", r"did not list\. 4\. \*\*Nothing", "RULING-1: the splice"),
    ("core.md", r"Bo\(rx\) := `/\(\?<d>\\d\)-\$\{\[\(=, _ = d\) = rx\]\}/`", "EXAMPLES-2: the remedy that separated nothing"),
    ("core.md", r"the label a parameter holds is not its to name\.", "RULING-5: nested-scope's statement without its exception"),
    ("core.md", r"body would name it through the parameter, `d\.year` \(a reading; not asked\)", "RULING-3: macro-types' unmarked reading"),
    ("core.md", r"- \"Places and then reads\", as today:", "RULING-3: the unmarked bullet"),
    ("parked.md", r"Trigger: a valid, safe set of rules for it \(his words\)", "RULING-5: the fired trigger"),
]
if s113("s12"):
    STALE113.append(("core.md", r"His remedy", "planted"))
st_hits = [(f_, why) for f_, rx_, why in STALE113 if re.search(rx_, JOIN113[f_])]
for x_ in st_hits:
    print("   STALE %s (%s)" % x_)
check("STALE113", not st_hits, "%d retired texts searched; found %s" % (len(STALE113), st_hits or "none"))   # noqa: F821

unit113("TEXT113", "each FIX-NOW mark the dispositions rule, present at its piece (the piece read by its tag, "
        "continuation lines joined): a list written from the dispositions, not from the documents")
TEXT113 = [
    ("RULING-2", "core/labels/export/named-list", "The list is the door on the place (core/labels/rule/argument-door), not labels of the body's own"),
    ("RULING-2", "core/labels/export/export-list", "On a parameter's place the list is the door (core/labels/rule/argument-door), not labels of the body's own"),
    ("RULING-2", "lib/convention/argument-labels", "is the door (core/labels/rule/argument-door)"),
    ("RULING-3", "core/operators/bindings/reference", "a marked reading, the fold's, pending the owner question reference-example-checked"),
    ("RULING-3", "core/operators/bindings/macro-types", "replaced by param-reference line 2"),
    ("RULING-5", "core/holes/bare-condition/nested-scope", "a parameter's labels are not its to name, but a reference's listed ones"),
    ("RULING-5", "core/labels/paths", "The exception: a declared reference's listed names"),
    ("RULING-5", "parked/ideas/reference-kind", "`A(a:, B) := B & (a: 5)`"),
    ("RULING-6", "core/labels/export/named-list", "the three \"Lacking it\" lines"),
    ("RULING-6", "core/operators/bindings/reference", "Cells still open, each with its trigger"),
    ("RULING-7", "parked/ideas/label-interface", "Unlocks, each with its trigger"),
    ("RULING-8", "lib/search/occurrences", "(its list the manager's call, transform-export)"),
    ("RULING-8", "lib/search/hits", "(the list under `hit` the manager's call under transform-export, hits-through-hit)"),
    ("EXAMPLES-3", "core/labels/rule/stacked-chain", "Y labels the argument and X reads `X.a.h`, the next line"),
    ("EXAMPLES-3", "core/labels/rule/caller-label", "read `Y.a.h` (ruled, caller-label-export"),
    ("EXAMPLES-3", "core/labels/rule/list-over-label", "the body writes `[p = [(=) = rx]]` to pass both; a marked reading"),
    ("EXAMPLES-3", "core/operators/bindings/reference-call", "write the call as a filter over the whole, the line above"),
    ("EXAMPLES-4", "core/operators/bindings/reference-call", "the native is planned over three values (lib/planned/standard)"),
    ("EXAMPLES-5", "core/labels/rule/argument-place", "nested-scope's line \"Example 1, the spot labelled\""),
]
if s113("s13"):
    TEXT113.append(("planted", "core/labels/rule/argument-door", "the remedy does nothing"))
DETJ = re.sub(r"\n  +", " ", NOWS["core_details.md"])       # noqa: F821
tx_bad = []
for fid, tag_, want_ in TEXT113:
    try:
        body_ = re.sub(r"\n  +", " ", piece8(tag_))         # noqa: F821
    except Exception:                                        # noqa: BLE001
        body_ = ""
    if want_ not in body_:
        tx_bad.append((fid, tag_))
for w_ in ["REVISED by param-reference", "open cell, a reference beside a label parameter", "open cell, a renamed list"]:
    if w_ not in DETJ:
        tx_bad.append(("details", w_))
check("TEXT113", not tx_bad, "%d marks at their pieces, 3 in the details; missing: %s" % (len(TEXT113), tx_bad or "none"))   # noqa: F821

unit113("SUCCESSOR113", "every in-force model re-run: predfold1128 in full (its SUCCESSOR128 re-runs predfix112 and the "
        "twenty before it, their outputs dumped beside it); each red DECLARED in predfix113_succ_decl.tsv by "
        "predfix90's `red_key10` key (the red's own FAIL line, no document line numbers); a traceback never")
P90_113 = os.path.join(LANES113, "predfix90_evidence", "predfix90_model.py")
_src90_113 = builtins.open(P90_113, encoding="utf-8").read()
exec(compile(_src90_113[_src90_113.index("CRASH10 = re.compile("):_src90_113.index("succ_bad, succ_n, succ_t, succ_seen = ")],   # noqa: S102
             P90_113, "exec"), globals())                    # predfix90's red key, verbatim
DECLF113 = os.path.join(HERE113, "predfix113_succ_decl.tsv")
SD113 = {}
if os.path.exists(DECLF113):
    for l_ in builtins.open(DECLF113, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SD113.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s113("s14") and SD113:
    _pm113 = sorted(SD113)[0]
    _pr113 = sorted(SD113[_pm113])[0]
    SD113[_pm113][_pr113] = (SD113[_pm113][_pr113][0], SD113[_pm113][_pr113][1] + " planted", SD113[_pm113][_pr113][2])
SCR113 = os.environ.get("PREDFIX113_SUCCDIR", "")
RD113 = os.environ.get("PREDFIX113_READDUMP") == "1"
sc_bad, sc_seen, sc_outs = [], [], {}
if not LIGHT113 or RD113:
    if not SCR113 or not os.path.isdir(SCR113):
        sc_bad.append(("PREDFIX113_SUCCDIR", SCR113, "NOT A DIRECTORY"))
    elif not RD113 and os.listdir(SCR113):
        sc_bad.append(("PREDFIX113_SUCCDIR", SCR113, "NOT EMPTY (a stale dump is read as a model)"))
    elif not RD113:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PREDFIX111_", "PREDFOLD1125_", "PREDFOLD1127_",
                                                                        "PREDFIX90_", "PREDFIX112_", "PREDFOLD1128_",
                                                                        "PREDFIX113_"))}
        env["PREDFOLD1128_SUCCDIR"] = SCR113
        o_ = subprocess.run([sys.executable, "-I", "-B", P128], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=5900).stdout
        builtins.open(os.path.join(SCR113, "predfold1128.out"), "w", encoding="utf-8").write(o_)
    if SCR113 and os.path.isdir(SCR113):
        for f_ in sorted(os.listdir(SCR113)):
            if f_.endswith(".out"):
                sc_outs[f_[:-4]] = builtins.open(os.path.join(SCR113, f_), encoding="utf-8").read()
    for mname, out in sorted(sc_outs.items()):
        lines_ = out.rstrip("\n").split("\n")
        last = lines_[-1]
        mm = re.match(r"%s_model: (\d+) checks, (\d+) failed(?: \(([^)]*)\))?$" % mname, last)
        reds = {}
        if mm and not any(x_.startswith("Traceback") for x_ in lines_):
            for r in [x_.strip() for x_ in (mm.group(3) or "").split(",") if x_.strip()]:
                fl_ = next((l_ for l_ in lines_ if l_.startswith("FAIL %s:" % r) or
                            re.match(r"%s\s+FAIL\b" % re.escape(r), l_)), "")
                reds[r] = red_key10(r, lines_, fl_)          # noqa: F821
        else:
            reds["TRACEBACK"] = ("TRACEBACK", last)
        decl = SD113.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            sc_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                sc_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            sc_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD = os.environ.get("PREDFIX113_WRITEDECL", "")
    if WD:
        with builtins.open(WD, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in sc_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SD113.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in sc_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR113", len(sc_outs) >= 22 and not sc_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(sc_outs), len(sc_seen), sum(len(v) for v in SD113.values()),
                                     sc_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR113 not run")

PLANTS113 = {"s1": "CANARY113", "s2": "ERRSWEEP113", "s3": "ERRSWEEP113", "s4": "OPEN113", "s5": "OPEN113",
             "s6": "SWEEP113", "s7": "ERRSWEEP113", "s8": "SPECLINES113", "s9": "HAND113", "s10": "MARK113",
             "s11": "QUOTES113", "s12": "STALE113", "s13": "TEXT113", "s14": "SUCCESSOR113"}
if SAB113 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS113.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFIX113_SABOTAGE=q_, PREDFIX113_LIGHT="1")
        if q_ == "s14":
            env["PREDFIX113_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY113], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS113", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed113 = [n_ for n_, ok_ in RESULTS if not ok_]           # noqa: F821
print("predfix113_model: %d checks, %d failed%s" % (len(RESULTS), len(failed113),   # noqa: F821
                                                   (" (%s)" % ", ".join(failed113)) if failed113 else ""))
sys.exit(1 if failed113 else 0)
