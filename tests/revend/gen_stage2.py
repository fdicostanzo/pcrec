#!/usr/bin/env python3
"""tests/revend/gen_stage2.py -- [OPT-REVEND] lane rev2corp: write
tests/revend/stage2_captures.rxt FROM libpcre2's answers (oracle first: every
m/n/ms/ns/g line is the oracle's answer, never pcrec's).

Usage: gen_stage2.py ORACLE_BIN SCRATCH_DIR > stage2_captures.rxt
ORACLE_BIN is tests/fuzz/pcre2_oracle.c built against libpcre2-8 (its
compiles are options=0, so the block's `flags i` / `encoding utf8` are carried
INTO THE PATTERN TEXT the oracle sees: a (*UTF)(*UCP) / (?i) prefix, which
PCRE2 treats exactly as the compile option). verify_stage2.py re-reads the
WRITTEN file and re-asks the oracle, so the file is checked by something that
does not share this table.

A CELL is (pattern, opts, why, [(startpos, subject)]). opts: set of
{"i", "utf8"} plus an optional "features=..." string. Subjects are python
str; under utf8 they are encoded UTF-8 and offsets are BYTES."""
import os, subprocess, sys

def C(pat, why, subs, i=False, utf8=False, feat=None, ucp=False):
    return (pat, i, utf8, feat, why, subs, ucp)

def S(*xs):                       # subjects at startpos 0
    return [(0, x) for x in xs]

CELLS = []
add = CELLS.append

HEADER = """# [OPT-REVEND] STAGE 2 correctness corpus (lane rev2corp, 2026-10-10).
# Capture-bearing END-PINNED patterns (`$`, `\\Z`, `\\z`, without (?m)): the
# population REVEND's stage 2 (docs/design/locate_finish.md section 4.3) hands
# to a reverse-seeded locator plus a VM finisher that places the groups. The
# corpus describes SEMANTICS main already implements; it exists so the L1/L2
# build is verified against answers fixed BEFORE it exists.
#
# ORACLE FIRST. Every m/n/ms/ns/g line is libpcre2 10.46's answer, written by
# tests/revend/gen_stage2.py (the case table lives there, with each family's
# rationale), never pcrec's; tests/revend/verify_stage2.py re-reads THIS file
# and re-asks the oracle for every span and every group slot (it shares no
# code with the generator). python `re` is NOT an oracle here (its `\\Z` is
# PCRE2's `\\z`), so every block is `# pcre2-only`. The oracle compiles at
# options=0: `flags i`, `flags u` and `encoding utf8` are carried into the
# oracle as (?i), (*UCP) and (*UTF) pattern prefixes.
#
# FAMILIES (the risk each stresses is named in docs/dev/lanes/rev2corp_report.md):
# A the n vs n-1 tie on a final newline; B group placement that depends on the
# remainder; C groups in loops (last iteration); D optional/unset groups;
# E alternation priority inside groups; F nested groups; G empty matches at the
# end; H search-from offsets near the end; I the census's unbounded shapes;
# J \\b and lookbehind near the match start; K UTF-8 multi-byte tails (byte
# offsets); L caseless tails; M other pin spellings and non-pinned controls.
"""

# ---- A. the n vs n-1 tie: subject ends in "\n" ($ and \Z accept both ends) ----
add(C(r"(a+)$", "A: `$` before a final newline: the match ends at n-1, never n (the 'a' run cannot cross the newline)",
      S("aa", "aa\n", "aa\n\n", "a\na", "a\na\n", "\n", "", "b\n")))
add(C(r"(a*)\Z", "A: `\\Z` with an EMPTY-able group: n-1 hit, then the empty tail past a second newline",
      S("aa", "aa\n", "aa\n\n", "", "\n", "\n\n", "ab\n")))
add(C(r"(a*)\z", "A: `\\z` is n only: the same subjects as the `\\Z` block, different answers",
      S("aa", "aa\n", "aa\n\n", "", "\n", "\n\n")))
add(C(r"(\n?)$", "A: a group that CAN take the final newline: greedy takes it, `$` accepts n",
      S("", "\n", "a", "a\n", "a\n\n", "\n\n")))
