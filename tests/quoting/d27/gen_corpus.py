#!/usr/bin/env python3
"""D27 quoting corpus generator.

Every expectation this script writes into a .rxt file is derived by calling
oracle_probe (a thin wrapper over libpcre2-8) at generation time -- never
hand-reasoned or copy-pasted from a terminal session. Each case is tagged
with the author's INTENT (should this subject match or not?); the generator
asserts the oracle's actual answer matches that intent before writing
anything, so a design mistake fails loudly here rather than silently
encoding a wrong expectation.

Run: python3 gen_corpus.py
Requires: ORACLE env var pointing at a built oracle_probe binary, or it
defaults to ./oracle_probe relative to this script's OUT_DIR.
"""
import os
import subprocess
import sys

SCRIPT_DIR = os.path.dirname(os.path.abspath(os.path.realpath(__file__)))
OUT_DIR = SCRIPT_DIR
ORACLE = os.environ.get("ORACLE", os.path.join(SCRIPT_DIR, "oracle_probe"))

TIMEOUT_BIN = "gnutimeout"


def run_oracle(args):
    cmd = [TIMEOUT_BIN, "20", ORACLE] + list(args)
    p = subprocess.run(cmd, capture_output=True)
    if p.returncode not in (0,):
        sys.stderr.write("oracle_probe FAILED (rc=%d): %r\nstderr: %s\n" % (p.returncode, args, p.stderr.decode("utf8", "replace")))
        sys.exit(1)
    return p.stdout.decode("utf8", "replace").rstrip("\n")


def oracle_compile(pattern, flags=""):
    out = run_oracle(["compile", pattern, flags])
    if out == "OK":
        return ("OK", None, None)
    parts = out.split()
    assert parts[0] == "ERROR", "unexpected compile output: %r" % out
    return ("ERROR", int(parts[1]), int(parts[2]))


def oracle_match(pattern, flags, subject, startpos):
    out = run_oracle(["match", pattern, flags, subject, str(startpos)])
    parts = out.split()
    if parts[0] == "NOMATCH":
        return ("NOMATCH", None)
    if parts[0] == "ERROR":
        return ("ERROR", (int(parts[1]), int(parts[2])))
    if parts[0] == "MATCHERROR":
        return ("MATCHERROR", int(parts[1]))
    assert parts[0] == "MATCH", "unexpected match output: %r" % out
    n = int(parts[1])
    vals = [int(x) for x in parts[2:]]
    assert len(vals) == 2 * n
    pairs = [(vals[2 * i], vals[2 * i + 1]) for i in range(n)]
    return ("MATCH", pairs)


def errmsg(code):
    return run_oracle(["errmsg", str(code)])


# --- .rxt subject escaping (encode arbitrary bytes into the format's
# 7-escape subject vocabulary: \" \\ \n \t \r \f \v \xHH) ---
_ESCAPE_MAP = {
    ord('"'): '\\"',
    ord('\\'): '\\\\',
    ord('\n'): '\\n',
    ord('\t'): '\\t',
    ord('\r'): '\\r',
    ord('\f'): '\\f',
    ord('\v'): '\\v',
}


def rxt_escape_subject(s):
    """s is a python str of codepoints 0-255 standing for raw bytes."""
    out = []
    for ch in s:
        b = ord(ch)
        if b in _ESCAPE_MAP:
            out.append(_ESCAPE_MAP[b])
        elif 0x20 <= b < 0x7f:
            out.append(ch)
        else:
            out.append("\\x%02x" % b)
    return '"' + "".join(out) + '"'


