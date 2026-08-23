#!/usr/bin/env python3
"""[M6.6.1] §6 -- THE ASSERTION-FAMILY REPLACEMENTS as design examples.

Frank, 2026-08-23: "for lookaround, consider as test cases/design examples the
replacements we were discussing, e.g. ^ under (?m)."

The replacements are [DD-11]/D66's definition-expansion forms: each member of
the assertion family rewritten as the lookaround it IS. This probe answers
four questions about them, and every one is a cell rather than a claim:

  E1  IS EACH EXPANSION ACTUALLY EQUIVALENT to the assertion it replaces,
      under libpcre2, over a subject set chosen for the boundaries (empty,
      trailing newline, consecutive newlines, CRLF, no newline at all)? An
      expansion table nobody checked is a list of guesses.

  E2  DOES EACH EXPANSION'S LOOKAROUND BODY FALL INSIDE THE SUBSET §2.5
      SHIPS? Per body: is it a lookahead (no width rule at all) or a
      lookbehind, and if a lookbehind, is every top-level branch fixed?
      This is the question that decides whether the expanded corpus (§6.3)
      is compilable by [M6.6.2] at all.

  E3  WHAT DOES python3 `re` DO with each expansion? The D27 author needs
      this per expansion, not per construct: `(?<=\\n)` is fine in python and
      `(?<=\\n?)` would not be, so "python rejects variable-width lookbehind"
      is only actionable once each expansion is placed on one side of it.

  E4  DOES pcrec's SHIPPED FOLDED form agree with libpcre2's expansion? This
      is the D66 self-oracle's libpcre2 half, run here on the expansions
      themselves rather than on a corpus, so §6.3's driver starts from a
      checked table.
"""
import importlib.util
import os
import subprocess
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
_spec = importlib.util.spec_from_file_location(
    "la_oracle", os.path.join(_HERE, "la_oracle.py"))
la = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(la)

PCREC = os.path.join(_ROOT, "build", "pcrec")

# The subject set. Chosen for the boundaries the assertion family lives on,
# not for coverage: an empty subject, a subject that is only a newline, a
# trailing newline, a leading newline, consecutive newlines, CRLF, and a
# subject with no newline at all. `assertions_design.md`'s own \Z/\z
# divergence and the (?m)^ curve both live in this set.
SUBJ = ["", "a", "ab", "\n", "a\n", "\na", "a\nb", "a\n\nb", "\n\n",
        "abc\ndef\n", "\r\n", "a\r\nb\r\n", "x\ny\nz", " a ", "a_b", "1a",
        "a b", "aa\n\nbb"]

# (name, folded spelling, expansion, note)
# The expansions are [DD-11]/D66's, transcribed from the plan row and the
# decision, NOT invented here.
EXPANSIONS = [
    (r"\b",    r"\b",     r"(?:(?<=\w)(?!\w)|(?<!\w)(?=\w))",
     "word boundary"),
    (r"\B",    r"\B",     r"(?:(?<=\w)(?=\w)|(?<!\w)(?!\w))",
     "non-boundary: \\b's negation, distributed"),
    (r"(?m)^", r"(?m)^",  r"(?:\A|(?<=\n)(?!\z))",
     "multiline ^ -- the (?!\\z) term IS the U11b carve-out"),
    (r"(?m)$", r"(?m)$",  r"(?:(?=\n)|\z)",
     "multiline $"),
    (r"\Z",    r"\Z",     r"(?=\n?\z)",
     "end, or before a final newline"),
    (r"$",     r"$",      r"(?=\n?\z)",
     "default-flags $ IS \\Z (measured, not assumed)"),
    (r"^",     r"^",      r"\A",
     "default-flags ^ IS \\A"),
    (r"\A",    r"\A",     r"\A",
     "a PRIMITIVE: no lookaround definition, it is the floor"),
    (r"\z",    r"\z",     r"\z",
     "a PRIMITIVE"),
    (r"\G",    r"\G",     None,
     "a PRIMITIVE against startpos -- NO lookaround expansion exists"),
    (r"\K",    r"\K",     None,
     "a match-START operator, not an assertion -- no expansion, and PCRE2 "
     "REFUSES it inside a lookaround (err 199)"),
]