add(C(r"(\n??)$", "A: lazy newline group: prefers the n-1 end, falls to n only when it must",
      S("", "\n", "a\n", "a\n\n")))
add(C(r"(.*)$", "A: dot cannot take the newline: n-1 end; an inner newline moves the start",
      S("ab", "ab\n", "ab\n\n", "a\nb", "a\nb\n", "\n", "")))
add(C(r"(.*?)$", "A: lazy dot to `$`: shortest group that reaches an accepted end",
      S("ab", "ab\n", "a\nb\n", "\n")))
add(C(r"(a|a\n)$", "A: alternation PRIORITY between ends: the n-1 arm first, so the shorter end wins",
      S("a\n", "a", "a\n\n", "ba\n")))
add(C(r"(a\n|a)$", "A: the n arm first: it wins whenever it can (leftmost-first, not longest or shortest)",
      S("a\n", "a", "a\n\n", "ba\n")))
add(C(r"(a\n?)$", "A: greedy optional newline: n over n-1",
      S("a\n", "a", "a\n\n")))
add(C(r"(a\n??)$", "A: lazy optional newline: n-1 over n",
      S("a\n", "a", "a\n\n")))
add(C(r"(a)\n?\z", "A: `\\z` after an optional newline: only n is accepted, so the newline MUST be taken",
      S("a\n", "a", "a\n\n", "a\nb")))
add(C(r"(a)\n?\Z", "A: `\\Z` after an optional newline: both ends accepted, greedy takes n",
      S("a\n", "a", "a\n\n")))
add(C(r"(\s*)\Z", "A: whitespace group and `\\Z`: the group may swallow the final newline",
      S("ab \n", "ab \n\n", "ab", "  ", " \n", "\n \n")))
add(C(r"(\s+)$", "A/I (census shape): trailing blanks; `$` n-1 vs n with \\s taking the newline",
      S("a  ", "a \n", "a \n ", "   ", "\n", "a", "a b", "a\t\n\n")))
add(C(r"(\s+)\z", "I (census shape): `\\z` with a blank run; the newline is part of the run",
      S("a  ", "a \n", "a \n ", "\n", "a")))

# ---- B. groups whose placement depends on the remainder ----
add(C(r"(a*)ab$", "B: greedy group must give back one 'a' for the literal tail",
      S("aaab", "ab", "b", "aab\n", "aaabx", "xaab", "a")))
add(C(r"(a*?)ab$", "B: lazy group: the leftmost START, then the shortest group; still must reach the end",
      S("aaab", "ab", "aab\n", "xab")))
add(C(r"(a+)(a?)$", "B: two adjacent groups share a run: the first is greedy, the second gets nothing",
      S("aaa", "a", "aaa\n", "baa", "")))
add(C(r"(a*)(a*)$", "B: greedy-greedy: group 2 is empty at the end",
      S("aab", "baa", "aa\n", "")))
add(C(r"(a|ab)(c|bcd)$", "B: alternation placement depends on the remainder: 'a'+'bcd' not 'ab'+'c'",
      S("abcd", "abc", "abcd\n", "xabcd", "abcde")))
add(C(r"(a|ab)(c|bcd)(d*)$", "B: three groups, remainder-dependent split",
      S("abcd", "abcdd", "abc", "abcd\n")))
add(C(r"(\d+)(\d)$", "B: greedy digits give one back to the final digit group",
      S("123", "1", "12", "ab123\n", "123a")))
add(C(r"(.+?)(\d+)$", "B: lazy then greedy: group 1 is as short as the digit tail allows",
      S("abc123", "a1b22", "a1", "12", "abc", "ab12\n")))
add(C(r"(.*)(\d)$", "B: greedy dot then digit: group 1 takes all but the last digit",
      S("abc123", "5", "a5\n", "abc")))
add(C(r"([a-z]+)([0-9]*)$", "B: the second group may be empty at the end",
      S("abc123", "abc", "123", "abc\n", "ab1c")))

# ---- C. groups inside loops: the LAST iteration is the capture ----
add(C(r"(?:(a)|(b))+$", "C: alternating arms in a loop: each group keeps its LAST participating iteration",
      S("abab", "ba", "aaa", "b", "abx", "ab\n", "")))
