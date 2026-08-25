#!/usr/bin/env python3
"""sr_gen.py -- the [DD-14.D27] blinded `recursion` corpus GENERATOR.

Idempotent: rewrites every d27/*.rxt from the spec below. NO expectation in
this file is hand-typed. Each case declares only

    (kind, subject, startpos)

where `kind` is the author's INTENT ('m' or 'n'); the span, and every group
span, come from libpcre2 10.46 through sr_oracle. If the oracle disagrees
with the stated intent the generator ABORTS -- a cell that does not test
what its author thought it tested is a corpus bug, not something to paper
over by taking the oracle's word silently.

D27: this author has never seen src/ or tests/. libpcre2 10.46 is the sole
oracle for match cells (D26); perl 5.40.1 is a SECOND oracle whose
divergences sr_perl.py records but never writes as an expectation.

Written from docs/testing.md's ".rxt format" section directly.
"""
import importlib.util
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
CELL = os.path.dirname(HERE)
_OR = os.path.join(CELL, "docs", "design", "subroutines_measurements",
                   "probes", "sr_oracle.py")
_s = importlib.util.spec_from_file_location("sr_oracle", _OR)
sr = importlib.util.module_from_spec(_s)
_s.loader.exec_module(sr)

# Patterns perl 5.40.1 answers differently from libpcre2 10.46, as measured
# by d27/sr_perl.py on its last run. Read here only to STAMP the affected
# blocks `# perl-diverges`; no expectation is ever taken from perl (D26).
_PD = os.path.join(HERE, "perl_diverges.txt")
PERL_DIVERGES = set()
if os.path.exists(_PD):
    for _l in open(_PD):
        _l = _l.strip()
        if _l:
            PERL_DIVERGES.add(bytes.fromhex(_l).decode("latin-1"))

EMAIL = os.path.join(CELL, "docs", "design", "subroutines_measurements",
                     "email_specimen")
ORIG = open(os.path.join(EMAIL, "orig.rx")).read().strip()
FACT = open(os.path.join(EMAIL, "factored.rx")).read().strip()

# ---------------------------------------------------------------------------
# .rxt subject encoding, per docs/testing.md's escape table -- and ONLY that
# table: \" \\ \n \t \r \f \v \xHH. Anything else printable goes through raw.
# ---------------------------------------------------------------------------
_SIMPLE = {'"': '\\"', '\\': '\\\\', '\n': '\\n', '\t': '\\t',
           '\r': '\\r', '\f': '\\f', '\v': '\\v'}


def enc(s):
    out = []
    for ch in s:
        if ch in _SIMPLE:
            out.append(_SIMPLE[ch])
        elif ' ' <= ch <= '~':
            out.append(ch)
        else:
            out.append('\\x%02x' % ord(ch))
    return '"%s"' % ''.join(out)


# ---------------------------------------------------------------------------
# The spec vocabulary.
# ---------------------------------------------------------------------------
def B(pat, feats, note, cases=(), perr=None, gu=(), engine=None,
      budget=(), flags=None, perl_skip=False, guclass="leftrec"):
    """One .rxt block. `perr` is None | 'both' (PCRE2 refuses too) |
    'pcrec' (PCRE2 ACCEPTS; pcrec refuses by a stated ruling)."""
    return dict(pat=pat, feats=list(feats), note=note, cases=list(cases),
                perr=perr, gu=list(gu), engine=engine, budget=list(budget),
                flags=flags, perl_skip=perl_skip, guclass=guclass)


def m(subj, start=0):
    return ('m', subj, start)


def n(subj, start=0):
    return ('n', subj, start)


R = "recursion"
NG = "named-groups"
BR = "backrefs"
AS = "assertions"
LA = "lookaround"
AT = "atomic-groups"
MO = "modifiers"

G10 = "(a)(b)(c)(d)(e)(f)(g)(h)(i)(j|k)"

# ===========================================================================
# FILE 1 -- sr_spellings.rxt
#   The construct table (extract 2.1/2.2/2.3): every call spelling put
#   through the ONE cell that separates a call from a reference, plus the
#   reference spellings as controls giving the OPPOSITE answer, plus the
#   forward and relative resolutions.
# ===========================================================================
SPELL_CALL = [
    ("(?1)", R), ("(?01)", R), ("(?001)", R), ("(?0001)", R),
    (r"\g<1>", R), (r"\g'1'", R), (r"\g<01>", R), (r"\g'01'", R),
    ("(?-1)", R), ("(?-01)", R), (r"\g<-1>", R), (r"\g'-1'", R),
]

F_SPELLINGS = []

F_SPELLINGS.append(B(
    "(a|b)(?1)", [R],
    "extract 2.1: THE discriminator, unanchored exactly as measured. A CALL "
    "re-RUNS the alternation, so 'ab' matches; the reference below cannot.",
    [m("ab"), m("aa"), n("a"), n("xy")]))

F_SPELLINGS.append(B(
    r"(a|b)\1", [R, BR],
    "extract 2.1 CONTROL, module backrefs: the same shape as a REFERENCE. "
    "'ab' must NOT match -- this is the half of the pair that makes the "
    "call cell mean something. A corpus with only the call row proves "
    "nothing about which construct was compiled.",
    [n("ab"), m("aa"), n("a")]))

for spelling, _ in SPELL_CALL:
    F_SPELLINGS.append(B(
        "^(a|b)%s$" % spelling, [R],
        "spelling %s put through the call/reference discriminator: 'ab' "
        "matches only if this spelling RE-RUNS group 1." % spelling,
        [m("ab"), m("aa"), n("a"), n("aba")]))

for spelling in ["(?&w)", "(?P>w)", r"\g<w>", r"\g'w'"]:
    F_SPELLINGS.append(B(
        "^(?<w>a|b)%s$" % spelling, [R, NG],
        "by-name call spelling %s through the discriminator." % spelling,
        [m("ab"), m("aa"), n("a")]))

F_SPELLINGS.append(B(
    "^(?P<w>a|b)(?P>w)$", [R, NG],
    "the python-style declaration and the python-style call together.",
    [m("ab"), m("aa"), n("a")]))

F_SPELLINGS.append(B(
    "^(?'w'a|b)(?&w)$", [R, NG],
    "the Perl-quoted declaration with a (?&name) call.",
    [m("ab"), m("aa"), n("a")]))

for ref, feats in [(r"\1", [R, BR]), (r"\g{1}", [R, BR]), (r"\g1", [R, BR])]:
    F_SPELLINGS.append(B(
        "^(a|b)%s$" % ref, feats,
        "REFERENCE control for the anchored discriminator: %s wants the "
        "same TEXT, so 'ab' is a nomatch where every call spelling above "
        "matches." % ref,
        [n("ab"), m("aa")]))

F_SPELLINGS.append(B(
    r"^(?<w>a|b)\k<w>$", [R, NG, BR],
    "by-NAME reference control: \\k<w> is backrefs', not this module's, and "
    "answers the opposite of \\g<w> on 'ab'.",
    [n("ab"), m("aa")]))

F_SPELLINGS.append(B(
    "^(?P<w>a|b)(?P=w)$", [R, NG, BR],
    "(?P=w) is the REFERENCE python spelling; (?P>w) two blocks up is the "
    "CALL. One letter apart, opposite answers on 'ab'.",
    [n("ab"), m("aa")]))

# --- forward calls -------------------------------------------------------
F_SPELLINGS.append(B(
    "^(?+1)(a|b)$", [R],
    "extract 2.3: THE shape that makes a call unlike a reference -- a "
    "FORWARD call runs group 1's pattern BEFORE group 1 has run.",
    [m("ab"), m("aa"), n("a"), n("abc")]))

F_SPELLINGS.append(B(
    r"^\2(a|b)(c)$", [R, BR],
    "extract 2.3 CONTROL: a forward REFERENCE can only ever read an unset "
    "group, so it fails where the forward call above succeeds.",
    [n("abc"), n("ac")]))

F_SPELLINGS.append(B(
    "^(?+1)(a)$", [R],
    "extract 2.3 row 3, with its measured capture: group 1 is set by its "
    "own LEXICAL run at offset 1, not by the call that ran first.",
    [m("aa"), n("a")]))

F_SPELLINGS.append(B(
    "^(?+2)(a)(b)$", [R],
    "extract 2.3 row 4: (?+2) counts forward PAST one group.",
    [m("bab"), n("aab"), n("ab")]))

F_SPELLINGS.append(B(
    r"^\g<+1>(a)$", [R],
    "extract 2.3 row 6: \\g<+N> obeys the same relative rule as (?+N).",
    [m("aa"), n("a")]))

