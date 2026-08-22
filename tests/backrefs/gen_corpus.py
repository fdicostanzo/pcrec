#!/usr/bin/env python3
"""tests/backrefs/gen_corpus.py — the GENERATOR that wrote every expectation
in tests/backrefs/*.rxt, and the reason none of them was typed by a human.

THE RULE IT ENFORCES (tests/CLAUDE.md's oracle discipline, and
backrefs_design.md §11.1's per-CELL marking): every cell is driven through
libpcre2 10.46 BEFORE it is written, and through python3 `re` in the SAME
pass. A block carries `# pcre2-only` exactly where python diverged or could
not compile the pattern — DETECTED, never assumed — with a comment recording
what the divergence was and over how many cells, so a reader can tell "python
disagrees" from "nobody checked".

WHY THAT MATTERS MORE HERE THAN ANYWHERE ELSE IN THE TREE. This module has the
largest oracle divergence pcrec has met: of 25 measured spellings, 20 are
accepted by libpcre2 and only 5 also work in python. python `re` refuses EVERY
self-reference and EVERY forward reference at COMPILE time ("cannot refer to an
open group"), has no `\\g`, no `\\k` and no `(?J)` at all, rejects `(?<n>...)`
in favour of `(?P<n>...)`, and refuses `(?i)` anywhere but the pattern start —
which is exactly where §3.1(c)'s two load-bearing cells live. R32 C3 found the
first draft of the test plan marking two of these files python-verifiable IN
THE DIRECTION THAT LOSES THE ORACLE, which is why the marking is computed
here instead of declared in the plan.

RE-RUN IT after changing a cell list:  python3 tests/backrefs/gen_corpus.py
It rewrites the .rxt files in place and prints a per-file census. It NEVER
reads pcrec: the expectations are PCRE2's, and pcrec is what they are then
used to test.
"""
import os
import re as pyre
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.normpath(os.path.join(HERE, "..", ".."))
sys.path.insert(0, os.path.join(ROOT, "docs", "design",
                                "backrefs_measurements", "probes"))
try:
    import br_oracle as O
except Exception as e:                                      # noqa: BLE001
    sys.stderr.write("gen_corpus: libpcre2 unavailable: %s\n" % e)
    sys.exit(3)
if O.SELFCHECK:
    sys.stderr.write("gen_corpus: oracle self-check failed: %r\n" % (O.SELFCHECK,))
    sys.exit(3)

CASELESS = O.PCRE2_CASELESS


def esc(s):
    """A subject as the .rxt format spells it: double-quoted, with exactly the
    escapes docs/testing.md lists and no others."""
    out = ['"']
    for ch in s:
        b = ord(ch)
        if ch == '"':
            out.append('\\"')
        elif ch == '\\':
            out.append('\\\\')
        elif ch == '\n':
            out.append('\\n')
        elif ch == '\t':
            out.append('\\t')
        elif ch == '\r':
            out.append('\\r')
        elif 0x20 <= b < 0x7f:
            out.append(ch)
        else:
            out.append('\\x%02x' % b)
    out.append('"')
    return ''.join(out)


def pad(groups, n):
    """PAD TO `n` WITH UNSET, and the padding is ORACLE-SIDE only.
    `pcre2_match` returns the highest CAPTURED pair plus one, so an ovector
    read at that count TRUNCATES trailing unset groups: `^(?:(a)x|(b)y)\\1$`
    on "axa" reports ONE group where the pattern has two. python's
    `Match.groups()` reports both, with the second as (-1,-1). Without this
    the two oracles disagree about a SHAPE rather than about an answer, and
    every such block would be marked `# pcre2-only` for no reason -- which is
    the direction that quietly loses the second oracle. The same defect
    appeared in this lane's own publish-discipline probe and was fixed on the
    same side."""
    g = list(groups[:n])
    while len(g) < n:
        g.append((-1, -1))
    return tuple(g)


def pcre2_answer(pat, subj, sp, caseless):
    try:
        c = O.compile(pat, CASELESS if caseless else 0)
    except Exception as e:                                  # noqa: BLE001
        return ('ERR', str(e))
    try:
        r = c.search(subj, sp)
    except Exception as e:                                  # noqa: BLE001
        return ('ERR', str(e))
    if r is None:
        return ('n',)
    # The two bindings spell an UNSET group differently -- libpcre2's returns
    # None, python's `span()` returns (-1, -1) -- and the .rxt `g` line spells
    # it `-1 -1`. Normalise HERE so a comparison between them is a comparison
    # and not a type check.
    groups = tuple((-1, -1) if g is None else g for g in r[1])
    return ('m', r[0][0], r[0][1], groups)


def python_answer(pat, subj, sp, caseless):
    flags = pyre.ASCII | (pyre.IGNORECASE if caseless else 0)
    try:
        c = pyre.compile(pat, flags)
    except Exception as e:                                  # noqa: BLE001
        return ('ERR', str(e))
    try:
        m = c.search(subj, sp)
    except Exception as e:                                  # noqa: BLE001
        return ('ERR', str(e))
    if m is None:
        return ('n',)
    groups = tuple((m.span(i + 1)) for i in range(c.groups))
    groups = tuple((-1, -1) if g == (-1, -1) else g for g in groups)
    return ('m', m.start(), m.end(), groups)


class Block:
    """One `pattern` block: the pattern, its module list, its caseless flag,
    the (subject, startpos) cells, and how many capture groups to assert."""

    def __init__(self, pat, cells, features=None, caseless=False,
                 groups=0, note=None, sweep=False, pcrec_refuses=None):
        self.pat = pat
        self.cells = cells          # list of (subject, startpos) or (subject,)
        self.features = features
        self.caseless = caseless
        self.groups = groups        # assert caps 1..groups on every match
        self.note = note
        self.sweep = sweep          # expand each subject over every startpos
        # A construct libpcre2 ACCEPTS and pcrec deliberately does not
        # implement: the block becomes a `perr`, and the comment records
        # PCRE2's real answer so the file states the gap rather than hiding
        # it behind a bare refusal. The value is the module pcrec names.
        self.pcrec_refuses = pcrec_refuses

    def expand(self):
        out = []
        for c in self.cells:
            subj = c[0]
            if self.sweep:
                for sp in range(len(subj) + 1):
                    out.append((subj, sp))
            elif len(c) > 1:
                out.append((subj, c[1]))
            else:
                out.append((subj, 0))
        return out


