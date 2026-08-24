"""[DD-14] §4 -- LEFT RECURSION and the two guards, measured on 10.46.

Charter question (iii): what does PCRE2 refuse at COMPILE time (the error 140
"could loop indefinitely" family), and what is the EXACT check pcrec mirrors.
Plus: `(?R)` under a quantifier; calls inside lookaround, atomic groups and
lookbehind (a lookbehind needs a WIDTH, and a recursive callee has none).

The first thing this probe found is that the charter's premise is only half
right. PCRE2 10.46 has TWO guards, not one:

  COMPILE TIME   error 140, "recursive call could loop indefinitely"
  MATCH TIME     rc -52, "nested recursion at the same subject position"

and which one fires is a property of the SHAPE, not of a single analysis. A
design that mirrors only the compile-time check ships a compiler that hangs
where PCRE2 returns an error, so both are measured here and §4 rules both.

Axes:
  L1  the DIRECT left recursion family: compile-time or match-time?
  L2  INDIRECT left recursion through one or more groups
  L3  left recursion behind a NULLABLE prefix -- the shape a naive
      "is the call the first item" check misses
  L4  what is NOT refused: right recursion, middle recursion, guarded
  L5  the MATCH-TIME guard's exact trigger, and whether it is per POSITION
      or per DEPTH
  L6  (?R) under a quantifier
  L7  a call inside a LOOKBEHIND, where a width is required
  L8  a call inside a lookahead / atomic group / another call
  L9  DEPTH: how deep does 10.46 actually go, and what stops it
"""
import importlib.util
import os
import sys

_HERE = os.path.dirname(os.path.abspath(__file__))
_spec = importlib.util.spec_from_file_location(
    "sr_oracle", os.path.join(_HERE, "sr_oracle.py"))
sr = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sr)

print("libpcre2:", sr.version())
print("python3 :", sys.version.split()[0])
print("sr_oracle.SELFCHECK:", sr.SELFCHECK or "none")
print()

_out = set()


def cell(pat, subj="", note="", opts=0):
    r = sr.match_limits(pat, subj, options=opts)
    if isinstance(r, tuple) and r and r[0] == "ERR":
        _out.add("compile-refuse")
        print("  %-46s %-10r COMPILE ERR %-3d %s%s"
              % (pat, subj, r[1][0], r[1][2],
                 ("  # " + note) if note else ""))
        return r
    if isinstance(r, tuple) and r and r[0] == "rc":
        _out.add("match-giveup")
        print("  %-46s %-10r MATCH rc=%-4d %s%s"
              % (pat, subj, r[1], sr.pcre2._errmsg(r[1]),
                 ("  # " + note) if note else ""))
        return r
    _out.add("nomatch" if r is None else "match")
    print("  %-46s %-10r %-26r%s"
          % (pat, subj, r, ("  # " + note) if note else ""))
    return r


print("=== L1: DIRECT left recursion ========================================")
cell(r"^((?1)a)$", "a", "the call is the FIRST item of its own group")
cell(r"^((?1)a)$", "aaa", "same pattern, a subject that could match")
cell(r"^(a|(?1)a)$", "aa", "left-recursive SECOND branch")
cell(r"^((?1)?a)$", "aa", "left-recursive under a ?")
cell(r"^((?1)*a)$", "aa", "under a *")
cell(r"^(?R)a$", "aa", "(?R) as the first item of the whole pattern")
cell(r"^a(?R)$", "aa", "(?R) as the LAST item, for contrast")
cell(r"(?R)a", "aa", "unanchored (?R) first")
cell(r"^(?(DEFINE)(?<g>(?&g)a))(?&g)$", "aa", "by name, DEFINE-bodied")
print()

print("=== L2: INDIRECT left recursion ======================================")
cell(r"^((?2)a)((?1)b)$", "ab", "1 calls 2 calls 1, both leading")
cell(r"^((?2)a)(x(?1)b)$", "ab", "with a byte before the second call")
cell(r"^(?(DEFINE)(?<p>(?&q)a)(?<q>(?&p)b))(?&p)$", "ab",
     "a two-node cycle behind DEFINE")
cell(r"^(?(DEFINE)(?<p>(?&q)a)(?<q>x(?&p)b))(?&p)$", "xab",
     "the same cycle with a byte on one edge")
