#!/usr/bin/env python3
"""predfix112_model.py: lane predfix112's evidence, the successor of predfold1127_model.py.

The fix after review r112 (docs/dev/reviews/2026-11-27-r112-predfold1127.md) and the fold of two owner rulings,
array-gate and body-own-name (record docs/design/plan_row_bodies/COND-FAMILY.md, 2026-11-27). DESIGN evidence
only: nothing here rules; no check under `make` reads it.

It LOADS predfold1127's model unchanged up to its checks (`# ==== CHECKS`; the older models load through it), then
patches its walker WALK1127 in one place, switched by X112[0] (off: predfold1127's walker as merged, the control):
  BODY112  body-own-name, from the statement as asked: "a path that skips nothing is always legal and reads the
           label directly under its last step; one-path limits only reads that skip a step." At each step, when
           some target of the name lies directly under the step (no node between), the targets reached by a skip
           are not counted; the direct ones keep the label flow (the last mention). Applied BEFORE the gate check,
           so a gate beside a direct target is not counted either (the statement's "always").
  array-gate is predfold1127's printed side (READ1127["array"] = "error"), now RULED.
  GROUND112 (a switch, never the printed rule) models the owner's own ground for the call case ("the d from A is
           outside and would have to gate through rx but rx as an arg cant be directly on a path"): BODY112 off,
           and a target reached across an argument's place is not counted when another target is.
Every legal printed line is also answered by MECH111 (python `re` on a regex built mechanically from the program
text and its bindings' bodies). The verdict is the last line, `predfix112_model: N checks, F failed`; it exits
non-zero iff that line reports a failure.
PINNED COMMITS (review r112 COORD-1): this model reads git ONLY by commit id (START112 below). The older models it
re-runs still read by branch NAME in one place: predfold1123_model.py reads `lane/pred-rev28:` (a clone without
that local branch turns predfold1123 QUOTES and predfix111 SUCCESSOR111 red); those lane files are historical and
are not edited.
`PREDFIX112_LIGHT=1` skips SUCCESSOR112; `PREDFIX112_SUCCDIR=DIR` an existing EMPTY scratch directory for the
successor outputs (the older models read every `.out` in it); `PREDFIX112_READDUMP=1` reads DIR instead of re-running; `PREDFIX112_SABOTAGE=sN` plants one wrong rule,
fact or text per check (PLANTS112); `=all` runs each plant in its own LIGHT subprocess.
Run: `timeout 6000 python3 -I -B <this dir>/predfix112_model.py`.
"""
import builtins
import os
import re
import subprocess
import sys

MY112 = os.path.abspath(__file__)
HERE112 = os.path.dirname(MY112)
LANES112 = os.path.normpath(os.path.join(HERE112, ".."))
P1127 = os.path.join(LANES112, "predfold1127_evidence", "predfold1127_model.py")
START112 = "2d7718d4e"                                       # this lane's starting commit (lane/predfix112), PINNED
SAB112 = os.environ.get("PREDFIX112_SABOTAGE", "")
LIGHT112 = os.environ.get("PREDFIX112_LIGHT") == "1"
_src1127 = builtins.open(P1127, encoding="utf-8").read()
_a112 = _src1127.index("\n# ==== CHECKS (a probe loads the model up to this line)") + 1
_sav112 = {k: os.environ.pop(k) for k in list(os.environ)
           if k.startswith(("PREDFOLD1127_", "PREDFIX111_", "PREDFOLD1125_", "PREDFIX90_"))}
__file__ = P1127
exec(compile(_src1127[:_a112], P1127, "exec"), globals())    # noqa: S102  predfold1127's engines, unchanged
__file__ = MY112
os.environ.update(_sav112)
X112 = [True]
GROUND112 = [False]


def s112(q):
    return SAB112 == q


# ================================================================== BODY112: the one patch to WALK1127
_W_OLD = _src1127[_src1127.index("def walk1127(P, path"):_src1127.index("class Prog1127(Prog111):")]
_HOOK = ("                uniq.append(c)\n")
_BODY = _HOOK + (
    "        uniq = _body112(uniq)                            # body-own-name (predfix112)\n")
assert _W_OLD.count(_HOOK) == 1, "WALK1127's hook moved"
exec(compile(_W_OLD.replace(_HOOK, _BODY), P1127 + " (patched by predfix112)", "exec"), globals())   # noqa: S102


def _body112(uniq):
    """body-own-name: a target directly under the step (nothing between: c[2] empty) is read; targets reached by a
    skip beside it are not counted. GROUND112: instead, a target across an argument's place is not counted when
    another target is."""
    if GROUND112[0]:
        own = [c for c in uniq if not any(n.k == "arg" for n in c[2])]
        return own if own and len(own) < len(uniq) else uniq
    if not X112[0] or s112("s1"):
        return uniq
    direct = [c for c in uniq if not c[2]]
    return direct if direct and len(direct) < len(uniq) else uniq


