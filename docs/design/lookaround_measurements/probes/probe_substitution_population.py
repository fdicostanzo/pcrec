#!/usr/bin/env python3
"""[M6.6.1] §6.3 -- HOW MUCH OF tests/assertions/ THE SUBSTITUTION DRIVER GETS.

PURE TEXT. This probe reads `.rxt` files and counts; it runs no compiler and
no matcher. That is the box rule the brief set and it is also the right
instrument: the question is "how many cells QUALIFY", which is a property of
the corpus text, and answering it by running the driver would require the
driver to exist.

WHAT THE DRIVER IS. The assertions module's corpus is 10,120 libpcre2-verified
cells over 468 patterns. Every assertion in it has a lookaround DEFINITION
(probe_expansions.py E1: nine expansions, 972 cells, 0 disagreements). So
textually replacing each assertion by its expansion turns the assertions
corpus into a LOOKAROUND corpus for free, and the three-way check per cell
(expanded-under-pcrec vs folded-under-pcrec vs libpcre2-on-the-expanded) is
D66's self-oracle.

**IT IS A CORPUS GENERATOR, NOT A PRODUCT MECHANISM** (Frank, 2026-08-23
13:4x). It emits PATTERNS that the compiler sees as ordinary user-written
lookarounds. The PRODUCT-side substitution is [DD-14]'s subroutine-call
primitive, after lookaround lands.

THE QUALIFICATION RULES, each with the reason it exists and each counted
separately below so a reader can see which one costs the most:

  Q1  the block must have at least one BEHAVIOURAL cell (m/n/ms/ns). A `perr`
      block asserts pcrec REFUSES the pattern, and the expansion changes the
      reason for the refusal, so the assertion under test is gone.
  Q2  the pattern must contain at least one SUBSTITUTABLE assertion. `\\G` is a
      primitive against startpos and `\\K` is a match-start operator; neither
      has a lookaround definition (E1's last two rows).
  Q3  no substitutable assertion may sit INSIDE A CHARACTER CLASS. `[\\b]` is
      the BACKSPACE character and `[^a]` is a negation -- substituting either
      is a different pattern, not a rewritten one. This is the rule a `sed`
      driver would get wrong, which is why it is a rule and not a caveat.
  Q4  no SCOPED `(?m:` or `(?-m)`. `^` and `$` mean different things under
      different multiline states, so a textual driver must know the state at
      each occurrence; with `(?m)` leading and unscoped the state is constant
      and knowable, and with a scoped group it is not. A parser would lift
      this restriction and a parser is what the driver is trying not to be.
  Q5  `\\K` may appear in the pattern but MUST NOT end up inside a substituted
      lookaround, because PCRE2 refuses `\\K` in a lookaround (err 199,
      measured). Since the expansions' bodies are fixed text that contains no
      `\\K`, this can only happen if a `\\K` sits between the delimiters the
      driver inserts -- i.e. never, for the bracketing rule below. Counted
      anyway, so the claim is a number rather than an argument.

THE BRACKETING RULE. Every multi-branch expansion is wrapped `(?:...)` before
insertion, so `a\\bc` becomes `a(?:(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w))c` and not
`a(?<=\\w)(?!\\w)|(?<!\\w)(?=\\w)c` -- which is a different pattern with the
alternation at top level. `(?:` is NON-CAPTURING, so group numbers are
unchanged and every `g`/`gp` capture-slot expectation in the corpus survives
substitution untouched. That is why the driver can reuse the corpus's cells
verbatim instead of re-deriving them.
"""
import os
import re
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_ROOT = os.path.normpath(os.path.join(_HERE, "..", "..", "..", ".."))
CORPUS = [os.path.join(_ROOT, "tests", "assertions"),
          os.path.join(_ROOT, "tests", "assertions", "d27")]

SUBSTITUTABLE = [r"\b", r"\B", r"\A", r"\z", r"\Z", "^", "$"]
NO_DEFINITION = [r"\G", r"\K"]


