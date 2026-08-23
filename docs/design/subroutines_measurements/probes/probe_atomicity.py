"""[DD-14] §3 -- CALL ATOMICITY, measured on libpcre2 10.46.

Charter question (ii): PCRE2 changed this across versions -- pre-10.30 a
subroutine call was ATOMIC (its first success was its only success), later
releases made it backtrackable. The answer picks the machinery: an RX_CUT at
the return label is a completely different emitted shape from a return that
leaves the callee's frames live.

THE DISCRIMINATOR has to isolate the CALL. `^(a|ab)(?1)c$` on "ababc" is the
obvious cell and it is NOT a discriminator: the LEXICAL group can retry too,
so a match is explained by either. The isolating form puts the body somewhere
only the call can reach -- `(?(DEFINE)...)`, or a branch guarded by `(?!)` --
so the only choice point in play is the callee's.

Axes:
  T1  the NAIVE cell, and why it decides nothing (both hypotheses match)
  T2  the ISOLATED cell: a DEFINE body, one call, a follow that forces a retry
  T3  the same at DEPTH, where a retreat must cross a return
  T4  ATOMIC controls: (?>...) and a possessive quantifier around the callee,
      so the cells that SHOULD be atomic are shown to be
  T5  quantified calls, and the empty-body guard
  T6  a call INSIDE an atomic group / a lookaround, where the cut is outside
  T7  the SHAPE OF THE COST: how many retries a call can produce
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


def cell(pat, subj, note="", opts=0):
    # match_limits(), not search(): a MATCH-TIME give-up must be a value in
    # the table. `^(?R)*$` on "" raises out of `Compiled.search` with
    # pcre2_match error -52, and a probe that dies at row 40 has measured
    # nothing about rows 41..80.
    r = sr.match_limits(pat, subj, options=opts)
    if isinstance(r, tuple) and r and r[0] == "ERR":
        _out.add("refuse")
        print("  %-44s %-12r ERR %-3d %s" % (pat, subj, r[1][0], r[1][2]))
        return r
    if isinstance(r, tuple) and r and r[0] == "rc":
        _out.add("giveup")
        print("  %-44s %-12r MATCH-TIME rc=%d %s%s"
              % (pat, subj, r[1], sr.pcre2._errmsg(r[1]),
                 ("  # " + note) if note else ""))
        return r
    _out.add("nomatch" if r is None else "match")
    print("  %-44s %-12r %-28r%s"
          % (pat, subj, r, ("  # " + note) if note else ""))
    return r


print("=== T1: the NAIVE cell, which decides NOTHING ========================")
print("# `(a|ab)` is reachable BOTH lexically and by the call, so a match is")
print("# explained by the LEXICAL group retrying and says nothing about the")
print("# call. Recorded so a reader does not mistake it for the evidence.")
cell(r"^(a|ab)(?1)c$", "ababc", "matches under BOTH hypotheses")
cell(r"^(a|ab)(?1)c$", "aabc", "ditto")
print()

print("=== T2: THE ISOLATED CELL -- only the call can reach the body ========")
print("# `(?(DEFINE)(?<g>a|ab))` -- group g NEVER runs lexically, so the only")
print("# alternation frame in existence belongs to the CALL. The follow `c`")
print("# fails after the first alternative and succeeds after the second.")
print("#   ATOMIC          -> nomatch")
print("#   BACKTRACKABLE   -> (0,3)")
cell(r"^(?(DEFINE)(?<g>a|ab))(?&g)c$", "abc", "THE DISCRIMINATOR")
cell(r"^(?(DEFINE)(?<g>a|ab))(?&g)c$", "ac",
     "control: the FIRST alternative already works, so this must match "
     "under both hypotheses")
cell(r"^(?(DEFINE)(?<g>ab|a))(?&g)c$", "ac",
     "branch order reversed: the SECOND alternative is the one needed")
print("# the (?!)-guarded-branch spelling of the same isolation, in case")
print("# DEFINE itself is doing something special:")
cell(r"^(?!)(?<g>a|ab)|^(?&g)c$", "abc", "same question, no DEFINE")
cell(r"^(?!)(?<g>ab|a)|^(?&g)c$", "abc", "reversed, no DEFINE")
print("# and with a QUANTIFIER rather than an alternation as the callee's")
print("# choice point, so the finding is not about alternation:")
cell(r"^(?(DEFINE)(?<g>a+))(?&g)ab$", "aaab",
     "a+ inside the call must give bytes back")
cell(r"^(?(DEFINE)(?<g>a*))(?&g)a$", "aaa", "a* likewise")
cell(r"^(?(DEFINE)(?<g>a{1,3}))(?&g)aa$", "aaa", "a bounded repeat")
print()

print("=== T3: the same at DEPTH -- a retreat that crosses a RETURN =========")
cell(r"^(?(DEFINE)(?<g>a(?&g)?b|x|xy))(?&g)$", "axyb",
     "the retreat has to re-enter the INNER call after the outer returned")
cell(r"^(?(DEFINE)(?<g>a(?&g)?b|x|xy))(?&g)$", "axb", "control, depth 2")
cell(r"^(?(DEFINE)(?<g>(?:x|xy)))(?&g)(?&g)y$", "xxyy",
     "two calls to the same body; the FIRST has to retry")
cell(r"^(?(DEFINE)(?<g>(?:x|xy)))(?&g)(?&g)y$", "xyxy",
     "and here the SECOND has to retry")
print()

print("=== T4: ATOMIC CONTROLS -- shapes that SHOULD refuse to retry ========")
cell(r"^(?(DEFINE)(?<g>(?>a|ab)))(?&g)c$", "abc",
     "the callee body is ATOMIC: expect nomatch")
cell(r"^(?(DEFINE)(?<g>a|ab))(?>(?&g))c$", "abc",
     "the CALL SITE is wrapped in an atomic group: expect nomatch")
cell(r"^(?(DEFINE)(?<g>a|ab))(?&g)++c$", "abc",
     "a possessive quantifier on the call: expect nomatch")
cell(r"^(?(DEFINE)(?<g>a+))(?>(?&g))ab$", "aaab",
     "atomic wrapper around a giving-back callee: expect nomatch")
print()

print("=== T5: QUANTIFIED calls and the empty-body guard ====================")
cell(r"^(?(DEFINE)(?<g>ab))(?&g){2}$", "abab", "a bounded repeat of a call")
cell(r"^(?(DEFINE)(?<g>ab))(?&g)+$", "ababab", "an unbounded repeat")
cell(r"^(?(DEFINE)(?<g>ab))(?&g)*$", "", "zero iterations")
cell(r"^(?(DEFINE)(?<g>a?))(?&g)*$", "aaa",
     "a NULLABLE callee under an unbounded quantifier -- the empty-iteration "
     "guard's territory")
cell(r"^(?(DEFINE)(?<g>))(?&g)*$", "",
     "an EMPTY callee under an unbounded quantifier")
cell(r"^(a?)(?1)*$", "aaa", "the same without DEFINE")
cell(r"^(?R)*$", "", "recursion under a quantifier: legal at all?")
cell(r"^(?R)?$", "", "and under ?")
cell(r"^(?R)$", "", "and bare")
cell(r"^a(?R)*b$", "aabb", "with something consumed before it")
cell(r"^(?(DEFINE)(?<g>))(?&g)*$", "",
     "an EMPTY callee under * -- the same shape without (?R)")
cell(r"^(?(DEFINE)(?<g>(?&g)?))(?&g)$", "",
     "a callee that recurses at the same position, no quantifier")
cell(r"^(a(?R)?b)*$", "abab", "(?R) under a quantifier, with a base case")
cell(r"^(a(?R)*b)$", "ab", "a recursive call under a * inside the body")
print()

print("=== T6: a call INSIDE an atomic group, a lookaround, a lookbehind ====")
cell(r"^(?(DEFINE)(?<g>a|ab))(?=(?&g)c)abc$", "abc",
     "the call lives inside a positive lookahead")
cell(r"^(?(DEFINE)(?<g>a|ab))(?!(?&g)c)abd$", "abd",
     "and a negative one")
cell(r"^(?(DEFINE)(?<g>ab))x(?<=(?&g))$", "xab",
     "a call inside a LOOKBEHIND: what does 10.46 say about the width?")
cell(r"^(?(DEFINE)(?<g>ab))ab(?<=(?&g))$", "ab",
     "a fixed-width call inside a lookbehind")
cell(r"^(?(DEFINE)(?<g>a|ab))ab(?<=(?&g))$", "ab",
     "a VARIABLE-width call inside a lookbehind")
cell(r"^(?(DEFINE)(?<g>a+))aa(?<=(?&g))$", "aa",
     "an unbounded-width call inside a lookbehind")
cell(r"^(?(DEFINE)(?<g>ab))(?>(?&g))$", "ab", "inside an atomic group")
cell(r"^(?(DEFINE)(?<g>\Kab))(?&g)$", "ab", "a \\K reached only by a call")
print()

print("=== T7: the SHAPE OF THE COST -- retries a call can produce ==========")
print("# If a call is backtrackable, a call to a body with k alternatives")
print("# inside a follow that fails costs k attempts, and n calls in")
print("# sequence cost k^n. Measured by the SMALLEST match_limit that still")
print("# reaches the answer -- PCRE2's own count of backtracks.")


def limit_of(pat, subj, lo=1, hi=50000000):
    top = sr.match_limits(pat, subj, match=hi)
    if top is None:
        return ("nomatch-at-hi", None)
    if isinstance(top, tuple) and top and top[0] in ("ERR", "rc"):
        return (top[0], top[1])
    a, b = lo, hi
    while a < b:
        mid = (a + b) // 2
        r = sr.match_limits(pat, subj, match=mid)
        ok = not (r is None or (isinstance(r, tuple) and r and r[0] == "rc"))
        if ok:
            b = mid
        else:
            a = mid + 1
    return ("limit", a)


# THE FIRST VERSION OF THIS AXIS MEASURED NOTHING, and it is left in the
# text because the shape is the one this project keeps re-finding: the body
# was `a|b|c|d|e|f|g|h` and the subject picked the LAST alternative, so every
# call succeeded on its 8th try and NO call was ever RE-ENTERED after a
# failing follow. The numbers came out LINEAR (8n+2) and the "atomic control"
# came out HIGHER than the backtrackable one -- a confident wrong number of
# exactly the shape the reachability rule exists to catch.
#
# The retry-forcing shape: a body preferring the SHORT alternative, and a
# follow that only succeeds when EVERY call took the LONG one. That is the
# LAST combination the search reaches, so n calls cost 2^n.
_two = r"(?(DEFINE)(?<g>a|aa))"
print("# (a) n CALLS to a 2-way body, only the all-long combination works:")
_calls = []
for n in range(1, 9):
    pat = "^" + _two + "(?&g)" * n + "b$"
    subj = "a" * (2 * n) + "b"
    r = limit_of(pat, subj)
    _calls.append(r[1] if r[0] == "limit" else None)
    print("  n=%d: %r   (subject %d bytes)" % (n, r, len(subj)))
print("# (b) THE CONTROL: the same language with the body INLINED n times,")
print("#     no calls at all. If (a) and (b) track, a call costs what its")
print("#     body costs and nothing more.")
_inline = []
for n in range(1, 9):
    pat = "^" + "(?:a|aa)" * n + "b$"
    subj = "a" * (2 * n) + "b"
    r = limit_of(pat, subj)
    _inline.append(r[1] if r[0] == "limit" else None)
    print("  n=%d: %r" % (n, r))
print("# (c) the RATIO, call / inlined:")
for n in range(1, 9):
    a, b = _calls[n - 1], _inline[n - 1]
    print("  n=%d  calls=%-8s inlined=%-8s ratio=%s"
          % (n, a, b, "%.3f" % (a / b) if a and b else "n/a"))
print("# (d) REACHABILITY: the sequence must GROW, or no retry happened.")
if _calls[0] and _calls[-1] and _calls[-1] > 4 * _calls[0]:
    print("  the call series grew %dx from n=1 to n=8 -- retries ARE being "
          "forced" % (_calls[-1] // _calls[0]))
else:
    print("  !! the call series did not grow: this axis measured no retry")
print()
print("# (e) and a RECURSIVE body, where the retry crosses a return:")
for n in range(1, 7):
    pat = r"^(?(DEFINE)(?<g>(?:a|aa)(?&g)?))(?&g)b$"
    subj = "a" * (2 * n) + "b"
    print("  depth<=%d (subject %2d bytes): %r"
          % (n, len(subj), limit_of(pat, subj)))
print()

print("=== REACHABILITY GUARD ==============================================")
print("outcomes populated:", sorted(_out))
missing = {"match", "nomatch"} - _out
if missing:
    print("!! VACUOUS: %s never occurred" % sorted(missing))
else:
    print("both match and no-match occur: the atomicity cells are separating "
          "two answers, not reporting one")