# --- relative resolution -------------------------------------------------
F_SPELLINGS.append(B(
    "^(a)(b)(?-1)$", [R],
    "extract 2.3 row 1: (?-1) is the NEAREST group to the LEFT -- group 2. "
    "'aba' must fail, or the cell would not have distinguished group 2 "
    "from group 1.",
    [m("abb"), n("aba"), n("ab")]))

F_SPELLINGS.append(B(
    "^(a)(b)(?-2)$", [R],
    "extract 2.3 row 2: (?-2) counts back two -- group 1.",
    [m("aba"), n("abb")]))

F_SPELLINGS.append(B(
    "^(a)(?-01)$", [R],
    "extract 2.3 row 5: a LEADING ZERO on a relative call is accepted and "
    "the whole digit run is read as decimal.",
    [m("aa"), n("a")]))

F_SPELLINGS.append(B(
    "^(a)(b)(?-01)$", [R],
    "(?-01) == (?-1) == group 2 -- the leading zero does not shift the "
    "count.",
    [m("abb"), n("aba")]))

F_SPELLINGS.append(B(
    r"^(a)(b)\g<-01>$", [R],
    "the \\g<> doorway takes a leading zero on a relative value too.",
    [m("abb"), n("aba")]))

F_SPELLINGS.append(B(
    r"^(a)(b)\g<-02>$", [R],
    "\\g<-02> == \\g<-2> == group 1.",
    [m("aba"), n("abb")]))

F_SPELLINGS.append(B(
    r"^(a)(b)\g'-1'$", [R],
    "the quoted doorway, relative.",
    [m("abb"), n("aba")]))

F_SPELLINGS.append(B(
    "^((a)(b))(?-1)$", [R],
    "relative resolution is at the CALL SITE'S OWN GROUP COUNT -- three "
    "'(' have been seen, so (?-1) is group 3, not group 1 and not the "
    "enclosing group.",
    [m("abb"), n("aba"), n("abab")]))

F_SPELLINGS.append(B(
    "^((a)(b))(?-2)$", [R],
    "…and (?-2) is group 2.",
    [m("aba"), n("abb")]))

F_SPELLINGS.append(B(
    "^((a)(b))(?-3)$", [R],
    "…and (?-3) is group 1, the group the call site is written INSIDE of "
    "having already closed -- two characters wide, not one.",
    [m("abab"), n("aba"), n("abb")]))

# --- two-digit calls -----------------------------------------------------
F_SPELLINGS.append(B(
    "^%s(?10)$" % G10, [R],
    "extract 2.2: a TWO-DIGIT absolute call. The whole digit run is "
    "decimal, so this is group 10 -- 'abcdefghija' (which is what a "
    "one-digit-prefix misparse into (?1) would accept) must FAIL.",
    [m("abcdefghijk"), m("abcdefghijj"), n("abcdefghija"), n("abcdefghijx")]))

F_SPELLINGS.append(B(
    r"^%s\g<10>$" % G10, [R],
    "the two-digit call through the \\g<> doorway.",
    [m("abcdefghijk"), n("abcdefghija")]))

F_SPELLINGS.append(B(
    r"^%s\g'10'$" % G10, [R],
    "the two-digit call through the quoted doorway.",
    [m("abcdefghijk"), n("abcdefghija")]))

F_SPELLINGS.append(B(
    "^%s(?-10)$" % G10, [R],
    "a two-digit RELATIVE call: ten groups back from a call site that has "
    "seen ten is group 1. 'abcdefghijk' -- which (?-1) would accept -- "
    "must FAIL.",
    [m("abcdefghija"), n("abcdefghijk")]))

F_SPELLINGS.append(B(
    "^%s(?-1)$" % G10, [R],
    "control for the row above: (?-1) at the same site IS group 10.",
    [m("abcdefghijk"), n("abcdefghija")]))

F_SPELLINGS.append(B(
    "^(?+10)%s$" % G10, [R],
    "a two-digit FORWARD call: ten groups forward from a site that has "
    "seen none is group 10.",
    [m("kabcdefghij"), m("jabcdefghij"), n("xabcdefghij"), n("aabcdefghij")]))

# ===========================================================================
# FILE 2 -- sr_root.rxt
#   Extract 2.4/2.4a: "the whole pattern" INCLUDES the anchors, and the
#   whole-digit-run rule. The anchored discriminator ^(a(?N)?b)$ on "aabb"
#   answers (0,4) for a call to GROUP 1 and nomatch for a call to the ROOT,
#   so every row below reads its target straight off a match/nomatch.
# ===========================================================================
F_ROOT = []

ROOT_TARGETS = [
    ("(?1)", "group 1", "m"), ("(?01)", "group 1", "m"),
    ("(?001)", "group 1", "m"), ("(?0001)", "group 1", "m"),
    (r"\g<1>", "group 1", "m"), (r"\g<01>", "group 1", "m"),
    (r"\g'1'", "group 1", "m"), (r"\g'01'", "group 1", "m"),
    ("(?R)", "the ROOT", "n"), ("(?0)", "the ROOT", "n"),
    ("(?00)", "the ROOT", "n"), (r"\g<0>", "the ROOT", "n"),
    (r"\g<00>", "the ROOT", "n"), (r"\g'0'", "the ROOT", "n"),
    (r"\g'00'", "the ROOT", "n"),
]

for spelling, target, verdict in ROOT_TARGETS:
    if verdict == "m":
        cases = [m("aabb"), m("ab"), m("aaabbb"), n("aab"), n("abb")]
    else:
        cases = [n("aabb"), m("ab"), n("aaabbb"), n("aab")]
    F_ROOT.append(B(
        "^(a%s?b)$" % spelling, [R],
        "extract 2.4/2.4a: %s targets %s. The ROOT rows re-run '^' and '$' "
        "TOO, so the inner '^' fails at offset 1 and 'aabb' is a nomatch; "
        "the group-1 rows have the anchors OUTSIDE what they call and "
        "match. This is the module's most counter-intuitive fact and the "
        "one an implementer is most likely to get wrong in the same "
        "direction a promise-first author might."
        % (spelling, target),
        cases))

F_ROOT.append(B(
    "(a(?R)?b)", [R],
    "extract 2.4 last row: with the anchors GONE, the very same (?R) "
    "reaches depth 2 and matches. The contrast with the anchored (?R) "
    "block above is the whole fact -- neither cell alone shows it.",
    [m("aabb"), m("ab"), m("aaabbb"), n("ba")]))

F_ROOT.append(B(
    r"(a\g<0>?b)", [R],
    "\\g<0> is a synonym for (?R), not 'call group 0': unanchored it "
    "recurses exactly as (?R) does.",
    [m("aabb"), m("ab")]))

F_ROOT.append(B(
    r"(a\g'00'?b)", [R],
    "…and so does the quoted double-zero spelling.",
    [m("aabb"), m("ab")]))

F_ROOT.append(B(
    "^(a(?1)?b)(?R)?$", [R],
    "a ROOT call and a GROUP call in ONE pattern: a lowering that "
    "collapsed the two targets would have to answer this wrong. The (?R) "
    "here re-runs the anchored whole pattern from the current position, "
    "so it can never contribute.",
    [m("aabb"), m("ab"), n("abab")]))

F_ROOT.append(B(
    "^x(?0)?y$", [R],
    "the root call under '?', with the anchors: PCRE2 re-runs '^x(?0)?y$' "
    "from the inner position, where '^' cannot hold.",
    [m("xy"), n("xxyy")]))

F_ROOT.append(B(
    "^a(?R)*b$", [R],
    "extract 3.4(f): (?R) under a quantifier is an ordinary repeatable "
    "item; its interaction with the anchors is unchanged by the "
    "quantifier.",
    [m("ab"), n("aabb")]))

F_ROOT.append(B(
    "(a(?R)*b)", [R],
    "extract 3.4(f), unanchored: (?R) under '*'.",
    [m("aabb"), m("ab")]))

# ===========================================================================
# FILE 3 -- sr_define.rxt
#   Extract 2.5/2.6 and D71 item 4: (?(DEFINE)...) and (?:X){0} are ONE
#   lowering with TWO spellings. Every block below that exists in one
#   spelling exists in the other, on the same subjects, expecting the same
#   answers -- a corpus exercising only one spelling has not covered the
#   other, which the ruling says in as many words.
# ===========================================================================
F_DEFINE = []

DEF11 = ["foo-bar", "fo-bar", "foofoo-bar", "f-bar", "-bar", "foo", "bar",
         "fooo-bar", "", "foo-baz", "fo"]

