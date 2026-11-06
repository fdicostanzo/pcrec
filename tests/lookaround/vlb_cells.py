#!/usr/bin/env python3
"""tests/lookaround/vlb_cells.py — gate 1's cell set for bounded VARIABLE
lookbehind ([VLOOKBEHIND] stage 1, docs/design/vlookbehind.md §6 gate 1).

Written from the spec's rule (pattern_language.md §7.4: written order, then
the farthest candidate start first, the body backtracking until it ends at
the cursor; the non-atomic form retries nearer) and from the design's
measured cells (§2, §7), never from the emitter. Each pattern is compared
against libpcre2 10.46 by run_lookaround_diff.sh §5 over every subject of its
mode's set, every startpos (character boundaries only under UTF-8), the
match span AND every group span.

THE CROSS (§6 gate 1): every spelling x {capturing, non-capturing} x {group
alternation, bounded quantifier, nested quantifier, nested lookaround,
atomic/possessive inside, call to a bounded group}, plus a second branch
after a varying one (W11's shape), a follow that forces the non-atomic retry,
and the §7 witnesses verbatim. Modes:
  byte          every shape
  utf8          the shapes whose body reads no context before its candidate
                (no `\\b`/`\\B`, no nested lookbehind): their answers are
                exact under PCRE2_UTF
  utf8-clip     the context-reading shapes under `-e utf8` on ASCII subjects,
                compared against libpcre2's BYTE answer: D142 item 3's stated
                divergence (match_api.md §9.4¶8). The cells where libpcre2's
                UTF answer differs are the expected-divergent subset, counted
                by the caller
  utf8-invalid  ill-formed subjects (W13, W15 and a generated set) under
                PCRE2_MATCH_INVALID_UTF, pcrec's reading (utf8_design.md §2.6)

K35: the script prints its own population per mode on stderr, and the caller
pins each count EXACTLY (a population change is deliberate).

Usage: vlb_cells.py <out-patterns.tsv> <subjects-root>
  writes `<mode>\\t<pattern>` lines, and one subject directory per mode under
  <subjects-root> (byte, utf8, utf8-clip, utf8-invalid).
"""
import os
import sys

SPELL = [("(?<=", ")"), ("(?<!", ")"), ("(?<*", ")"), ("(*naplb:", ")")]

# Variable bodies: (name, body, reads-context-before-its-start).
BODIES = [
    ("alt",       "a|bc",              False),
    ("alt3",      "ab|a|b",            False),
    ("rep",       "a{1,2}",            False),
    ("rep0",      "a{0,2}",            False),
    ("rep13",     "a{1,3}",            False),
    ("opt",       "ab?",               False),
    ("nested",    "(?:ab?){1,2}",      False),
    ("lazy",      "a{1,2}?b|a{1,2}",   False),
    ("look",      "a{1,2}(?=x)",       False),
    ("lookneg",   "a{1,2}(?!a)",       False),
    ("atomic",    "(?>a|ab)b?",        False),
    ("poss",      "a{1,2}+b?",         False),
    ("cls",       "[ab]{1,2}",         False),
    ("wordb",     "\\ba{1,2}",         True),
    ("nwordb",    "\\Ba{1,2}",         True),
    ("caret",     "^a{0,2}",           False),
    ("inner_lb",  "(?<=b)a{1,2}",      True),
]

FOLLOWS = ["x", "a"]

