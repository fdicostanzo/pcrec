#!/usr/bin/env python3
"""tests/codegen/lookaround_classify.py — the BUCKET SPLIT for module
`lookaround`'s byte-identity gate ([M6.6.2] wave B+C).

Splits a pattern list into lookaround-BEARING and lookaround-FREE.

WHY IT IS A SCAN AND NOT A GREP. `(?=` inside a character class is three
literal bytes (`[(?=]` matches `(`, `?` or `=`), `\\(?=` is an escaped paren
followed by an ordinary `?` quantifier, and `(?<name>` is a NAMED GROUP that
belongs to a different module — SR-9 split the `<` selector by TAIL for exactly
that reason, after a 256-byte sweep found that exactly three tails (`=`, `!`,
`*`) are lookaround and every other byte is the named-group path. A substring
test gets all three of those wrong, and it gets them wrong in the direction
that ADMITS a pattern to the identity population it does not belong in — a
silent pass.

IT FAILS SAFE TOWARD THE BEARING BUCKET, and the gate's positive control is
what makes that safe rather than merely convenient: the bearing bucket is
asserted to be REFUSED IN FULL by the pinned pre-module reference, so
OVER-classifying is caught loudly (a `(?i)` pattern filed as bearing makes the
control red) while costing at worst a pattern from the identity population.
UNDER-classifying is the direction with no such backstop, so three cases go to
BEARING though no rule names them: a truncated `(?` at end of pattern, a
truncated `(?<` at end of pattern, and any `(*name:` whose name merely
CONTAINS "look".

Usage: lookaround_classify.py <patterns> <bearing-out> <free-out>
"""
import sys

# The module's spellings, design §2.1. The twelve ALPHA ones plus `(*nanla:`
# and `(*nanlb:` — which PCRE2 does not have (err 195) and which are about this
# module whatever PCRE2 thinks of them, so a pattern spelling one is not part
# of an identity claim about lookaround-free code.
ALPHA = frozenset((
    "pla", "nla", "plb", "nlb", "napla", "naplb", "nanla", "nanlb",
    "positive_lookahead", "negative_lookahead",
    "positive_lookbehind", "negative_lookbehind",
    "non_atomic_positive_lookahead", "non_atomic_positive_lookbehind",
))


def bearing(p):
    """True if `p` contains a lookaround spelling, or if the scan is unsure."""
    esc = incls = False
    i, n = 0, len(p)
    while i < n:
        c = p[i]
        if esc:
            esc = False
            i += 1
            continue
        if c == "\\":
            esc = True
            i += 1
            continue
        if incls:
            # Inside a class every one of this module's opener bytes is an
            # ordinary member: `[(?=]` is three literals, not an assertion.
            # (A `]` as the class's FIRST member is literal in PCRE2, which
            # would close the class early here — the error direction is
            # toward BEARING, since the scan then keeps looking at bytes it
            # would otherwise have skipped. Safe.)
            if c == "]":
                incls = False
            i += 1
            continue
        if c == "[":
            incls = True
            i += 1
            continue
        if c == "(":
            t = p[i + 1:]
            if t.startswith("?"):
                u = t[1:]
                if u == "":
                    return True                 # truncated `(?` — UNSURE
                if u[0] in "=!*":               # (?=   (?!   (?*
                    return True
                if u[0] == "<":
                    # SR-9's split: `=` `!` `*` are the three lookbehinds and
                    # every other tail byte is the named-group path. A `<` at
                    # end of pattern is UNSURE.
                    if len(u) == 1 or u[1] in "=!*":
                        return True
            elif t.startswith("*"):
                name = ""
                for ch in t[1:]:
                    if ch.isalnum() or ch == "_":
                        name += ch
                    else:
                        break
                if name in ALPHA:
                    return True
                # UNSURE tier: a verb name nobody listed that still says what
                # it is. Costs a pattern from the identity population at worst.
                if "look" in name.lower():
                    return True
        i += 1
    return False


def main():
    src, bout, fout = sys.argv[1], sys.argv[2], sys.argv[3]
    b, f = [], []
    with open(src, encoding="utf-8", errors="surrogateescape") as fh:
        for line in fh:
            p = line.rstrip("\n")
            if not p:
                continue
            (b if bearing(p) else f).append(p)
    for path, rows in ((bout, b), (fout, f)):
        with open(path, "w", encoding="utf-8", errors="surrogateescape") as fh:
            fh.write("".join(r + "\n" for r in rows))
    sys.stderr.write("lookaround-classify: %d bearing / %d free\n"
                     % (len(b), len(f)))


if __name__ == "__main__":
    main()