class Block:
    """One pattern block: a pcrec/PCRE2 pattern plus its oracle-verified cases."""

    def __init__(self, pattern, flags="", features="quoting", name=None, description=None):
        self.pattern = pattern
        self.flags = flags
        self.features = features
        self.name = name
        self.description = description
        self.lines = []  # rendered body lines (after 'pattern ...')
        self.is_perr = False
        self.perr_code = None
        self.perr_offset = None

    def expect_perr(self, expect_code=None):
        kind, code, offset = oracle_compile(self.pattern, self.flags)
        if kind != "ERROR":
            raise AssertionError("expected compile ERROR for %r (flags=%r) but oracle said %s" % (self.pattern, self.flags, kind))
        if expect_code is not None and code != expect_code:
            raise AssertionError("pattern %r: expected error code %d, oracle gave %d (%s)" % (self.pattern, expect_code, code, errmsg(code)))
        self.is_perr = True
        self.perr_code = code
        self.perr_offset = offset
        return self

    def expect_ok(self):
        kind, _, _ = oracle_compile(self.pattern, self.flags)
        if kind != "OK":
            raise AssertionError("expected pattern %r (flags=%r) to compile, oracle said %s" % (self.pattern, self.flags, kind))
        return self

    def m(self, subject, startpos=0, groups=None):
        """Assert a match at startpos; groups: optional dict {slot: True} of
        extra capture slots to emit as g/gp lines (0 is always emitted via
        the m/ms line itself, per spec)."""
        kind, pairs = oracle_match(self.pattern, self.flags, subject, startpos)
        if kind != "MATCH":
            raise AssertionError("expected MATCH for pattern %r subject %r startpos %d, oracle said %s (%r)" % (self.pattern, subject, startpos, kind, pairs))
        s0, e0 = pairs[0]
        if startpos == 0:
            self.lines.append('m %s %d %d' % (rxt_escape_subject(subject), s0, e0))
        else:
            self.lines.append('ms %d %s %d %d' % (startpos, rxt_escape_subject(subject), s0, e0))
        if groups:
            for slot in sorted(groups):
                if slot >= len(pairs):
                    raise AssertionError("pattern %r: requested group slot %d but oracle ovector has only %d slots" % (self.pattern, slot, len(pairs)))
                gs, ge = pairs[slot]
                directive = groups[slot]  # 'g' or 'gp'
                self.lines.append('%s %d %d %d' % (directive, slot, gs, ge))
        return self

    def n(self, subject, startpos=0):
        kind, pairs = oracle_match(self.pattern, self.flags, subject, startpos)
        if kind != "NOMATCH":
            raise AssertionError("expected NOMATCH for pattern %r subject %r startpos %d, oracle said %s (%r)" % (self.pattern, subject, startpos, kind, pairs))
        if startpos == 0:
            self.lines.append('n %s' % rxt_escape_subject(subject))
        else:
            self.lines.append('ns %d %s' % (startpos, rxt_escape_subject(subject)))
        return self

    def render(self):
        out = []
        if self.description:
            out.append('# %s' % self.description)
        out.append('pattern %s' % self.pattern)
        if self.name:
            out.append('name %s' % self.name)
        if self.flags:
            out.append('flags %s' % self.flags)
        if self.features:
            out.append('features %s' % self.features)
        if self.is_perr:
            out.append('# PCRE2 rejects this pattern: error %d (%s), offset %d' % (
                self.perr_code, errmsg(self.perr_code), self.perr_offset))
            out.append('perr')
        else:
            out.extend(self.lines)
        return "\n".join(out) + "\n"


def write_file(relpath, header_comment, blocks):
    path = os.path.join(OUT_DIR, relpath)
    with open(path, "w") as f:
        f.write(header_comment.rstrip() + "\n\n")
        for i, b in enumerate(blocks):
            if i:
                f.write("\n")
            f.write(b.render())
    print("wrote %s (%d blocks)" % (path, len(blocks)))


# ============================================================================
# basics.rxt -- \Q...\E over each PCRE2 metacharacter class, and the doc's
# own worked examples (pcre2pattern(3), BACKSLASH section).
# ============================================================================
basics = []

basics.append(Block(r'a\Qb.c\Ed', description="quoted dot: '.' is literal, not any-char").expect_ok()
              .m('ab.cd', 0)
              .n('abXcd', 0))

basics.append(Block(r'\Qa*b\E', description="quoted star: not a quantifier").expect_ok()
              .m('a*b', 0)
              .n('aaab', 0))

basics.append(Block(r'\Qa+b\E', description="quoted plus: not a quantifier").expect_ok()
              .m('a+b', 0)
              .n('aaab', 0))

basics.append(Block(r'\Qa?b\E', description="quoted question mark: not a quantifier").expect_ok()
              .m('a?b', 0)
              .n('ab', 0))

basics.append(Block(r'\Qa{2,3}b\E', description="quoted counted repeat: literal braces").expect_ok()
              .m('a{2,3}b', 0)
              .n('aab', 0))