# The lookaround bodies each expansion contains, for E2. Written out rather
# than parsed, because a parser here would be a second implementation of
# §2.5's branch-splitting rule -- the same argument §4.4 makes about the
# codegen check's declared count.
BODIES = [
    (r"(?<=\w)",   "behind", ["\\w"],        "one class, width 1"),
    (r"(?!\w)",    "ahead",  ["\\w"],        "one class"),
    (r"(?<!\w)",   "behind", ["\\w"],        "one class, width 1"),
    (r"(?=\w)",    "ahead",  ["\\w"],        "one class"),
    (r"(?<=\n)",   "behind", ["\\n"],        "one literal, width 1"),
    (r"(?!\z)",    "ahead",  ["\\z"],        "an ANCHOR as the body"),
    (r"(?=\n)",    "ahead",  ["\\n"],        "one literal"),
    (r"(?=\n?\z)", "ahead",  ["\\n?\\z"],    "OPTIONAL + anchor -- widths 1..2"),
]


def show(v):
    if v == "ERR":
        return "ERR"
    if v is None:
        return "nomatch"
    return "(%d,%d)" % (v[0][0], v[0][1])


def hdr(t):
    print()
    print("=" * 78)
    print(t)
    print("=" * 78)


print("libpcre2:", la.version())
print("python3  :", sys.version.split()[0])
print("la_oracle SELFCHECK:", la.SELFCHECK or "none")
print("pcrec    :", "present" if os.path.exists(PCREC) else "ABSENT")

# ---------------------------------------------------------------------------
hdr("E1 -- IS EACH EXPANSION EQUIVALENT? (libpcre2 against itself)")
print("Both arms are wrapped `(?m:...)` or plain to match the folded form's own")
print("option state. A first version of this measurement put `(?m)` on ONE arm")
print("and reported three disagreements that were about `$`, not about the")
print("expansion -- see out/CLAUDE.md defect 4. The tails below therefore")
print("include `$` and `\\b` DELIBERATELY, because those are option-sensitive")
print("and are where a one-armed wrapping shows up.")
print()
TAILS = ["", "x", r"\w", "$", r"\b", r"\n"]
print("%-9s %-36s | cells | disagreements" % ("construct", "expansion"))
print("-" * 78)
total_cells = 0
total_dis = 0
for name, folded, expanded, note in EXPANSIONS:
    if expanded is None:
        print("%-9s %-36s |   --  | NO EXPANSION (%s)" % (name, "-", note))
        continue
    dis = []
    n = 0
    for s in SUBJ:
        for t in TAILS:
            # `(?m:...)` on BOTH arms whenever the construct carries `(?m)`,
            # so the tail means the same thing on both sides.
            if folded.startswith("(?m)"):
                pa = "(?m:" + folded[4:] + t + ")"
                pb = "(?m:" + expanded + t + ")"
            else:
                pa, pb = folded + t, expanded + t
            ra, rb = la.search(pa, s), la.search(pb, s)
            n += 1
            if show(ra) != show(rb):
                dis.append((pa, pb, s, show(ra), show(rb)))
    total_cells += n
    total_dis += len(dis)
    print("%-9s %-36s | %5d | %d" % (name, expanded, n, len(dis)))
    for pa, pb, s, ra, rb in dis[:8]:
        print("      DISAGREE %-22s vs %-30s subj=%-12s %s vs %s"
              % (pa, pb, repr(s), ra, rb))
    if len(dis) > 8:
        print("      ... and %d more" % (len(dis) - 8))