READ1127["array"] = "error"                                  # array-gate, RULED: "error. Agree with lean"
READ1127["direct"] = "error"                                 # predfold1127's switch stays as merged; BODY112 decides


# ==== CHECKS112 (a probe loads the model up to this line)
RESULTS.clear()                                              # noqa: F821
PB = "P := /(?<d>\\d)/"
QB = "Q := /,(?<d>\\d)/"
AD = "A := /(?<d>\\d)/"
BD = "B(rx) := /${rx}-(?<d>\\d)/"
BPD = "B(rx) := /${[p = rx]}-(?<d>\\d)/"
XB = "X := [a = P] SEQ /;(?<d>\\d)/"
DATE = 'date := [y = /(?<v>\\d)/] SEQ "-" SEQ [m = /(?<v>\\d)/]'
T2 = ["7,3", "3,7", "1,2", "7,7", "x3,1", "3,3", "7,3x"]
TD = ["7-3", "3-7", "1-2", "7-7", "x3-1", "3-3"]
TS = ["7;3", "3;7", "1;2", "9;9", "x3;1", "3;3"]


def unit112(name, what):
    print("== %s: %s" % (name, what))


def same_as(P, rx_, texts):
    """the program's answers (whole, searched, find-all) against a regex written by hand from the ruled sentence."""
    return P is not None and ans11(P, texts) == ans11(RePg(rx_), texts)   # noqa: F821


unit112("CANARY112", "X112 off is predfold1127's walker as merged (the control): `c.d` over a body and an argument that "
        "each set `d` refused; X112 on (body-own-name) legal, the body's own")
X112[0] = False
c0 = run11("[c = B(A)] & (c.d: <5)", [AD, BD])               # noqa: F821
X112[0] = True
c1 = run11("[c = B(A)] & (c.d: <5)", [AD, BD])               # noqa: F821
check("CANARY112", c0[0] is None and c1[0] is not None and same_as(c1[0], r"\d-[0-4]", TD),   # noqa: F821
      "off: %s; on: %s" % (c0[1], "legal, the body's own" if c1[0] else c1[1]))

unit112("RULE112", "reads judged by the model's full program builder against hand-filled verdicts, each citing the "
        "ruled line it rests on; every legal read's answers against a regex written by hand from the sentence")
RULE112 = [
    ("[c = B(A)] & (c.d: <5)", [AD, BD], r"\d-[0-4]", "body-own-name: nothing skipped, the body's own"),
    ("B(A) & (B.d: <5)", [AD, BD], r"\d-[0-4]", "body-own-name: the call-prefix line, the body's own"),
    ("B(/(?<d>\\d)/) & (B.d: <5)", [BD], r"\d-[0-4]", "body-own-name: two-sources' \"The body's own\""),
    ("B(A) & (A.d: <5)", [AD, BD], r"[0-4]-\d", "argument-default: the argument's own by its source"),
    ("X & (X.d: <5)", [PB, XB], r"\d;[0-4]", "body-own-name: X's own"),
    ("X & (X.a.d: <5)", [PB, XB], r"[0-4];\d", "rule 1, the full path"),
    ("B(A) & (B.d: <5)", [AD, BPD], r"\d-[0-4]", "body-own-name: the body's own beside a written label on the spot"),
    ("B(A) & (B.p.d: <5)", [AD, BPD], r"[0-4]-\d", "rule 1, through the body's label"),
    ("B(A) & (B.h: <5)", ["A := /(?<h>\\d)/", "B(rx) := /${[p = rx]}(?<h>\\d)/"], r"\d[0-4]",
     "body-own-name: the shorthand cell's case, the body's own `h`"),
    ("[n = (P SEQ /,(?<d>\\d)/)] & (n.d: <5)", [PB], r"\d,[0-4]", "body-own-name's \"always\": the direct group beside a gate"),
    ("[n = (P SEQ /,(?<d>\\d)/)] & (n.P.d: <5)", [PB], r"[0-4],\d", "alone-as-middle: the gate as a step"),
    ("D2 & (D2.c: \"3\")", ["D2 := /(?<c>\\d)(?<c>\\d)/"], r"\d3", "label flow: nothing skipped, the last mention"),
    ("date & (date.v: <5)", [DATE], ("refused", "`date.m.v`"), "one-path line 4, unchanged"),
    ("[n = ([a = P] SEQ Q)] & (n.d: <5)", [PB, QB], ("refused", "behind a gate"), "gate-beside-label, unchanged"),
    ("[n = (P SEQ Q)] & some(@n.d, <5)", [PB, QB], ("refused", "behind a gate"), "array-gate: an error, array or not"),
    ("[n = (P SEQ Q)] & (n.d: <5)", [PB, QB], ("refused", "behind a gate"), "one-path line 2, unchanged"),
    ("W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: \"3\")", ["W(a, b) := [(=) = a] SEQ [(=) = b]"], ("refused", "2 labels `h`"),
     "one-path line 4: both skipped (aliases), unchanged"),
    ("pair(A) & (pair.d: <5)", [AD, "pair(p) := /${[(=) = p]},${[(=) = p]}/"], ("refused", "2 labels `d`"),
     "one-path line 5: both skipped, unchanged"),
    ("list_of(/(?<h>\\d)/, sep = \",\") & (list_of.h: \"5\")", [], ("refused", "2 labels `h`"),
     "one-path line 5: both skipped, unchanged"),
    ("W([x = /(?<h>\\d)/], [y = /;(?<h>\\d)/]) & (y.h: \"3\")", ["W(a, b) := [(=) = a] SEQ [(=) = b]"], r"\d;3",
     "argument-label: the caller's label (EXAMPLES-5's names)"),
]
if s112("s2"):
    RULE112[0] = (RULE112[0][0], RULE112[0][1], r"[0-4]-\d", RULE112[0][3])