def render(block, census):
    lines = []
    cells = block.expand()
    p2 = [pcre2_answer(block.pat, s, sp, block.caseless) for s, sp in cells]
    py = [python_answer(block.pat, s, sp, block.caseless) for s, sp in cells]

    # A construct PCRE2 accepts and pcrec refuses: `perr`, with PCRE2's own
    # answer written down beside it.
    if block.pcrec_refuses:
        census['perr'] += 1
        if block.note:
            lines.append('# ' + block.note)
        if p2[0][0] == 'ERR':
            raise SystemExit('gen_corpus: %r is marked pcrec_refuses but '
                             'libpcre2 refuses it too' % block.pat)
        lines.append('# libpcre2 ACCEPTS this and answers %r on %s; pcrec '
                     'refuses it naming module %r, which is the truthful '
                     'answer while that module has no producer -- claiming '
                     'the spelling would be the miscompile D26 tier 1 forbids'
                     % (p2[0][:3], esc(cells[0][0]), block.pcrec_refuses))
        if py[0][0] != 'ERR':
            lines.append('# pcre2-only')
            census['pcre2_only'] += 1
        lines.append('pattern ' + block.pat)
        if block.features:
            lines.append('features ' + block.features)
        if block.caseless:
            lines.append('flags i')
        lines.append('perr')
        return lines

    # A block whose PATTERN does not compile in PCRE2 is a `perr` block: the
    # pattern text is the whole test.
    if p2 and p2[0][0] == 'ERR':
        census['perr'] += 1
        if block.note:
            lines.append('# ' + block.note)
        lines.append('# pcre2 refuses: %s' % p2[0][1].split('(')[0].strip())
        if py[0][0] != 'ERR':
            lines.append('# pcre2-only')
        if block.note:
            pass
        lines.append('pattern ' + block.pat)
        if block.features:
            lines.append('features ' + block.features)
        if block.caseless:
            lines.append('flags i')
        lines.append('perr')
        return lines

    # DIVERGENCE, MEASURED. Compare only the SPAN (the .rxt m/n lines) plus,
    # where the block asserts them, the group slots.
    diverge = []
    for i, (s, sp) in enumerate(cells):
        a, b = p2[i], py[i]
        if b[0] == 'ERR':
            diverge.append((i, a, b))
            continue
        if a[0] != b[0]:
            diverge.append((i, a, b))
            continue
        if a[0] == 'm':
            if a[1] != b[1] or a[2] != b[2]:
                diverge.append((i, a, b))
            elif block.groups:
                if pad(a[3], block.groups) != pad(b[3], block.groups):
                    diverge.append((i, a, b))

    if block.note:
        lines.append('# ' + block.note)
    if diverge:
        i, a, b = diverge[0]
        s, sp = cells[i]
        # Report the SPANS, and the GROUPS as well when the spans agree --
        # otherwise the comment reads `pcre2=('m',0,3) python=('m',0,3)` and
        # says nothing about what actually differed, which is the shape of a
        # divergence note nobody can act on.
        if b[0] == 'ERR':
            shown_a, shown_b = repr(a[:3]), repr(('ERR', b[1]))
        elif a[:3] != b[:3]:
            shown_a, shown_b = repr(a[:3]), repr(b[:3])
        else:
            shown_a = repr(a[:3]) + ' groups=' + repr(pad(a[3], block.groups))
            shown_b = repr(b[:3]) + ' groups=' + repr(pad(b[3], block.groups))
        lines.append('# python DIVERGES here, measured rather than assumed: '
                     '%s @%d pcre2=%s python=%s (%d of %d cells)'
                     % (esc(s), sp, shown_a, shown_b,
                        len(diverge), len(cells)))
        lines.append('# pcre2-only')
        census['pcre2_only'] += 1
    else:
        census['python_verified'] += 1
    lines.append('pattern ' + block.pat)
    if block.features:
        lines.append('features ' + block.features)
    if block.caseless:
        lines.append('flags i')
    for i, (s, sp) in enumerate(cells):
        a = p2[i]
        if a[0] == 'ERR':
            raise SystemExit('gen_corpus: %r compiles for one cell and not '
                             'another?!' % block.pat)
        if a[0] == 'n':
            lines.append(('ns %d %s' % (sp, esc(s))) if sp else
                         ('n %s' % esc(s)))
        else:
            lines.append(('ms %d %s %d %d' % (sp, esc(s), a[1], a[2])) if sp
                         else ('m %s %d %d' % (esc(s), a[1], a[2])))
            for g, (lo, hi) in enumerate(pad(a[3], block.groups), 1):
                lines.append('g %d %d %d' % (g, lo, hi))
        census['cells'] += 1
    return lines


def write(fname, header, sections):
    census = {'cells': 0, 'pcre2_only': 0, 'python_verified': 0, 'perr': 0}
    out = [header.rstrip('\n'), '']
    for title, blocks in sections:
        out.append('# ' + '=' * 68)
        out.append('# ' + title)
        out.append('# ' + '=' * 68)
        out.append('')
        for b in blocks:
            out.extend(render(b, census))
            out.append('')
    path = os.path.join(HERE, fname)
    with open(path, 'w') as f:
        f.write('\n'.join(out).rstrip('\n') + '\n')
    print('%-18s %4d cells  %2d blocks python-verified  %2d pcre2-only  %2d perr'
          % (fname, census['cells'], census['python_verified'],
             census['pcre2_only'], census['perr']))
    return census


B = Block
BR = "backrefs"
BRN = "backrefs,named-groups"
BRM = "backrefs,modifiers"
BRNM = "backrefs,modifiers,named-groups"