print()
print("TOTAL: %d cells, %d disagreements" % (total_cells, total_dis))
print()
print("# VACUITY GUARD: a WRONG expansion must be able to show up here.")
print("# The control is `(?m)^` expanded WITHOUT the (?!\\z) term, which D66's")
print("# own text says is load-bearing:")
ctl = 0
ctln = 0
for s in SUBJ:
    for t in TAILS:
        pa = "(?m:^" + t + ")"
        pb = "(?m:(?:\\A|(?<=\\n))" + t + ")"
        ctln += 1
        if show(la.search(pa, s)) != show(la.search(pb, s)):
            ctl += 1
print("    `\\A|(?<=\\n)` (no (?!\\z)) disagrees on %d of %d cells" % (ctl, ctln))
if ctl == 0:
    print("    !! ZERO -- this population cannot tell a wrong expansion from a")
    print("    !! right one, and E1's zeros above measure nothing")

# ---------------------------------------------------------------------------
hdr("E2 -- DOES EACH BODY FALL INSIDE THE SUBSET §2.5 SHIPS?")
print("A lookAHEAD body has NO width rule -- any body is legal. A lookBEHIND")
print("body must have every top-level branch fixed-width. Measured per body by")
print("asking libpcre2 for PCRE2_INFO_MAXLOOKBEHIND on a lookbehind built from")
print("it, and by asking whether the body compiles as a lookbehind at all.")
print()
print("%-13s %-7s %-30s | pcre2 as (?<=B) | maxlb | ships?" %
      ("body", "dir", "note"))
print("-" * 100)
for body, direction, parts, note in BODIES:
    inner = body[body.index(":") + 1:-1] if False else None
    # reconstruct the inner text from the spelling itself
    for pre in ("(?<=", "(?<!", "(?=", "(?!"):
        if body.startswith(pre):
            inner = body[len(pre):-1]
            break
    as_lb = "(?<=" + inner + ")x"
    e = la.compile_err(as_lb)
    mlb = la.maxlookbehind(as_lb)
    if direction == "ahead":
        ships = "YES (a lookahead has no width rule)"
    else:
        ships = "YES (fixed width %s)" % mlb if e is None and mlb else "NO"
    print("%-13s %-7s %-30s | %-15s | %-5s | %s"
          % (body, direction, note,
             "ok" if e is None else "err %d" % e[0],
             "-" if mlb is None else mlb, ships))
print()
print("# BODIES pcrec's §2.5 RULE REFUSES AS LOOKBEHINDS THOUGH PCRE2 ACCEPTS")
print("# THEM. Note the column: PCRE2 says `ok` to all three, because PCRE2")
print("# ships variable-length lookbehind and pcrec does not. maxlb alone")
print("# cannot show this -- an OPTIONAL body has minw 0 and maxw 1, and")
print("# PCRE2 publishes only the max -- so the classification is by the")
print("# BODY's own shape and is stated, not read off the oracle:")
for b, mn, mx in [(r"\n?\z", 0, 1), (r"\n?", 0, 1), (r"\w?", 0, 1),
                  (r"\n", 1, 1), (r"\w", 1, 1)]:
    e = la.compile_err("(?<=" + b + ")x")
    print("    (?<=%-8s)x  pcre2=%-8s maxlb=%-4s minw=%d maxw=%d  pcrec: %s"
          % (b, "ok" if e is None else "err %d" % e[0],
             la.maxlookbehind("(?<=" + b + ")x"), mn, mx,
             "SHIPS" if mn == mx else "REFUSED (variable)"))
print("    ^ `(?=\\n?\\z)` is a LOOKAHEAD in the \\Z/$ expansion, so its")
print("      optional body is legal THERE and would be refused as a")
print("      LOOKBEHIND. The distinction is DIRECTION, not the body -- which")
print("      is why every expansion in E1 compiles under §2.5 despite one of")
print("      them containing an optional.")