add(C(r"(a|b)+$", "C: one group, last iteration wins",
      S("xab", "ab", "ba\n", "x", "aab")))
add(C(r"(\w\d)*$", "C: star over a group, empty iteration count at the end",
      S("a1b2", "a1b", "", "a1\n", "xx")))
add(C(r"((\d)|x)+$", "C: nested capture in a loop; the inner group keeps an EARLIER iteration after an 'x' one",
      S("1x", "x1", "12", "xx", "1x\n")))
add(C(r"((a)|(b))*$", "C: star of alternating groups at the end",
      S("ab", "ab\n", "ba", "c", "")))
add(C(r"(a+|b)*c$", "C: loop then a literal tail that decides which iteration is last",
      S("aabc", "bbc", "c", "aab", "aabc\n")))
add(C(r"(a*)*$", "C: a nullable group under a star: the empty final iteration",
      S("aab", "aa", "", "baa\n")))
add(C(r"(a*)+$", "C: a nullable group under a plus: the empty iteration at the end",
      S("aab", "aa", "", "b\n")))
add(C(r"(\d{1,2})+$", "C: bounded group under a plus: how the digits split into iterations",
      S("12345", "1", "123", "a12\n", "")))
add(C(r"(ab|a)*b$", "C: loop then a literal, last iteration after backtracking",
      S("ababb", "abab", "aab", "b", "abb\n")))

# ---- D. optional / unset groups ----
add(C(r"(a)?$", "D: optional group; unset when the match is the empty tail",
      S("a", "ba", "b", "", "a\n", "ab")))
add(C(r"(?:(a)|(b)|(c))$", "D: exactly one of three groups is set; the others stay -1",
      S("a", "b", "c", "xb", "d", "c\n")))
add(C(r"(x)?(y)?$", "D: two optional groups; all four set/unset combinations",
      S("xy", "y", "x", "", "xyx", "zxy\n")))
add(C(r"(?:(a)b)?c?$", "D: optional compound group; the empty tail",
      S("abc", "ab", "c", "", "xc", "abx")))
add(C(r"(a)?(?:b|$)", "D: group set, end-pin only in one arm",
      S("ab", "a", "b", "ba", "a\n")))
add(C(r"(a)|b$", "D/ctrl: the end pin binds only the second alternative: a match need not reach the end",
      S("a", "b", "ab", "xb", "ba", "b\n", "xa")))
add(C(r"(a$)|(b)", "D/ctrl: the pin is inside group 1 only",
      S("a", "ab", "ba", "b", "aa", "a\n")))
add(C(r"(?:x(a)|y)$", "D: pinned alternation with a capture in one arm",
      S("xa", "y", "ya", "xay", "xa\n", "")))

# ---- E. alternation priority inside groups ----
add(C(r"(a|ab)$", "E: first arm fails at the pin, second arm wins",
      S("ab", "a", "xab", "ab\n", "aba")))
add(C(r"(ab|a)$", "E: longer arm first",
      S("ab", "a", "xab", "ab\n")))
add(C(r"(foo|foobar)$", "E: prefix arm first, then the longer on pin failure",
      S("foobar", "foo", "xfoobar", "foobar\n", "foobarx")))
add(C(r"(foo|foobar|bar)$", "E: three arms, the leftmost start with any arm",
      S("foobar", "foobar\n", "bar", "fooba")))
add(C(r"(\w+|\w+\.)$", "E: alternation of overlapping quantified arms",
      S("ab", "ab.", "ab. ", "ab\n", ".", "ab.\n")))
add(C(r"(?:a|ab)(c|bcd)?$", "E: outer alternation unstored, inner optional group stored",
      S("abcd", "ac", "abc", "ab", "a")))

# ---- F. nested groups ----
add(C(r"((a)(b))$", "F: nested pair, numbering by opening paren",
      S("ab", "xab", "ab\n", "a", "abab")))
add(C(r"((a+)(b+))+$", "F: nested groups under a loop: all three keep the last iteration",
      S("aabbab", "ab", "aabb\n", "aab", "abb")))