# ======================================================================
# numeric.rxt
# ======================================================================
NUMERIC = [
    ("UNSET (§3.3): PCRE2 FAILS an unset reference; it does not match empty", [
        B(r"^(a)?\1$", [("",), ("aa",), ("a",)], BR, groups=1,
          note="U1-U3. `^(a)?\\1$` on \"\" is NO MATCH -- the group did not "
               "participate, so the reference has nothing to compare and "
               "PCRE2 fails. An implementation that matched empty here would "
               "be implementing PCRE2_MATCH_UNSET_BACKREF, which flips 2 of "
               "the 8 measured U cells and is explicitly out of scope (§3.3)."),
        B(r"^(?:(a)|b)\1$", [("b",), ("aa",), ("bb",)], BR, groups=1),
        B(r"^(?:(a)x|(b)y)\1$", [("byb",), ("axa",)], BR, groups=2),
        B(r"^(?:(a)x|(b)y)\2$", [("byb",), ("axa",)], BR, groups=2,
          note="The separating pair: \\2 on \"byb\" MATCHES with group 1 unset "
               "and group 2 = (0,1), while \\1 on the same subject does not. "
               "A single unset test over the wrong slot passes one and fails "
               "the other."),
    ]),
    ("EMPTY (§3.4): a group that captured the empty string is SET", [
        B(r"^(x?)y\1z$", [("yz",), ("xyxz",), ("xyz",)], BR, groups=1,
          note="E1. The failure mode this catches is the OPPOSITE of §3.3's: "
               "an implementation testing `ref_end > ref_start` as a proxy "
               "for \"is it set\" turns every empty capture into a failure "
               "and gets \"yz\" wrong. Sabotage row S105."),
        B(r"^(a*)\1$", [("",), ("aa",), ("aaa",), ("a",)], BR, groups=1),
        B(r"^(a?)\1{3}$", [("",), ("aaaa",), ("aa",)], BR, groups=1),
    ]),
    ("QUANTIFIED (§3.6): a backreference is an ordinary repeatable atom", [
        B(r"^(a)\1*$", [("a",), ("aaaa",), ("ab",)], BR, groups=1),
        B(r"^(\w)\1+$", [("bbbb",), ("b",)], BR + ",classes", groups=1),
        B(r"(\w)\1+", [("abbbc",), ("abcd",)], BR + ",classes", groups=1,
          note="Q3 is the one that needs the SEARCH to move: the match is at "
               "(1,4) with group 1 = (1,2), so an implementation that only "
               "ever tried offset 0 answers nomatch."),
        B(r"^(a*)\1*$", [("aaa",), ("aaaa",)], BR, groups=1,
          note="The shape that looks paradoxical: the outer `\\1*` iterates "
               "over a body whose LENGTH changes as group 1 is re-decided by "
               "backtracking. It works because the reference reads the slots "
               "as they are at that instant and the loop's own frames restore "
               "them."),
    ]),
    ("STARTPOS (§11.2 F12): which start the search is given is an axis", [
        B(r"(a)\1", [("xaa",)], BR, groups=1, sweep=True,
          note="P1/P2. (1,3) at startpos 0 and 1, and NO MATCH at 2 -- a "
               "suite that fixed startpos could not tell a correct "
               "implementation from one that ignores the argument."),
        B(r"(\w)\1", [("abcdd",)], BR + ",classes", groups=1, sweep=True),
    ]),
    ("MULTI-DIGIT references above \\9 (§5 rider: they exist)", [
        B(r"^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)\10$",
          [("abcdefghijj",), ("abcdefghij\x08",)], BR, groups=10,
          note="Rule 3 with TEN groups BEFORE the escape: `\\10` is a "
               "backreference to group 10. The second subject is the OCTAL "
               "reading (0x08) and must NOT match, which is what makes this "
               "cell a discriminator rather than a smoke test."),
    ]),
]

# ======================================================================
# octal.rxt -- §5's four ordered questions, at the ATOM position
# ======================================================================
OCTAL = [
    ("RULE 1: `\\0` is ALWAYS octal, at most three digits total", [
        B(r"^\0$", [("\x00",), ("0",)], BR),
        B(r"^\012$", [("\n",), ("\x01" "2",)], BR),
        B(r"^\0377$", [("\x1f7",), ("\xff",)], BR,
          note="Three digits COUNTING THE LEADING 0: `\\037` then a literal "
               "'7'. A reader who counts three digits AFTER the zero gets "
               "0xff and this cell says so."),
        B(r"^(a)\0$", [("a\x00",), ("aa",)], BR, groups=1,
          note="Still octal with a group in scope: there is no group 0 to "
               "address, so no ambiguity exists for this row to resolve."),
    ]),
    ("RULE 2: one digit 1-9 is ALWAYS a backreference, WHOLE-pattern count", [
        B(r"^\1(a)$", [("aa",), ("\x01a",)], BR, groups=1,
          note="THE ASYMMETRY WITH RULE 3, and no test using only "
               "groups-before will see it: `\\1` sees the whole pattern, so "
               "the group AFTER the escape counts. (The match is nomatch on "
               "\"aa\" because a FORWARD reference is unset when read -- §3.5 "
               "-- but the pattern COMPILES, which is the fact this row "
               "pins.)"),
        B(r"^(a)\1$", [("aa",), ("a\x01",)], BR, groups=1),
        B(r"^\8$", [("\x08",), ("8",)], BR,
          note="`\\8` with no group is PCRE2 error 115 -- NOT octal, NOT the "
               "literal '8'. The `perr` shape is the assertion."),
        B(r"^\9$", [("\x09",)], BR),
        B(r"^(a)(b)(c)(d)(e)(f)(g)(h)\8$", [("abcdefghh",), ("abcdefgh\x08",)],
          BR, groups=8,
          note="`\\8` WITH eight groups is a backreference to group 8."),
    ]),
    ("RULE 3: two or more digits, run beginning 1-7 -- SO FAR or OCTAL", [
        B(r"^(a)\10$", [("a\x08",), ("aa0",)], BR, groups=1,
          note="ONE group before, so `\\10` has no reference reading and is "
               "OCTAL 010 = 0x08. Sabotage S112 makes rule 3 count the WHOLE "
               "pattern instead, and every groups-before cell still passes -- "
               "only this shape and `\\10(a)..(j)` below fail."),
        B(r"^\10(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)$",
          [("\x08abcdefghij",), ("jabcdefghij",)], BR, groups=10,
          note="TEN groups AFTER: still OCTAL, because rule 3's count is the "
               "one SO FAR. Deferring this decision would let a later group "
               "retroactively turn an octal literal into a reference."),
        B(r"^(a)\18$", [("a\x01" "8",), ("aa8",)], BR, groups=1,
          note="`\\18` is octal `\\01` then a LITERAL '8' -- 8 terminates an "
               "octal run that has already started, which is a different "
               "thing from BEGINNING one (rule 3')."),
        B(r"^\12(a)(b)(c)(d)(e)(f)(g)(h)(i)(j)(k)(l)$",
          [("\nabcdefghijkl",)], BR),
        B(r"^\1234$", [("\x534",)], BR,
          note="The octal re-read takes at most three digits and the rest "
               "stand for themselves: `\\123` then '4'."),
    ]),
    ("RULE 3': a run BEGINNING 8 or 9 is ALWAYS a DECIMAL backreference", [
        B(r"^\81$", [("\x08" "1",)], BR,
          note="R32 E3. 8 and 9 are not octal digits, so the octal re-read "
               "would consume ZERO digits and produce nothing; PCRE2 reads "
               "the whole decimal number instead. With no group 81 this is "
               "error 115, and the failure a naive rule 3 produces is a "
               "SILENT MIS-PARSE rather than an error. Sabotage S113."),
        B(r"^\89$", [("\x08" "9",)], BR),
        B(r"^\91$", [("\x09" "1",)], BR),
    ]),
    ("RULE 4: the octal value ceiling", [
        B(r"^\400$", [("\x00",)], BR,
          note="PCRE2 error 151: the octal value exceeds \\377 in 8-bit "
               "non-UTF mode. `\\4` starts a run with an octal reading, no "
               "group 400 exists, and 0400 is out of range."),
        B(r"^\377$", [("\xff",), ("\xfe",)], BR),
    ]),
    ("RULE 5: the EXPLICIT forms never take the octal branch", [
        B(r"^\g10$", [("\x08",)], BR,
          note="`\\g10` with no groups is error 115, not the octal byte 0x08. "
               "The `\\g` spelling has no octal reading at all."),
        B(r"^\g{10}$", [("\x08",)], BR),
    ]),
]