TEXTS112 = {"X & ": TS, "[n = (P SEQ /,": T2, "D2": ["73", "37", "13", "3"], "B(A) & (B.h": ["73", "37", "12", "x31"],
            "W([x": ["7;3", "3;7", "1;3", "x3;7"]}
r_bad, r_leg = [], 0
for e_, b_, want, why in RULE112:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    texts = next((v for k, v in TEXTS112.items() if e_.startswith(k)), None) or TD
    if isinstance(want, tuple):
        ok_ = P_ is None and want[1] in (err_ or "") and not (err_ or "").startswith("CRASH")
        got = (err_ or "LEGAL")[:150]
    else:
        ok_ = same_as(P_, want, texts)
        r_leg += 1
        got = "legal, %s the hand regex `%s`" % ("equal to" if ok_ else "NOT equal to", want) if P_ else err_
    if not ok_:
        r_bad.append((e_, got))
    print("   %-62s %s | %s" % (e_[:62], why, got[:130]))
check("RULE112", not r_bad and r_leg >= 12, "%d reads (%d legal against hand regexes); not as the ruling says: %s" % (   # noqa: F821
    len(RULE112), r_leg, r_bad or "none"))

unit112("READINGS112", "the manager's readings (a)-(c) of the body-own-name entry, each RUN; his ground against the asked "
        "statement (the switch GROUND112); the gate beside a direct target, both sides")
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
rdg = {}
sites = {t_: re.sub(r"\n  +", " ", piece8(t_)) for t_ in ("core/labels/rule/one-path", "core/labels/paths/call-prefix",   # noqa: F821
                                                            "core/labels/paths/two-sources")}
if s112("s3"):
    sites["core/labels/paths/two-sources"] += " two labels `d` are visible from `B`, the argument's and the body's"
gone_f = [t_ for t_, v_ in sites.items() if re.search(r"two labels `d` are visible from `[Bc]`, the argument's|One target "
                                                       r"reached directly and one by a skip|no path names the body's own", v_)]
has_b = [t_ for t_, v_ in sites.items() if "body-own-name" in v_]
rdg["(a) reading (f) replaced at its three sites"] = (not gone_f and len(has_b) == 3,
                                                      "(f) text left at %s; body-own-name named at %d of 3" % (gone_f or "none", len(has_b)))
GR = [("[c = B(A)] & (c.d: <5)", [AD, BD], "c.d"), ("B(A) & (B.d: <5)", [AD, BD], "B.d"),
      ("B(/(?<d>\\d)/) & (B.d: <5)", [BD], "B.d"), ("B(A) & (B.d: <5)", [AD, BPD], "B.d"),
      ("X & (X.d: <5)", [PB, XB], "X.d")]
gr_rows, gr_part = [], []
for e_, b_, r_ in GR:
    va = walk_v27(e_, b_, r_)
    Pa, _ = run11(e_, b_)                                    # noqa: F821
    GROUND112[0] = True
    vg = walk_v27(e_, b_, r_)
    Pg, _ = run11(e_, b_)                                    # noqa: F821
    GROUND112[0] = False
    call = r_.split(".")[0] in ("B", "c")
    txt = TS if e_.startswith("X") else TD
    agree = va[:3] == vg[:3] and Pa is not None and Pg is not None and ans11(Pa, txt) == ans11(Pg, txt)   # noqa: F821
    if call and not agree:
        gr_part.append(e_)
    gr_rows.append("%s %s: asked %s / ground %s" % (e_[:30], [x for x in b_ if x.startswith("B")] or "", va[:3], vg[:3]))
    if Pa is not None:
        print("   asked  %-34s %s" % (e_, fmt(Pa, txt[:3], " ".join(txt[1::-1]), " ".join(txt[:4]))))   # noqa: F821
    if Pg is not None:
        print("   ground %-34s %s" % (e_, fmt(Pg, txt[:3], " ".join(txt[1::-1]), " ".join(txt[:4]))))   # noqa: F821
for x_ in gr_rows:
    print("   " + x_)