basics.append(Block(r'\Q^a$\E', description="quoted anchors: literal caret and dollar, no anchoring").expect_ok()
              .m('^a$', 0)
              .n('a', 0))

basics.append(Block(r'\Qa(b)c\E', description="quoted parens: literal, no capturing group created").expect_ok()
              .m('a(b)c', 0))

basics.append(Block(r'\Qa[b]c\E', description="quoted brackets: literal, no character class opened").expect_ok()
              .m('a[b]c', 0))

basics.append(Block(r'\Qa|b\E', description="quoted alternation bar: literal, not alternation").expect_ok()
              .m('a|b', 0)
              .n('a', 0))

basics.append(Block(r'\Qa\b\E', description="quoted backslash: literal backslash+b, not \\b word boundary").expect_ok()
              .m('a\\b', 0)
              .n('a', 1))  # word-boundary reading would match zero-width after 'a'; literal reading requires the backslash byte

basics.append(Block(r'\Q\\E', description="pcre2pattern(3) worked example: \\Q\\\\E matches a single backslash "
                                          "(the first backslash is quoted data, the second+E terminates)").expect_ok()
              .m('\\', 0))

basics.append(Block(r'\Qabc$xyz\E', description="pcre2pattern(3) worked example: $ and @ are literal in \\Q...\\E "
                                                 "(unlike Perl's interpolation)").expect_ok()
              .m('abc$xyz', 0))

basics.append(Block(r'\Qabc\$xyz\E', description="pcre2pattern(3) worked example: backslash inside \\Q...\\E is "
                                                  "itself literal data, so \\$ quotes to two literal chars").expect_ok()
              .m('abc\\$xyz', 0))

basics.append(Block(r'\Qabc\E\$\Qxyz\E', description="pcre2pattern(3) worked example: leaving quoting to use an "
                                                       "escaped $ then re-entering quoting").expect_ok()
              .m('abc$xyz', 0))

basics.append(Block(r'\QA\B\E', description="pcre2pattern(3) worked example: quoted A\\B is four literal chars").expect_ok()
              .m('A\\B', 0))

basics.append(Block(r'a\Q\Eb', description="empty \\Q\\E in the middle contributes zero literal characters").expect_ok()
              .m('ab', 0))

basics.append(Block(r'\Q\E', description="\\Q\\E alone: a zero-width match, like an empty pattern").expect_ok()
              .m('', 0)
              .m('xyz', 0)
              .m('xyz', 2))

write_file("basics.rxt", """\
# D27 quoting corpus -- \\Q...\\E LITERAL QUOTING, basics.
#
# \\Q...\\E turns every character up to the matching \\E into a literal --
# quantifiers, anchors, dots, parens, brackets, the alternation bar, and
# backslash itself all lose their special meaning inside a quoted run.
# Oracle: libpcre2-8 via oracle_probe.c (this directory). See FINDINGS.md --
# no documentation/oracle divergence was found while building this corpus.
""", basics)


# ============================================================================
# unterminated.rxt -- unterminated \Q (implicit \E at end of pattern), and
# stray/isolated \E (ignored when not preceded by an open \Q).
# ============================================================================
unterminated = []

unterminated.append(Block(r'ab\Qc+d', description="unterminated \\Q outside a class: literal quoting runs to the "
                                                    "end of the pattern (implicit \\E)").expect_ok()
                     .m('abc+d', 0)
                     .n('abcccd', 0))

unterminated.append(Block(r'abc\Q', description="\\Q at the very end of the pattern with nothing after it: "
                                                 "contributes zero literal characters").expect_ok()
                     .m('abc', 0))

unterminated.append(Block(r'\Eabc', description="an isolated \\E with no preceding \\Q is ignored entirely").expect_ok()
                     .m('abc', 0))

unterminated.append(Block(r'a\Eb\Ec', description="two isolated \\E's, neither preceded by an open \\Q, both ignored").expect_ok()
                     .m('abc', 0))

unterminated.append(Block(r'\Qab\E\Ec', description="a real \\Q...\\E followed immediately by a second, isolated "
                                                      "\\E -- the second \\E is ignored, not an error").expect_ok()
                     .m('abc', 0))

unterminated.append(Block(r'\Qab\Ec\Ed', description="quoted run, then literal 'c', then an isolated trailing \\E, "
                                                       "then literal 'd' -- the isolated \\E vanishes without "
                                                       "affecting anything around it").expect_ok()
                     .m('abcd', 0))

