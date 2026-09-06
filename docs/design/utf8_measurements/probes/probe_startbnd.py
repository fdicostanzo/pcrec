#!/usr/bin/env python3
"""probe_startbnd.py — [K50-BNDSTART]: WHERE MAY A MATCH START, and what does
a mid-character `startoffset` do?

Two questions, both of which the K50 charter says must be MEASURED against
the reference oracle before anything is pinned:

  §1  **The candidate-start rule.** K50 is that pcrec's `-e utf8` unanchored
      DFA reports match starts at BYTE offsets, so a pattern nullable at a
      mid-character position answers there. This section walks EVERY
      startoffset of a multi-byte subject for a family of patterns that are
      nullable-with-an-assertion (the direction §2.6.1 says INVERTS), and
      prints all three option words side by side. `options=0` is included on
      purpose: K50's whole finding is that pcrec under `-e utf8` returns the
      `options=0` column, so a reader can see the two columns disagree.

  §2  **BADUTFOFFSET — the CALLER-STARTPOS half.** Frank's 2026-09-05 ruling
      gives the emitted entry a default-on boundary guard refusing a
      mid-character caller `startpos` with a typed code. The charter's
      instruction is to MEASURE 10.46's own behaviour first, "transcript not
      assertion, before pinning any compat claim". This section asks whether
      `PCRE2_UTF`'s refusal is UNIFORM (every mid-character offset, every
      pattern) or pattern-dependent — which is the difference between "pcrec
      refuses like PCRE2 does" being a claim about a shape and a claim about
      a table.

  §3  **The ill-formed traversal that must SURVIVE the fix.** Charter (b):
      §2.6(c) stands — the search still traverses ill-formed bytes; the gate
      is on where attempts BEGIN. These rows are the ones a fix must not
      move, and they also record where pcrec's ruled semantics (ASK 1: the
      automaton's answer, no validation pass) legitimately part company with
      both of PCRE2's UTF modes.

D26: PCRE2 is the source of truth for SEMANTICS. Nothing here is pcrec, and
no check reads this transcript — it is evidence for the lane's report and the
K50 entry, per ../CLAUDE.md's two rules.
"""
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import u8_oracle as o                                       # noqa: E402

WORDS = [o.opts(), o.opts("UTF"), o.opts("UTF", "MATCH_INVALID_UTF")]


def show(r):
    """One cell, in the narrowest spelling that stays unambiguous."""
    if r is None:
        return "no-match"
    if r[0] == "ERRM":
        return "ERRM %d" % r[1]
    if r[0] == "ERRC":
        return "ERRC %d" % r[1]
    (s, e), _ = r
    return "(%d,%d)" % (s, e)


def sweep(pat, subj, note=""):
    """Every startoffset of `subj`, every option word, one block."""
    print("  pattern %-14s subject %-18s %s"
          % (o.pshow(pat), o.hexs(subj), note))
    for w in WORDS:
        cells = ["%d:%s" % (st, show(o.match(pat, subj, st, w)))
                 for st in range(len(subj) + 1)]
        print("      %-30s %s" % (o.opts_name(w), "  ".join(cells)))
    print()


print(o.header("[K50-BNDSTART] candidate match starts and mid-character "
               "startoffsets"))
warn = o.require_1046()
if warn:
    print(warn)
    print()

print("BOUNDARY LEGEND. A subject's CHARACTER BOUNDARIES are printed with each")
print("block. Under UTF-8 a position p is a boundary iff p == n or s[p] is not")
print("a continuation byte (s[p] & 0xC0) != 0x80 — the same local predicate")
print("`next_pos` and the [K49] advance already implement.")
print()

# ------------------------------------------------------------------ §1
print("=" * 74)
print("§1  THE CANDIDATE-START RULE — every startoffset, three option words")
print("=" * 74)
print()
print("K50's own witness first. `a` then alpha: boundaries 0, 1, 3; byte 2 is")
print("alpha's continuation byte. pcrec's DFA reports (2,2) from startpos 0.")
print()
sweep(rb"\B", b"a\xce\xb1", "boundaries 0,1,3")
sweep(rb"\Bx?", b"a\xce\xb1", "boundaries 0,1,3")