# The §7 witnesses and §2's cells, verbatim (mode, pattern).
WITNESSES = [
    ("byte", "(?<=(a|aa))c"),                       # W1
    ("byte", "(?<=a{1,2})x"),                       # W2, W16
    ("byte", "(?<=(a|ab)(b|))x"),                   # W3
    ("byte", "(?<=a{1,2})a"),                       # W3b
    ("byte", "(?<!a{1,2})a"),
    ("byte", "(?<!ab?)x"),                          # W4
    ("byte", "(?<*(a{1,3}))c\\1"),                  # W5
    ("byte", "(?<*(a|aaa))c\\1"),                   # W5 (gap)
    ("byte", "(?<=a{1,2})b"),                       # W7
    ("byte", "(?<=(a)|(aa))c"),                     # W10
    ("byte", "(?<=a{1,2}|b)x"),                     # W11 (a)
    ("byte", "(?<=a{1,2}|bc)x"),
    ("byte", "(?<=a{2,3}|b)x"),
    ("byte", "(?<=a{1,9})x"),                       # W12 (a)
    ("byte", "(?<=a{1,2}|b{1,2})x"),                # W12 (b)
    ("byte", "(?<=\\Ga{1,2})b"),                    # W14
    ("byte", "(?<*(a{1,2})|(aa))\\2"),              # W16
    ("byte", "(?<=(ab)|(b{1,2}))c"),
    ("byte", "(?<=\\ba{1,2})x"),
    ("byte", "(?<=^a{0,2})x"),
    ("byte", "(?<=\\Aa{0,2})x"),
    ("byte", "(?<=a{1,2}(?=xy))x"),
    ("byte", "(?<=(?>a|ab)b)x"),
    ("byte", "(?<=(?:a|ab)b)x"),
    ("byte", "(?<!(?>a|ab)b)x"),
    ("byte", "(?<=a{1,2}+a)x"),
    ("byte", "(?<=a{1,2})x|(?<=b{0,1})y"),
    ("byte", "(?:(?<=a{1,9})b)+"),
    ("byte", "^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$"),
    ("byte", "^(?:(?<g>a|ab)){0}ab(?<=(?&g))$"),
    ("byte", "(?<=(?:a{1,2}){1,2})x"),
    ("byte", "(?<=a(?<=a{1,2})b{0,1})x"),
    ("utf8", "(?<=(\u00e9{1,2}))x"),
    ("utf8", "(?<=(\u00e9{0,2}))x"),                 # W6
    ("utf8", "(?<=\u00e9{2,3}|\u00e9)x"),            # W11 (b)
    ("utf8", "(?<=a{1,9})x"),                       # W12 (a) twin
    ("utf8", "(?<=\\G\u00e9{1,2})b"),               # W14
    ("utf8", "(?i)(?<=(k{1,2})|(b))x"),             # W14 Kelvin
    ("utf8", "(?<=\u00e9|bc)x"),
    ("utf8", "(?<=[\u00e9a]{1,3})x"),
    ("utf8", "(?<*(\u00e9|\u00e9\u00e9\u00e9))c\\1"),
    ("utf8-invalid", "\u00e9(?<=(a?))"),            # W13
    ("utf8-invalid", "\u00e9(?<=a{0,1})"),          # W13
    ("utf8-invalid", "(?<=(a{0,2}))b"),             # W15
    ("utf8-invalid", "(?<=(\u00e9{0,2}))b"),        # W15
    ("utf8-invalid", "(?<=(\u00e9{1,2}|a))x"),
    ("utf8-invalid", "(?<!\u00e9{0,2})b"),
    ("utf8-invalid", "(?<*(.{1,3}))b"),
]

SUBJECTS = {
    "byte": ["", "a", "x", "b", "ax", "bx", "aax", "aaax", "bcx", "abx",
             "bax", "acx", "abbx", "aaa", "aac", "abbc", "aaaca", "aaxy",
             "aaxz", " aax", "baax", "aab", "bbbbbbbbbax", "aaaa", "bc",
             "ab", "ba", "bab", "abab", "xbax", "aaab"],
    "utf8": ["", "x", "\u00e9x", "a\u00e9\u00e9x", "\u00e9\u00e9b",
             "b\u212ax", "\u00e9\u00e9\u00e9\u00e9\u00e9\u00e9\u00e9\u00e9\u00e9ax",
             "\u00e9\u00e9\u00e9ca", "\u00e9\u00e9\u00e9c\u00e9", "bcx",
             "a\u00e9x", "aax", "\u00e9b", "kx", "Kkx"],
    "utf8-clip": ["", "x", " aax", "baax", "aax", "abx", "bax", "aaax",
                  "ba", "bab", "xbaax"],
    "utf8-invalid": [b"\xc3\xa9\xa9", b"\xff\x61\x62", b"\xa9\xc3\xa9\x62",
                     b"\xc3\xa9\xa9x", b"\xa9ax", b"a\xffax", b"\xc3x",
                     b"\xe2\x82x", b"ab", b"\xc3\xa9b", b"\xc3\xa9\xc3\xa9x"],
}


def generated():
    """The cross, deduplicated, in a stable order."""
    out = []
    for (o, c) in SPELL:
        for name, body, ctx in BODIES:
            for capture in (False, True):
                b = "(" + body + ")" if capture else body
                for fol in FOLLOWS:
                    pat = o + b + c + fol
                    out.append(("byte", pat))
                    out.append(("utf8-clip" if ctx else "utf8", pat))
            # a second, one-length branch after the varying one (W11)
            out.append(("byte", o + body + "|d" + c + "x"))
        # a call to a bounded group, behind the varying branch's loop
        out.append(("byte", "(?(DEFINE)(?<g>a|bc))" + o + "(?&g)" + c + "x"))
        # non-atomic retry: the follow fails at the first candidate
        out.append(("byte", o + "(a{1,3})" + c + "c\\1"))
    return out


def main():
    patfile, root = sys.argv[1], sys.argv[2]
    seen, rows = set(), []
    for mode, pat in WITNESSES + generated():
        if (mode, pat) not in seen:
            seen.add((mode, pat))
            rows.append((mode, pat))
    with open(patfile, "w", encoding="utf-8") as f:
        for mode, pat in rows:
            f.write("%s\t%s\n" % (mode, pat))
    for mode, subs in SUBJECTS.items():
        d = os.path.join(root, mode)
        os.makedirs(d, exist_ok=True)
        for i, s in enumerate(subs):
            with open(os.path.join(d, "s%02d" % i), "wb") as f:
                f.write(s if isinstance(s, bytes) else s.encode("utf-8"))
    counts = {}
    for mode, _ in rows:
        counts[mode] = counts.get(mode, 0) + 1
    sys.stderr.write("vlb_cells: %s\n" % " ".join(
        "%s=%d" % (m, counts.get(m, 0)) for m in SUBJECTS))


if __name__ == "__main__":
    main()