# ======================================================================
# octal_class.rxt -- §5.2's MUST-NOT-CHANGE cells, with the module ON
# ======================================================================
OCTAL_CLASS = [
    ("THE CLASS POSITION IS BASE SYNTAX and this module must not touch it", [
        B(r"^[\1]$", [("\x01",), ("1",)], BR,
          note="With module `backrefs` ENABLED, every cell in this file must "
               "answer exactly what the BASE tier answered before it existed: "
               "inside a class a backreference is impossible, so `\\0`..`\\7` "
               "are octal and `\\8` `\\9` `\\g` `\\k` are the literal "
               "characters (FIX-3/K13, 41 measured cells). Sabotage S110 "
               "makes the module's atom port claim the class position too, "
               "and these twelve cells are the only thing that sees it."),
        B(r"^[\10]$", [("\x08",), ("\x01",), ("0",)], BR),
        B(r"^[\8]$", [("8",), ("\x08",)], BR),
        B(r"^[\9]$", [("9",), ("\x09",)], BR),
        B(r"^[\k]$", [("k",)], BR),
        B(r"^[\g]$", [("g",)], BR),
        B(r"^[\g<]$", [("g",), ("<",), ("x",)], BR,
          note="THE CELL THE TWO NEW `recursion` ROWS COULD HAVE BROKEN. The "
               "class doorway arbitrates on the SAME tail the atom doorway "
               "does, so adding `RK_ESC` rows with tails `<` and `'` would "
               "have taken `[\\g<]` away from the base `\\g` row -- and with "
               "it the literal-fallback answer, which is BASE syntax. The new "
               "rows therefore carry the identical base scalar class port, "
               "and these three cells are what says so."),
        B(r"^[\g']$", [("g",), ("'",), ("<",)], BR),
        B(r"^[\g<1>]$", [("g",), ("<",), ("1",), (">",), ("x",)], BR),
        B(r"^[\377]$", [("\xff",)], BR),
        B(r"^[\400]$", [("\x00",)], BR),
        B(r"^[\0]$", [("\x00",)], BR),
        B(r"^[\1-\7]$", [("\x01",), ("\x07",), ("\x08",)], BR),
        B(r"^(a)[\1]$", [("a\x01",), ("aa",)], BR, groups=1,
          note="A group IN SCOPE does not make the class position a "
               "reference: `[\\1]` is still the byte 0x01."),
    ]),
]

# ======================================================================
# selfref.rxt -- §3.5's S/F cells AND §3.2's RE-ENTRY class (E1's landing
# condition). python refuses every one of these at COMPILE time.
# ======================================================================
SELFREF = [
    ("SELF-REFERENCE (§3.5): legal, and governed entirely by the unset rule", [
        B(r"(a\1)", [("a",), ("",)], BR, groups=1,
          note="S1. The parser must NOT reject this, which is a real "
               "instruction because the natural implementation does. It "
               "COMPILES and then fails at match time on §3.3's unset rule: "
               "group 1 has not been traversed when the reference is read."),
        B(r"^(\1a)$", [("a",)], BR, groups=1),
        B(r"^(?:\1(a))+$", [("aa",)], BR, groups=1),
    ]),
    ("THE RE-ENTRY CLASS -- E1's landing condition (§3.2)", [
        B(r"(a|b\1)+", [("ab",), ("a",), ("ba",)], BR, groups=1,
          note="S3, AND THE COUNTEREXAMPLE THAT REFUTED THE FIRST DESIGN. "
               "libpcre2 answers (0,1) with group 1 = (0,1). Under "
               "WRITE-ON-TRAVERSE -- start written at the opening position, "
               "end at the closing one -- iteration 2 leaves start=1 and "
               "end=1 with NO capture published, both non-UNSET, and the "
               "model answers (0,2) with group 1 = (1,2). Publish-at-close is "
               "what makes the unset test total. Sabotage S103."),
        B(r"^(?:(a|b\1)y)+", [("aybay",), ("ay",), ("aybby",)], BR, groups=1,
          note="THE MEMORY-SAFETY CELL. On \"aybay\" iteration 2 opens the "
               "group at 2 while iteration 1's end is 1, so write-on-traverse "
               "gives ref_start = 2 > ref_end = 1 and the emitted "
               "`(size_t)(ref_end - ref_start)` UNDERFLOWS to SIZE_MAX -- an "
               "out-of-bounds read in EMITTED code, K27's class, in a matcher "
               "someone else compiles. A published pair has start <= end by "
               "construction, so the underflow is structurally absent rather "
               "than merely mitigated."),
        B(r"^(?:(a|b\1))+$", [("ab",), ("a",), ("abb",)], BR, groups=1),
        B(r"^(?:(a|b\1)c)+$", [("acbac",), ("ac",)], BR, groups=1),
    ]),
    ("FORWARD REFERENCE (§3.5): legal, and the FIRST ITERATION answers it", [
        B(r"\2(a)(b)", [("ab",)], BR, groups=2),
        B(r"(\2(a)|b)+", [("ba",), ("baa",)], BR, groups=2,
          note="F3/F4, and the charter's own question. On iteration 1 group 2 "
               "is unset, the `\\2(a)` branch fails AT THE REFERENCE, the `b` "
               "branch matches, and the loop then cannot continue -- "
               "iteration 2's `\\2` is STILL unset, because the branch that "
               "would set it never ran. So the whole match is (0,1) on "
               "\"baa\" as well as on \"ba\"."),
        B(r"^(?:\1(a))+$", [("aa",), ("a",)], BR, groups=1),
    ]),
    ("A REFERENCE UNDER A CUT (§3.7): the cross-module cell", [
        B(r"^(?:(a|b)x)++\1$", [("axbxb",), ("axbxa",)], BR + ",atomic-groups",
          groups=1,
          note="After a cut, `slot_values` holds the CUT PATH's writes, which "
               "is exactly right: the cut path is the only surviving one. A "
               "possessive quantifier followed by a reference into it compares "
               "against the COMMITTED iteration. Module `atomic-groups` "
               "shipped one row earlier, so this population is live from the "
               "day this module lands."),
        B(r"^(a|b)++\1$", [("abb",), ("aba",)], BR + ",atomic-groups", groups=1),
    ]),
]