rdg["(b) his ground and the asked statement agree on every call case, `/${[p = rx]}-(?<d>\\d)/` included"] = (
    not gr_part, "parting: %s (X.d is no call: his ground is silent there)" % (gr_part or "none"))
Pc_, ec_ = run11("B(A) & (A.d: <5)", [AD, BD])           # noqa: F821  the walker places no start `A`: the builder
rdg["(c) the argument's own label read by its source, `A.d`"] = (same_as(Pc_, r"[0-4]-\d", TD),
                                                                 "legal, A's `d` (hand regex `[0-4]-\\d`)" if Pc_ else ec_)
F5 = "[n = (P SEQ /,(?<d>\\d)/)] & (n.d: <5)"
f5a = walk_v27(F5, [PB], "n.d")
X112[0] = False
f5m = walk_v27(F5, [PB], "n.d")
X112[0] = True
if s112("s4"):
    f5a = f5m
rdg["a direct target beside a gate: the asked statement's \"always\" legal; gate-beside-label's manager reading refused"] = (
    f5a[0] == "legal" and f5m[0] == "refused", "asked %s / gate-beside reading %s" % (f5a[:3], f5m[1][:90]))
for k_, (ok_, why_) in rdg.items():
    print("   %s: %s (%s)" % (k_, "SUPPORTED" if ok_ else "NOT SUPPORTED", why_))
check("READINGS112", all(v[0] for v in rdg.values()), "%d readings run, %d supported" % (   # noqa: F821
    len(rdg), sum(1 for v in rdg.values() if v[0])))

unit112("TABLE112", "the label-kind table of core/labels/rule/kinds, read cell by cell, against KINDS111 (the rows the "
        "walker models); the two rows added (a list's alias, an argument's place) against the walker's node kinds")
exec(compile(_src1127[_src1127.index("ROWS111 = {"):_src1127.index("D8.clear()", _src1127.index("ROWS111 = {"))],   # noqa: S102
             P1127, "exec"), globals())
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s112("s5"):
    D8["core.md"] = D8["core.md"].replace("| always passed, a node between (one-path, a reading); a target", "| no (a reading); a target", 1)   # noqa: F821
kp = piece8("core/labels/rule/kinds")                        # noqa: F821
tb_bad, tb_seen, tb_new = [], set(), {}
for L_ in kp.split("\n"):
    L_ = L_.strip()
    if not L_.startswith("| ") or L_.startswith("| the kind") or L_.startswith("|---"):
        continue
    cells = [c.strip() for c in L_.strip("|").split(" | ")]
    name = re.sub(r"\s*\(.*$|\s*`.*$", "", cells[0]).strip()
    if name in ("a list's alias", "an argument's place"):
        tb_new[name] = cells
    k = ROWS111.get(name)                                    # noqa: F821
    if k is None:
        continue
    tb_seen.add(k)
    got = tuple(cell_code(i, c) for i, c in enumerate(cells[1:6]))   # noqa: F821
    want = tuple("no" if (i == 0 and w == "no") else w for i, w in enumerate(KINDS111[k]))   # noqa: F821
    if got != want:
        tb_bad.append((name, got, want))
    print("   ROW %-28s document %s, walker %s" % (name, got, want))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
Pw_ = Prog1127(*prep1127('W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: "3")', ["W(a, b) := [(=) = a] SEQ [(=) = b]"])[:2])
Pb_ = Prog1127(*prep1127("B(A) & (B.d: <5)", [AD, BD])[:2])
wk = {"a list's alias": sorted(set(str(kind_of(n)) for n in _subtree(Pw_.root) if n.k == "list")),   # noqa: F821
      "an argument's place": sorted(set(str(kind_of(n)) for n in _subtree(Pb_.root) if n.k == "arg"))}   # noqa: F821
for nm_, cells in sorted(tb_new.items()):
    walker_passes = wk[nm_] == ["None"]                      # no kind: the walker passes it as a node between
    doc_passes = cells[3].startswith("always passed") and cells[1].startswith("no") and cells[2].startswith("no")
    print("   ROW %-28s document start %r, middle %r, skippable %r; walker kinds %s" % (nm_, cells[1][:20], cells[2][:20],
                                                                                     cells[3][:30], wk[nm_]))
    if walker_passes != doc_passes:
        tb_bad.append((nm_, cells[3][:40], wk[nm_]))
check("TABLE112", not tb_bad and tb_seen == set(ROWS111.values()) and len(tb_new) == 2,   # noqa: F821
      "%d rows modelled, %d rows added read; differing: %s" % (len(tb_seen), len(tb_new), tb_bad or "none"))

unit112("SWEEP112", "every printed three-mode line RUN under this model; the starting commit %s's lines under the "
        "control (X112 off: predfold1127's walker) against these, keyed by the program; every key gone DECLARED" % START112)