add(C(r"(a(b(c)?)?)$", "F: nested optionals, depth three",
      S("abc", "ab", "a", "xab", "abc\n", "ac")))
add(C(r"((\d+)-(\d+))$", "F: range-like nesting at the end",
      S("1-2", "10-20\n", "x10-20", "10-", "10-20-30")))
add(C(r"(((a)))$", "F: triple-nested single group",
      S("a", "ba", "a\n", "ab")))

# ---- G. empty matches at the end ----
add(C(r"(\s*)$", "G: nullable group: the empty match AT the end when no blank run exists",
      S("abc", "abc  ", "abc \n", "", "\n", "abc\n\n")))
add(C(r"()$", "G: empty group, match at n-1 first (leftmost) when a final newline exists",
      S("", "a", "a\n", "a\n\n", "\n")))
add(C(r"(a?)\z", "G: optional group at `\\z`: empty at n unless the last byte is 'a'",
      S("b", "a", "ba", "ab", "", "a\n")))
add(C(r"(a*)$", "G: leftmost start decides: 'baaa' starts at 1, 'aaab' only matches empty at 4",
      S("baaa", "aaab", "aaa", "", "aaab\n", "b\n")))
add(C(r"(x*)\Z", "G: empty match at n-1 vs n: `\\Z` accepts both, the leftmost is n-1",
      S("ab\n", "ab\n\n", "ab", "xx\n", "\n")))
add(C(r"(?:(x)|)$", "G: empty alternative reached only at the pin",
      S("x", "y", "", "yx", "x\n", "y\n")))
add(C(r"(\b)$", "G: word boundary + end: only after a word char",
      S("ab", "ab ", "ab\n", "", " ", "a b")))
add(C(r"(a|)$", "G: empty alternative last",
      S("a", "b", "ba", "", "a\n")))

# ---- H. search_from / start offsets near the end ----
H = [(0, "12345"), (1, "12345"), (3, "12345"), (4, "12345"), (5, "12345"),
     (0, "ab12\n"), (2, "ab12\n"), (3, "ab12\n"), (4, "ab12\n"), (5, "ab12\n"),
     (1, "\n"), (0, "\n")]
add(C(r"(\d+)$", "H/I (census shape): start offsets across a digit tail, with and without a final newline", H))
add(C(r"(a*)$", "H: start == n gives the empty match; start inside the run shortens the group",
      [(0, "aaa"), (1, "aaa"), (2, "aaa"), (3, "aaa"), (0, "aaa\n"), (3, "aaa\n"), (4, "aaa\n")]))
add(C(r"(\w+)\z", "H/I (census shape): start in the middle of a word on a word subject",
      [(0, "foo bar"), (4, "foo bar"), (5, "foo bar"), (6, "foo bar"), (7, "foo bar"), (3, "foo bar"), (0, "foo bar\n"), (5, "foo bar\n")]))
add(C(r"(\b\w+)$", "H/J: `\\b` at the search start: no boundary mid-word, so a mid-word start must skip to the next",
      [(0, "foo bar"), (4, "foo bar"), (5, "foo bar"), (6, "foo bar"), (7, "foo bar"), (3, "foo bar"), (2, "ab")]))
add(C(r"(a)b?$", "H: start AT the final newline and past it",
      [(0, "xa\n"), (1, "xa\n"), (2, "xa\n"), (3, "xa\n"), (0, "xab"), (2, "xab"), (3, "xab")]))
add(C(r"(\s+)$", "H/I: start inside a blank run",
      [(0, "a   "), (1, "a   "), (2, "a   "), (3, "a   "), (4, "a   "), (2, "a  \n"), (4, "a  \n")]))
add(C(r"(.*)\z", "H: dot-star to `\\z` from every start of a short subject",
      [(0, "ab"), (1, "ab"), (2, "ab"), (0, "a\nb"), (1, "a\nb"), (2, "a\nb"), (3, "a\nb")]))
add(C(r"(\d)(\d)?$", "H: two groups, start between them",
      [(0, "12"), (1, "12"), (2, "12"), (0, "123"), (1, "123"), (2, "123")]))