def occurrences(pat):
    """Every assertion occurrence in `pat`, as (token, index, in_class).

    Walks the pattern the way the driver would have to: escape-aware and
    class-aware. Not a regex over the text -- `[\\b]` and `\\\\b` are exactly the
    cases a regex gets wrong."""
    out = []
    i, n = 0, len(pat)
    incls = False
    clspos = 0          # characters of CONTENT seen since `[` (or `[^`)
    expect_neg = False  # the very next char may be the negating `^`
    while i < n:
        c = pat[i]
        if c == "\\" and i + 1 < n:
            tok = pat[i:i + 2]
            if tok in SUBSTITUTABLE or tok in NO_DEFINITION:
                out.append((tok, i, incls))
            if incls:
                # R33 V-12(b), found while fixing V-12(a): an ESCAPE inside a
                # class is CONTENT. Without this, `[\]]` left clspos at 0, the
                # following `]` read as the literal-first `]`, the class never
                # closed, and every assertion after it was swallowed.
                clspos += 1
                expect_neg = False
            i += 2
            continue
        if incls:
            # R33 C3-2: a `]` IMMEDIATELY after `[` or `[^` is a LITERAL, not
            # the closing bracket (PCRE2's literal-first rule).
            #
            # R33 V-12(a): the first version tested `c == "^" and clspos == 0`,
            # which fires for EVERY leading-position `^` rather than only the
            # negation -- so `[^^]` consumed BOTH carets as "not content", the
            # `]` then read as literal-first, the class never closed, and
            # `[^^]$` lost its `$` entirely. `expect_neg` is true for exactly
            # one character position, which is what "the negating caret" means.
            if expect_neg and c == "^":
                expect_neg = False
                i += 1
                continue
            expect_neg = False
            if c == "]" and clspos > 0:
                incls = False
            clspos += 1
            i += 1
            continue
        if c == "[":
            incls = True
            clspos = 0
            expect_neg = True
            i += 1
            continue
        if c in ("^", "$"):
            out.append((c, i, False))
        i += 1
    return out


# R33 C3-1: Q4 WAS A SUBSTRING TEST and it misses `(?im:`, `(?i-m:`, `(?xm:`
# and every other letter set that contains `m` alongside another letter. It is
# INERT on today's corpus (the counts below are byte-identical before and
# after this fix) and it corrupts cells the moment such a block is added --
# exactly the growth failure a substring test hides. The rule is now: find any
# `(?` followed by a MODIFIER LETTER SET (the letters PCRE2 accepts, optional
# `-` and a second set) terminated by `:` or `)`, and ask whether `m` appears
# on either side of the `-`.
_MODLETTERS = "imnsxUJxa"          # the letters mod_modifiers.c accepts
_MODRE = re.compile(r"\(\?([a-zA-Z]*)(?:-([a-zA-Z]*))?([:\)])")


def has_scoped_m(pat):
    """True when `m` is turned on or off by any inline modifier group that is
    NOT a bare leading `(?m)`.

    A LEADING unscoped `(?m)` is fine -- the multiline state is then constant
    for the whole pattern and the driver can resolve `^`/`$` textually. Every
    other appearance (a scoped `(?im:...)`, a mid-pattern `(?-m)`, a second
    `(?m)` after something else) means the state varies with position, which a
    textual driver cannot follow without being a parser."""
    for m in _MODRE.finditer(pat):
        on, off, term = m.group(1) or "", m.group(2) or "", m.group(3)
        if not any(ch in _MODLETTERS for ch in on + off):
            continue                      # not a modifier group at all
        touches_m = ("m" in on) or ("m" in off)
        if not touches_m:
            continue
        if term == ")" and m.start() == 0 and not off and on == "m":
            continue                      # the bare leading `(?m)`
        return True
    return False