F_DEFINE.append(B(
    "^(?(DEFINE)(?<w>fo+))(?&w)-bar$", [R, NG],
    "extract 2.5: the DEFINE container's body never runs where it is "
    "written and exists only to be called. Note g1 UNSET on the match -- "
    "the declaring occurrence contributed nothing.",
    [(None, s, 0) for s in DEF11]))

F_DEFINE.append(B(
    "^(?:(?<w>fo+)){0}(?&w)-bar$", [R, NG],
    "D71 item 4: the SAME PROGRAM as the DEFINE block above, spelled with "
    "a {0}-parked callee. Same subjects, same answers, same unset g1.",
    [(None, s, 0) for s in DEF11]))

F_DEFINE.append(B(
    "^(?!)(?<w>fo+)|^(?&w)-bar$", [R, NG, LA],
    "extract 2.5: the (?!)-guarded-branch spelling -- an EXACT substitute "
    "on all 11 measured subjects. The (?!) kills the declaring branch, the "
    "name is still declared, the call still resolves.",
    [(None, s, 0) for s in DEF11]))

F_DEFINE.append(B(
    "^(?:(?<w>foo))?(?&w)-bar$", [R, NG],
    "extract 2.5 CONTROL: the OPTIONAL group actually RUNS. On the shared "
    "subject list it agrees with DEFINE on nine of eleven and DIVERGES on "
    "'foofoo-bar', which the DEFINE form refuses and this one accepts -- "
    "the group ate a copy. Not an exact substitute.",
    [(None, s, 0) for s in DEF11]))

F_DEFINE.append(B(
    "^(?<w>foo)?+(?&w)-bar$", [R, NG, AT],
    "extract 2.5 third substitute: the POSSESSIVE optional consumes and "
    "will not give back, so it fails outright where DEFINE matches -- it "
    "is wrong on the other nine subjects instead.",
    [(None, s, 0) for s in DEF11]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<w>a))(?&w)*b$", [R, NG],
    "the DEFINE/optional difference reduced to ONE PAIR OF BLOCKS whose "
    "spans are IDENTICAL and whose captures are not: here g1 is UNSET on "
    "every subject, because the declaring occurrence never ran.",
    [m("ab"), m("aab"), m("aaab"), m("b")]))

F_DEFINE.append(B(
    "^(?:(?<w>a))?(?&w)*b$", [R, NG],
    "…and here g1 is (0,1), because the optional group DID run. Same "
    "spans, different captures. A span-only corpus cannot tell these two "
    "blocks apart at all, which is exactly why every match case in this "
    "corpus carries a g line for every slot.",
    [m("ab"), m("aab"), m("aaab"), m("b")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<a>x)(?<b>y))(?&a)(?&b)(?&a)$", [R, NG],
    "TWO definitions in ONE DEFINE container (a concatenation, not two "
    "branches -- two branches is PCRE2's own error 154, tested in "
    "sr_refusals.rxt), each called, one of them twice.",
    [m("xyx"), n("xy"), n("xyy")]))

F_DEFINE.append(B(
    "^(?:(?<a>x)(?<b>y)){0}(?&a)(?&b)(?&a)$", [R, NG],
    "the {0} spelling of the block above -- D71 item 4's 'one lowering, "
    "two spellings' again, this time with two definitions.",
    [m("xyx"), n("xy"), n("xyy")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>ab))(?&g)(?&g)(?&g)$", [R, NG],
    "ONE callee called THREE times in sequence -- a lowering that emitted "
    "the body once per call site rather than calling it would still pass "
    "this, but a lowering that mis-scoped the FOLLOW after a return would "
    "not.",
    [m("ababab"), n("abab"), n("abababab")]))

# --- quantified calls and the empty-body guard ---------------------------
F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>a?))(?&g)*$", [R, NG],
    "extract 2.6: a NULLABLE callee under '*' TERMINATES. A lowering "
    "without an empty-body guard loops here forever.",
    [m("aaa"), m(""), m("a")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>))(?&g)*$", [R, NG],
    "extract 2.6: an EMPTY callee under '*' terminates too -- the sharper "
    "half of the guard, since the body cannot even consume on its first "
    "iteration.",
    [m(""), n("a")]))

F_DEFINE.append(B(
    "^(?:(?<g>)){0}(?&g)*$", [R, NG],
    "the empty callee, {0} spelling.",
    [m(""), n("a")]))

F_DEFINE.append(B(
    "^(a?)(?1)*$", [R],
    "extract 2.6: a nullable NUMBERED callee under '*', with its capture. "
    "g1 is the LEXICAL run's span, not any call's.",
    [m("aaa"), m(""), m("a")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>ab))(?&g){2}$", [R, NG],
    "extract 2.6: a bounded repeat of a call.",
    [m("abab"), n("ab"), n("ababab")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>ab))(?&g)+$", [R, NG],
    "extract 2.6: an unbounded repeat of a call.",
    [m("ab"), m("ababab"), n("aba"), n("")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>ab))(?&g)*$", [R, NG],
    "…and '*', which must accept the empty subject.",
    [m(""), m("abab")]))

F_DEFINE.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?&g){2}c$", [R, NG],
    "a bounded repeat of a callee that has a CHOICE POINT: the second "
    "iteration has to be able to take the other branch.",
    [m("aabc"), m("abac"), m("aac"), n("abc")]))

# ===========================================================================
# FILE 4 -- sr_captures.rxt
#   Extract 3.1: a subroutine call is CAPTURE-TRANSPARENT. The design's own
#   evidence for this is a live callout inside the called body; a blinded
#   corpus has no callout, so every cell here is built the way the extract
#   asks for instead -- so that the DURING-call value would LEAK into the
#   final answer if the return did not put the old one back. Every match
#   case carries a g line for every slot, because a span-only cell cannot
#   see a restore bug at all.
# ===========================================================================
F_CAPS = []

F_CAPS.append(B(
    "^((a))(?1)$", [R],
    "extract 3.1 C2 without a callout. The call re-runs group 1, which "
    "re-runs group 2 and writes g2=(1,2). The RETURN undoes that: the "
    "answer is g2=(0,1). A lowering that never restored would report "
    "(1,2) here and the g line catches it.",
    [m("aa"), n("a"), n("aaa")]))

F_CAPS.append(B(
    r"^((a|b))(?1)\2$", [R, BR],
    "THE restore discriminator that needs no callout: the call writes "
    "g2='b' while it runs, then returns; the \\2 AFTER the return reads "
    "whatever survived. 'aba' matches only if the OLD value ('a') came "
    "back; 'abb' matches only if the callee's value ('b') leaked. The two "
    "subjects together pin the direction -- one alone does not.",
    [m("aba"), n("abb"), m("aaa"), m("bab"), n("baa")]))

F_CAPS.append(B(
    r"^((a|bb))(?1)\2$", [R, BR],
    "the same discriminator with UNEQUAL branch widths, so a leak would "
    "also move the match END and not merely change a capture.",
    [m("abba"), n("abbbb"), m("aaa")]))

F_CAPS.append(B(
    "^((a)(?1)?(b))$", [R],
    "extract 3.1 C3, AT DEPTH: during the call the inner level's own "
    "g2/g3 are visible, then restored, then the OUTERMOST level's own "
    "values are written last and are the final answer. A restore bug that "
    "only shows at depth >= 2 is reachable here and not in a one-level "
    "cell.",
    [m("aabb"), m("ab"), m("aaabbb"), n("aab")]))

F_CAPS.append(B(
    r"^(a)(b\1)(?2)$", [R, BR],
    "extract 3.1 C5: THE CALLEE INHERITS THE CALLER'S CAPTURES. Group 2's "
    "body is 'b\\1'; the call re-ran it and \\1 was still 'a'. A lowering "
    "that gave the call a FRESH capture environment answers this wrong.",
    [m("ababa"), n("abab"), n("aba")]))

F_CAPS.append(B(
    r"^(a)(b\1)(?2)$#CONTROL", [R, BR],
    "PLACEHOLDER -- replaced below.",
    []))
F_CAPS.pop()

F_CAPS.append(B(
    r"^((a|b)(?1)?\2)$", [R, BR],
    "extract 3.1 C3 second row: PER LEVEL. Each level's \\2 refers to "
    "THAT level's capture, so 'abba' matches and 'abab' does not -- the "
    "inner level chose 'b' and had to close on 'b'.",
    [m("abba"), n("abab"), m("aa"), n("ab")]))