print("THE SECOND SITE. K50's site list names `ENG_ATTEMPT`'s `start++` loop")
print("(src/gen/emit_dfa.c) as a mechanism a fix must also reach, but files no")
print("witness for it — §5.5 and ASK 5 assert it merely wastes attempts. A")
print("pattern with a BOT-family branch routes to that engine, and a second")
print("branch nullable-at-a-boundary keeps its interior start state live:")
print()
sweep(rb"(?m)^a|\B", b"a\xce\xb1", "boundaries 0,1,3")

print("WIDER CHARACTERS. The reported position moves further inside the")
print("character as the encoding widens, so a 4-byte subject has three wrong")
print("answers available where a 2-byte one has one.")
print()
sweep(rb"\B", b"a\xe4\xb8\xad", "boundaries 0,1,4")
sweep(rb"\B", b"a\xf0\x9f\x98\x80", "boundaries 0,1,5")

print("THE NEGATIVE-ASSERTION FAMILY — §2.6.1's inversion, which is what")
print("turns a mid-character start from a wasted attempt into an answer.")
print()
sweep(rb"(?!\xce)", b"a\xce\xb1", "boundaries 0,1,3")
sweep(rb"(?<!.)", b"\xce\xb1\xce\xb2", "boundaries 0,2,4")
sweep(rb"(?!.)", b"\xce\xb1\xce\xb2", "boundaries 0,2,4")
sweep(rb"(?:(?<!q)|x)", b"\xce\xb1\xce\xb2", "boundaries 0,2,4")

# ------------------------------------------------------------------ §2
print("=" * 74)
print("§2  BADUTFOFFSET — is the refusal UNIFORM, or pattern-dependent?")
print("=" * 74)
print()
print("Subject CE B1 CE B2 (alpha beta): boundaries 0, 2, 4; offsets 1 and 3")
print("are mid-character. If `PCRE2_UTF` answers the same way for every")
print("pattern at 1 and 3, the refusal is a property of the OFFSET, which is")
print("what an O(1) entry guard can reproduce. If it is pattern-dependent, an")
print("entry guard is the wrong shape and the charter's design needs revising.")
print()
for pat in (rb"", rb"a", rb".", rb"\B", rb"\b", rb"(?<!.)", rb"(?!.)",
            rb"\xce\xb1", rb"[\x00-\xff]", rb"x*"):
    sweep(pat, b"\xce\xb1\xce\xb2", "boundaries 0,2,4")

print("AND AT THE OTHER END OF THE RANGE: `startoffset == n` is a boundary,")
print("and `startoffset > n` is a separate question the pcrec entry answers")
print("with 0 (match_api.md §3.1). Measured rather than assumed:")
print()
for st in (4, 5, 6):
    print("      start=%d  %s"
          % (st, show(o.match(rb"x*", b"\xce\xb1\xce\xb2", st, o.opts("UTF")))))
print()

# ------------------------------------------------------------------ §3
print("=" * 74)
print("§3  ILL-FORMED TRAVERSAL — the rows a fix must NOT move (charter (b))")
print("=" * 74)
print()
print("utf8_design.md §2.6(c): a search finds matches AFTER an ill-formed")
print("byte. pcrec's own ruling (ASK 1) is the automaton's answer with no")
print("validation pass, which is `MATCH_INVALID_UTF`'s column on the cells")
print("§2.6 measured — these rows record where that agreement holds and where")
print("it does not, so the fix's own tests can tell the two apart.")
print()
sweep(rb"a", b"\xffa", "0xFF is a boundary byte by the predicate")
sweep(rb"a", b"a\xff", "")
sweep(rb"a.c", b"a\xffc", "matches THROUGH an ill-formed byte?")
sweep(rb"\B", b"a\xff\xb1", "byte 2 is a continuation byte after an illegal one")
sweep(rb"\B", b"\xce\x61", "truncated: CE declares 2, run is 1")

print("=" * 74)
print("END")
print("=" * 74)