# ======================================================================
# nested.rxt -- §3.7's N cells: the trail restores the OLD slot values
# ======================================================================
NESTED = [
    ("NESTED REPEATS re-decide the referenced capture PER ITERATION", [
        B(r"^(?:(a|b)\1)+$", [("aabb",), ("aab",), ("aa",), ("bb",)],
          BR, groups=1,
          note="N1 IS THE LOAD-BEARING CELL: on \"aabb\" the answer is (0,4) "
               "with group 1 = (2,3), NOT (0,1). The reference must compare "
               "against THIS iteration's capture, and on backtracking the "
               "PREVIOUS iteration's value must come back. That is the trail's "
               "EXACT RESTORE -- `RX_SET` records the value it displaced and "
               "the fail label rewinds to the popped frame's mark before "
               "transferring control -- not a clear."),
        B(r"^((a)|(b))+\2$", [("aba",), ("ab",)], BR, groups=3),
        B(r"^(?:(a)(b)\2\1)+$", [("abba",), ("abbaabba",), ("abab",)],
          BR, groups=2),
    ]),
    ("THE REVDET SHAPE (§3.6/R32 E9): a group in the body, a reference OUT", [
        B(r"(?:(a|bb)x)+\1", [("axbbxbb",), ("axbbxa",), ("axa",)],
          BR, groups=1,
          note="N5/N6. `(?:(a|bb)x)+y` takes the reverse-deterministic rung, "
               "which SUPPRESSES the per-iteration capture writes and "
               "reconstructs the last iteration's values with a backward "
               "walk. A reference OUTSIDE that loop therefore reads slots "
               "written by the backward walk rather than by the loop. The "
               "interaction was traced correct and UNNAMED in the first "
               "design; publish-at-close is what makes it designable, because "
               "the pending write and the pair it feeds are one publication "
               "and the suppression covers both or neither. Sabotage S118 "
               "drops the pending write alone."),
        B(r"(?:(a|bb)x)+\1y", [("axbbxbby",), ("axbbxay",)], BR, groups=1),
    ]),
    ("NESTED BACKREFERENCES: a reference inside a REFERENCED group", [
        B(r"^(a)((b)\1)\2$", [("ababab",), ("abab",)], BR, groups=3,
          note="The R32 panel measured this family safe over 2,402 cells with "
               "0 false negatives in either reading, and publish-at-close "
               "correct on nested re-entry over 2,692 cells. The structural "
               "reason: an inner group is re-set only by re-entering the "
               "OUTER one, and the trail keeps the two in step, so at the "
               "reference site the inner value is the one that produced the "
               "outer capture."),
        B(r"^(?:(a(b))\2)+$", [("abb",), ("abbabb",), ("ab",)], BR, groups=2),
    ]),
]