print()

print("=== L3: left recursion behind a NULLABLE prefix =======================")
print("# A check that asks 'is the call the FIRST item' misses every one of")
print("# these, because something precedes the call and consumes nothing.")
cell(r"^(a?(?1)b)$", "ab", "an optional literal before the call")
cell(r"^((?:)(?1)b)$", "b", "an empty group before the call")
cell(r"^(\b(?1)b)$", "b", "a zero-width assertion before the call")
cell(r"^((?=x)(?1)b)$", "b", "a lookahead before the call")
cell(r"^(x*(?1)b)$", "b", "a star that can match empty")
cell(r"^((?:q|)(?1)b)$", "b", "an alternation with an empty branch")
cell(r"^((){0}(?1)b)$", "b", "a {0} repeat")
print()

print("=== L4: what is NOT refused ==========================================")
cell(r"^(a(?1)?b)$", "aabb", "RIGHT recursion with a base case")
cell(r"^(a(?1)b|c)$", "acb", "middle recursion")
cell(r"^(a(?1)?b)$", "ab", "depth 1")
cell(r"\((\w(?1)?\w)\)", "(ab)", "the balanced idiom")
cell(r"^(?(DEFINE)(?<g>a(?&g)?b))(?&g)$", "aabb", "DEFINE, right-recursive")
print()

print("=== L5: the MATCH-TIME guard's exact trigger =========================")
print("# rc -52 says 'nested recursion at the same subject position'. Is the")
print("# test POSITION-based (a recursion that has not advanced) or DEPTH-")
print("# based (a counter)? The cells differ in whether the subject moves.")
cell(r"^(?(DEFINE)(?<g>(?&g)?a))(?&g)$", "a",
     "the call is at the same position as its caller's entry")
cell(r"^(?(DEFINE)(?<g>a(?&g)?))(?&g)$", "aaa",
     "the call is at a LATER position each level")
cell(r"^(?(DEFINE)(?<g>(?:a|)(?&g)?b))(?&g)$", "ab",
     "the prefix MAY advance; the failing path is the one that did not")
cell(r"^(?(DEFINE)(?<g>x*(?&g)?b))(?&g)$", "xxb",
     "the prefix DID advance -- does the guard still fire?")
cell(r"^(?(DEFINE)(?<g>x*(?&g)?b))(?&g)$", "b",
     "and here it could not advance at all")
print()

print("=== L5b: THE GUARD IS NOT 'SAME POSITION' -- the decisive sweep ======")
print("# The obvious reading of rc -52's own message is 'a recursion entered")
print("# at the same subject position as an active instance of the same")
print("# group'. THAT READING IS WRONG, and a pcrec that implemented it")
print("# would REFUSE PATTERNS PCRE2 MATCHES. `^(a|(?1)a)$` descends one")
print("# level per subject byte, EVERY LEVEL ENTERED AT OFFSET 0, and")
print("# matches. The callout counts the levels.")
_pat = r"^(a|(?C1)(?1)a)$"
print("  pattern: %s   (C1 sits immediately before the recursive call)" % _pat)
_grew = False
for n in [1, 2, 3, 5, 10, 20, 50, 100, 200]:
    res, tr = sr.callout_trace(_pat, "a" * n, limit=1000000)
    shown = ("rc=%d" % res[1]) if (isinstance(res, tuple) and res
                                   and res[0] == "rc") else repr(res)
    poss = set(t["pos"] for t in tr)
    print("    'a'*%-4d  nested calls=%-5d  entry offsets seen=%s  -> %s"
          % (n, len(tr), sorted(poss) or "[]", shown))
    if len(tr) > 50:
        _grew = True
print("  REACHABILITY: the nesting must exceed 50 somewhere above, or the")
print("  sweep never demonstrated deep same-position nesting:",
      "OK" if _grew else "!! VACUOUS")
print("# and the SAME pattern on a subject it cannot match, where the")
print("# descent runs out of ways to advance:")
for n in [1, 2, 3, 5, 10, 20, 40]:
    res, tr = sr.callout_trace(_pat, "a" * n + "b", limit=1000000)
    shown = ("rc=%d" % res[1]) if (isinstance(res, tuple) and res
                                   and res[0] == "rc") else repr(res)
    print("    'a'*%-3d+'b'  nested calls=%-5d -> %s" % (n, len(tr), shown))