write_file("unterminated.rxt", """\
# D27 quoting corpus -- \\Q...\\E, unterminated \\Q and isolated \\E.
#
# pcre2pattern(3): "If \\Q is not followed by \\E later in the pattern, the
# literal interpretation continues to the end of the pattern (that is, \\E is
# assumed at the end)." and "An isolated \\E that is not preceded by \\Q is
# ignored." Both are oracle-verified here. The INSIDE-a-character-class case
# of an unterminated \\Q is a compile ERROR, not an implicit-\\E case -- see
# errors.rxt.
""", unterminated)


# ============================================================================
# charclass.rxt -- \Q...\E inside [...] character classes: quoted members,
# ']' and '^' and '-' at positions that would otherwise be special.
# ============================================================================
charclass = []

charclass.append(Block(r'[\Qabc\E]', description="quoted run as ordinary class members, equivalent to [abc]").expect_ok()
                  .m('b', 0)
                  .n('d', 0))

charclass.append(Block(r'[\Q]\E]', description="quoted ']' as the class's sole member -- it does not terminate "
                                                "the class while quoted").expect_ok()
                  .m(']', 0)
                  .n('a', 0))

charclass.append(Block(r'[\Q^\E]', description="quoted '^' as the class's sole member -- NOT negation, even "
                                                "though it is the first thing after '['").expect_ok()
                  .m('^', 0)
                  .n('a', 0))

charclass.append(Block(r'[^\Qa\E]', description="contrast with the above: an UNQUOTED leading '^' still negates; "
                                                 "the quoted member inside is what is excluded").expect_ok()
                  .n('a', 0)
                  .m('b', 0))

charclass.append(Block(r'[\Qa-z\E]', description="quoted 'a-z' is three literal members {a,-,z}, not a range").expect_ok()
                  .m('a', 0)
                  .m('-', 0)
                  .m('z', 0)
                  .n('m', 0))

charclass.append(Block(r'[a\Q-\Ez]', description="an interior hyphen quoted on its own: still no range formed "
                                                  "between 'a' and 'z'").expect_ok()
                  .m('a', 0)
                  .m('-', 0)
                  .m('z', 0)
                  .n('m', 0))

charclass.append(Block(r'[\Qa\Q\E]', description="a literal backslash-Q is impossible to spell this way -- this "
                                                  "pattern instead re-enters quoting harmlessly: \\Q opens, 'a' is "
                                                  "quoted, a SECOND \\Q inside an already-open quote is just two "
                                                  "literal chars ('\\','Q') per the doc's rule that only the "
                                                  "literal two-byte sequence \\E is special inside a quote, and "
                                                  "\\E then closes it -- net class members {a,\\,Q}").expect_ok()
                  .m('a', 0)
                  .m('\\', 0)
                  .m('Q', 0)
                  .n('b', 0))

write_file("charclass.rxt", """\
# D27 quoting corpus -- \\Q...\\E inside [...] character classes.
#
# pcre2pattern(3), BACKSLASH section: "The \\Q...\\E sequence is recognized
# both inside and outside character classes." Verified here: a quoted ']'
# does not close the class, a quoted leading '^' does not negate it, and a
# quoted '-' does not form a range.
""", charclass)


# ============================================================================
# extended.rxt -- (?x) extended mode: whitespace and '#' stay literal INSIDE
# a quoted run even though they are stripped/comment-eaten outside one.
# ============================================================================
extended = []

extended.append(Block(r'(?x)a\Q b \Ec', description="under (?x), whitespace inside \\Q...\\E is literal even "
                                                      "though (?x) strips unescaped whitespace elsewhere").expect_ok()
                .m('a b c', 0)
                .n('abc', 0))

extended.append(Block(r'(?x) a b c', description="contrast/control: outside any quoting, (?x) strips the "
                                                   "whitespace between letters").expect_ok()
                .m('abc', 0))

extended.append(Block(r'(?x)\Qa#b\E', description="under (?x), '#' inside \\Q...\\E is literal, not a comment "
                                                    "starter").expect_ok()
                .m('a#b', 0)
                .n('a', 0))