# ======================================================================
# spellings.rxt -- §2: every spelling, and the \g doorway's TWO constructs
# ======================================================================
SPELLINGS = [
    ("`\\g` BY NUMBER and BY RELATIVE POSITION", [
        B(r"^(a)\g1$", [("aa",), ("ab",)], BR, groups=1),
        B(r"^(a)(b)\g2$", [("abb",), ("aba",)], BR, groups=2),
        B(r"^(a)\g{1}$", [("aa",), ("ab",)], BR, groups=1),
        B(r"^(a)\g{-1}$", [("aa",), ("ab",)], BR, groups=1,
          note="RELATIVE resolution happens at COMPILE time against the count "
               "SO FAR: `\\g{-1}` is the most recently OPENED group."),
        B(r"^(a)(b)\g{-1}$", [("abb",), ("aba",)], BR, groups=2),
        B(r"^(a)(b)\g{-2}$", [("aba",), ("abb",)], BR, groups=2),
        B(r"^\g{+1}(a)$", [("aa",), ("a",)], BR, groups=1,
          note="`\\g{+1}` is a relative FORWARD reference and resolves at "
               "compile time in that direction too -- it COMPILES, and then "
               "fails at match time on the unset rule, which is the same "
               "answer §3.5's forward references get."),
        B(r"^(a)\g-1$", [("aa",), ("ab",)], BR, groups=1),
        B(r"^(a)\g+1(b)$", [("abb",), ("aab",)], BR, groups=2,
          note="Measured: the BARE `\\g+1` really is relative-forward, not a "
               "literal '+'. `(a)\\g+1` alone is error 115 -- there is no "
               "group 2 -- so this cell adds the group that makes it legal."),
        B(r"^(a)\g{ 1 }$", [("aa",), ("ab",)], BR, groups=1,
          note="MEASURED over all 256 bytes in both positions: HT and SP -- "
               "and only those two -- are skipped at each end of a `\\g{...}` "
               "or `\\k{...}` body. The angle-bracket, quote and `(?P=` forms "
               "skip NOTHING (`\\k< n >` is a PCRE2 error), which is why this "
               "cell exists in the brace form only."),
        B(r"^(a)\g{01}$", [("aa",)], BR, groups=1),
    ]),
    ("`\\g` REFUSALS", [
        B(r"^(a)\g{0}$", [("aa",)], BR, note="there is no capture group 0"),
        B(r"^(a)\g0$", [("aa",)], BR),
        B(r"^(a)\g{-0}$", [("aa",)], BR),
        B(r"^(a)\g{-2}x$", [("ab",)], BR),
        B(r"^(a)\g$", [("aa",)], BR),
        B(r"^(a)\g{1x}$", [("aa",)], BR),
        B(r"^(a)\g{}$", [("aa",)], BR),
    ]),
    ("`\\k` BY NAME -- three delimiters, one meaning", [
        B(r"^(?<n>a)\k<n>$", [("aa",), ("ab",)], BRN, groups=1),
        B(r"^(?<n>a)\k'n'$", [("aa",), ("ab",)], BRN, groups=1),
        B(r"^(?<n>a)\k{n}$", [("aa",), ("ab",)], BRN, groups=1),
        B(r"^(?<n>a)\k{ n }$", [("aa",)], BRN, groups=1),
        B(r"^(?<a_1>x)\k<a_1>$", [("xx",)], BRN, groups=1),
    ]),
    ("`\\k` REFUSALS: a name may not start with a digit, and a delimiter is required", [
        B(r"^(a)\k<1>$", [("aa",)], BRN),
        B(r"^(a)\k{1}$", [("aa",)], BRN),
        B(r"^(?<n>a)\kn$", [("aa",)], BRN),
        B(r"^(?<n>a)\k<n$", [("aa",)], BRN),
        B(r"^(?<n>a)\k<>$", [("aa",)], BRN),
        B(r"^(a)\k<q>$", [("aa",)], BRN,
          note="A well-formed name this pattern never declares: the "
               "error-115 class, raised by §5.3's END-OF-PARSE pass rather "
               "than at the escape."),
    ]),
    ("`(?P=name)` -- the python spelling, and the one by-name form python has", [
        B(r"^(?P<n>a)(?P=n)$", [("aa",), ("ab",)], BRN, groups=1),
        B(r"^(?<n>a)(?P=n)$", [("aa",), ("ab",)], BRN, groups=1,
          note="LEGAL in PCRE2 and a python COMPILE ERROR: python has only "
               "the `(?P<n>...)` declaring spelling. Measured, not assumed."),
        B(r"^(a)(?P=1)$", [("aa",)], BRN),
        B(r"^(?<n>a)(?P=q)$", [("aa",)], BRN),
        B(r"^(?<n>a)(?P=)$", [("aa",)], BRN),
    ]),
    ("`\\g<` and `\\g'` are SUBROUTINE CALLS -- module `recursion`, not this one", [
        B(r"^(a|b)\g<1>$", [("ab",), ("aa",)], BRN, pcrec_refuses="recursion",
          note="THE MEASURED DISCRIMINATOR (§2). A subroutine call re-runs the "
               "group's PATTERN, so this matches \"ab\"; a BACKREFERENCE "
               "compares the captured TEXT, so `^(a|b)\\1$` and "
               "`^(a|b)\\g{1}$` report NO MATCH on the same subject. The "
               "split runs exactly along the DELIMITER, which is why the two "
               "tailed rows name module `recursion` and this module's port "
               "never sees them. With `recursion` unavailable the honest "
               "answer is a refusal that NAMES it -- claiming the spelling "
               "would be a miscompile of the kind D26 tier 1 forbids."),
        B(r"^(a|b)\g'1'$", [("ab",)], BRN, pcrec_refuses="recursion"),
    ]),
]

# ======================================================================
# caseless.rxt -- §4: WHERE the (?i) is read, and WHAT folds
# ======================================================================
CASELESS_CELLS = [
    ("THE CASELESSNESS IS THE OPTION IN FORCE AT THE REFERENCE (§3.1(c))", [
        B(r"^(a)(?i:\1)$", [("aA",), ("aa",), ("Aa",)], BRM, groups=1,
          note="F7's positive half: the reference is inside `(?i:...)`, so the "
               "COMPARE folds and \"aA\" matches. `Ast.caseless` is set from "
               "the scoped state AT THE BACKREFERENCE, exactly as "
               "`Ast.multiline` is set at the `$`. Sabotage S106 ignores the "
               "field and this cell is what sees it."),
        B(r"^(?i:(a))\1$", [("aA",), ("aa",), ("Aa",), ("AA",)], BRM, groups=1,
          note="F7's negative half, and the one a plausible implementation "
               "gets wrong: the `(?i)` is at the GROUP, not at the reference, "
               "so the compare is CASE-SENSITIVE and \"aA\" does NOT match. "
               "An implementation reading the option in force at the group -- "
               "or at end of pattern -- passes the cell above and fails this "
               "one."),
        B(r"^((?i)a)\1$", [("aA",), ("aa",), ("AA",)], BRM, groups=1,
          note="python REFUSES this pattern outright (\"global flags not at "
               "the start of the expression\"), so one of §3.1(c)'s two "
               "load-bearing cells has no python oracle at all. R32 C3 found "
               "the first test plan calling this file python-verifiable."),
        B(r"^(?i)(a)(?-i)\1$", [("aA",), ("aa",)], BRM, groups=1),
    ]),
    ("WHAT FOLDS: exactly the 52 ASCII letters, and nothing else", [
        B(r"^(\xdf)\1$", [("\xdf\xdf",)], BRM, caseless=True,
          note="AXIS A, measured over all 256 bytes against libpcre2's 8-bit "
               "NON-UTF build: the compare folds EXACTLY the 52 ASCII "
               "letters, each with one partner, and NO non-ASCII byte folds. "
               "0xdf (sharp s) is one of the three the design names."),
        B(r"^(ss)\1$", [("ssss",), ("ss\xdf",)], BRM, caseless=True,
          note="THE CELL THE SIGNATURE IS DESIGNED FOR. In an 8-bit build "
               "every fold pair is one byte to one byte, so the compare "
               "cannot change length and \"ss\\xdf\" does NOT match. A UTF-8 "
               "backend would have to answer this family differently -- one "
               "captured character folding to two -- which is why the residual "
               "entry returns a LENGTH rather than a bool: the shared emitter "
               "never computes one, it only adds the one it is given."),
        B(r"^(a)\1$", [("aA",), ("Aa",), ("aa",), ("AA",)], BR,
          caseless=True, groups=1),
        B(r"^(\w+)\1$", [("AbcaBC",), ("Abcabd",)], BR + ",classes", caseless=True, groups=1),
        B(r"^(\xb5)\1$", [("\xb5\xb5",)], BR, caseless=True),
        B(r"^(\xff)\1$", [("\xff\xff",)], BR, caseless=True),
    ]),
]