F_CAPS.append(B(
    "^(?:((a))(?1)x|(?1)y)$", [R],
    "extract 3.1 C4: AFTER A FAILED CALL, NOTHING SURVIVES. On 'ay' the "
    "first branch's call ran, its body wrote g2, and then the branch "
    "died; the second branch's call ran and succeeded. Both g1 and g2 "
    "must come back UNSET -- a lowering that restored too little leaves a "
    "stale span here.",
    [m("ay"), m("aax"), n("axy")]))

F_CAPS.append(B(
    "^((a)(?1)?(b))(?1)$", [R],
    "a depth-nested callee called AGAIN from outside, so the final answer "
    "is written by the outer lexical run and then a whole second call "
    "tree runs and returns over the top of it.",
    [m("abab"), m("aabbab"), n("ab")]))

F_CAPS.append(B(
    "^(?(DEFINE)(?<g>(?<h>a)(?&g)?(?<i>b)))(?&g)$", [R, NG],
    "the same depth-nesting entirely inside a DEFINE, where NO group has "
    "a lexical run at all: every capture in the final answer was written "
    "by a call and survived its return.",
    [m("ab"), m("aabb"), m("aaabbb"), n("aab")]))

F_CAPS.append(B(
    "^(x)?(?:(a(?2)?b)){0}(?2)$", [R],
    "extract 3.5 Z0 second row: a RECURSIVE callee parked under {0}, "
    "reached only by call, with an unset optional group beside it. g1 and "
    "g2 must BOTH be unset in the answer.",
    [m("aabb"), m("ab"), n("aab")]))

F_CAPS.append(B(
    r"^(a)(?1)(?<=(a))\1$", [R, BR, LA],
    "a call, then a lookbehind that writes a capture, then a reference: "
    "three writers to the slot space in one pattern, one of them inside a "
    "call.",
    [m("aaa"), n("aa")]))

# ===========================================================================
# FILE 5 -- sr_atomicity.rxt
#   Extract 3.2: calls are BACKTRACKABLE on 10.46. Every positive row is
#   paired with the atomic CONTROL that must answer the OPPOSITE way -- the
#   extract is explicit that a corpus with only the positives has not
#   established atomicity at all, since a lowering that pops the call frame
#   on return makes the positives read exactly like the controls.
# ===========================================================================
F_ATOM = []

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?&g)c$", [R, NG],
    "extract 3.2 row 1: the ISOLATED backtracking cell. The retriable "
    "body sits where ONLY the call can reach it, so the lexical group "
    "cannot retry on its behalf. BACKTRACKABLE -- atomic would be "
    "nomatch.",
    [m("abc"), m("ac"), n("abbc")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>(?>a|ab)))(?&g)c$", [R, NG, AT],
    "ATOMIC CONTROL 1 for the row above: an atomic callee BODY. Must be "
    "the OPPOSITE answer on 'abc'. The contrast is the fact.",
    [n("abc"), m("ac")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?>(?&g))c$", [R, NG, AT],
    "ATOMIC CONTROL 2: an atomic wrapper on the CALL SITE.",
    [n("abc"), m("ac")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?&g)++c$", [R, NG, AT],
    "ATOMIC CONTROL 3: a POSSESSIVE quantifier on the call.",
    [n("abc"), m("ac")]))

F_ATOM.append(B(
    "^(?!)(?<g>a|ab)|^(?&g)c$", [R, NG, LA],
    "extract 3.2 row 2: the same backtracking fact WITHOUT DEFINE, in "
    "case DEFINE is special in the lowering.",
    [m("abc"), m("ac")]))

F_ATOM.append(B(
    "^(?:(?<g>a|ab)){0}(?&g)c$", [R, NG],
    "…and again with the {0}-parked spelling. Three spellings of one "
    "fact, because D71 item 4 makes two of them the same program and the "
    "third an exact substitute.",
    [m("abc"), m("ac")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a+))(?&g)ab$", [R, NG],
    "extract 3.2 row 3: a QUANTIFIER, not an alternation, as the callee's "
    "choice point -- 'a+' has to give back two characters across the "
    "return.",
    [m("aaab"), m("aab"), m("aaaab"), n("ab")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a+))(?>(?&g))ab$", [R, NG, AT],
    "ATOMIC CONTROL 4: an atomic wrapper around a GIVING-BACK callee. "
    "Opposite answer to the row above.",
    [n("aaab"), n("aab")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a+))(?&g)++ab$", [R, NG, AT],
    "the possessive form of control 4.",
    [n("aaab")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a{1,3}))(?&g)aa$", [R, NG],
    "extract 3.2 row 4: a BOUNDED repeat as the callee's choice point.",
    [m("aaa"), m("aaaa"), n("aa")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a{1,3}))(?>(?&g))aa$", [R, NG, AT],
    "…and its atomic control.",
    [n("aaa"), m("aaaaa")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>a(?&g)?b|x|xy))(?&g)$", [R, NG],
    "extract 3.2's sharpest cell: IT RETRIES ACROSS A RETURN, AT DEPTH. "
    "The retreat has to re-enter the INNER call after the OUTER one has "
    "already returned. A lowering that CUT at the return fails exactly "
    "here and nowhere shallower.",
    [m("axyb"), m("axb"), m("aaxbb"), n("axyyb")]))

F_ATOM.append(B(
    "^(?(DEFINE)(?<g>(?>a(?&g)?b|x|xy)))(?&g)$", [R, NG, AT],
    "the atomic control for the retry-across-a-return cell: with the "
    "callee body made atomic, the inner retry is cut off.",
    [n("axyb"), m("axb")]))

F_ATOM.append(B(
    "^(a|ab)(?1)c$", [R],
    "extract 3.2's own WARNING CELL, kept deliberately: this is the "
    "OBVIOUS test for atomicity and it does NOT isolate it -- it matches "
    "under both hypotheses because the LEXICAL group can retry too. It is "
    "here so the corpus records that it was considered and is not "
    "mistaken for the isolated cells above.",
    [m("ababc"), m("aabc"), m("abac")]))

# ===========================================================================
# FILE 6 -- sr_wrapped.rxt
#   Extract 3.5: A CALL'S TARGET MAY LIVE INSIDE A LOOKAROUND OR AN ATOMIC
#   GROUP. A called group runs as its OWN region -- forward, consuming,
#   cut-free, back-step-free -- WHATEVER its lexical wrapper is. This is the
#   family the extract calls the most implementer-hostile in the module: an
#   obvious lowering gets every row wrong the same way, by letting the
#   wrapper's semantics travel with the group.
# ===========================================================================
F_WRAP = []

F_WRAP.append(B(
    "^ab(?<=(ab))(?1)$", [R, LA],
    "extract 3.5 W1: the call CONSUMES, though group 1's lexical home is "
    "a LOOKBEHIND -- normally zero-width, and it rewinds. Run forward "
    "through the call, it eats two characters.",
    [m("abab"), n("ab"), n("ababab")]))

F_WRAP.append(B(
    "^(?!(z|zy))x(?1)c$", [R, LA],
    "extract 3.5 W2: the call RETRIES into 'zy', though the group's home "
    "is a NEGATIVE LOOKAHEAD -- normally cut on success with the whole "
    "region discarded. 'xzyc' needs the second alternative; 'xzc' is the "
    "control where the first suffices.",
    [m("xzyc"), m("xzc"), n("xc")]))

F_WRAP.append(B(
    "^(?>(a|ab))z(?1)c$", [R, AT],
    "extract 3.5 W3: the call CAN GIVE BACK 'a' and take 'ab' on retry, "
    "though the group's home is ATOMIC. The atomicity belongs to the "
    "(?>...) OCCURRENCE, not to group 1.",
    [m("azabc"), m("azac"), n("abzabc")]))

F_WRAP.append(B(
    "^(?>(a|ab))z(?:a|ab)c$", [R, AT],
    "extract 3.5 W3's CONTROL: the callee written INLINE with the atomic "
    "wrapper kept. Same answer as W3 -- which is what says W3's answer is "
    "about the wrapper not travelling, and not about the alternation.",
    [m("azabc"), m("azac")]))

F_WRAP.append(B(
    "^(?:((?>a|ab))){0}(?1)z$", [R, AT],
    "extract 3.5 Z0 third row -- the contrast that makes W3 sharp: here "
    "atomicity DOES travel with the callee, because the (?> is written "
    "INSIDE the group. 'abz' must FAIL where W3's shape succeeds.",
    [m("az"), n("abz")]))

