#!/usr/bin/env python3
"""predarg moves: each printed line whose verdict the candidate changes, its re-spelling, and the re-spelling RUN
(WHOLE / SEARCHED / FIND-ALL, python `re` built mechanically from the program text by rxbuild.py) against the
printed answers of the moved line. The verdicts are cand.py's walker modes where it parses (A: the carve-out as a
door; B: the listed labels the body's own); hand verdicts are marked. Prints; asserts nothing.
Run: timeout 600 python3 -I -B moves.py
"""
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import cand  # noqa: E402
import load  # noqa: E402
import rxbuild  # noqa: E402

NS = load.NS
A = "A := /(?<h>\\d)/"
TXP = "WHOLE `3xx` HOLDS, `7xx` FAILS / SEARCHED `7xx 3xx` `3xx`@4 / FIND-ALL `3xx 7xx 4xx` [`3xx`@0, `4xx`@8]"
TX = (["3xx", "7xx"], "7xx 3xx", "3xx 7xx 4xx")


def built(prog, binds, cond, spec, texts):
    b = rxbuild.Build(prog, binds)
    g = b.pick(*spec)
    return rxbuild.modes(b.regex(g, cond), g, *texts)


def walk(prog, binds, read):
    return "; ".join("%s %s" % (m, cand.verdict(prog, binds, read, m)) for m in ("now", "A", "B"))


MOVES = [
    # (where, moved line, binds, read, re-spelling, its binds, its read, cond, target spec, texts, printed answers)
    ("core.md, core/labels/rule/paths, \"Through a call, the middle label skipped\"", "B(A) & (B.h: <5)",
     [A, "B(rx) := /${[p = rx]}xx/"], "B.h", "B(A) & (A.h: <5)", None, "A.h", "<5", ("h", 1), TX, TXP),
    ("core.md, core/labels/rule/alone-as-middle, \"A macro call used alone, a step\"",
     "[n = (P SEQ B(Q))] & (n.B.p.d: <5)", ["P := /(?<d>\\d)/", "Q := /,(?<d>\\d)/", "B(rx) := /${[p = rx]}xx/"],
     "n.B.p.d", "[n = (P SEQ B(Q))] & (Q.d: <5)", None, "Q.d", "<5", ("d", 2),
     (["7,3xx", "3,7xx"], "3,7xx 7,3xx", "7,3xx 3,7xx 4,1xx"),
     "WHOLE `7,3xx` HOLDS, `3,7xx` FAILS / SEARCHED `3,7xx 7,3xx` `7,3xx`@6 / FIND-ALL `7,3xx 3,7xx 4,1xx` [`7,3xx`@0, `4,1xx`@12]"),
    ("core.md, core/labels/paths/closed-argument, \"Through the body's path\"", "B(A) & (B.p.d: <5)",
     ["A := /(?<d>\\d)/", "B(rx) := /${[p = rx]}-(?<d>\\d)/"], "B.p.d", "B(A) & (A.d: <5)", None, "A.d", "<5",
     ("d", 1), (["7-3", "3-7", "3-3"], "7-3 3-7", "7-3 3-7 1-2 9-9"),
     "WHOLE `7-3` FAILS, `3-7` HOLDS, `3-3` HOLDS / SEARCHED `7-3 3-7` `3-7`@4 / FIND-ALL `7-3 3-7 1-2 9-9` [`3-7`@4, `1-2`@8]"),
    ("core.md, core/labels/paths/argument-default and shorthand-outside, \"From outside, written out\" (twice)",
     "[pub = B([A = A])] & (pub.A.h: <5)", [A, "B(rx) := /${[p = rx]}xx/"], "pub.A.h",
     "[pub = B([A = A])] & (A.h: <5)", None, "A.h", "<5", ("h", 1), TX, TXP),
    ("core.md, core/labels/rule/stacked-chain, \"Two binding levels, the middles skipped\" (re-spelled by "
     "changing B: no spelling in X or Y keeps it)", "X & (X.c.h: <5)",
     [A, "B(rx) := /${[p = rx]}xx/", "Y := [c = B(A)] SEQ \"!\"", "X := [y = Y] SEQ \";\""], "X.c.h",
     "X & (X.c.h: <5)", [A, "B(rx) := /${[p = [(=) = rx]]}xx/", "Y := [c = B(A)] SEQ \"!\"", "X := [y = Y] SEQ \";\""],
     "X.c.h", "<5", ("h", 1), (["3xx!;", "7xx!;"], "7xx!; 3xx!;", "3xx!; 7xx!; 4xx!;"),
     "WHOLE `3xx!;` HOLDS, `7xx!;` FAILS / SEARCHED `7xx!; 3xx!;` `3xx!;`@6 / FIND-ALL `3xx!; 7xx!; 4xx!;` [`3xx!;`@0, `4xx!;`@12]"),
]