# ======================================================================
# dupnames.rxt -- §8: (?J), the resolution rule, and the RE-ENTRY cells
# ======================================================================
DUPNAMES = [
    ("THE `(?J)` SCOPING RULE: checked AT EACH DECLARATION (§8.1)", [
        B(r"^(?J)(?<a>x)(?<a>y)$", [("xy",)], BRNM, groups=2),
        B(r"^(?<a>x)(?J)(?<a>y)$", [("xy",)], BRNM, groups=2,
          note="LEGAL, and it is the cell that kills \"the check is made at "
               "the pattern's start\": the SECOND declaration is under "
               "`(?J)`, which is all the rule requires."),
        B(r"^(?J:(?<a>x)(?<a>y))$", [("xy",)], BRNM, groups=2),
        B(r"^(?J:(?<a>x))(?<a>y)$", [("xy",)], BRNM,
          note="ERROR: the second declaration is NOT under the `(?J)`, which "
               "was scoped away at its own closing paren."),
        B(r"^(?<a>x)(?<a>y)(?J)$", [("xy",)], BRNM,
          note="ERROR, and this is the sharpest cell of the four: `(?J)` "
               "AFTER both declarations does not help, which kills the "
               "reading that `(?J)` anywhere in the pattern legalises "
               "everything."),
        B(r"^(?J)(?<a>x)(?-J)(?<a>y)$", [("xy",)], BRNM,
          note="ERROR: an inline `(?-J)` turns the state back OFF, and "
               "measured against libpcre2 it does so EVEN WITH the "
               "PCRE2_DUPNAMES API bit set -- the inline letter is the "
               "authoritative scoped state, not a way of turning an option "
               "on. That measurement is what settles ASK-2: pcrec gets the "
               "letter and no option bit."),
        B(r"^(?J)(?<a>x)(?:(?-J)q)(?<a>y)$", [("xqy",)], BRNM, groups=2,
          note="LEGAL: the `(?-J)` really is scoped to its group and restored "
               "at the closing paren -- the ordinary modifier-scope "
               "discipline, not a special case."),
        B(r"^(?J)(?<a>x)(?^)(?<a>y)$", [("xy",)], BRNM, groups=2,
          note="`(?^)` resets the options to their defaults and does NOT "
               "clear J -- measured, not inherited from the letter list. "
               "Clearing it would turn a legal pattern into an error: the "
               "safe-LOOKING direction, and still wrong."),
        B(r"^(?<a>x)(?<A>y)$", [("xy",)], BRNM, groups=2,
          note="Names are CASE-SENSITIVE, so these are not duplicates at all "
               "and no `(?J)` is needed (D59, reconfirmed)."),
        B(r"^(?<a>x)(?<a>y)$", [("xy",)], BRNM,
          note="The base case: without `(?J)` in force, a duplicate name is a "
               "compile error."),
    ]),
    ("THE RESOLUTION RULE: FIRST OF THE NAME-RUN, BY NUMBER, THAT IS SET (§8.3)", [
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\k<a>$", [("xx",), ("yy",), ("xy",), ("yx",)],
          BRNM, groups=2,
          note="The four cells that separate four candidate rules. \"yy\" "
               "MATCHES with group 1 unset and group 2 = (0,1), which "
               "eliminates \"first by number\" taken unconditionally; \"xy\" "
               "and \"yx\" do NOT match, which eliminates \"any one of them\"."),
        B(r"(?J)^(?<a>x)(?<a>y)\k<a>$", [("xyx",), ("xyy",)], BRNM, groups=2,
          note="BOTH members set. \"xyx\" matches (it used #1) and \"xyy\" "
               "does NOT, which eliminates \"last set\" / \"highest number\". "
               "Sabotage rows S114 and S115 are these two rules, and each "
               "is caught by exactly ONE of these cells -- which is the point "
               "of writing them as separate rows."),
        B(r"(?J)^(?:(?<a>p)|(?<a>q)|(?<a>r))\k<a>$",
          [("pp",), ("qq",), ("rr",), ("pq",)], BRNM, groups=3,
          note="Three duplicates, with the MIDDLE and the LAST participating "
               "in turn -- the shape a two-member run cannot distinguish."),
        B(r"(?J)^(?:(?<a>x)|(?<a>y)|z)\k<a>$", [("z",), ("zz",)], BRNM,
          note="NONE set: §3.3's ordinary unset-reference failure applies. "
               "There is no separate rule for names."),
        B(r"(?J)^(?<a>x?)(?<a>y)\k<a>$", [("y",), ("yy",)], BRNM, groups=2,
          note="\"SET\" INCLUDES SET-TO-EMPTY. The run's FIRST entry captured "
               "the empty string, resolution STOPPED THERE, and the reference "
               "consumed nothing -- so \"y\" matches and \"yy\" does not. A "
               "\"first NON-EMPTY\" reading gets both cells wrong."),
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\2$", [("yy",), ("xx",)], BRNM, groups=2,
          note="NUMERIC references are unaffected by dupnames: a number names "
               "ONE group, duplicated name or not."),
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\1$", [("yy",), ("xx",)], BRNM, groups=2),
    ]),
    ("ALL FOUR BY-NAME SPELLINGS AGREE on the resolution", [
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\k'a'$", [("yy",)], BRNM, groups=2),
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\k{a}$", [("yy",)], BRNM, groups=2),
        B(r"(?J)^(?:(?<a>x)|(?<a>y))(?P=a)$", [("yy",)], BRNM, groups=2),
        B(r"(?J)^(?:(?<a>x)|(?<a>y))\g{a}$", [("yy",)], BRNM, groups=2),
    ]),
    ("THE RE-ENTRY CELLS OVER A NAME RUN (R32 re-check E13)", [
        B(r"(?J)^(?:(?<a>q))?(?:(?<a>a|b\k<a>))+$", [("aba",), ("a",), ("ab",)],
          BRNM, groups=2,
          note="THE CELL THAT MADE THE MARKED SET A UNION. \"aba\" is (0,3) "
               "with group 1 UNSET and group 2 = (1,3): the resolution chain "
               "falls THROUGH the unset first member to the second, which is "
               "the one being RE-ENTERED -- so it is exactly the member that "
               "must be published at close. Marking only the \"resolved\" "
               "member is not merely incomplete; there is no statically "
               "resolved member to speak of. Sabotage S104 marks one "
               "member of the run and this cell is its only detector."),
        B(r"(?J)^(?:(?<a>a|b\k<a>))+$", [("aba",), ("a",)], BRNM, groups=1),
        B(r"(?J)^(?<a>x)(?:(?<a>a|b\k<a>))+$", [("xbx",), ("x",)], BRNM,
          groups=2,
          note="The same shape with the fall-through removed: both members "
               "set, and the chain stops at the first."),
    ]),
]

