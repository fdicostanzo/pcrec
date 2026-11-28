#!/usr/bin/env python3
"""predarg probes: the adversarial programs of the study, each RUN.

For every probe: the in-force walker's verdict on each read in five modes (cand.py: now, A0, A, A2, B; body-own-name
and array-gate applied in all), then each READING the study names, answered in WHOLE / SEARCHED / FIND-ALL by a
python `re` regex built mechanically from the program text (rxbuild.py; the reading names which group the read
targets). A verdict the walker cannot reach (label parameters, named lists, provided natives) is given by HAND and
marked "hand". First a CONTROL: printed lines of the documents answered by the same builder, compared to the printed
answers. Prints; asserts nothing. Run: timeout 600 python3 -I -B probes.py
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cand  # noqa: E402
import load  # noqa: E402
import rxbuild  # noqa: E402

NS = load.NS
A = "A := /(?<h>\\d)/"
TX = (["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx")
MODES = ("now", "A0", "A", "A2", "B")


def run_reading(prog, binds, cond, spec, texts):
    b = rxbuild.Build(prog, binds)
    if isinstance(spec, list):                               # a group question `some`: any of the targets
        rxs = [b.regex(b.pick(*s), cond) for s in spec]
        tg = [b.pick(*s) for s in spec]
        alts = []
        for r, t in zip(rxs, tg):
            alts.append(r.replace("(?P<", "(?P<ZZ%d_" % len(alts)).replace("ZZ%d_%s>" % (len(alts), t), "T%d>" % len(alts)))
        rx = "(?:%s)" % "|".join(alts)
        import re
        c = re.compile(rx)

        class _M:
            pass
        out = rxbuild.modes(rx.replace("(?P<T0>", "(?P<T>", 1), "T", *texts) if len(alts) == 1 else None
        if out is None:                                      # a match counts where any target is set
            def ok_rx(t):
                return t
            w, s, f = texts
            def ok(m):
                return m is not None and any(m.group("T%d" % i) is not None for i in range(len(alts)))

            def srch(t):
                for i in range(len(t) + 1):
                    m = c.match(t, i)
                    if ok(m):
                        return "`%s`@%d" % (m.group(0), i)
                return "FAILS"

            def fa(t):
                o, i = [], 0
                while i <= len(t):
                    m = c.match(t, i)
                    if ok(m):
                        o.append("`%s`@%d" % (m.group(0), i))
                        i = m.end() if m.end() > i else i + 1
                        continue
                    i += 1
                return "[%s]" % ", ".join(o)
            out = "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` %s" % (
                ", ".join("`%s` %s" % (x, "HOLDS" if ok(c.fullmatch(x)) else "FAILS") for x in w), s, srch(s), f, fa(f))
        return out, rx
    g = b.pick(*spec)
    rx = b.regex(g, cond)
    return rxbuild.modes(rx, g, *texts), rx


CONTROL = [
    # (where, program, binds, cond, target spec, texts, printed answer)
    ("core.md, Through a call, the middle label skipped", "B(A) & (B.h: <5)", [A, "B(rx) := /${[p = rx]}xx/"], "<5",
     ("h", 1), TX, "WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]"),
    ("core.md, Used twice alone, the last mention", "pair(A) & (A.d: <5)", ["A := /(?<d>\\d)/", "pair(p) := /${p},${p}/"],
     "<5", ("d", 2), (["7,3", "3,7"], "3,7 7,3", "7,3 3,7 1,2"),
     "WHOLE `7,3` HOLDS, `3,7` FAILS / SEARCHED `3,7 7,3` `7,3`@4 / FIND-ALL `7,3 3,7 1,2` [`7,3`@0, `1,2`@8]"),
    ("core.md, d as the call exports it, the body's own", "[c = B(A)] & (c.d: <5)",
     ["A := /(?<e>\\d)/", "B(rx) := /${rx}-(?<d>\\d)/"], "<5", ("d", 1), (["7-3", "3-7", "3-3"], "3-7 7-3", "7-3 3-7 1-2 9-9"),
     "WHOLE `7-3` HOLDS, `3-7` FAILS, `3-3` HOLDS / SEARCHED `3-7 7-3` `7-3`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`7-3`@0, `1-2`@8]"),
    ("library.md, Two arguments, labelled", "W([a = /(?<h>\\d)/], [b = /;(?<h>\\d)/]) & (b.h: \"3\")",
     ["W(a, b) := [(=) = a] SEQ [(=) = b]"], "\"3\"", ("h", 2), (["7;3", "3;7"], "x3;7 7;3", "7;3 3;7 1;3"),
     "WHOLE `7;3` HOLDS, `3;7` FAILS / SEARCHED `x3;7 7;3` `7;3`@5 / FIND-ALL `7;3 3;7 1;3` [`7;3`@0, `1;3`@8]"),
    ("core.md, The mark written", "R(x:, A) & (x.h: <5)", [A, "R(l:, v) := /${[l = v]}xx/"], "<5", ("h", 1), TX,
     "WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]"),
]

L1 = "L1(x) := /${[(=) = x]}/"
L2 = "L2(x) := /${[(=) = x]}/"
T1 = "T1(x) := /${[t = x]}/"
T2 = "T2(x) := /${[t = x]}/"
TD = (["3", "7"], "7 3", "3 7 4")
TDASH = (["3-7", "7-3", "3-3", "7-7"], "7-7 3-7", "3-7 7-3 1-2 9-9")

PROBES = [
    dict(id="list-over-label", title="a body that lists a place it also labels, `[(=) = [p = rx]]`",
         prog="B1(A) & (B1.h: <5)", binds=[A, "B1(rx) := /${[(=) = [p = rx]]}xx/"], reads=["B1.h", "B1.p.h", "B1.p"],
         texts=TX, readings={"B1.h reads A's h (the list passes the part [p = rx]'s labels)": ("h", 1)}),
    dict(id="label-over-list", title="a body that labels a listed place, `[p = [(=) = rx]]`",
         prog="B2(A) & (B2.h: <5)", binds=[A, "B2(rx) := /${[p = [(=) = rx]]}xx/"], reads=["B2.h", "B2.p.h", "B2.p"],
         texts=TX, readings={"B2.h, B2.p.h read A's h": ("h", 1)}),
    dict(id="named-list-has", title="a named list `[(=h) = rx]`, the argument has h (his use-error lean: legal here)",
         prog="N(A) & (N.h: <5)", binds=[A, "N(rx) := /${[(=h) = rx]}xx/"], reads=["N.h"], texts=TX,
         readings={"N.h reads A's h": ("h", 1)},
         hand="the walker does not parse a named list; printed today: a compile error AT N's DEFINITION "
              "(core/labels/export/arguments, the line \"A named list on a spot\"); under his lean: legal for A"),
    dict(id="named-list-twice", title="a named list `[(=h) = rx]`, the argument sets h twice",
         prog="N(A2) & (N.h: <5)", binds=["A2 := /(?<h>\\d)(?<h>\\d)/", "N(rx) := /${[(=h) = rx]}xx/"], reads=["N.h"],
         texts=(["37xx", "73xx"], "37xx 73xx", "37xx 73xx 44xx"),
         readings={"the last mention (export-list: the alias has the part's settings; flow: last mention)": ("h", 2),
                   "the first setting": ("h", 1)},
         hand="the alias reads A2's own h, which two groups of ONE literal set: label flow, the last mention "
              "(core/labels/flow, `D2.c`); it is a use that is legal, not an error, whatever the lean"),
    dict(id="named-list-lacks", title="a named list `[(=h) = rx]`, the argument lacks h, has it behind a wall, or "
                                      "behind a gate",
         prog="N(Ae) SEQ N(Aw) SEQ N(Ag)", binds=["Ae := /(?<e>\\d)/", "Aw := [_w = /(?<h>\\d)/]", "Q := /(?<h>\\d)/",
                                                  "Ag := /${Q}/", "N(rx) := /${[(=h) = rx]}xx/"], reads=[], texts=TX,
         readings={},
         hand="his lean: each call is a USE error at the call (Ae exports no h; Aw keeps it behind `_w`; Ag uses Q "
              "alone, exporting nothing): the error names the call and the argument; N's definition is legal"),
    dict(id="named-list-nested", title="his use error when the named-list macro is called inside another body",
         prog="M(Ae) & (M.h: <5)", binds=["Ae := /(?<e>\\d)/", "M(r) := /<${[(=) = N(r)]}>/",
                                           "N(rx) := /${[(=h) = rx]}xx/"], reads=["M.h"], texts=TX, readings={},
         hand="M's definition cannot be judged (r is unknown there), so the error surfaces at `M(Ae)`, two bodies away "
              "from the list that requires h; the message must name N's list, M's place and Ae. With M2(r) := "
              "/<${N([q = r])}>/ the candidate DECIDES it at M2's definition: `[q = r]` exports only q (the place "
              "of r passes nothing through q), so `(=h)` can never be met: a definition error after all"),
    dict(id="sent-label-over-body-label", title="a sent label placed above a label the body writes on the place",
         prog="R2(x:, A) & (x.h: <5)", binds=[A, "R2(l:, v) := /${[l = [p = v]]}xx/"], reads=[], texts=TX,
         readings={"x.h reads A's h (the sender's own name x starts the path)": ("h", 1)},
         hand="the walker does not parse label parameters. Reading (i): x is the sender's own name, so x.h and x.p.h "
              "are legal (route 3). Reading (ii): the path from x crosses the body's p and then the argument's place, "
              "so x.p.h (and x.h, which skips p) go THROUGH the place: errors. Today: legal (the sent label is a "
              "start, one-path skips p)"),
    dict(id="label-forward", title="a label parameter forwarded, the sent label read",
         prog="F(x:, A) & (x.h: <5)", binds=[A, "F(l:, v) := /<${R(l:, v)}>/", "R(l:, v) := /${[l = v]}xx/"], reads=[],
         texts=(["<3xx>", "<7xx>"], "<7xx> <3xx>", "<3xx> <7xx> <4xx>"), readings={"x.h reads A's h": ("h", 1)},
         hand="the sender's own name x, placed by R on its place which holds F's place: route 3 under both readings "
              "of the probe before (x labels the place itself, nothing of the body's lies between)"),
    dict(id="shorthand-twice", title="the same binding passed twice, a body that labels both places",
         prog="B2a([a = A], [b = A]) & (b.h: <5)", binds=[A, "B2a(u, v) := /${[p = u]}-${[q = v]}/"],
         reads=["B2a.q.h", "B2a.h"], texts=(["7-3", "3-7"], "3-7 7-3", "7-3 3-7 1-2 9-9"),
         readings={"b.h reads the second A's h": ("h", 2)},
         hand="`B2a(A, A) & (A.h: ..)` is condition 1's compile error today and after (A referenced twice); today "
              "`B2a.q.h` names the second; under the candidate only the caller's labels do"),
    dict(id="in-place", title="an in-place argument: its group is the sender's own, read bare",
         prog="B(/(?<d>\\d)/) & (d: <5)", binds=["B(rx) := /${[p = rx]}xx/"], reads=["B.d", "B.p.d"], texts=TX,
         readings={"d bare (two-sources: the caller's own)": ("d", 1)}),
    dict(id="nested-list-list", title="B(C(A)), both bodies list", prog="L1(L2(A)) & (L1.h: <5)", binds=[A, L1, L2],
         reads=["L1.h"], texts=TD, readings={"L1.h reads A's h": ("h", 1)},
         hand="`L2.h` (the inner call's name, written in the caller's text) is a start the walker does not place: "
              "by hand legal under the candidate (the sender's own name for the inner call, which lists)"),
    dict(id="nested-list-label", title="B(C(A)), the outer lists, the inner labels", prog="L1(T2(A)) & (L1.h: <5)",
         binds=[A, L1, T2], reads=["L1.h", "L1.t.h"], texts=TD, readings={"A.h (the shorthand)": ("h", 1)}),
    dict(id="nested-label-list", title="B(C(A)), the outer labels, the inner lists", prog="T1(L2(A)) & (T1.h: <5)",
         binds=[A, T1, L2], reads=["T1.h", "T1.t.h"], texts=TD, readings={"A.h (the shorthand)": ("h", 1)}),
    dict(id="body-passes-on-listed", title="a body that passes its argument to another macro, which lists; the outer "
                                           "lists that call",
         prog="Mx(A) & (Mx.h: <5)", binds=[A, L2, "Mx(r) := /<${[(=) = L2(r)]}>/"], reads=["Mx.h"],
         texts=(["<3>", "<7>"], "<7> <3>", "<3> <7> <4>"), readings={"Mx.h reads A's h": ("h", 1)}),
    dict(id="body-passes-on-labelled", title="a body that passes its argument to another macro, which labels; the "
                                             "outer lists that call",
         prog="Mt(A) & (Mt.h: <5)", binds=[A, T2, "Mt(r) := /<${[(=) = T2(r)]}>/"], reads=["Mt.h", "Mt.t.h"],
         texts=(["<3>", "<7>"], "<7> <3>", "<3> <7> <4>"), readings={"A.h (the shorthand)": ("h", 1)}),
    dict(id="array-listed-twice", title="the array form over a place listed twice", prog="pair(A) & some(@pair.d, <5)",
         binds=["A := /(?<d>\\d)/", "pair(p) := /${[(=) = p]},${[(=) = p]}/"], reads=["@pair.d"],
         texts=(["7,3", "3,7", "7,7"], "7,7 3,7", "7,3 7,7 1,2"), readings={"every setting": [("d", 1), ("d", 2)]}),
    dict(id="array-labelled", title="the array form through a labelled place", prog="B(A) & some(@B.h, <5)",
         binds=[A, "B(rx) := /${[p = rx]}xx/"], reads=["@B.h"], texts=TX, readings={"A's h": [("h", 1)]}),
    dict(id="array-gate-listed", title="the array form through a call used alone that lists (the gate)",
         prog="[n = (P SEQ L1(Q))] & some(@n.d, <5)", binds=["P := /(?<d>\\d)/", "Q := /,(?<d>\\d)/", L1],
         reads=["@n.d", "n.L1.d"], texts=(["7,3", "3,7"], "3,7 7,3", "7,3 3,7 1,2"),
         readings={"n.L1.d, Q's d": ("d", 2)}),
    dict(id="index", title="metadata of a label inside an argument, and of the body's own label on the place",
         prog="[c = Bm(A)] & (c.a.h: <5)", binds=[A, "Bm(x) := [a = x] | [b = /z/]"], reads=["c.a.h", "c.a"],
         texts=(["3", "z", "7"], "7 z 3", "3 z 7 4"), readings={"A.h": ("h", 1)},
         hand="`(c.a.index: 1)` (the body's own label's metadata, a path that ends on the place) and `(c.b.index: 2)` "
              "stay legal; `c.a.h` and any metadata below it (`c.a.h.index` where h sits under a member) go through "
              "the place"),
    dict(id="capture", title="a capture request for an argument's label", prog="B(A) & (B.h: <5)",
         binds=[A, "B(rx) := /${[p = rx]}xx/"], reads=["B.h"], texts=TX, readings={},
         hand="`B(A) & (B.h: capture(\"h\"))` is route (1): an error under the candidate (the path is the read's, "
              "lib/structural/capture: \"the label is named where conditions name labels, by its path\"); "
              "`(A.h: capture(\"h\"))` and, through a list, `identity(A) & (identity.h: capture(\"h\"))` stay"),
    dict(id="when-shape", title="when's then branch: test and then both set h (the shape W of the library)",
         prog="W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: <5)", binds=["W(a, b) := [(=) = a] SEQ [(=) = b]"], reads=["W.h"],
         texts=(["7;3", "3;7"], "3;7 7;3", "7;3 3;7 1;2"),
         readings={"the last mention, then's h (reading B: the listed labels are the body's own)": ("h", 2)}),
    dict(id="map", title="a map built by a macro from its arguments (as a pattern: labelled alternatives)",
         prog="[m = Mk(A, Z)] & (m.a.h: <5)", binds=[A, "Z := /z/", "Mk(x, y) := [a = x] | [b = y]"], reads=["m.a.h", "m.a"],
         texts=(["3", "z", "7"], "7 z 3", "3 z 7 4"), readings={"A.h": ("h", 1)},
         hand="a module's members are reached by `.`; a member a macro builds on an argument (`{a = x}`) is the "
              "body's own label on the place: `m.a` stays, `m.a.h` is route (1); `{a = [(=) = x]}` would be the "
              "carve-out"),
    dict(id="own-then-listed", title="unpredictability: the body's own d BEFORE the listed place",
         prog="Bo(Ad) & (Bo.d: <5)", binds=["Ad := /(?<d>\\d)/", "Bo(rx) := /(?<d>\\d)-${[(=) = rx]}/"],
         reads=["Bo.d"], texts=TDASH,
         readings={"the body's own d (body-own-name: direct beats a skip)": ("d", 1),
                   "the argument's d (reading B: both own, the last mention)": ("d", 2)}),
    dict(id="own-then-listed-no-d", title="the same body, the argument without d", prog="Bo(Ae) & (Bo.d: <5)",
         binds=["Ae := /(?<e>\\d)/", "Bo(rx) := /(?<d>\\d)-${[(=) = rx]}/"], reads=["Bo.d"], texts=TDASH,
         readings={"the body's own d": ("d", 1)}),
    dict(id="listed-then-own", title="the body's own d AFTER the listed place, the argument with d",
         prog="Bb(Ad) & (Bb.d: <5)", binds=["Ad := /(?<d>\\d)/", "Bb(rx) := /${[(=) = rx]}-(?<d>\\d)/"],
         reads=["Bb.d"], texts=TDASH, readings={"the body's own d (both readings agree)": ("d", 2)}),
    dict(id="body-label-beside-own", title="body-own-name's reading (b): the argument under a label the body "
                                           "writes, the body's own d beside it",
         prog="B(A) & (B.d: <5)", binds=["A := /(?<d>\\d)/", "B(rx) := /${[p = rx]}-(?<d>\\d)/"], reads=["B.d"],
         texts=(["7-3", "3-7", "3-3"], "3-7 7-3", "7-3 3-7 1-2 9-9"), readings={"the body's own d": ("d", 2)}),
    dict(id="w-one-arg-has", title="two listed places, only one argument sets h", prog="W(/(?<h>\\d)/, /;(?<e>\\d)/) & (W.h: <5)",
         binds=["W(a, b) := [(=) = a] SEQ [(=) = b]"], reads=["W.h"], texts=(["3;7", "7;3"], "7;3 3;7", "3;7 7;3 1;2"),
         readings={"the first argument's h": ("h", 1)}),
    dict(id="own-label-on-place", title="the body's own label on the place, read as itself; its message below",
         prog="B(A) & (B.p: \"3\")", binds=[A, "B(rx) := /${[p = rx]}xx/"], reads=["B.p", "B.p.h"], texts=TX,
         readings={"B.p, the label's text": ("p", 1)}),
    dict(id="outside-written", title="a label the caller writes in an argument, read from a binding that uses the "
                                     "caller", prog="Y & (Y.a.h: <5)", binds=[A, "B(rx) := /${[p = rx]}xx/",
                                                                          "Y := [c = B([a = A])] SEQ \"!\""],
         reads=["Y.a.h", "Y.c.a.h", "Y.c.h"], texts=(["3xx!", "7xx!"], "7xx! 3xx!", "3xx! 7xx! 4xx!"), readings={"A's h": ("h", 1)},
         hand="reading (i): Y's text writes `a`, and a binding exports the labels its own text writes (export "
              "statement 3), so Y.a.h is legal; reading (ii): the path Y, B, p, the place, a crosses B's place: an "
              "error, and then a caller's label in an argument never leaves the caller"),
]


def main():
    print("== CONTROL: printed lines answered by rxbuild (the builder against the documents' printed answers)")
    for where, prog, binds, cond, spec, texts, printed in CONTROL:
        got, _ = run_reading(prog, binds, cond, spec, texts)
        print("%s %s\n   printed %s\n   built   %s" % ("SAME" if got == printed else "DIFF", where, printed, got))
    for p in PROBES:
        print("\n== %s: %s\n   program `%s`, %s" % (p["id"], p["title"], p["prog"], "; ".join(p["binds"])))
        for rd in p["reads"]:
            arr = rd.startswith("@")
            r = rd.lstrip("@")
            vs = {m: cand.verdict(p["prog"], p["binds"], r, m, array=arr) for m in MODES}
            print("   read %s" % rd)
            for m in MODES:
                print("      %-4s %s" % (m, vs[m]))
        if p.get("hand"):
            print("   hand: %s" % p["hand"])
        cond = None
        import re
        mm = re.search(r"(?:\((?:[\w.]+)\s*:\s*|some\(@[\w.]+,\s*)(<\s*\d|\"\d\"|\d)", p["prog"])
        cond = mm.group(1) if mm else "<5"
        for name, spec in p["readings"].items():
            try:
                got, rx = run_reading(p["prog"], p["binds"], cond, spec, p["texts"])
                print("   RUN %s:\n      %s\n      (regex %s)" % (name, got, rx))
            except Exception as x:                           # noqa: BLE001
                print("   RUN %s: the builder failed: %s" % (name, x))


if __name__ == "__main__":
    main()