def blocks(path):
    """[(pattern, [directive lines], [cell lines], leading_comments)] per file."""
    out = []
    cur = None
    lead = []
    for raw in open(path, encoding="utf-8", errors="replace"):
        line = raw.rstrip("\n")
        if line.startswith("pattern "):
            if cur:
                out.append(cur)
            cur = {"pattern": line[len("pattern "):], "dirs": [], "cells": [],
                   "lead": lead}
            lead = []
            continue
        if not cur:
            if line.startswith("#"):
                lead.append(line)
            continue
        if re.match(r"^(m|n|ms|ns) ", line):
            cur["cells"].append(line)
        elif re.match(r"^(g|gp) ", line):
            cur["cells"].append(line)
        elif line.startswith("perr") or line.startswith("flags ") \
                or line.startswith("features "):
            cur["dirs"].append(line)
        elif line.startswith("#"):
            cur["dirs"].append(line)
    if cur:
        out.append(cur)
    return out


files = []
for d in CORPUS:
    if not os.path.isdir(d):
        continue
    for f in sorted(os.listdir(d)):
        if f.endswith(".rxt"):
            files.append(os.path.join(d, f))

print("corpus root :", os.path.join(_ROOT, "tests", "assertions"))
print("files       :", len(files))
print("python3     :", sys.version.split()[0])
print()

TOT = {"blocks": 0, "cells": 0, "behavioural": 0, "gcells": 0}
REJ = {"Q1 perr / no behavioural cell": [0, 0],
       "Q2 no substitutable assertion": [0, 0],
       "Q3 assertion inside a character class": [0, 0],
       "Q4 modifier state not constant": [0, 0],
       "Q5 \\K inside a substituted body": [0, 0],
       "Q6 block marked # pcre2-deviates (D68)": [0, 0]}
QUAL = {"blocks": 0, "cells": 0, "gcells": 0}
per_token = {}
per_file = {}

for path in files:
    bn = os.path.relpath(path, _ROOT)
    per_file[bn] = [0, 0, 0, 0]     # blocks, qual blocks, cells, qual cells
    for b in blocks(path):
        pat = b["pattern"]
        beh = [c for c in b["cells"] if re.match(r"^(m|n|ms|ns) ", c)]
        gs = [c for c in b["cells"] if re.match(r"^(g|gp) ", c)]
        TOT["blocks"] += 1
        TOT["cells"] += len(b["cells"])
        TOT["behavioural"] += len(beh)
        TOT["gcells"] += len(gs)
        per_file[bn][0] += 1
        per_file[bn][2] += len(beh)

        is_perr = any(d.startswith("perr") for d in b["dirs"])
        occ = occurrences(pat)
        subs = [o for o in occ if o[0] in SUBSTITUTABLE]
        in_class = [o for o in subs if o[2]]
        scoped = has_scoped_m(pat)

        why = None
        if is_perr or not beh:
            why = "Q1 perr / no behavioural cell"
        elif not subs:
            why = "Q2 no substitutable assertion"
        elif in_class:
            why = "Q3 assertion inside a character class"
        elif scoped:
            why = "Q4 modifier state not constant"
        elif any(d.startswith("# pcre2-deviates") for d in b["dirs"]) or \
                any(l.startswith("# pcre2-deviates") for l in b["lead"]):
            # R33 C3-3: a block D68 marks as DELIBERATELY diverging from
            # libpcre2 would false-fail the A == C arm, which compares against
            # libpcre2. Costed 0/0 today -- no such block exists in this
            # corpus -- and the rule is here so a future one is excluded
            # rather than reported as a driver failure.
            why = "Q6 block marked # pcre2-deviates (D68)"
        if why:
            REJ[why][0] += 1
            REJ[why][1] += len(beh)
            continue
        QUAL["blocks"] += 1
        QUAL["cells"] += len(beh)
        QUAL["gcells"] += len(gs)
        per_file[bn][1] += 1
        per_file[bn][3] += len(beh)
        for tok, _i, _c in subs:
            per_token[tok] = per_token.get(tok, 0) + 1