GAINS = [
    # reading B only: a read that was an error becomes the label flow's last mention
    ("library.md, lib/convention/argument-labels, \"Two arguments\"", "W(/(?<h>\\d)/, /;(?<h>\\d)/) & (W.h: \"3\")",
     ["W(a, b) := [(=) = a] SEQ [(=) = b]"], "W.h", "\"3\"", ("h", 2), (["7;3", "3;7"], "x3;7 7;3", "7;3 3;7 1;3")),
    ("core.md, core/labels/paths/call-prefix, \"An argument used twice by the body\"", "pair(A) & (pair.d: <5)",
     ["A := /(?<d>\\d)/", "pair(p) := /${[(=) = p]},${[(=) = p]}/"], "pair.d", "<5", ("d", 2),
     (["7,3", "3,7", "3,3"], "3,7 7,3", "7,3 3,7 1,2 9,9")),
    ("library.md, lib/records/list-of, \"Through the call\"", "list_of(/(?<h>\\d)/, sep = \",\") & (list_of.h: \"5\")",
     [], "list_of.h", "\"5\"", ("h", 2), (["7,3,5", "7,5,3"], "x7,5 3,5", "1,5 3 5")),
]


def hits_modes(texts, ref):
    """hits(/a(?<g>x)?/) & (<ref>: "x"): the body is atomic and anchored, so one parse; the label is the LAST pass's
    own (core/labels/labels-vs-captures): g counts only where its span lies inside the last hit's span."""
    rx = re.compile(r"\A(?>(?:(?s:.*?)(?P<hit>a(?P<g>x)?))*[\s\S]*)\Z")

    def ok(t):
        m = rx.match(t)
        if not m or m.group("hit") is None or m.group("g") is None:
            return False
        return m.start("hit") <= m.start("g") and m.end("g") <= m.end("hit") and m.group("g") == "x"
    w, s, f = texts
    whole = ", ".join("`%s` %s" % (x, "HOLDS" if ok(x) else "FAILS") for x in w)
    return "WHOLE %s / SEARCHED `%s` %s / FIND-ALL `%s` %s (the hit list is the whole subject's)" % (
        whole, s, "`%s`@0" % s if ok(s) else "FAILS", f, "[`%s`@0]" % f if ok(f) else "[]")


def main():
    print("== MOVES: legal at the start commit, a compile error under the candidate (both readings)")
    for where, prog, binds, read, re_prog, re_binds, re_read, cond, spec, texts, printed in MOVES:
        rb = re_binds or binds
        got = built(re_prog, rb, cond, spec, texts)
        print("\n%s\n   moved      `%s`  (%s)\n   walker     %s" % (where, prog, "; ".join(binds), walk(prog, binds, read)))
        print("   re-spelled `%s`%s" % (re_prog, "  (%s)" % "; ".join(rb) if re_binds else ""))
        if re_binds:
            print("   walker     %s" % walk(re_prog, rb, re_read))
        else:
            print("   verdict    route (3), the sender's own name: unchanged by the candidate (the walker does not "
                  "place this start; documents' rule: legal)")
        print("   printed    %s\n   RUN        %s\n   %s" % (printed, got, "SAME" if got == printed else "DIFFERENT"))
    print("\n== MOVES the walker cannot parse, run by hand-written regexes from the body text")
    t = (["aax", "axa"], "axa", "aax axa")
    print("library.md, lib/search/hits, the first line: `hits(/a(?<g>x)?/) & (hits.hit.g: \"x\")` moves to a compile "
          "error (route 1, through the label `hit` the body writes on the place); re-spelled `hits(/a(?<g>x)?/) & "
          "(g: \"x\")` (the caller's own, read bare: the line \"Bare, the caller's own\"), the SAME label node:")
    print("   printed    WHOLE `aax` HOLDS, `axa` FAILS / SEARCHED `axa` FAILS / FIND-ALL `aax axa` []")
    print("   RUN        %s" % hits_modes(t, "g"))
    print("library.md, lib/search/occurrences, \"The argument's group, through the hit\": `occurrences(/(?<n>\\d+)/) & "
          "(occurrences.hit.n: \"3\")` moves (route 1); re-spelled `occurrences(/(?<n>\\d+)/) & (n: \"3\")`, the same "
          "label node, so the same answers by construction (the lazy loop re-chooses its hits under a condition: "
          "python `re` cannot run that condition, NOT RUN here; the printed answers stand for both)")
    print("core.md, core/labels/paths/argument-default, \"Through a part label in the body\": `B(A) & (B.dd.d: <100)` "
          "(A := `[d = rx.digits]`) moves (route 1); re-spelled `B(A) & (A.d: <100)`, printed with the same bindings "
          "and the same answers as core/holes/bare-condition/nested-scope's \"Example 1, the spot labelled, by the "
          "argument's name\" (both lines `same` in the model's sweep; not re-run here: rx.digits)")
    print("\n== GAINS under reading B only: a compile error at the start commit, legal (the last mention) when the "
          "listed labels count as the body's own")
    for where, prog, binds, read, cond, spec, texts in GAINS:
        print("\n%s\n   `%s`  (%s)\n   walker     %s" % (where, prog, "; ".join(binds), walk(prog, binds, read)))
        print("   RUN, the last mention  %s" % built(prog, binds, cond, spec, texts))
        print("   RUN, the first spot    %s" % built(prog, binds, cond, (spec[0], 1), texts))


if __name__ == "__main__":
    main()