F_WRAP.append(B(
    "^(?:(?<g>a|ab)){0}(?&g)c$", [R, NG],
    "extract 3.5 Z0 row 1: the callee is defined inside X{0}, a region a "
    "lowering emits no code for lexically. The call still reaches it, and "
    "the callee still has its choice point.",
    [m("abc"), m("ac")]))

F_WRAP.append(B(
    "^(?=(a|ab))..(?1)$", [R, LA],
    "extract 3.5 W5: a POSITIVE lookahead as the lexical home.",
    [m("abab"), m("aba"), n("ab")]))

F_WRAP.append(B(
    "^((?=(b))|a)+(?2)$", [R, LA],
    "extract 3.5 W5 second row: a lookahead nested inside a QUANTIFIED "
    "group -- the wrapper is two levels up and repeated.",
    [m("ab"), n("aa")]))

F_WRAP.append(B(
    "^(?<!(xy))ab(?1)$", [R, LA],
    "a NEGATIVE LOOKBEHIND as the lexical home -- the fourth wrapper "
    "kind, which extract 3.5 does not itself list. A negative lookbehind "
    "never leaves its group set, and the call must still run the body "
    "forward and consuming.",
    [m("abxy"), n("ab")]))

F_WRAP.append(B(
    "^(?(DEFINE)(?<g>ab))(?=(?&g))(?&g)$", [R, NG, LA],
    "the two directions COMPOSED in one pattern: a call written INSIDE a "
    "lookahead (extract 3.4(e)) to a callee parked in a DEFINE, and the "
    "same callee called again outside. A mis-scoped follow shows up as "
    "the lookahead's rewind eating the second call or vice versa.",
    [m("ab"), n("a"), n("abab")]))

F_WRAP.append(B(
    "^ab(?<=(a(?1)?b))$", [R, LA],
    "a RECURSIVE group whose lexical home is a lookbehind, called from "
    "INSIDE that same lookbehind: the wrapped-target family and extract "
    "3.4(d)'s recursive-callee refusal meeting in one pattern. The "
    "refusal wins on both sides -- a recursive callee has no bounded "
    "width, whichever direction you reach it from. Existence only.",
    perr="both"))

# ===========================================================================
# FILE 7 -- sr_interactions.rxt
#   Extract 3.4: \K, duplicate names, calls inside lookarounds and atomic
#   groups, and \G/\A/\z against a non-zero startpos. The ms/ns cells are
#   here because 3.4(e2) is entirely about startpos and a startpos-0-only
#   corpus cannot exercise it at all.
# ===========================================================================
F_INTER = []

# --- (b) \K survives the return -----------------------------------------
F_INTER.append(B(
    r"^(a\Kb)(?1)$", [R, AS],
    "extract 3.4(b): \\K inside a CALLED body MOVES the reported match "
    "start, and the last one executed on the successful path wins. \\K is "
    "a PATH fact, not capture state, and unlike every capture it is NOT "
    "undone by the return -- the reported start lands at 3, inside the "
    "call's own text.",
    [m("abab"), n("ab")]))

F_INTER.append(B(
    r"^(?(DEFINE)(?<g>a\Kb))(?&g)$", [R, NG, AS],
    "extract 3.4(b) row 2: the \\K fires in a body that has NO lexical "
    "run at all, and still moves the start.",
    [m("ab"), n("a")]))

F_INTER.append(B(
    r"^(a(?1)?\Kb)$", [R, AS],
    "extract 3.4(b) row 3: \\K AT DEPTH. The last \\K executed on the "
    "successful path wins, so the start is 3 and not 1 -- a lowering that "
    "restored TOO MUCH on return (undoing \\K along with the captures) "
    "reports 1 here.",
    [m("aabb"), m("ab")]))

F_INTER.append(B(
    r"^(?(DEFINE)(?<g>a\Kb))(?=(?&g))ab$", [R, NG, AS, LA],
    "MEASURED, and it REFUTES the reading the extract's own 3.4(b) prose "
    "invites: PCRE2's error-199 rule is about the LEXICAL nesting of the "
    "\\K, and the \\K here is lexically inside a DEFINE, not inside the "
    "lookahead -- so the pattern COMPILES, the call runs the \\K from "
    "inside the lookahead, and the reported start MOVES to 1 even though "
    "the lookahead itself is zero-width and rewinds. The extract asked "
    "for this to be measured rather than assumed; this is the "
    "measurement.",
    [m("ab"), n("ba")]))

F_INTER.append(B(
    r"^(?(DEFINE)(?<g>a\Kb))ab(?<=(?&g))$", [R, NG, AS, LA],
    "the same refutation through a LOOKBEHIND: a \\K reached by a call "
    "from inside a lookbehind compiles and moves the reported start out "
    "of the assertion.",
    [m("ab")]))

F_INTER.append(B(
    r"^(?:(a\Kb)){0}(?=(?1))ab$", [R, AS, LA],
    "…and through a NUMBERED call from a {0}-parked body, so the fact is "
    "not an artefact of DEFINE or of by-name resolution.",
    [m("ab")]))

F_INTER.append(B(
    r"^(?=a\Kb)ab$", [R, AS, LA],
    "the CONTROL for the three blocks above, and the reason they are "
    "surprising: written DIRECTLY inside the lookaround the same \\K is "
    "refused (PCRE2 error 199). Refusal tested for EXISTENCE only.",
    perr="both"))

F_INTER.append(B(
    r"^(?(DEFINE)(?<g>b))a\K(?=(?&g))b$", [R, NG, AS, LA],
    "the mirror: the \\K is outside, the CALL is inside the lookahead. "
    "Ordinary, and here to keep the three refutation blocks honest.",
    [m("ab")]))

# --- (c) duplicate names: a CALL and a REFERENCE resolve DIFFERENTLY -----
DUP_CALL = ["(?&a)", "(?P>a)", r"\g<a>", r"\g'a'"]
for sp in DUP_CALL:
    F_INTER.append(B(
        "^(?J)(?:(?<a>x)|q)(?<a>y)%s$" % sp, [R, NG, MO, BR],
        "extract 3.4(c): a CALL by name to a DUPLICATED name runs the "
        "FIRST DECLARATION's pattern, STATICALLY, whether or not that "
        "group is set. 'qyx' matches, 'qyy' does not -- the exact "
        "opposite of the reference blocks below. Spelling %s." % sp,
        [m("qyx"), n("qyy")]))

for sp, feats in [(r"\k<a>", [R, NG, BR, MO]), ("(?P=a)", [R, NG, BR, MO]),
                  (r"\k'a'", [R, NG, BR, MO]), (r"\g{a}", [R, NG, BR, MO])]:
    F_INTER.append(B(
        "^(?J)(?:(?<a>x)|q)(?<a>y)%s$" % sp, feats,
        "extract 3.4(c) REFERENCE half: a backreference by name reads the "
        "first SET member of the run, DYNAMICALLY. 'qyy' matches and "
        "'qyx' does not. These two rows on the SAME pattern shape, "
        "expecting DIFFERENT answers, are the discriminating test -- a "
        "corpus with only one of the two spellings cannot catch a "
        "lowering that resolved a call the way it resolves a reference. "
        "Spelling %s." % sp,
        [n("qyx"), m("qyy")]))

F_INTER.append(B(
    "^(?J)(?<a>x)(q)(?<a>y)(?&a)z$", [R, NG, MO, BR],
    "extract 3.4(c) last row: a call does NOT retry into later "
    "same-named members. 'xqyxz' matches, 'xqyyz' does not.",
    [m("xqyxz"), n("xqyyz")]))