# ======================================================================
# gated.rxt -- §10's two matrices. Every ACCEPT cell is oracle-verified
# against libpcre2 first (R32 C7).
# ======================================================================
GATED = [
    ("WITH THE MODULE ON: what each partial enable actually buys", [
        B(r"^(a)\1$", [("aa",), ("ab",)], BR, groups=1,
          note="The NUMERIC spellings need `backrefs` and nothing else."),
        B(r"^(a)\g{-1}$", [("aa",)], BR, groups=1),
        B(r"^(?<n>a)\k<n>$", [("aa",)], BRN, groups=1,
          note="The BY-NAME spellings need `named-groups` too, because "
               "without it there is no such thing as a group NAME."),
        B(r"^(?<n>a)(?P=n)$", [("aa",)], BRN, groups=1),
        B(r"^(?J)(?<a>x)(?<a>y)\k<a>$", [("xyx",)], BRNM, groups=2,
          note="`(?J)` needs `modifiers` as well, because the LETTER lives in "
               "that module's option-run dispatch even though `backrefs` owns "
               "what it means. That three-module dependency is this module's "
               "real partial-enable boundary."),
    ]),
    ("THE CLASS COLUMN DOES NOT MOVE, whatever is enabled", [
        B(r"^[\1]$", [("\x01",)], "classes",
          note="Base syntax: `[\\1]` compiles to 0x01 in EVERY feature set, "
               "including ones where `\\1` at atom position refuses. The "
               "granularity of D65's built column is the ATOM POSITION only, "
               "and this cell is that fact from the other side."),
        B(r"^[\1]$", [("\x01",)], BR),
        B(r"^[\1]$", [("\x01",)], "none"),
    ]),
]


HDR = """# tests/backrefs/%s -- module `backrefs` ([M6.5.2]): %s
#
# GENERATED BY tests/backrefs/gen_corpus.py, and that is a property rather
# than a convenience: every expectation below was produced by driving the cell
# through libpcre2 10.46 (via the committed ctypes binding at
# docs/design/backrefs_measurements/probes/br_oracle.py) BEFORE it was written.
# python3 `re` was driven over the SAME cells in the same pass, and a block
# carries `# pcre2-only` exactly where python diverged or could not compile the
# pattern -- DETECTED, never assumed, with the first divergence and the cell
# count recorded above the marking.
#
# THAT MARKING IS THE WHOLE REASON THE GENERATOR EXISTS. This module has the
# largest oracle divergence pcrec has met: python `re` refuses EVERY
# self-reference and EVERY forward reference at compile time, has no `\\g`, no
# `\\k` and no `(?J)` at all, rejects the `(?<n>...)` declaring spelling, and
# refuses `(?i)` anywhere but the pattern start -- which is exactly where the
# two cells that decide WHERE the caseless flag is read live. R32 C3 found the
# first test plan marking two files python-verifiable in the direction that
# LOSES the oracle; computing the marking removes the species.
#
# Design: docs/design/backrefs_design.md. Divergences are catalogued in
# docs/dev/upstream_issues.md.
"""


def main():
    tot = {'cells': 0, 'pcre2_only': 0, 'python_verified': 0, 'perr': 0}
    files = [
        ("numeric.rxt",
         "the numeric spellings `\\1`..`\\9` and above -- unset, empty, "
         "quantified, and the startpos axis (SS3.3, 3.4, 3.6)",
         NUMERIC),
        ("octal.rxt",
         "PCRE2's octal disambiguation at the ATOM position: the four ordered "
         "questions of S5, cell by cell, each with a DISCRIMINATOR subject so "
         "\"it compiled\" is never mistaken for \"it is a backreference\"",
         OCTAL),
        ("octal_class.rxt",
         "the CLASS position, which this module must leave byte-identical to "
         "the base tier (S5.2). Every cell here is a MUST-NOT-CHANGE pin, run "
         "with the module ENABLED",
         OCTAL_CLASS),
        ("selfref.rxt",
         "self-references, forward references, and the RE-ENTRY class that "
         "refuted the first design (SS3.2, 3.5)",
         SELFREF),
        ("nested.rxt",
         "nested repeats, the reverse-deterministic interaction, and nested "
         "backreferences (S3.7)",
         NESTED),
        ("spellings.rxt",
         "every spelling of a backreference, and the `\\g` doorway's OTHER "
         "construct (S2)",
         SPELLINGS),
        ("caseless.rxt",
         "WHERE the `(?i)` is read and WHAT the compare folds (S4)",
         CASELESS_CELLS),
        ("dupnames.rxt",
         "`(?J)`, its scoping rule, and the resolution rule for a reference to "
         "a duplicated name (S8)",
         DUPNAMES),
        ("gated.rxt",
         "the module-gating matrix: what each partial enable buys, and the "
         "class column that does not move (S10)",
         GATED),
    ]
    for fname, blurb, sections in files:
        c = write(fname, HDR % (fname, blurb), sections)
        for k in tot:
            tot[k] += c[k]
    print("-" * 72)
    print("TOTAL %d cells, %d blocks python-verified, %d pcre2-only, %d perr"
          % (tot['cells'], tot['python_verified'], tot['pcre2_only'],
             tot['perr']))


if __name__ == "__main__":
    main()
