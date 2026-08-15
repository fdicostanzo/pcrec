#!/usr/bin/env python3
"""R23-semantics INDEPENDENT shape generator.

Written after reading gen_shapes.py specifically so as NOT to share its
skeleton.  gen_shapes.py emits exactly `(?: WRAP( X | Yq ) )OUTER` — one
quantified atom, one plain atom, at most two loop levels, and NOTHING
concatenated after the inner group inside the outer loop.  The families below
are chosen to be the ones that skeleton structurally cannot produce:

  F1  SEQ   : a K18-shaped inner loop FOLLOWED by a second loop, both inside
              an outer loop.  This is the shape that makes an inner redirect
              truncate the open-loop stack and then PUSH over the truncated
              slots (the S1 hypothesis).
  F2  DEEP  : three levels of loop nesting with the K18 lazy shape at the
              bottom -- gen_shapes tops out at two.
  F3  SIB   : two sibling nullable quantifiers inside one loop body.
  F4  EMPTY : bodies with an EMPTY alternative `(?:a|)`, which is a nullable
              arm that is not a quantifier at all.
  F5  ANCH  : `^`/`$` inside a {0,n} or starred body (N_BOT/N_EOL are the two
              closure cases that can also stop a walk).
  F6  BREP  : {0,n} bodies wrapping the SEQ and DEEP shapes (the `{0,2}`
              sub-case that refuted candidate B, crossed with F1/F2).
"""
import itertools
import sys

LAZY = ["b*?", "b??", "b{0,2}?", "(?:b|)"]
GREEDY = ["b*", "b?", "b{0,2}"]
NULL = LAZY + GREEDY

INNER_ALT = []
for n in NULL:
    INNER_ALT.append("a|%s" % n)
    INNER_ALT.append("%s|a" % n)

WRAPQ = ["*", "+", "{0,2}", "{1,2}", "?", "*?"]
SECOND = ["c*", "c*?", "(?:c)*", "(?:c*)*", "c{0,2}", "(?:c|)*", "c?"]

out = []


def add(p):
    if p not in out:
        out.append(p)


# F1 SEQ: (?: (?:(?:ALT)?)Q  SECOND )*      -- inner K18 loop then a 2nd loop
for alt in INNER_ALT:
    for q in ("*", "+", "{0,2}"):
        for sec in SECOND:
            add("(?:(?:(?:%s)?)%s%s)*" % (alt, q, sec))
            add("(?:%s(?:(?:%s)?)%s)*" % (sec, alt, q))

# F2 DEEP: three loop levels
for alt in INNER_ALT:
    for q in ("*", "+", "{0,2}"):
        for mid in ("(?:%s)*", "(?:%s)+", "(?:%s){0,2}", "(?:%s)*?"):
            add("(?:%s)*" % (mid % ("(?:(?:%s)?)%s" % (alt, q))))

# F3 SIB: two sibling nullable quantifiers in one body
for x, y in itertools.product(NULL, NULL):
    add("(?:(?:%s)(?:%s))*" % (x, y))
    add("(?:(?:%s|a)(?:%s|d))*" % (x, y))
    add("(?:(?:%s)(?:%s)a?)*" % (x, y))

# F4 EMPTY alternatives
for q in WRAPQ:
    add("(?:(?:a|)%s)*" % q)
    add("(?:(?:|a)%s)*" % q)
    add("(?:(?:a|(?:b|))%s)*" % q)
    add("(?:(?:(?:b|)|a)%s)*" % q)
    add("(?:(?:a|b*?|)%s)*" % q)

# F5 ANCH: anchors inside nullable bodies
for a in ("^", "$", "^a", "a$"):
    for q in ("*", "{0,2}", "?"):
        add("(?:(?:%s|b*?)%s)*" % (a, q))
        add("(?:(?:b*?|%s)%s)*" % (a, q))
        add("(?:(?:a|b*?)%s%s)*" % (q, a))

# F6 BREP: {0,n} wrappers crossed with F1/F2 shapes
for alt in INNER_ALT[:8]:
    for sec in ("c*", "(?:c*)*"):
        add("(?:(?:(?:%s)?){0,2}%s){0,2}" % (alt, sec))
        add("(?:(?:(?:(?:%s)?){0,2})*%s)*" % (alt, sec))

lim = int(sys.argv[1]) if len(sys.argv) > 1 else len(out)
print("\n".join(out[:lim]))