# --- (d) a call inside a LOOKBEHIND, and the [DD-14.LB] amendment --------
F_INTER.append(B(
    "^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$", [R, NG, LA],
    "extract 3.4(d) row 1 and the amendment's first bullet: an ACYCLIC, "
    "FIXED-PER-BRANCH callee composes and SHIPS. PCRE2 computes the "
    "callee's width THROUGH the call; pcrec's stricter lookbehind subset "
    "accepts this one because the callee's one branch is fixed at 2.",
    [m("ab"), n("aab")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>ab))(?(DEFINE)(?<h>(?&g)))ab(?<=(?&h))$", [R, NG, LA],
    "the amendment's 'two-hop acyclic call chain': the lookbehind calls "
    "h, which calls g. The width has to be carried through TWO calls.",
    [m("ab"), n("aab")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>ab))(?(DEFINE)(?<h>cd))abcd(?<=(?&g)|(?&h))$",
    [R, NG, LA],
    "the amendment's 'alternation of calls written at the lookbehind "
    "body's own top level': two branches, each a single call, each "
    "individually fixed-width.",
    [m("abcd"), n("abc")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>ab))(?(DEFINE)(?<h>cde))abcde(?<=(?&g)|(?&h))$",
    [R, NG, LA],
    "the same, with the two branches at DIFFERENT fixed widths (2 and 3). "
    "Each top-level branch is still individually fixed, which is the rule "
    "the amendment names -- so this must be accepted while the "
    "single-branch variable-width block below is refused. The pair is the "
    "point; either alone would look arbitrary.",
    [m("abcde")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$", [R, NG, LA],
    "extract 3.4(d) row 2 / the amendment's SECOND bullet: a single call "
    "that is itself the lookbehind's ONE top-level branch, whose callee "
    "has an alternation of DIFFERENT fixed widths (1..2). PCRE2 ACCEPTS "
    "this and matches (0,2); pcrec REFUSES it by ruling, because from the "
    "lookbehind body's own point of view this is one branch of variable "
    "width -- the (?<=(a|bc))x shape module lookaround already refuses. "
    "Being reached through a call does not change that. Existence only.",
    perr="pcrec"))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a(?&g)?b))aabb(?<=(?&g))$", [R, NG, LA],
    "extract 3.4(d) row 5 / the amendment's THIRD bullet: a RECURSIVE "
    "callee inside a lookbehind is REFUSED ON BOTH SIDES -- PCRE2's own "
    "error 125, and pcrec refuses it too.",
    perr="both"))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a+))aa(?<=(?&g))$", [R, NG, LA],
    "extract 3.4(d) row 3: an UNBOUNDED callee width. Refused on both "
    "sides (PCRE2 error 125).",
    perr="both"))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a{1,300}))aaaa(?<=(?&g))$", [R, NG, LA],
    "extract 3.4(d) row 4: a callee whose width is BOUNDED but too long "
    "(PCRE2 error 200). Refused on both sides, for whatever each side's "
    "own reason is -- existence only, never wording (D26).",
    perr="both"))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>(?<=x)ab))x(?&g)$", [R, NG, LA],
    "the OTHER direction: a LOOKBEHIND INSIDE THE CALLEE, looking back at "
    "text the CALLER consumed. A call changes neither the subject nor the "
    "position, so the lookbehind sees the caller's 'x'.",
    [m("xab"), n("yab")]))

# --- (e) a call inside a lookahead or an atomic group --------------------
F_INTER.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?=(?&g))ab$", [R, NG, LA],
    "extract 3.4(e): a call inside a POSITIVE lookahead behaves as the "
    "construct it is wrapped in -- zero-width, and it rewinds.",
    [m("ab"), n("ba")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?!(?&g))xy$", [R, NG, LA],
    "…inside a NEGATIVE lookahead.",
    [m("xy")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?!(?&g))ab$", [R, NG, LA],
    "…and the control that shows the negative lookahead really fired.",
    [n("ab")]))

F_INTER.append(B(
    "^(?(DEFINE)(?<g>a|ab))(?>(?&g))b?c$", [R, NG, AT],
    "extract 3.4(e): inside an ATOMIC group the call's retries are "
    "suppressed -- the callee takes 'a', cannot give it back, and the "
    "'b?' outside the wrapper has to absorb the 'b'.",
    [m("abc"), m("ac")]))

# --- (e2) \G, \A, \z, and a NON-ZERO startpos ---------------------------
F_INTER.append(B(
    r"(?(DEFINE)(?<g>\Ga))(?&g)", [R, NG, AS],
    "extract 3.4(e2): \\G is a test against STARTPOS, and a call changes "
    "neither the subject nor startpos. At startpos 0 the 'x' blocks it; "
    "at startpos 1 it holds. These two cases differ ONLY in startpos -- a "
    "startpos-0-only corpus cannot exercise this at all.",
    [n("xa"), ('m', "xa", 1), ('m', "xaa", 1), ('n', "xa", 0)]))

F_INTER.append(B(
    r"(?(DEFINE)(?<g>\Aa))x?(?&g)", [R, NG, AS],
    "extract 3.4(e2): \\A is a test against the SUBJECT's absolute start, "
    "which startpos does not move. Nomatch at either startpos.",
    [n("xa"), ('n', "xa", 1)]))

F_INTER.append(B(
    r"(?(DEFINE)(?<g>a\z))x(?&g)", [R, NG, AS],
    "extract 3.4(e2): \\z inside a callee tests the subject's absolute "
    "end.",
    [m("xa"), ('m', "yxa", 1)]))

F_INTER.append(B(
    r"(?(DEFINE)(?<g>a\z))x(?&g)b", [R, NG, AS],
    "…and the control: with a 'b' after the call, the callee's \\z can "
    "never be satisfied.",
    [n("xab")]))

F_INTER.append(B(
    "^(a|b)(?1)$", [R],
    "STARTPOS vs '^': the caret anchors to ABSOLUTE offset 0 regardless "
    "of startpos, so this call-bearing pattern cannot match from "
    "startpos 1 even though the text there would fit.",
    [('n', "xab", 1), ('m', "ab", 0)]))

F_INTER.append(B(
    "(a|b)(?1)", [R],
    "the unanchored control for the block above: the same call, the same "
    "subject, the same startpos, and it DOES match -- so the nomatch "
    "above is the anchor and not the call.",
    [('m', "xab", 1), ('m', "xab", 0)]))

F_INTER.append(B(
    "(a(?1)?b)", [R],
    "a RECURSIVE call from a non-zero startpos.",
    [('m', "xaabb", 1), ('m', "xaabb", 0)]))

F_INTER.append(B(
    r"(?(DEFINE)(?<g>a\Kb))(?&g)", [R, NG, AS],
    "\\K through a call from a non-zero startpos -- the reported start "
    "moves relative to where the call actually ran, not to startpos.",
    [('m', "xab", 1)]))

F_INTER.append(B(
    r"(?(DEFINE)(?<g>\bab))(?&g)", [R, NG, AS],
    "\\b inside a callee looks at the real neighbouring bytes, which "
    "startpos does not hide: at startpos 1 of 'xab' the boundary fails, "
    "at startpos 2 of 'x ab' it holds.",
    [('n', "xab", 1), ('m', "x ab", 2)]))

F_INTER.append(B(
    "(?<=x)(a|b)(?1)", [R, LA],
    "a lookbehind BEFORE a call, exercised at two startpos values: the "
    "lookbehind may read text before startpos.",
    [('m', "xab", 1), ('m', "xab", 0)]))

# ===========================================================================
# FILE 8 -- sr_depth.rxt
#   Extract 3.3 and 5. Left recursion has NO compile-time refusal: the guard
#   is at match time. On pcrec that guard is a DEPTH-CAPACITY give-up, and
#   `gu frames "<subject>"` is how a corpus expects it. The `m` cells below
#   the ceiling and the `gu` cells above it are the same fact from both
#   sides; either alone would let a lowering that simply gives up early, or
#   one that never gives up at all, pass.
#
#   The give-up boundary was located by COMPILING AND RUNNING the cell -- an
#   EXISTENCE question the extract explicitly permits ("you MAY compile a
#   cell and run it to learn whether it gives up, never to derive a match
#   expectation"). Every match expectation here is still libpcre2's.
# ===========================================================================
CEIL_OK = 342      # ^(a(?1)?b)$ still MATCHES at this n (684-byte subject)
CEIL_GU = 343      # …and gives up at this one (686-byte subject)
F_DEPTH = []

F_DEPTH.append(B(
    "^(a(?1)?b)$", [R],
    "extract 5's named ceiling shape, BELOW the ceiling. n=342 is the "
    "largest depth that still answers; n=300 is the same fact with "
    "margin. MEASURED on the compiler as an existence question; the spans "
    "are libpcre2's.",
    [m("ab"), m("aabb"), m("a" * 8 + "b" * 8),
     m("a" * 300 + "b" * 300), m("a" * CEIL_OK + "b" * CEIL_OK),
     n("a" * 4 + "b" * 3)],
    gu=[("frames", "a" * CEIL_GU + "b" * CEIL_GU),
        ("frames", "a" * 500 + "b" * 500),
        ("frames", "a" * 2000 + "b" * 2000)], guclass="capacity"))

F_DEPTH.append(B(
    "^(a|(?1)a)$", [R],
    "extract 3.3's LOAD-BEARING cell. 199 nested recursions, every one "
    "entered at offset 0, and PCRE2 MATCHES -- which refutes the naive "
    "reading of its own -52 message ('refuse a recursion at a position an "
    "ancestor already occupies' would refuse this very cell). A LEFT-"
    "recursive shape that must not be answered by giving up.",
    [m("a" * 10), m("a" * 100), m("a" * 199), m("a" * 200), m("a" * 342)],
    gu=[("frames", "a" * 10 + "b"), ("frames", "a" * 40 + "b")]))