# ---- I. the unbounded start-unanchored shapes the census names ----
add(C(r"(\d+)$", "I (census): digits at end; non-matches and interior runs",
      S("abc123", "123abc", "12 34", "12 34\n", "1\n", "\n", "", "007", "1a2", "a1\n\n")))
add(C(r"(\w+)\z", "I (census): word at end under `\\z`",
      S("foo bar", "foo bar\n", "foo ", "", "foo_bar9", "!", "a b c")))
add(C(r"([^/]+)$", "I (census): last path segment; the class ALSO matches the newline, so n over n-1",
      S("a/b/c", "a/b/", "/", "a/b/c\n", "a", "", "a/\n", "\n")))
add(C(r"(.*)\.txt$", "I (census): extension strip; greedy group, repeated suffix, dot-star stops at newlines",
      S("a.txt", "a.txt\n", "a.txt.txt", ".txt", "a.txtx", "x\na.txt", "a.TXT", "a.txt\n\n", "txt")))
add(C(r"([^.]*)\.txt$", "I: class-star variant of the extension strip",
      S("a.txt", "a.b.txt", ".txt", "a.txt\n", "a.tx")))
add(C(r"(\s+)$", "I (census): trailing whitespace (see also A, H)",
      S("   ", "a", "a b ", "ab\r\n", "a\n \n")))

# ---- J. \b and lookbehind near the start of the match ----
add(C(r"\b(\w+)$", "J: `\\b` at the match start",
      S("ab cd", " cd", "ab", "-ab", "ab-", "ab cd\n", "")))
add(C(r"(?<=,)(\d+)$", "J: lookbehind sees the byte before the match start",
      S("1,22", "1,22\n", "122", ",5", "1,2,3", "1,"), feat="assertions"))
add(C(r"(?<!x)(a+)$", "J: negative lookbehind forces the start past an 'x'",
      S("xaa", "aa", "xa", "baa", "xaa\n", "x"), feat="assertions"))
add(C(r"(?<=\s)(\S+)\z", "J: lookbehind on a class, token at the very end",
      S("ab cd", "ab cd\n", "cd", " cd", "ab\tcd", "ab "), feat="assertions"))
add(C(r"(?<=^|,)(\w+)$", "J: lookbehind alternation with an anchor",
      S("ab", "x,ab", "x,ab\n", "x;ab", ",", "x,"), feat="assertions"))
add(C(r"(\w)\b$", "J: `\\b` just before the pin: a word char at the end",
      S("ab", "ab\n", "a-", "", "a b")))

# ---- K. UTF-8 multi-byte tails (offsets are BYTES) ----
U = dict(utf8=True)
add(C(r"(.)$", "K: a multi-byte final character: the group spans 2 bytes",
      S("aé", "é", "日本", "aé\n", "é\n\n", "a", ""), **U))
add(C(r"(\w+)\z", "K: word run over multi-byte letters (\\w is ASCII-only without UCP, so a multi-byte letter ENDS the run)",
      S("héllo", "x hé", "日本語", "héllo\n", "aé ", "é-"), **U))
add(C(r"([^/]+)$", "K: path segment with multi-byte characters, 3- and 4-byte",
      S("日/本", "a/\U0001F600", "\U0001F600", "日/\n", "/é\n"), **U))
add(C(r"(\x{e9}+)$", "K: a multi-byte literal under a plus at the end",
      S("aéé", "éa", "éé\n", "é", ""), **U))
add(C(r"(\s+)$", "K: Unicode whitespace tail (U+00A0, U+2003): 2- and 3-byte \\s under UCP",
      S("a ", "a  ", "a \n", "a   ", " "), ucp=True, **U))
add(C(r"(\d+)$", "K: Unicode digits at the end (Arabic-Indic, 2 bytes each) under UCP",
      S("a٣٤", "٣", "12٣", "٣a", "a٣\n"), ucp=True, **U))
add(C(r"(.*)\.txt$", "K: dot-star over multi-byte text before an ASCII suffix",
      S("é.txt", "日本.txt\n", "é.txt.txt", "é.txté"), **U))
add(C(r"(\p{L}+)$", "K: a property class at the end",
      S("1éè", "ab1", "日本", "日本\n", "aé "), feat=None, **U))