# ---------------------------------------------------------------------------
hdr("E3 -- python3 `re` on each expansion (the D27 goal-facts input)")
print("%-9s %-36s | python3 re" % ("construct", "expansion"))
print("-" * 90)
for name, folded, expanded, note in EXPANSIONS:
    if expanded is None:
        print("%-9s %-36s | (no expansion)" % (name, "-"))
        continue
    c, err = la.pyre(expanded + "x")
    print("%-9s %-36s | %s" % (name, expanded, "ok" if err is None else err))
print()
print("# and the FOLDED spellings, for the same author:")
for name, folded, expanded, note in EXPANSIONS:
    c, err = la.pyre(folded + "x")
    print("    %-9s -> %s" % (folded, "ok" if err is None else err))
print()
print("# the variable-width lookbehind the charter warns about, as its own cell:")
for p in [r"(?<=\n?\z)x", r"(?<=\n?)x", r"(?<=\w)x", r"(?<!\w)x", r"(?<=\n)x"]:
    c, err = la.pyre(p)
    e2 = la.compile_err(p)
    print("    %-16s python=%-46s pcre2=%s"
          % (p, "ok" if err is None else err,
             "ok" if e2 is None else "err %d" % e2[0]))

# ---------------------------------------------------------------------------
hdr("E4 -- pcrec's SHIPPED FOLDED form against libpcre2's EXPANSION")
print("The D66 self-oracle's shape, run on the expansions themselves. pcrec")
print("compiles the FOLDED spelling (module `assertions`, shipped); libpcre2")
print("evaluates the EXPANSION. Agreement here is what makes §6.3's corpus-wide")
print("driver worth building; a disagreement would kill the hand-off.")
print()
if not os.path.exists(PCREC):
    print("  SKIPPED -- no build/pcrec (this line is the skip, not silence)")
else:
    scratch = os.environ.get("LA_SCRATCH", "/tmp")
    ndis = ncell = nskip = 0
    for name, folded, expanded, note in EXPANSIONS:
        if expanded is None:
            continue
        for t in ("", r"\w"):
            pat = folded + t
            src = os.path.join(scratch, "la_e%d.c" % (abs(hash(pat)) % 100000))
            exe = src[:-2]
            r = subprocess.run(
                ["/usr/bin/gnutimeout", "20", PCREC, "-p", "rx",
                 "--features", "all", "--emit-main", "-o", src, pat],
                capture_output=True, text=True, cwd=_ROOT)
            if r.returncode != 0:
                nskip += 1
                print("  pcrec REFUSED %-12s : %s" % (repr(pat), r.stderr.strip()[:60]))
                continue
            c = subprocess.run(["/usr/bin/gnutimeout", "120", "nice", "-n", "19",
                                "gcc", "-O1", "-o", exe, src],
                               capture_output=True, text=True)
            if c.returncode != 0:
                nskip += 1
                print("  gcc FAILED on %-12s : %s" % (repr(pat), c.stderr.strip()[:60]))
                continue
            exp = ("(?m:" + expanded + t + ")") if folded.startswith("(?m)") \
                else (expanded + t)
            for s in SUBJ:
                got = subprocess.run(["/usr/bin/gnutimeout", "10", exe, s],
                                     capture_output=True, text=True).stdout.strip()
                want = la.search(exp, s)
                wants = ("nomatch" if want is None
                         else "match %d %d" % (want[0][0], want[0][1]))
                ncell += 1
                if got != wants:
                    ndis += 1
                    if ndis <= 12:
                        print("  DISAGREE %-10s subj=%-12s pcrec(folded)=%-14s "
                              "pcre2(expanded)=%s" % (pat, repr(s), got, wants))
    print()
    print("  pcrec FOLDED vs libpcre2 EXPANDED: %d disagreements over %d cells "
          "(%d patterns skipped)" % (ndis, ncell, nskip))
    if ncell == 0:
        print("  !! ZERO CELLS -- this arm measured nothing")