F_DEPTH.append(B(
    "(a|(?1)a)", [R],
    "the same shape UNANCHORED, where the leftmost answer is one "
    "character and no depth is needed at all.",
    [m("aaa"), m("a"), n("bbb")]))

for lr in ["((?1)a)", "((?1)?a)", "((?1)*a)", "(?R)a"]:
    F_DEPTH.append(B(
        lr, [R],
        "extract 3.3: PCRE2 refuses NO left-recursive shape at compile "
        "time, and neither may pcrec -- the guard is entirely at match "
        "time. The n cases are subjects on which libpcre2 reaches a "
        "DEFINITE nomatch without ever recursing (there is no 'a' to "
        "start on), so they are ordinary expectations; the gu cases are "
        "subjects on which libpcre2 itself declines with rc -52 and the "
        "only assertion available is that pcrec declines too rather than "
        "answering wrong.",
        [n("b"), n("")],
        gu=[("frames", "aaa"), ("frames", "aaaaaa")]))

# THE SHAPE THAT SEPARATES "DECLINES" FROM "CONCLUDES". On (a|(?1)a)b
# libpcre2 reaches a definite NOMATCH on every subject that does not match,
# and a definite MATCH on the one that does -- it never once returns -52.
# Every case below is therefore an ordinary, fully oracle-backed
# expectation, with no give-up anywhere in the block. It is in the corpus
# because a lowering that answers a left-recursive shape only when the
# answer is YES, and exhausts its frames whenever the answer is NO, passes
# every gu cell in this file and fails here.
for tail in ["b", "c"]:
    F_DEPTH.append(B(
        "(a|(?1)a)%s" % tail, [R],
        "a left-recursive callee followed by a literal %r. libpcre2 "
        "CONCLUDES on every one of these subjects -- match on 'a%s' "
        "nomatch on the rest -- so there is no give-up to expect and none "
        "is written. The nomatch cases are the load-bearing ones: "
        "concluding NO on a left-recursive shape is harder than "
        "concluding YES, and only the nomatch cases ask for it."
        % (tail, tail),
        [n("a"), n("aa"), n("aaa"), n("b"), n(""),
         m("a" + tail)]))

for q in ["(?R)*", "(?R)?", "(?R){0,2}"]:
    F_DEPTH.append(B(
        "^%s$" % q, [R],
        "extract 2.6/3.4(f): ^%s$ is a DEPTH-CAPACITY give-up cell, not a "
        "match/nomatch guess -- PCRE2 answers rc -52 and pcrec gives up. "
        "Written as a gu directive precisely because guessing 'matches "
        "the empty string' is the plausible wrong answer." % q,
        gu=[("frames", ""), ("frames", "ab")]))

F_DEPTH.append(B(
    "^(?(DEFINE)(?<g>a(?&g)?b))(?&g)$", [R, NG],
    "the ceiling shape again with the callee parked in a DEFINE, so the "
    "recursion is reached ONLY through calls. Below the ceiling it "
    "matches; the gu cells check that this spelling gives up too rather "
    "than diverging.",
    [m("ab"), m("a" * 100 + "b" * 100)],
    gu=[("frames", "a" * 2000 + "b" * 2000)], guclass="capacity"))

# ===========================================================================
# FILE 9 -- sr_refusals.rxt
#   Extract 5's flat list, and NOTHING ELSE: this module has no
#   recursion-specific decline beyond these, and the extract says in as
#   many words not to go looking for one. Every block is an EXISTENCE
#   assertion; no diagnostic wording is tested anywhere (D26).
# ===========================================================================
F_REF = []

for z in ["(?-0)", "(?-00)", "(?+0)", "(?+00)", r"\g<-0>", r"\g<+0>",
          r"\g'-0'", r"\g<-00>", r"\g'+00'"]:
    F_REF.append(B(
        "^(a)%s$" % z, [R],
        "extract 5 / 2.4a: a RELATIVE call at value ZERO is refused (%s). "
        "Note this is NOT the absolute-zero case -- (?0), (?00), \\g<0> "
        "and \\g<00> are all VALID calls to the root, and each has its "
        "own matching block in sr_root.rxt. A lowering that refused both, "
        "or accepted both, would need only one of the two families to "
        "look right." % z,
        perr="both"))

for miss in ["(?2)", "(?9)", "(?12)", r"\g<7>", r"\g'7'", "(?-2)", "(?+2)",
             r"\g<-2>"]:
    F_REF.append(B(
        "^(a)%s$" % miss, [R],
        "extract 5: a call to a group NUMBER that does not exist -- one "
        "group is declared and %s names another. A missing-target compile "
        "error on both sides." % miss,
        perr="both"))

for miss in ["(?&nope)", "(?P>nope)", r"\g<nope>", r"\g'nope'"]:
    F_REF.append(B(
        "^(?<w>a)%s$" % miss, [R, NG],
        "extract 5: a call to a NAME that does not exist (%s)." % miss,
        perr="both"))

F_REF.append(B(
    "^(?(DEFINE)(?<a>x)|(?<b>y))(?&a)$", [R, NG],
    "extract 5: a DEFINE container with TWO OR MORE BRANCHES. PCRE2 "
    "itself refuses this (its own error 154) -- a DEFINE holds exactly "
    "one alternative-free definition -- and pcrec inherits the rule by "
    "construction.",
    perr="both"))

F_REF.append(B(
    "^(?(DEFINE)x|y)a$", [R],
    "the same rule with unnamed branches, so the refusal is about the "
    "BRANCH and not about the names.",
    perr="both"))

# ===========================================================================
# FILE 10 -- sr_email.rxt
#   The RFC 5322 specimen: a real pattern and a hand-factored version of the
#   SAME pattern using {0}-parked named callees and (?&name) calls. Real
#   shape, not invented to embarrass a lowering: many named callees, several
#   called more than once, alternation and bounded repeat inside callee
#   bodies, and a callee (octet) called from inside a {3}-bounded repeat.
#   Both forms carry the SAME subject list and must agree with each other
#   and with libpcre2 on every one.
# ===========================================================================
EMAIL_SUBJ = [
    "user@example.com", "a.b-c@sub.domain.org", '"abc"@example.com',
    "x@[127.0.0.1]", "user@[1.2.3.4]", "a@b.co",
    "!#$%&'*+/=?^_`{|}~-@example.com", "first.last@a-b.example.museum",
    "x@[255.255.255.255]",
    "bad@@example.com", "no-at-sign", "user@-bad.com", "user@example",
    "@example.com", "user@", "x@[999.1.1.1]", "x@[1.2.3]",
    "a..b@example.com", "",
]

F_EMAIL = [
    B(ORIG, [R], "the RFC 5322 address-spec specimen as ordinarily written "
                "-- no calls at all. It is here as the CONTROL: the "
                "factored form below must agree with it on every subject, "
                "and neither the corpus nor the compiler gets to pick "
                "which one is right.",
      [(None, s, 0) for s in EMAIL_SUBJ]),
    B(FACT, [R, NG],
      "the SAME language, hand-factored with (?:(?<name>BODY)){0} callee "
      "parking and (?&name) calls: four named callees, `atom` and `label` "
      "each called more than once, `octet` called from inside a "
      "{3}-bounded repeat. A real-world-shaped exercise of every "
      "mechanism this module ships, on a pattern nobody wrote to catch a "
      "compiler out.",
      [(None, s, 0) for s in EMAIL_SUBJ]),
]

