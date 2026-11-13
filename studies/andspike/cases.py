"""cases.py -- the hard cases, each with a hand-derived expected value.

Every row: name, what the oracle returned, what was derived by hand (the
derivation is the comment beside it), PASS/FAIL. Rows marked PROBE have no
hand value: they record what PCRE2 does where the docs leave it open.
Run: python3 -B cases.py  (writes nothing; results/cases.txt is its stdout).
"""
import spanoracle as so
import p2cb as p

rows = []


def check(name, got, want, why=""):
    rows.append(("PASS" if got == want else "FAIL", name, got, want, why))


def probe(name, got, why=""):
    rows.append(("PROBE", name, got, None, why))


o = so.Oracle()
E = lambda x, s, i=0: o.ends(x, s, i)["ends"]

# -- premise and preference order ------------------------------------------
check("premise (?:a|ab) @0 'abc'", E("a|ab", "abc"), [1, 2], "brief's PREMISE TEST")
check("greedy a* 'aaa'", E("a*", "aaa"), [3, 2, 1, 0], "longest first, down to empty")
check("lazy a*? 'aaa'", E("a*?", "aaa"), [0, 1, 2, 3], "empty first")
check("(a|ab)(c|bcd) 'abcd'", E("(a|ab)(c|bcd)", "abcd"), [4, 3],
      "a+bcd=4 first (arm1 then its 2nd inner arm), then ab+c=3")
check("first end == PCRE2's own match", E("(a|ab)(c|bcd)", "abcd")[0],
      o.plain_first("(a|ab)(c|bcd)", "abcd", 0), "callout-free route")

# -- empty matches ------------------------------------------------------------
check("empty pattern @1", E("", "abc", 1), [1], "only the empty span [1,1)")
check("(?:)|a 'a'", E("(?:)|a", "a"), [0, 1], "empty arm first")
check("a? & b* on 'a'", o.and_sets("a?", "b*", "a"), (0, 0),
      "X ends [1,0]; b* rejects [0,1), accepts [0,0)")
check("a? & b* inline", o.and_inline("a?", "b*", "a"), (0, 0), "same, PCRE2 owns the loop")

# -- lookaround reaching outside the span (in-context semantics) -------------
check("(?<=a)b @1 'ab'", E("(?<=a)b", "ab", 1), [2], "lookbehind sees s[0] outside the span")
check("(?<=a)b & b on 'ab'", o.and_sets("(?<=a)b", "b", "ab"), (1, 2), "")
check("(?<=a)b isolated [1,2)", o.spans("(?<=a)b", "ab", 1, 2, isolated=True), False,
      "isolated semantics: the substring 'b' has nothing behind it")
check("a(?=b) & a on 'ab'", o.and_sets("a(?=b)", "a", "ab"), (0, 1), "lookahead sees s[1] past j")
check("a(?=b) & a on 'ac'", o.and_sets("a(?=b)", "a", "ac"), None, "")
check("a\\b spans [0,1) of 'ab'", o.spans(r"a\b", "ab", 0, 1), False, "no word boundary at 1 in context")
check("a\\b isolated [0,1) of 'ab'", o.spans(r"a\b", "ab", 0, 1, isolated=True), True, "")
check("a$ spans [0,1) of 'ab'", o.spans("a$", "ab", 0, 1), False, "$ sees the real end")
check("a$ isolated [0,1) of 'ab'", o.spans("a$", "ab", 0, 1, isolated=True), True, "")

# -- backreferences ---------------------------------------------------------
check("(a+)\\1 'aaaaaa'", E(r"(a+)\1", "aaaaaa"), [6, 4, 2], "a+ = aaa, aa, a; \\1 doubles")
check("(a+)\\1 & a{4}", o.and_sets(r"(a+)\1", "a{4}", "aaaaaa"), (0, 4), "")
check("(a|aa)\\1* 'aaaa'", E(r"(a|aa)\1*", "aaaa"), [4, 3, 2, 1], "a-run greedy 4..1; aa-run adds nothing new")
check("Y's own group numbering", o.and_sets("(b)", r"(a|b)\1?", "b"), (0, 1),
      "each operand compiles alone: Y's \\1 is Y's group, not X's")

# -- \K ---------------------------------------------------------------------
r = o.ends(r"foo\Kbar", "foobar", 0)
check("foo\\Kbar ends", r["ends"], [6], "")
probe("foo\\Kbar callout start_match", r["kstart"],
      "pcre2callout says \\K changes start_match (would be 3); 10.49 reports 0 here and in pcre2test")
check("foo\\Kbar & .* inline (attempt span)", o.and_inline(r"foo\Kbar", ".*", "xfoobar"), (1, 7),
      "the leading (?C2) records the attempt start; \\K only moves the REPORTED start")
check("foo\\Kbar & bar", o.and_sets(r"foo\Kbar", "bar", "foobar"), None,
      "attempt-span semantics: Y must match [0,6), not the reported [3,6)")

# -- atomic / possessive ----------------------------------------------------
check("(?>a|ab) 'abc'", E("(?>a|ab)", "abc"), [1], "atomic: 'ab' is never reached")
check("(?>a|ab) & ab", o.and_sets("(?>a|ab)", "ab", "ab"), None, "although 'ab' is in L(a|ab)")
check("a|ab & ab", o.and_sets("a|ab", "ab", "ab"), (0, 2), "the non-atomic control")
check("a*+ 'aaa'", E("a*+", "aaa"), [3], "possessive: only the maximal end")
check("a*+ & aa on 'aaa'", o.and_sets("a*+", "aa", "aaa"), (1, 3), "start 0 fails, start 1 reaches 3")
check("(?=(a|ab))\\1 'ab'", E(r"(?=(a|ab))\1", "ab"), [1], "a lookahead is atomic: its capture is fixed at 'a'")