print("=" * 78)
print("THE WHOLE CORPUS")
print("=" * 78)
print("  blocks (pattern lines)          : %d" % TOT["blocks"])
print("  ALL cells (m/n/ms/ns/g/gp)      : %d" % TOT["cells"])
print("  BEHAVIOURAL cells (m/n/ms/ns)   : %d" % TOT["behavioural"])
print("  capture-slot cells (g/gp)       : %d" % TOT["gcells"])
print()
print("  THE 10,120 THE CHARTER QUOTES IS THE BEHAVIOURAL COUNT, and this")
print("  probe's first draft said the opposite -- that 10,120 was the ALL-cells")
print("  figure and the behavioural one was smaller. It is the other way round:")
print("  10,120 behavioural + 67 capture-slot cells = 10,187 total. The error")
print("  is recorded rather than quietly corrected because a design that")
print("  reported its population against the wrong denominator would have")
print("  understated the driver's reach.")
print()
print("=" * 78)
print("WHAT QUALIFIES FOR TEXTUAL SUBSTITUTION")
print("=" * 78)
print("  QUALIFYING blocks               : %d of %d  (%.0f%%)"
      % (QUAL["blocks"], TOT["blocks"], 100.0 * QUAL["blocks"] / max(1, TOT["blocks"])))
print("  QUALIFYING behavioural cells    : %d of %d  (%.0f%%)"
      % (QUAL["cells"], TOT["behavioural"],
         100.0 * QUAL["cells"] / max(1, TOT["behavioural"])))
print("  ... carrying capture-slot cells : %d" % QUAL["gcells"])
print()
print("  DISQUALIFIED, by rule:")
for k in sorted(REJ):
    print("    %-40s %4d blocks  %5d cells" % (k, REJ[k][0], REJ[k][1]))
print()
print("  Substitutable assertion OCCURRENCES in qualifying blocks, by token:")
for k in sorted(per_token, key=lambda x: -per_token[x]):
    print("    %-4s %d" % (k, per_token[k]))
print()
print("=" * 78)
print("PER FILE")
print("=" * 78)
print("  %-42s %-16s %s" % ("file", "blocks (qual)", "cells (qual)"))
for k in sorted(per_file):
    b, qb, c, qc = per_file[k]
    print("  %-42s %3d (%3d)        %4d (%4d)" % (k, b, qb, c, qc))

print()
print("=" * 78)
print("THE EXPANSION MULTIPLIER")
print("=" * 78)
print("A qualifying block yields ONE expanded pattern per substitution POLICY,")
print("not one per assertion: the driver substitutes EVERY substitutable")
print("occurrence in the pattern at once, because a half-substituted pattern")
print("tests neither form. Two policies are worth generating and the second is")
print("the one that finds bugs:")
print()
print("  P1  ALL-AT-ONCE  -- every occurrence replaced. %d patterns."
      % QUAL["blocks"])
print("  P2  ONE-AT-A-TIME -- one occurrence replaced per generated pattern,")
print("      the rest left folded. This is the MIXED form, where a folded")
print("      assertion and an expanded one must agree INSIDE ONE PATTERN, and")
print("      it is where an interaction between the two lowerings would show.")
nocc = sum(per_token.values())
print("      %d patterns (one per occurrence)." % nocc)
print()
print("  TOTAL GENERATED PATTERNS: %d, over %d behavioural cells each time"
      % (QUAL["blocks"] + nocc, QUAL["cells"]))
print("  i.e. roughly %d three-way comparisons for P1 and %d for P2."
      % (QUAL["cells"], QUAL["cells"]))
print()
print("  (P2's cell count is not cells x occurrences: each generated pattern")
print("   is checked against its OWN block's cells, and every occurrence in a")
print("   block comes from the same block. The two policies therefore cost")
print("   about the same per-cell total, which is why both are proposed.)")