add(C(r"(\w+)$", "K: start offsets on character boundaries near the end (\\w is ASCII-only: UCP \\w is refused under utf8)",
      [(0, "aéb"), (1, "aéb"), (3, "aéb"), (4, "aéb"), (2, "éé"), (4, "éé")], **U))
add(C(r"(.)\Z", "K: `\\Z` n-1 vs n with a multi-byte last character before the newline",
      S("é\n", "é\n\n", "\n", "日", "a日\n"), **U))
add(C(r"(a|\x{e9})+$", "K: loop whose iterations differ in byte length: the last iteration's span",
      S("aé", "éa", "ééa\n", "bé"), **U))

# ---- L. case-insensitive tails ----
add(C(r"(abc)$", "L: caseless literal tail",
      S("xABC", "abc", "AbC\n", "ab", "ABCD"), i=True))
add(C(r"(a+)\z", "L: caseless run under `\\z`",
      S("AaA", "AaA\n", "bAa", "b", ""), i=True))
add(C(r"([a-c]+)$", "L: caseless class tail",
      S("xABCx", "xABC", "CBa\n", "d", "aBc"), i=True))
add(C(r"([^a]+)$", "L: caseless NEGATED class: neither 'a' nor 'A'",
      S("bAb", "bA", "Ab\n", "aA", "b"), i=True))
add(C(r"(.*)\.TXT$", "L: caseless extension strip",
      S("a.txt", "a.TxT\n", "a.txt.Txt", "a.tx"), i=True))
add(C(r"(k)$", "L: caseless 'k' in UTF-8 mode: the Kelvin sign U+212A folds to it",
      S("K", "K", "xk", "K\n", "a"), i=True, utf8=True))
add(C(r"(\x{e9}+)$", "L: caseless non-ASCII in UTF-8 mode (U+00C9 folds to U+00E9)",
      S("É", "éÉ", "xÉ\n", "e"), i=True, utf8=True))

# ---- M. other end-pinned spellings and controls ----
add(C(r"((a)\z)", "M: the pin inside a group",
      S("a", "ba", "a\n", "ab")))
add(C(r"(a$)", "M: `$` inside a group",
      S("a", "ba", "a\n", "a\n\n")))
add(C(r"(a)(?:$)", "M: `$` in a non-capturing group",
      S("a", "a\n", "ab")))
add(C(r"(?s)(.+)$", "M: DOTALL: the group may take the newline, n over n-1 again",
      S("ab\n", "a\nb", "\n", "ab")))
add(C(r"(a++)$", "M: possessive group before the pin", S("aa", "aab", "aa\n", "baa"), feat="atomic-groups"))
add(C(r"(?>a+)(b)$", "M: atomic prefix then a captured tail", S("aab", "ab", "aabb", "aab\n", "b"), feat="atomic-groups"))
add(C(r"(?m)(\d+)$", "M/ctrl: MULTILINE `$` is NOT end-pinned: every line end is a candidate",
      S("12\n34", "12\n34\n", "a1\nb", "12", "x\n"), feat="classes"))
add(C(r"(\d+)$|(x)", "M/ctrl: a top-level alternation whose second branch is unpinned",
      S("a12", "x1", "1x", "12x", "ab")))

# ---- N. the design note's named witnesses: lazy ties, \\K, clamped widths, pins under a loop ----
add(C(r"(\s+?){2}$", "N (locate_finish 4.3 E3): the LAZY tie that moves the window: end priority differs from max(D); the search-from-not-verify-at witness",
      S("a    ", "a  ", "a   \n", "a \n", "a \n \n", "    ", "a ", "  \n")))
add(C(r"(\s+?)\s*$", "N: lazy group then a greedy tail to the pin; the group is the first blank only",
      S("a   ", "a \n", "   ", "a", " \n  ")))
add(C(r"(a+?)$", "N: a lazy group still has to reach the pin; the leftmost start is forced to the run start",
      S("aaa", "baa", "aa\n", "b")))
add(C(r"(a\z)+", "N (T5 unbounded witness): the pin INSIDE a loop; only the last iteration can satisfy it",
      S("a", "aa", "ba", "a\n", "")))