# -- verbs ------------------------------------------------------------------
check("a(*ACCEPT)b|ab", o.ends("a(*ACCEPT)b|ab", "ab", 0)["status"], "accept-bypass",
      "(*ACCEPT) ends the match without reaching the end callout: detected, not enumerable")
check("(?=a(*ACCEPT)b)a", E("(?=a(*ACCEPT)b)a", "a"), [1], "inside a lookahead ACCEPT only ends the assertion")
check("a(*COMMIT)|ab ends", E("a(*COMMIT)|ab", "ab"), [1], "truncated: the language view is {1,2}")
check("a(*COMMIT)|b & b sets", o.and_sets("a(*COMMIT)|b", "b", "ab"), (1, 2), "A: our start loop ignores COMMIT")
check("a(*COMMIT)|b & b inline", o.and_inline("a(*COMMIT)|b", "b", "ab"), None,
      "B: PCRE2 semantics, COMMIT forbids later starts")
check("aa(*SKIP)b|a & a sets", o.and_sets("aa(*SKIP)b|a", "a", "aab"), (1, 2), "A ignores SKIP's bump target")
check("aa(*SKIP)b|a & a inline", o.and_inline("aa(*SKIP)b|a", "a", "aab"), None,
      "B: SKIP bumps the next start to 2")
check("a(*PRUNE)|a. & .. sets", o.and_sets("a(*PRUNE)|a.", "..", "ab"), None, "PRUNE at a fixed start: same as B")
check("a(*PRUNE)|a. & .. inline", o.and_inline("a(*PRUNE)|a.", "..", "ab"), None, "")
check("a(*THEN)|ab & ab", (o.and_sets("a(*THEN)|ab", "ab", "ab"), o.and_inline("a(*THEN)|ab", "ab", "ab")),
      ((0, 2), (0, 2)), "THEN only skips to the next arm: enumeration intact")

# -- recursion ------------------------------------------------------------
BAL = r"\((?:[^()]|(?R))*\)"
check("balanced parens '(a(b))'", E(BAL, "(a(b))"), [6], "only the outer close")
naive = so.Oracle(recursion_guard=False)
probe("balanced parens UNGUARDED (?C1)", naive.ends(BAL, "(a(b))", 0)["ends"],
      "without (?(R)|...) the callout fires at the inner recursion's end too")
check("balanced '(a)(b)' @0", E(BAL, "(a)(b)"), [3], "")
check("subroutine (a|b)(?1) 'ab'", E("(a|b)(?1)", "ab"), [2], "")
check("lookahead_order agrees on recursion", o.lookahead_order(BAL, "(a(b))", 0), [6], "callout-free route")

# -- UTF --------------------------------------------------------------------
u = so.Oracle(utf=True)
check("UTF .+ on 'é€a'", u.ends(".+", "é€a", 0)["ends"], [6, 5, 2], "byte offsets of char ends")
check("UTF starts", u.starts("é€a".encode()), [0, 2, 5, 6], "char boundaries only")
check("UTF .+ & (?:€a|é)", u.and_sets(".+", "€a|é", "é€a"), (0, 2), "")
check("UTF inline agrees", u.and_inline(".+", "€a|é", "é€a"), (0, 2), "")
check("UTF lookahead_order", u.lookahead_order(".+", "é€a", 0), [6, 5, 2], "remaining counted in chars")
check("non-UTF .+ byte ends", len(o.ends(".+", "é€a".encode(), 0)["ends"]), 6, "every byte is a char")

# -- missing-callout optimizations (PROBE: what NO_OPT protects) -------------
opt = so.Oracle(no_opt=False)
for x, s in (("a+", "aaa"), ("a*b?", "aab"), ("(?:a|b)+", "ab"), ("[ab]*", "ab")):
    probe("default opts %s on %r" % (x, s), (opt.ends(x, s, 0)["ends"], o.ends(x, s, 0)["ends"]),
          "(default-options ends, NO_OPT ends), GUARDED wrapper")
# The brief's plain form `(?:X)(?C1)`, no (?(R)...) guard: at default options
# PCRE2 auto-possessifies a repeat that the end callout follows.
bare_opt = so.Oracle(no_opt=False, recursion_guard=False)
bare = so.Oracle(recursion_guard=False)
for x, s in (("a+", "aaa"), (r"(\d+)", "1234"), ("(?:a|b)+", "ab"), ("[ab]*", "ab")):
    probe("plain (?:X)(?C1) default opts %s on %r" % (x, s),
          (bare_opt.ends(x, s, 0)["ends"], bare.ends(x, s, 0)["ends"]),
          "(default-options ends, NO_OPT ends), UNGUARDED wrapper")

if __name__ == "__main__":
    nfail = 0
    for st, name, got, want, why in rows:
        nfail += st == "FAIL"
        w = "" if st == "PROBE" else "  want=%r" % (want,)
        print("%-5s %-42s got=%r%s  %s" % (st, name, got, w, why))
    print("cases: %d  pass %d  fail %d  probe %d" % (len(rows), sum(r[0] == "PASS" for r in rows),
                                                      nfail, sum(r[0] == "PROBE" for r in rows)))
    print("pcre2", p.version())