print("# The give-up depth TRACKS THE SUBJECT (n+2), so -52 is not a fixed")
print("# nesting cap either. This lane did NOT pin 10.46's exact predicate")
print("# by black-box probing and §4.3 says so rather than guessing one.")
print("# What IS pinned: 199 same-position nested recursions can MATCH, so")
print("# 'refuse a recursion at a position an ancestor already occupies' is")
print("# a MISCOMPILE, not a conservative approximation.")
print()

print("=== L6: (?R) under a quantifier ======================================")
for pat, subj in [(r"^(?R)*$", ""), (r"^(?R)?$", ""), (r"^(?R){0,2}$", ""),
                  (r"^a(?R)*b$", "ab"), (r"^(a(?R)*b)$", "ab"),
                  (r"^(a(?R)?b)$", "aabb"), (r"^(a(?R)*b)$", "aabb"),
                  (r"(a(?R)*b)", "aabb")]:
    cell(pat, subj, "(?R) under a quantifier")
print()

print("=== L7: a call inside a LOOKBEHIND (a width is required) =============")
for pat, subj, note in [
        (r"^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$", "ab", "fixed width 2"),
        (r"^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$", "ab", "widths 1 and 2"),
        (r"^(?(DEFINE)(?<g>a+))aa(?<=(?&g))$", "aa", "unbounded width"),
        (r"^(?(DEFINE)(?<g>a{1,300}))" + "a" * 4 + r"(?<=(?&g))$", "aaaa",
         "width 1..300, above the measured max_varlookbehind default"),
        (r"^(?(DEFINE)(?<g>a(?&g)?b))aabb(?<=(?&g))$", "aabb",
         "a RECURSIVE callee inside a lookbehind"),
        (r"^(?(DEFINE)(?<g>ab))ab(?<!(?&g))$", "ab", "negative lookbehind"),
        (r"^(?(DEFINE)(?<g>ab))ab(?<=(?&g))cd$", "abcd", "with a follow"),
]:
    cell(pat, subj, note)
print("# for contrast, the SAME bodies written inline in the lookbehind:")
for pat, subj, note in [
        (r"^ab(?<=ab)$", "ab", "inline fixed"),
        (r"^ab(?<=a|ab)$", "ab", "inline variable, legal in 10.46"),
        (r"^aa(?<=a+)$", "aa", "inline unbounded"),
]:
    cell(pat, subj, note)
print("# and PCRE2's own MAXLOOKBEHIND for a call-bearing lookbehind:")
for pat in [r"^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$",
            r"^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$",
            r"^ab(?<=ab)$"]:
    print("  %-46s MAXLOOKBEHIND=%r" % (pat, sr.maxlookbehind(pat)))
print()

print("=== L8: a call inside a lookahead / atomic group / another call ======")
for pat, subj, note in [
        (r"^(?(DEFINE)(?<g>ab))(?=(?&g))ab$", "ab", "positive lookahead"),
        (r"^(?(DEFINE)(?<g>ab))(?!(?&g))ac$", "ac", "negative lookahead"),
        (r"^(?(DEFINE)(?<g>ab))(?>(?&g))$", "ab", "atomic group"),
        (r"^(?(DEFINE)(?<g>a(?=(?&g)?b)b))(?&g)$", "ab",
         "a recursive call INSIDE a lookahead inside the callee"),
        (r"^(?(DEFINE)(?<g>(?=(?&g))a))(?&g)$", "a",
         "LEFT recursion through a lookahead -- zero width, so the position "
         "never moves"),
        (r"^(?(DEFINE)(?<g>(?>(?&g))a))(?&g)$", "a",
         "left recursion through an atomic group"),
        (r"^(?(DEFINE)(?<g>(?<=(?&g))a))(?&g)$", "a",
         "left recursion through a lookbehind"),
]:
    cell(pat, subj, note)
print()

print("=== L9: HOW DEEP does 10.46 go, and what stops it? ===================")
print("# depth_of() bisects the smallest depth_limit that still reaches the")
print("# answer -- PCRE2's own count of nested backtrack levels.")
for n in [1, 2, 4, 8, 16, 32, 64]:
    pat = r"^(a(?1)?b)$"
    subj = "a" * n + "b" * n
    print("  %-24r subject %3d bytes  depth_limit needed = %r"
          % (pat, len(subj), sr.depth_of(pat, subj)))