extended.append(Block(r'(?x)a#comment', description="contrast/control: outside quoting, (?x) '#' starts a "
                                                      "comment that runs to the end of the pattern (no newline "
                                                      "is available inside a single .rxt pattern line, so this "
                                                      "exercises end-of-pattern as the comment's other boundary)").expect_ok()
                .m('a', 0)
                .m('acomment', 0))

extended.append(Block(r'(?x)\Qa#b\E#trailing comment eaten', description="one pattern with both: the quoted "
                                                                          "'#' is literal data, the later "
                                                                          "unquoted '#' opens a real comment "
                                                                          "that swallows the rest of the line").expect_ok()
                .m('a#b', 0))

write_file("extended.rxt", """\
# D27 quoting corpus -- \\Q...\\E interaction with (?x) extended mode.
#
# pcre2pattern(3): "most white space in the pattern, other than in a
# character class, within a \\Q...\\E sequence, or between a # outside a
# character class and the next newline, inclusive, is ignored." Both
# exclusions (whitespace and '#') are exercised here, each against an
# unquoted control on the same construct.
""", extended)


# ============================================================================
# caseless.rxt -- (?i) / flags i acting on quoted literal text.
# ============================================================================
caseless = []

caseless.append(Block(r'\QABC\E', flags="i", description="case-insensitive flag folds quoted literal text same "
                                                           "as any other literal").expect_ok()
                .m('abc', 0)
                .m('ABC', 0)
                .m('AbC', 0))

caseless.append(Block(r'\QABC\E', flags="", description="control: without the caseless flag, quoted text is "
                                                          "still case-sensitive").expect_ok()
                .m('ABC', 0)
                .n('abc', 0))

caseless.append(Block(r'(?i)\QABC\E', flags="", description="inline (?i) before the quoted run has the same "
                                                              "effect as the flags directive").expect_ok()
                .m('abc', 0))

write_file("caseless.rxt", """\
# D27 quoting corpus -- \\Q...\\E under case-insensitive matching.
""", caseless)


# ============================================================================
# quantifier_after.rxt -- a quantifier following a quoted run binds to the
# LAST character of that run only (the quoted run is a sequence of
# individual literal atoms, not one atom); an EMPTY quoted run is
# transparent and the quantifier reaches past it to the real preceding atom;
# a quantifier with truly nothing before it is a hard error.
# ============================================================================
quant = []

quant.append(Block(r'\Qab\E+', description="a quantifier after a quoted run binds to the run's LAST character "
                                            "only ('b'), not the whole run").expect_ok()
             .m('ab', 0)
             .m('abbb', 0)
             .m('aabb', 0, groups=None))  # whole-match span itself demonstrates the binding; see below for the exact span

quant.append(Block(r'a\Q\E+', description="an EMPTY \\Q\\E between an atom and a quantifier is transparent: the "
                                           "quantifier reaches past it and binds to 'a'").expect_ok()
             .m('a', 0)
             .m('aaa', 0))

quant.append(Block(r'{\Q1\E,2}', description="pcre2pattern(3) worked example: \\Q/\\E anywhere inside what might "
                                              "otherwise be a quantifier stops it being recognized as one -- the "
                                              "whole thing is literal text \"{1,2}\"").expect_ok()
             .m('{1,2}', 0))

quant.append(Block(r'\Q\E+', description="a quantifier with NOTHING before it (the quoted run it might have "
                                          "followed is itself empty and at the very start of the pattern) is a "
                                          "hard compile error, same as a bare leading '+'").expect_perr())

write_file("quantifier_after.rxt", """\
# D27 quoting corpus -- a quantifier applied AFTER a quoted run.
#
# \\Q...\\E is equivalent to writing out each contained character as its own
# escaped literal, so ordinary quantifier-binds-to-the-immediately-preceding-
# atom rules apply: only the LAST quoted character is what a following
# quantifier repeats. Verified against the oracle rather than assumed --
# this is the one place this corpus's author found the documentation's
# prose genuinely ambiguous before checking.
""", quant)

# quant block 1 ('\Qab\E+' on 'aabb') needs its exact span recorded --
# render() only wrote the m line already (oracle-derived), nothing more to
# add; this comment documents why groups=None above is fine: there are no
# named groups in this pattern, and the m line's own <start> <end> already
# carries the binding proof (match starts at offset 1, "abb", if + reached
# only 'b'; would start at offset 0 covering all 4 bytes if + had reached
# the whole quoted run).