FILES = [
    ("sr_spellings.rxt", "the construct table: every call spelling through "
     "the call/reference discriminator, plus the relative and forward "
     "resolutions (extract 2.1-2.3)", F_SPELLINGS),
    ("sr_root.rxt", "(?R) / (?0) / \\g<0> re-run the WHOLE PATTERN, anchors "
     "included, and the whole-digit-run rule (extract 2.4, 2.4a)", F_ROOT),
    ("sr_define.rxt", "(?(DEFINE)...) and (?:X){0} -- one lowering, two "
     "spellings (D71 item 4) -- and quantified calls (extract 2.5, 2.6)",
     F_DEFINE),
    ("sr_captures.rxt", "a call is CAPTURE-TRANSPARENT: the callee writes "
     "and the return restores (extract 3.1)", F_CAPS),
    ("sr_atomicity.rxt", "calls are BACKTRACKABLE, each positive cell "
     "paired with the atomic control that must answer the opposite way "
     "(extract 3.2)", F_ATOM),
    ("sr_wrapped.rxt", "a called group runs as its OWN region whatever its "
     "lexical wrapper is (extract 3.5)", F_WRAP),
    ("sr_interactions.rxt", "\\K, duplicate names, lookarounds, atomic "
     "groups, and \\G/\\A/\\z against a non-zero startpos (extract 3.4)",
     F_INTER),
    ("sr_depth.rxt", "left recursion has no compile-time refusal; the "
     "guard is a match-time depth-capacity give-up (extract 3.3, 5)",
     F_DEPTH),
    ("sr_refusals.rxt", "extract 5's flat refusal list, existence only, "
     "no wording (D26)", F_REF),
    ("sr_email.rxt", "the RFC 5322 specimen, unfactored and factored, on "
     "one shared subject list", F_EMAIL),
]


# ===========================================================================
# The emitter. Every span and every group span below comes out of the
# oracle; the spec above supplies only patterns, subjects, startpos values
# and the author's INTENT, and a disagreement between intent and oracle is
# a hard abort.
# ===========================================================================
def wrap(text, width=72, prefix="# "):
    words = text.split()
    lines, cur = [], prefix
    for w in words:
        if len(cur) + len(w) + 1 > width and cur != prefix:
            lines.append(cur.rstrip())
            cur = prefix
        cur += w + " "
    if cur.strip() != prefix.strip():
        lines.append(cur.rstrip())
    return lines


def emit_file(fname, blurb, blocks, errors):
    out = []
    out.append("# %s" % fname)
    out += wrap(blurb)
    out.append("#")
    out += wrap("[DD-14.D27] blinded corpus for module `recursion`. GENERATED "
                "by d27/sr_gen.py -- do not hand-edit; edit the spec and "
                "regenerate. Every m/n span and every g line is libpcre2 "
                "10.46's answer through docs/design/subroutines_measurements/"
                "probes/sr_oracle.py (D26: PCRE2 is the source of truth). "
                "Blocks marked `# perl-diverges` are ones where perl 5.40.1 "
                "answers differently; perl's answer is RECORDED in "
                "d27/PERL_DIVERGENCES.md and is never the expectation.")
    out.append("")

    counts = dict(blocks=0, m=0, n=0, ms=0, ns=0, g=0, gu=0, perr=0)

    for b in blocks:
        pat = b["pat"]
        opts = 0
        cerr = sr.compile_err(pat, opts)

        # --- refusal blocks ------------------------------------------------
        if b["perr"] is not None:
            if b["perr"] == "both" and cerr is None:
                errors.append("%s: perr='both' but libpcre2 ACCEPTS %r"
                              % (fname, pat))
                continue
            if b["perr"] == "pcrec" and cerr is not None:
                errors.append("%s: perr='pcrec' but libpcre2 REFUSES %r (%s)"
                              % (fname, pat, cerr[2]))
                continue
            counts["blocks"] += 1
            counts["perr"] += 1
            out += wrap(b["note"])
            if b["perr"] == "pcrec":
                out += wrap("libpcre2 10.46 ACCEPTS this pattern; the "
                            "refusal expected here is pcrec's own, by the "
                            "[DD-14.LB] amendment. Recorded so a reader "
                            "does not mistake it for a PCRE2 fact.")
            if pat in PERL_DIVERGES:
                out.append("# perl-diverges")
            out.append("pattern %s" % pat)
            if b["feats"]:
                out.append("features %s" % ",".join(b["feats"]))
            out.append("perr")
            out.append("")
            continue

        if cerr is not None:
            errors.append("%s: libpcre2 REFUSES %r (%s) but the block "
                          "expects cases" % (fname, pat, cerr[2]))
            continue

        ncap = sr.ngroups(pat, opts) or 0
        counts["blocks"] += 1
        out += wrap(b["note"])
        if pat in PERL_DIVERGES:
            out.append("# perl-diverges")
        out.append("pattern %s" % pat)
        if b["flags"]:
            out.append("flags %s" % b["flags"])
        if b["feats"]:
            out.append("features %s" % ",".join(b["feats"]))
        if b["engine"]:
            out.append("engine %s" % b["engine"])
        for bg in b["budget"]:
            out.append("budget %s" % bg)

        for kind, subj, start in b["cases"]:
            r = sr.search(pat, subj, start, opts)
            got = "n" if r is None else "m"
            if kind is not None and kind != got:
                errors.append("%s: INTENT %s but libpcre2 says %s for %r on "
                              "%r startpos %d" % (fname, kind, got, pat,
                                                  subj, start))
                continue
            if r is None:
                if start:
                    out.append("ns %d %s" % (start, enc(subj)))
                    counts["ns"] += 1
                else:
                    out.append("n %s" % enc(subj))
                    counts["n"] += 1
            else:
                (s, e), groups = r
                if start:
                    out.append("ms %d %s %d %d" % (start, enc(subj), s, e))
                    counts["ms"] += 1
                else:
                    out.append("m %s %d %d" % (enc(subj), s, e))
                    counts["m"] += 1
                for k in range(1, ncap + 1):
                    gsp = groups[k - 1]
                    if gsp is None:
                        out.append("g %d -1 -1" % k)
                    else:
                        out.append("g %d %d %d" % (k, gsp[0], gsp[1]))
                    counts["g"] += 1

        for code, subj in b["gu"]:
            # A gu cell asserts pcrec DECLINES TO ANSWER, which is not a
            # semantic fact libpcre2 can supply -- so the generator asserts
            # what CLASS of give-up the block claims, and refuses a cell
            # whose oracle side does not match that class:
            #
            #   guclass="leftrec"  -- unbounded left recursion. libpcre2
            #       ITSELF declines (rc -52). The two engines agree in kind
            #       and the cell asserts only that pcrec does not answer
            #       wrong.
            #   guclass="capacity" -- the D73 depth ceiling. libpcre2
            #       ANSWERS (given depth); the give-up is pcrec's fixed
            #       backtracking capacity and nothing else. Only the shape
            #       and number the extract names may use this class.
            #
            # Writing `gu frames` for a subject libpcre2 answers with a
            # clean NOMATCH would bake a capacity artifact in as a
            # semantic expectation; that is what this check exists to stop.
            r = sr.match_limits(pat, subj, 0, depth=10000000)
            declined = isinstance(r, tuple) and r and r[0] == "rc"
            if b["guclass"] == "leftrec" and not declined:
                errors.append("%s: gu cell class 'leftrec' but libpcre2 "
                              "ANSWERS %r for %r on a %d-byte subject -- "
                              "pcrec would be giving up where the oracle "
                              "has a definite answer"
                              % (fname, r if r is None else r[0], pat,
                                 len(subj)))
                continue
            if b["guclass"] == "capacity" and declined:
                errors.append("%s: gu cell class 'capacity' but libpcre2 "
                              "ALSO declines (%r) for %r -- that is the "
                              "leftrec class, not a capacity cell"
                              % (r, pat))
                continue
            out.append("gu %s %s" % (code, enc(subj)))
            counts["gu"] += 1
        out.append("")

    return "\n".join(out) + "\n", counts


def main():
    if sr.SELFCHECK:
        print("ORACLE SELFCHECK FAILED:", sr.SELFCHECK)
        return 1
    errors = []
    total = dict(blocks=0, m=0, n=0, ms=0, ns=0, g=0, gu=0, perr=0)
    print("libpcre2:", sr.version())
    for fname, blurb, blocks in FILES:
        text, c = emit_file(fname, blurb, blocks, errors)
        with open(os.path.join(HERE, fname), "w") as fh:
            fh.write(text)
        for k in total:
            total[k] += c[k]
        print("  %-22s blocks=%-4d m=%-4d n=%-4d ms=%-3d ns=%-3d g=%-5d "
              "gu=%-3d perr=%d"
              % (fname, c["blocks"], c["m"], c["n"], c["ms"], c["ns"],
                 c["g"], c["gu"], c["perr"]))
    print("  %-22s blocks=%-4d m=%-4d n=%-4d ms=%-3d ns=%-3d g=%-5d "
          "gu=%-3d perr=%d"
          % ("TOTAL", total["blocks"], total["m"], total["n"], total["ms"],
             total["ns"], total["g"], total["gu"], total["perr"]))
    if errors:
        print("\n%d SPEC ERROR(S) -- nothing above is trustworthy until "
              "these are resolved:" % len(errors))
        for e in errors:
            print("  *", e)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