exec(compile(_src11[_src11.index("def sw11(docs):"):_src11.index("def key11(k):")], P1125, "exec"), globals())   # noqa: S102,F821
exec(compile(_src111[_src111.index("_sweep_one11, _modes_of11, _fmt11 = "):_src111.index("OLD111 = {")], P111, "exec"),   # noqa: S102,F821
     globals())
OLD112 = {f_: _git8("docs/design/predicates/" + f_, START112) for f_ in DOCF}   # noqa: F821
X112[0] = False
OLD_T112 = sw11(OLD112)                                      # noqa: F821
X112[0] = True
NOWS112 = dict(NOWS)                                         # noqa: F821
if s112("s6"):
    NOWS["core.md"] = NOWS["core.md"].replace("The binding's own, nothing skipped: WHOLE `7;3` HOLDS", "The binding's own, nothing skipped: WHOLE `7;3` FAILS", 1)   # noqa: F821
NEW_T112 = sw11(NOWS)                                        # noqa: F821
NOWS.update(NOWS112)                                         # noqa: F821
GONE112 = {
    "B(A) & (B.d: <5)": "body-own-name: \"By the macro's name\" re-spelled with A := /(?<d>\\d)/, its old answers (the "
                        "argument setting no `d` was the predfold1127 keeper)",
    'W([a = /(?<h>\\d)/], [b = /;(?<h>\\d)/]) & (b.h: "3")': "review r112 EXAMPLES-5: the caller's labels renamed `x`, "
                                                            "`y`, the same answers",
}
inh = set((k_, f_, st_) for k_, vs in OLD_T112.items() for f_, _, st_, _, _ in vs if st_ != "same")
sw_bad, sw_moved, sw_gone, sw_new, sw_inh, cnt, used = [], [], [], [], [], {}, set()
for k_, vs in NEW_T112.items():
    for f_, ln_, st_, got_, pr_ in vs:
        cnt[st_] = cnt.get(st_, 0) + 1
        if st_ != "same":
            (sw_inh if (k_, f_, st_) in inh else sw_bad).append((f_, ln_, st_, k_[0], got_[:160]))
for k_, vs0 in OLD_T112.items():
    for f0 in sorted(set(v_[0] for v_ in vs0)):
        vs = [v_ for v_ in vs0 if v_[0] == f0]
        nk = [v_ for v_ in NEW_T112.get(k_, []) if v_[0] == f0]
        if nk:
            po, pn = sorted(set(v_[4] for v_ in vs)), sorted(set(v_[4] for v_ in nk))
            if po != pn:
                sw_moved.append((f0, k_[0], " || ".join(po)[:200], " || ".join(pn)[:200]))
            continue
        if k_[0] in GONE112:
            used.add(k_[0])
            print("   DROPPED OR MOVED BY A RULING %s:%d `%s`: %s" % (vs[0][0], vs[0][1], k_[0], GONE112[k_[0]]))
            continue
        sw_gone.append((vs[0][0], vs[0][1], k_[0], vs[0][2]))
stale = sorted(k_ for k_ in GONE112 if k_ not in used)
for k_, vs in NEW_T112.items():
    if k_ not in OLD_T112:
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
check("SWEEP112", OLD_T112 and not sw_bad and not sw_moved and not sw_gone and not stale,   # noqa: F821
      "%d printed lines now (%s), %d keys at the starting commit; not same and not inherited %d (inherited %d); "
      "moved %d; gone %d; declared %d; added %d; stale %d" % (
          sum(len(v) for v in NEW_T112.values()), ", ".join("%s %d" % kv for kv in sorted(cnt.items())),
          len(OLD_T112), len(sw_bad), len(sw_inh), len(sw_moved), len(sw_gone), len(GONE112), len(sw_new),
          len(stale)))

unit112("ERRSWEEP112", "every printed compile-error line of the base files refused under this model, no crash; each "
        "named form in the refusal's message (MSG111's rows and predfold1127's MSG1127, less the reads now legal)")
exec(compile(_src9[_src9.index("def err_lines(docs"):_src9.index("es_now = err_lines(D8)")], P1124, "exec"),   # noqa: S102,F821
     globals())
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
if s112("s7"):
    D8["core.md"] = D8["core.md"].replace("The array form through a gate: modes: a compile error (`[n = (P SEQ Q)] & some(@n.d, <5)`",
                                          "The array form through a gate: modes: a compile error (`[n = ([a = P] SEQ [b = Q])] & some(@n.d, <5)`", 1)   # noqa: F821
es_now = [x_ for x_ in err_lines(D8) if not x_[0].endswith("_details.md")]   # noqa: F821
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
exec(compile(_src111[_src111.index("MSG111 = {"):_src111.index("}\n", _src111.index("MSG111 = {")) + 2], P111, "exec"),   # noqa: S102,F821
     globals())
exec(compile(_src1127[_src1127.index("MSG1127 = dict(MSG111)"):_src1127.index("es_bad, es_msg = [], []")], P1127, "exec"),   # noqa: S102
     globals())