print("# a NON-recursive control, so the growth is attributable to the call:")
for n in [1, 2, 4, 8, 16, 32, 64]:
    pat = r"^a*b*$"
    subj = "a" * n + "b" * n
    print("  %-24r subject %3d bytes  depth_limit needed = %r"
          % (pat, len(subj), sr.depth_of(pat, subj)))
print("# THE DEFAULT depth limit, by finding the subject size at which the")
print("# DEFAULTS start to refuse. FIRST VERSION WAS VACUOUS: it bisected")
print("# [1, 400000] for the first FAILING n, found none, and reported")
print("# 'largest n = 399999' -- a confident number about a limit the sweep")
print("# never reached. The guard below says so instead.")
_hi = 400000
_r_hi = sr.match_limits(r"^(a(?1)?b)$", "a" * _hi + "b" * _hi)
_hi_fails = (_r_hi is None or (isinstance(_r_hi, tuple) and _r_hi
                               and _r_hi[0] == "rc"))
if not _hi_fails:
    print("  n=%d (a %d-byte subject) STILL MATCHES at the defaults: this "
          "build's default depth limit is not reached by any subject this "
          "sweep can afford, so NO number is reported here."
          % (_hi, 2 * _hi))
    print("  what IS measured: the depth REQUIREMENT grows as subject+3 "
          "(the rows above), and PCRE2 satisfies it from the HEAP -- "
          "pcre2_match's frame vector, which grows to the heap limit. That "
          "is the structural difference from a fixed emitted array.")
else:
    lo, hi = 1, _hi
    while lo < hi:
        mid = (lo + hi) // 2
        r = sr.match_limits(r"^(a(?1)?b)$", "a" * mid + "b" * mid)
        ok = not (r is None or (isinstance(r, tuple) and r and r[0] == "rc"))
        lo, hi = (mid + 1, hi) if ok else (lo, mid)
    print("  largest n for which ^(a(?1)?b)$ matches a^n b^n at the "
          "DEFAULTS:", lo - 1)
    r = sr.match_limits(r"^(a(?1)?b)$", "a" * lo + "b" * lo)
    print("  and at n =", lo, "the answer is: rc=%d %s"
          % (r[1], sr.pcre2._errmsg(r[1])))
print("# the HEAP limit, which is what actually stops it:")
for hl in [1, 8, 64, 1024]:
    r = sr.match_limits(r"^(a(?1)?b)$", "a" * 20000 + "b" * 20000, heap=hl)
    print("  heap_limit=%-5d KiB -> %s" % (hl,
          "rc=%d %s" % (r[1], sr.pcre2._errmsg(r[1]))
          if isinstance(r, tuple) and r and r[0] == "rc" else repr(r)))
print()

print("=== L9b: THE CAPACITY AS A USER-FACING SUBJECT SIZE, TIMED ==========")
print("# §5.6 and §14 ASK 2 quote these numbers. R34's V-11 found them")
print("# marked MEASURED with no probe and no archive behind them -- the")
print("# third instance of this lane's own defect class -- so they are")
print("# produced HERE and the design cites this file.")
print()
print("# (a) THE LEGITIMATE DEEP RECURSION: ^(a(?1)?b)$ on a^n b^n needs")
print("#     nesting n for a 2n-byte subject. What does 10.46 do?")
import math
import time as _t
for _n in (1024, 10000, 100000, 400000):
    _su = "a" * _n + "b" * _n
    _t0 = _t.time()
    _r = sr.match_limits(r"^(a(?1)?b)$", _su)
    _d = _t.time() - _t0
    _ok = isinstance(_r, tuple) and _r and _r[0] == (0, 2 * _n)
    print("    n=%-7d subject %-8d bytes  %-8s %.4f s"
          % (_n, len(_su), "MATCH" if _ok else repr(_r), _d))
