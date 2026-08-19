r"""mlscan.py — WHERE IS `(?m)` IN FORCE, decided from the pattern TEXT.

[M6.2] wave C. THREE committed checks need the same question answered and it
is not a substring test, so it lives here once rather than three times — the
M2.12 rule ("M2.7 forked a second copy, and the fork is exactly how the
prefilter and skip loops went missing from the `$` path for a whole
milestone") applied to a fork that has not happened yet:

  - tests/codegen/run_mlinectx_identity.sh splits its corpus on
    `multiline_anchor` — does the pattern carry a `^` or `$` that a set `m`
    reaches? That is exactly the condition for the machine to build an
    N_BOT_M/N_EOL_M, i.e. for `-DPCREC_NO_MLINECTX` to change anything.
  - tests/assertions/run_mline_diff.sh excludes `multiline_caret` patterns
    from its python arm (upstream_issues.md U11b).
  - the `.rxt` corpus generator marks the same patterns `# pcre2-only`.

WHY IT IS A TEXT SCAN AND NOT A CALL INTO pcrec. A split derived from
`Dfa.clsctx`, or from any other verdict pcrec computes about the pattern
under test, would be the check reading its own subject's answer — this
project's recorded check-design failure. So this walks the GRAMMAR
(src/parse/mod_modifiers.c's own measured rules) and nothing else.

THE TWO TRAPS, both of which cost a real run before this file existed:

  1. `^` INSIDE A BRACKET EXPRESSION IS NOT AN ANCHOR. `[^c]` is a negated
     class, and half of this module's corpus is `[^c]`-shaped. A scan that
     missed that excluded `(?m)[^c]{1,3}$` — the D47.5 GUARD CELL — from
     python cross-verification, on a `^` that is a class negation. This is
     the same trap tests/codegen/run_wordctx_identity.sh documents for `[\b]`.
  2. SETTING `m` IS NOT ENOUGH; an anchor must RECEIVE it. `(?m)\Aa`,
     `(?m)\Bfoo` and `a$(?m)` all set the option and produce no multiline
     node at all — the first two have no bare `^`/`$`, the third's `$` is
     textually before the setter. A coarser split reported ten such patterns
     as a dead reference knob.

SCOPING follows the parser: a BARE `(?m)` mutates the enclosing scope and
survives to that scope's `)`; a `(?m:` scopes to its own group body; `(?^...)`
resets to the hardwired defaults, where multiline is off. Verified against
libpcre2: `((?m))a$` and `(?:(?m))a$` do NOT match "a\\nb" while `(?m)a$`
does.
"""

OPTLETTERS = "imsxUJnarDPSTW^-"


def _opt_run(p, i):
    """If `p[i:]` starts an option run `(?<letters>`, return
    (terminator_index, sets_m, unsets_m, resets); else None.

    A `(?` followed by anything the grammar does not admit is not an option
    run at all — it is `(?:`, `(?=`, `(?<name>`, `(?#`, ... — and returning
    None is what makes those fall through to the ordinary-group arm."""
    if not p.startswith("(?", i):
        return None
    j = i + 2
    unset = resets = sets_m = unsets_m = False
    if j < len(p) and p[j] == '^':
        resets = True
        j += 1
    while j < len(p) and p[j] in OPTLETTERS:
        if p[j] == '-':
            unset = True
        elif p[j] == 'm':
            if unset:
                unsets_m = True
            else:
                sets_m = True
        j += 1
    if j >= len(p) or p[j] not in '):':
        return None
    return (j, sets_m, unsets_m, resets)