MSG112 = dict(MSG1127)                                       # noqa: F821
MSG112.pop("B(/(?<d>\\d)/) & (B.d: <5)")                     # legal again (body-own-name): no compile-error line
es_bad, es_msg = [], []
for f_, ln_, e_, b_ in es_now:
    Pg, err = run11(e_, b_)                                  # noqa: F821
    if Pg is not None or (err or "").startswith("CRASH"):
        es_bad.append((f_, ln_, e_, "legal" if Pg is not None else err[:100]))
    elif e_ in MSG112 and MSG112[e_] not in err:
        es_msg.append((f_, ln_, e_, MSG112[e_], err[:140]))
for x_ in es_bad:
    print("   BAD (printed a compile error, runs legal or crashes) %s" % (x_,))
for x_ in es_msg:
    print("   MESSAGE %s:%d `%s` lacks %s: %s" % x_)
msg_unseen = sorted(set(MSG112) - set(e_ for _, _, e_, _ in es_now))
check("ERRSWEEP112", es_now and not es_bad and not es_msg and not msg_unseen,   # noqa: F821
      "%d compile-error lines read, each refused with no crash: bad %s; named form missing %s; message rows with no "
      "line %s" % (len(es_now), es_bad or "none", es_msg or "none", msg_unseen or "none"))

unit112("SPECLINES112", "every printed line new in this lane (not in its file at the starting commit) is RUN: a "
        "three-mode line SAME as run, a compile-error line refused")
newset = {f_: set(NOWS[f_].split("\n")) - set(OLD112[f_].split("\n")) for f_ in BASES11}   # noqa: F821
nl3, nle, nl_bad = 0, 0, []
for k_, vs in NEW_T112.items():
    for f_, ln_, st_, got_, pr_ in vs:
        if f_ in newset and NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:   # noqa: F821
            nl3 += 1
            if st_ != "same":
                nl_bad.append((f_, ln_, st_))
for f_, ln_, e_, b_ in es_now:
    if NOWS[f_].split("\n")[ln_ - 1] in newset[f_]:           # noqa: F821
        nle += 1
        if run11(e_, b_)[0] is not None:                      # noqa: F821
            nl_bad.append((f_, ln_, "legal"))
nl_all = sum(1 for f_ in BASES11 for L_ in newset[f_] if re.search(r"WHOLE `|modes: a compile error", L_))   # noqa: F821
if s112("s8"):
    nl_all += 1
check("SPECLINES112", not nl_bad and nl3 + nle == nl_all, "%d new printed lines: three-mode %d, compile-error %d, "   # noqa: F821
      "unread %d; not as printed: %s" % (nl_all, nl3, nle, nl_all - nl3 - nle, nl_bad or "none"))

unit112("STALE112", "the base files, continuation lines joined, hold none of the texts this fix retires")
STALE112 = [
    (r"owner question body-own-name", "body-own-name ruled"),
    (r"owner question array-gate", "array-gate ruled"),
    (r"One target reached directly and one by a skip are two", "body-own-name replaces reading (f)"),
    (r"no path names the body's own", "body-own-name"),
    (r"Through the call, both", "body-own-name: two-sources' line \"The body's own\" back"),
    (r"the conservative reading \(a marked reading", "array-gate ruled"),
    (r"a `d` sits behind a gate \(a marked reading\)", "array-gate ruled"),
    (r"W\(\[a = /\(\?<h>", "review r112 EXAMPLES-5"),
    (r"`A := `/\(\?<e>\\d\)/`, B\(rx\) := `/\$\{rx\}-\(\?<d>\\d\)/`\)\s*$", "body-own-name: `B.d` with the d-argument"),
]
if s112("s9"):
    STALE112.append((r"The binding's own, nothing skipped", "planted"))
joined = {f_: re.sub(r"\n  +", " ", NOWS[f_]) for f_ in BASES11}   # noqa: F821
st_hits = [(f_, rx_, why) for rx_, why in STALE112 for f_ in BASES11 if re.search(rx_, joined[f_], re.M)]   # noqa: F821
for x_ in st_hits:
    print("   STALE %s `%s` (%s)" % x_)
check("STALE112", not st_hits, "%d retired texts searched; found %s" % (len(STALE112), st_hits or "none"))   # noqa: F821

unit112("QUOTES112", "the owner's words this lane quotes, each in the record at the PINNED starting commit and in its "
        "piece; every record title a predfix112 item cites is a title of that record")
REC112 = _git8("docs/design/plan_row_bodies/COND-FAMILY.md", START112)   # noqa: F821
QQ112 = [
    ("body-own-name: agree", "core/labels/rule/one-path"),
    ("a path that skips nothing is always legal and reads the label directly under its last step; one-path limits "
     "only reads that skip a step.", "core/labels/rule/one-path"),
    ("Within the macro, the d from A is outside and would have to gate through rx but rx as an arg cant be directly "
     "on a path.", "core/labels/rule/one-path"),
    ("array-gate: error. Agree with lean", "core/labels/rule/one-path"),
    ("one-path: yes all five", "core/labels/rule/one-path"),
]
if s112("s10"):
    QQ112.append(("body-own-name: disagree", "core/labels/rule/one-path"))