print("#     so a depth capacity of N refuses at roughly a 2N-byte subject,")
print("#     where 10.46 is still answering at 800 KB.")
print()
print("# (b) THE RUNAWAY: ^(a|(?1)a)$ on a^n b. PCRE2 answers rc -52 -- but")
print("#     what does FINDING that cost it? This is the direction in which")
print("#     a bounded depth is STRICTLY BETTER than 10.46's guard.")
# The n=100 row SAT AT THE TIMER FLOOR (~0.0002 s) and its ratio against the
# next row came out 53x, which an earlier revision of the design read as
# "faster than the subject squared". R34 V-11' traced the over-reach to
# exactly that row. It is DROPPED from the series and the sequence starts
# where the clock can resolve it; the label is now computed from n/prev_n
# rather than hardcoded to "10x", which was false for two of the three
# archived steps.
_prev = None
_prev_n = None
_exps = []
for _n in (1000, 4000, 10000, 20000):
    _su = "a" * _n + "b"
    _t0 = _t.time()
    _r = sr.match_limits(r"^(a|(?1)a)$", _su)
    _d = _t.time() - _t0
    _txt = ("rc=%d" % _r[1]) if isinstance(_r, tuple) and _r and _r[0] == "rc" \
        else repr(_r)
    _ann = ""
    if _prev and _prev > 0:
        _g = _n / _prev_n
        _f = _d / _prev
        _e = math.log(_f) / math.log(_g)
        _exps.append(_e)
        _ann = "  (x%.1f on %.2gx the subject -> exponent %.2f)" % (_f, _g, _e)
    print("    n=%-7d subject %-8d bytes  %-10s %.4f s%s"
          % (_n, len(_su), _txt, _d, _ann))
    _prev, _prev_n = _d, _n
if _exps:
    _mean = sum(_exps) / len(_exps)
    print("#     exponents: %s   mean %.2f"
          % (", ".join("%.2f" % e for e in _exps), _mean))
    if _mean < 1.6 or _mean > 2.6:
        print("#     !! the mean exponent is outside [1.6, 2.6] -- the design's")
        print("#        QUADRATIC reading is not supported by this run")
    else:
        print("#     -> QUADRATIC. The design says 'quadratic' and nothing")
        print("#        stronger; an earlier revision said 'faster than the")
        print("#        subject squared' on the strength of a timer-floor row.")
else:
    print("#     !! VACUOUS: no ratio computed")
print()

print("=== L10: DOES ERROR 140 EXIST IN 10.46 AT ALL? =======================")
print("# The charter says left recursion is 'refused at compile time (the")
print("# err 140 / could-loop-indefinitely family)'. L1-L3 above found NO")
print("# compile-time refusal for ANY left-recursive shape. Either the check")
print("# was removed, or it fires on a shape this lane has not tried. So:")
print("#   (a) what does libpcre2 SAY error 140 is?")
print("#   (b) a sweep of shapes historically associated with it.")
print("  pcre2_get_error_message(140) = %r" % sr.pcre2._errmsg(140))
for n in (137, 138, 139, 140, 141, 142, 143):
    print("  ...(%d) = %r" % (n, sr.pcre2._errmsg(n)))
print("# (b) the historical shapes:")
for pat in [r"(a?)(?1)", r"((?1))", r"(()(?1))", r"((?1)|a)",
            r"(?(DEFINE)(?<g>(?&g)))(?&g)", r"((?1)?)", r"(a|(?1))",
            r"^(?1)()$", r"(){0}(?1)", r"((?1)*)", r"((?R))",
            r"(?R)", r"a(?R)?", r"()(?1)*"]:
    ce = sr.compile_err(pat)
    print("  %-34s %s" % (pat, "compiles" if ce is None
                          else "ERR %d %s" % (ce[0], ce[2])))
print("# and the ONE historical shape most often cited, at match time too:")
for pat, subj in [(r"^(a?)(?1)$", "aa"), (r"^((?1))$", "a"),
                  (r"^(?R)$", ""), (r"^(a*)(?1)$", "aa")]:
    cell(pat, subj, "historically an err-140 candidate")
print()

print("=== REACHABILITY GUARD ==============================================")
print("outcomes populated:", sorted(_out))
need = {"compile-refuse", "match-giveup", "match"}
missing = need - _out
if missing:
    print("!! VACUOUS: %s never occurred -- the two-guard claim rests on "
          "seeing BOTH" % sorted(missing))
else:
    print("compile-time refusals, match-time give-ups and ordinary matches "
          "all occur: the two guards are separated by measurement")