def _scan(p, want):
    """Walk `p`, tracking the scoped multiline state, and return True at the
    first character in `want` found at ATOM position while it is on."""
    ml = False
    stack = []
    i, n = 0, len(p)
    while i < n:
        c = p[i]
        if c == '\\' and i + 1 < n:
            i += 2
            continue
        if c == '[':
            # TRAP 1: skip the whole bracket expression. A leading `^` and a
            # leading `]` are literal members of it, per the base grammar.
            i += 1
            if i < n and p[i] == '^':
                i += 1
            if i < n and p[i] == ']':
                i += 1
            while i < n and p[i] != ']':
                i += 2 if p[i] == '\\' else 1
            i += 1
            continue
        if c == '(':
            run = _opt_run(p, i)
            if run is not None:
                end, sets_m, unsets_m, resets = run
                new_ml = False if resets else ml
                if sets_m:
                    new_ml = True
                if unsets_m:
                    new_ml = False
                if p[end] == ')':
                    ml = new_ml            # bare run: mutates THIS scope
                else:
                    stack.append(ml)       # `(?m:` — scopes to the body
                    ml = new_ml
                i = end + 1
                continue
            stack.append(ml)               # ordinary group
            i += 1
            continue
        if c == ')':
            if stack:
                ml = stack.pop()
            i += 1
            continue
        if c in want and ml:
            return True
        i += 1
    return False


def multiline_anchor(p):
    """Does a `^` or `$` at atom position fall in the scope of a set `m`?
    Equivalently: will this pattern build an N_BOT_M or an N_EOL_M?"""
    return _scan(p, '^$')


def multiline_caret(p):
    """Does a `^` at atom position fall in the scope of a set `m`?
    That is U11b's exclusion: PCRE2's multiline `^` does not match after a
    newline that ENDS the string and python3 `re`'s does."""
    return _scan(p, '^')


# --- self-check ------------------------------------------------------------
# A scanner nobody exercises is a scanner that drifts. Run this file directly
# to check it against the cases that cost a real run, plus the three
# libpcre2-verified scoping cells.
_CASES = [
    # (pattern, multiline_anchor, multiline_caret)
    (r'(?m)^a',            True,  True),
    (r'(?m)a$',            True,  False),
    (r'(?m:a$)',           True,  False),
    (r'(?m)a$(?-m)',       True,  False),
    (r'(?m)[^c]{1,3}$',    True,  False),   # trap 1: `^` is a class negation
    (r'(?m)[^c]+$',        True,  False),   # trap 1
    (r'(?m)[$^]',          False, False),   # trap 1, both characters
    (r'(?m)\A',            False, False),   # trap 2: no anchor to receive it
    (r'(?m)\Aa',           False, False),   # trap 2
    (r'(?m)\Bfoo',         False, False),   # trap 2
    (r'(?m)a\Z',           False, False),   # trap 2
    (r'(?m:\Aa)',          False, False),   # trap 2
    (r'a$(?m)',            False, False),   # trap 2: setter AFTER the anchor
    (r'(?-m)a$',           False, False),
    (r'a$',                False, False),
    (r'^a',                False, False),
    (r'(?im)^x',           True,  True),
    (r'(?^m)^x',           True,  True),
    (r'(?m)(?^)^x',        False, False),   # `(?^)` resets multiline off
    (r'(?i)(?m)a$',        True,  False),
    (r'((?m))a$',          False, False),   # bare run scoped to its group
    (r'(?:(?m))a$',        False, False),
    (r'((?m:a))$',         False, False),
    (r'(?:(?m:a$)|b$)',    True,  False),
    (r'(?m)^a|b$',         True,  True),
    (r'a(?m)^b|c',         True,  True),
    (r'\[(?m)^a',          True,  True),    # an ESCAPED `[` opens no class
]

if __name__ == "__main__":
    import sys
    bad = []
    for pat, want_anchor, want_caret in _CASES:
        got = (multiline_anchor(pat), multiline_caret(pat))
        if got != (want_anchor, want_caret):
            bad.append((pat, got, (want_anchor, want_caret)))
    for pat, got, want in bad:
        print("FAIL: %r -> %r, expected %r" % (pat, got, want))
    print("mlscan self-check: %d cases, %d failed" % (len(_CASES), len(bad)))
    sys.exit(1 if bad else 0)