add(C(r"(a+)$", "N (T5 unbounded witness): the plain unbounded group, long runs and interior non-matches",
      S("aaaaaaaaaaaaaaaaaaaa", "aaaaaaaaaaaaaaaaaaaab", "baaaaaaaaaaaaaaaaaaa\n", "aaaaaaaaaabaaaaaaaaaa")))
add(C(r"(\d{2,4})$", "N (clamped width): a bounded group at the end: the locator window is clamped, the start is leftmost-feasible",
      S("1", "12", "12345", "123456\n", "x123", "x12\n\n")))
add(C(r"(a{3})$", "N (clamped width): an exact-count group",
      S("aaa", "aaaa", "aa", "aaa\n", "baaa", "aaab")))
add(C(r"(\w{1,3})\z", "N (clamped width): bounded word group under \\z",
      S("abcdef", "ab", "abcd ", "a b", "abc\n", "")))
add(C(r"(x)\K(\d+)$", "N (\\K): the reported match start moves past the first group; the groups keep their own spans",
      S("x12", "x12\n", "ax1", "x", "xx12"), feat="classes"))
add(C(r"(?:a|(b))\K(c)?$", "N (\\K): K with an optional trailing group at the pin",
      S("ac", "b", "bc", "a\n", "ab")))

# -----------------------------------------------------------------------

def esc(b):
    out = []
    for ch in b:
        if ch == "\n": out.append("\\n")
        elif ch == "\t": out.append("\\t")
        elif ch == "\r": out.append("\\r")
        elif ch == '"': out.append('\\"')
        elif ch == "\\": out.append("\\\\")
        elif 32 <= ord(ch) < 127: out.append(ch)
        else: out.append("".join("\\x%02x" % x for x in ch.encode("utf-8")))
    return "".join(out)

def oracle(binp, scratch, pat, i, utf8, ucp, subj, sp):
    pre = ("(*UTF)" if utf8 else "") + ("(*UCP)" if ucp else "") + ("(?i)" if i else "")
    f = os.path.join(scratch, "subj")
    with open(f, "wb") as h:
        h.write(subj.encode("utf-8"))
    r = subprocess.run([binp, pre + pat, f, str(sp)], capture_output=True, timeout=60)
    return r.stdout.decode().strip()

def main():
    binp, scratch = sys.argv[1:3]
    os.makedirs(scratch, exist_ok=True)
    print(HEADER.rstrip("\n"))
    for pat, i, utf8, feat, why, subs, ucp in CELLS:
        print()
        print("# " + why)
        print("# pcre2-only")
        print("pattern " + pat)
        if i or ucp: print("flags " + ("i" if i else "") + ("u" if ucp else ""))
        if utf8: print("encoding utf8")
        fs = [x for x in (feat or "").split(",") if x]
        if any(t in pat for t in ("\\z", "\\Z", "\\b", "\\K", "(?m)")) and "assertions" not in fs: fs.append("assertions")
        if fs and any(t in pat for t in ("\\d", "\\D", "\\w", "\\W", "\\s", "\\S", "[")) and "classes" not in fs: fs.append("classes")
        if "(?m)" in pat and "modifiers" not in fs: fs.append("modifiers")
        if "(?<" in pat and "lookaround" not in fs: fs.append("lookaround")
        if fs: print("features " + ",".join(fs))
        for sp, s in subs:
            ans = oracle(binp, scratch, pat, i, utf8, ucp, s, sp).split()
            kw = "m" if sp == 0 else "ms"
            nk = "n" if sp == 0 else "ns"
            pre = "" if sp == 0 else "%d " % sp
            if not ans or ans[0] not in ("match", "nomatch"):
                sys.exit("oracle: %r on %r: %s" % (pat, s, ans))
            if ans[0] == "nomatch":
                print('%s %s"%s"' % (nk, pre, esc(s)))
                continue
            v = list(map(int, ans[1:]))
            print('%s %s"%s" %d %d' % (kw, pre, esc(s), v[0], v[1]))
            for k in range(1, len(v) // 2):
                print("g %d %d %d" % (k, v[2 * k], v[2 * k + 1]))

main()