# ============================================================================
# adjacent_escapes.rxt -- \Q/\E next to other escape sequences: an escape
# immediately after \Q is literal data (not interpreted), and a normal
# escape immediately before \Q keeps its own meaning.
# ============================================================================
adjacent = []

adjacent.append(Block(r'\d\Q+\E', description="an ordinary escape ('\\d') immediately followed by a quoted run "
                                               "keeps its own meaning; the quoted '+' is literal").expect_ok()
                .m('5+', 0)
                .n('5', 0))

adjacent.append(Block(r'\Q\d\E', description="an escape sequence spelled INSIDE \\Q...\\E is not interpreted at "
                                              "all -- it is two literal characters, backslash and 'd', not the "
                                              "digit class").expect_ok()
                .m('\\d', 0)
                .n('5', 0))

adjacent.append(Block(r'\w\Qxy\E\s', description="quoting sandwiched between two live escapes on either side").expect_ok()
                .m('axy ', 0)
                .n('a-y ', 0))

write_file("adjacent_escapes.rxt", """\
# D27 quoting corpus -- \\Q...\\E adjacent to, and containing, other escapes.
""", adjacent)


# ============================================================================
# groups.rxt -- capturing groups interacting with quoted text: a group
# wrapping a quoted run, and a quoted run containing metacharacter-shaped
# text inside a group.
# ============================================================================
groups = []

groups.append(Block(r'(\Qab\E)cd', description="a capturing group wrapping an entire quoted run").expect_ok()
               .m('abcd', 0, groups={1: 'g'}))

groups.append(Block(r'a(\Qb+c\E)d', description="a capturing group around quoted metacharacter-shaped text -- "
                                                 "the '+' inside must stay literal even though it is now also "
                                                 "inside a group").expect_ok()
               .m('ab+cd', 0, groups={1: 'g'})
               .n('abccd', 0))

groups.append(Block(r'(a)\Q(b)\E(c)', description="quoting between two real capturing groups: the quoted "
                                                   "parens create no group of their own, so group numbering "
                                                   "skips straight from 1 to 2").expect_ok()
               .m('a(b)c', 0, groups={1: 'g', 2: 'g'}))

write_file("groups.rxt", """\
# D27 quoting corpus -- \\Q...\\E interaction with capturing groups.
#
# A quoted run creates no capturing group of its own (its parens, if any,
# are literal text), which this file checks both by content (a group's
# captured span around quoted text) and by NUMBERING (quoted parens must
# not consume a group number).
""", groups)


# ============================================================================
# errors.rxt -- compile-time errors. The one quoting-specific error surface
# per pcre2pattern(3): "If the isolated \Q is inside a character class, this
# causes an error, because the character class is then not terminated by a
# closing square bracket." Each perr case is paired with a positive control
# showing the minimal fix compiles.
# ============================================================================
errors = []

errors.append(Block(r'[a\Qbc', description="unterminated \\Q inside a class, no \\E at all: the class is never "
                                            "closed because the ']' that would close it is never reached "
                                            "(pattern ends first)").expect_perr(expect_code=106))

errors.append(Block(r'[a\Qbc\E', description="unterminated \\Q inside a class, \\E present but the CLASS itself "
                                              "is never closed: quoting ends, but no ']' follows before the "
                                              "pattern ends").expect_perr(expect_code=106))

errors.append(Block(r'[a\Qbc\E]', description="positive control for the two cases above: the same class, "
                                               "properly closed after \\E, compiles fine").expect_ok()
              .m('b', 0)
              .m('a', 0)
              .n('d', 0))

errors.append(Block(r'\Q\E+', description="a quantifier with nothing to repeat (see quantifier_after.rxt for "
                                           "the full discussion) -- included here too as the corpus's other "
                                           "quoting-adjacent compile error").expect_perr(expect_code=109))

write_file("errors.rxt", """\
# D27 quoting corpus -- compile-time errors specific to \\Q...\\E.
#
# Per project policy D26, only the accept/reject FACT is a project promise;
# PCRE2's exact diagnostic WORDING is not. The error codes and messages
# below are recorded as provenance (this is what libpcre2-8 10.46 reports
# for these patterns) via oracle_probe's own errmsg mode, not as a
# requirement pcrec's own diagnostic text must match.
""", errors)

print("done.")