D8.clear()                                                   # noqa: F821
D8.update(NOWS)                                              # noqa: F821
q_miss = [(q_[:50], t_) for q_, t_ in QQ112 if ws(q_) not in ws(REC112) or ws(q_) not in ws(piece8(t_))]   # noqa: F821
DET112 = NOWS["core_details.md"] + NOWS["library_details.md"] + NOWS["parked_details.md"]   # noqa: F821
DOLD112 = set((OLD112["core_details.md"] + OLD112["library_details.md"] + OLD112["parked_details.md"]).split("\n"))
cited = sorted(set(m_.group(1) for l_ in DET112.split("\n") if l_ not in DOLD112
                   for m_ in re.finditer(r'\(record:\s*"(.+?)"\)(?=[;,.:\s]|$)', l_)))
heads = [ws(h_) for h_ in re.findall(r"^#{2,3} (.*)$", REC112, re.M)]   # noqa: F821
t_miss = [t_[:80] for t_ in cited if not any(h_.rstrip(".") == ws(t_) or h_.startswith(ws(t_) + " (") for h_ in heads)]   # noqa: F821
check("QUOTES112", not q_miss and not t_miss and cited, "%d quoted sentences (missing: %s); %d record titles cited "   # noqa: F821
      "(not a title at %s: %s)" % (len(QQ112), q_miss or "none", len(cited), START112, t_miss or "none"))

unit112("MECH112", "every read this lane makes legal answered by MECH111 (python `re` on the regex built mechanically "
        "from the program text and its bindings' bodies, the target group named), against the engine")
MECH112 = [
    ("[c = B(A)] & (c.d: <5)", [AD, BD], ("B", 1, "d"), TD),
    ("B(A) & (B.d: <5)", [AD, BD], ("B", 1, "d"), TD),
    ("B(/(?<d>\\d)/) & (B.d: <5)", [BD], ("B", 1, "d"), TD),
    ("B(A) & (B.d: <5)", [AD, BPD], ("B", 1, "d"), TD),
    ("X & (X.d: <5)", [PB, XB], ("X", 1, "d"), TS),
    ("[n = (G SEQ /,(?<d>\\d)/)] & (n.d: <5)", ["G := /(?<d>\\d)/"], ("P", 1, "d"), T2),   # MECH111 names the program text `P`
]
if s112("s11"):
    MECH112[0] = (MECH112[0][0], MECH112[0][1], ("A", 1, "d"), MECH112[0][3])
mc_bad = []
for e_, b_, tgt, texts in MECH112:
    P_, err_ = run11(e_, b_)                                 # noqa: F821
    try:
        R_ = mech(e_, b_, target=tgt, cond=(0, 4))           # noqa: F821
    except MechError as x_:                                  # noqa: F821
        mc_bad.append((e_, "MECH " + str(x_)))
        continue
    same = P_ is not None and answers(P_, texts) == answers(R_, texts)   # noqa: F821
    print("   %-58s MECH111 %s the engine" % (e_[:58], "equal to" if same else "NOT equal to"))
    if not same:
        mc_bad.append((e_, err_ or "answers differ"))
check("MECH112", not mc_bad, "%d reads; not equal: %s" % (len(MECH112), mc_bad or "none"))   # noqa: F821

unit112("SUCCESSOR112", "every in-force model re-run: predfold1127 in full, and the nineteen its SUCCESSOR1127 re-runs "
        "(their outputs dumped through it); each red DECLARED in predfix112_succ_decl.tsv by predfix90's `red_key10` key, "
        "which carries the red's own FAIL line and no document line numbers; a traceback never")
P90_112 = os.path.join(LANES112, "predfix90_evidence", "predfix90_model.py")
_src90_112 = builtins.open(P90_112, encoding="utf-8").read()
exec(compile(_src90_112[_src90_112.index("CRASH10 = re.compile("):_src90_112.index("succ_bad, succ_n, succ_t, succ_seen = ")],   # noqa: S102
             P90_112, "exec"), globals())                    # predfix90's red key, verbatim
DECLF112 = os.path.join(HERE112, "predfix112_succ_decl.tsv")
SD112 = {}
if os.path.exists(DECLF112):
    for l_ in builtins.open(DECLF112, encoding="utf-8").read().split("\n"):
        if l_ and not l_.startswith("#"):
            m_, r_, cls_, why_, key_ = l_.split("\t", 4)
            SD112.setdefault(m_, {})[r_] = (cls_, key_, why_)
if s112("s12") and SD112:
    _m = sorted(SD112)[0]
    _r = sorted(SD112[_m])[0]
    SD112[_m][_r] = (SD112[_m][_r][0], SD112[_m][_r][1] + " planted", SD112[_m][_r][2])
SCR112 = os.environ.get("PREDFIX112_SUCCDIR", "")
RD112 = os.environ.get("PREDFIX112_READDUMP") == "1"
sc_bad, sc_seen, sc_outs = [], [], {}
if not LIGHT112 or RD112:
    if not RD112 and os.listdir(SCR112):                    # the older models read EVERY .out in the directory:
        sc_bad.append(("PREDFIX112_SUCCDIR", SCR112, "NOT EMPTY (a stale dump is read as a model)"))   # a fresh one
    if not RD112:
        env = {k: v for k, v in os.environ.items() if not k.startswith(("PREDFIX111_", "PREDFOLD1125_", "PREDFOLD1127_",
                                                                        "PREDFIX90_", "PREDFIX112_"))}
        env["PREDFOLD1127_SUCCDIR"] = SCR112
        o_ = subprocess.run([sys.executable, "-I", "-B", P1127], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=5700).stdout
        builtins.open(os.path.join(SCR112, "predfold1127.out"), "w", encoding="utf-8").write(o_)
    for f_ in sorted(os.listdir(SCR112)):
        if f_.endswith(".out"):
            sc_outs[f_[:-4]] = builtins.open(os.path.join(SCR112, f_), encoding="utf-8").read()
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
        decl = SD112.get(mname, {})
        print("   %-13s last line: %s" % (mname, last[:150]))
        for r, (cls_, key_) in sorted(reds.items()):
            sc_seen.append((mname, r, cls_, key_))
            d_ = decl.get(r)
            if cls_ == "TRACEBACK" or d_ is None or d_[1] != key_:
                sc_bad.append((mname, r, "UNDECLARED" if d_ is None else ("KEY CHANGED" if cls_ != "TRACEBACK" else cls_)))
        for r in sorted(set(decl) - set(reds)):
            sc_bad.append((mname, r, "DECLARED, NOW GREEN"))
    WD = os.environ.get("PREDFIX112_WRITEDECL", "")
    if WD:
        with builtins.open(WD, "w", encoding="utf-8") as fh:
            fh.write("# model\tred\tclass\twhy\tkey (red_key10: the red's own FAIL line text, no document line numbers)\n")
            for mname, r, cls_, key_ in sc_seen:
                fh.write("%s\t%s\t%s\t%s\t%s\n" % (mname, r, cls_, SD112.get(mname, {}).get(r, ("", "", "WHY?"))[2], key_))
    for x_ in sc_bad:
        print("   NOT AS DECLARED %s %s: %s" % x_)
    check("SUCCESSOR112", len(sc_outs) >= 20 and not sc_bad, "%d models read, %d reds, each against its declared "   # noqa: F821
          "key (%d declared): %s" % (len(sc_outs), len(sc_seen), sum(len(v) for v in SD112.values()),
                                     sc_bad or "all as declared"))
else:
    print("   LIGHT: SUCCESSOR112 not run")

PLANTS112 = {"s1": "CANARY112", "s2": "RULE112", "s3": "READINGS112", "s4": "READINGS112", "s5": "TABLE112",
             "s6": "SWEEP112", "s7": "ERRSWEEP112", "s8": "SPECLINES112", "s9": "STALE112", "s10": "QUOTES112",
             "s11": "MECH112", "s12": "SUCCESSOR112"}
if SAB112 == "all":
    caught = []
    for q_, tgt in sorted(PLANTS112.items(), key=lambda kv: int(kv[0][1:])):
        env = dict(os.environ, PREDFIX112_SABOTAGE=q_, PREDFIX112_LIGHT="1")
        if q_ == "s12":
            env["PREDFIX112_READDUMP"] = "1"
        o_ = subprocess.run([sys.executable, "-I", "-B", MY112], stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                            text=True, env=env, timeout=3000)
        fl = [l_ for l_ in o_.stdout.split("\n") if l_.startswith("FAIL ")]
        ok_ = o_.returncode != 0 and any(l_.startswith("FAIL %s:" % tgt) for l_ in fl) and "Traceback" not in o_.stdout
        caught.append((q_, tgt, ok_))
        print("   PLANT %s -> %s: %s; FAIL lines: %s" % (q_, tgt, "CAUGHT" if ok_ else "NOT CAUGHT",
                                                       [l_[:90] for l_ in fl]))
    check("PLANTS112", all(c_[2] for c_ in caught), "%d plants, caught %d" % (len(caught), sum(c_[2] for c_ in caught)))   # noqa: F821

failed112 = [n_ for n_, ok_ in RESULTS if not ok_]           # noqa: F821
print("predfix112_model: %d checks, %d failed%s" % (len(RESULTS), len(failed112),   # noqa: F821
                                                   (" (%s)" % ", ".join(failed112)) if failed112 else ""))
sys.exit(1 if failed112 else 0)
