#!/usr/bin/env python3
"""R23-semantics generator, SECOND independent family set.

Aimed at ingredients neither gen_shapes.py nor my own gen_r23.py produces:
  G1  three-arm and four-arm alternations with MORE THAN ONE nullable arm
  G2  nullable bodies under `+` and `{1,n}` (a loop that must iterate once,
      whose body is nullable -- the empty-iteration rule still applies)
  G3  lazy OUTER quantifiers over nullable bodies (`(?:...)*?`, `(?:...){0,3}?`)
  G4  nested lazy/greedy ALTERNATION (a lazy loop preferring exit into a
      greedy loop preferring body, and the mirror)
  G5  character-class bodies and `.`-bodies rather than single letters
  G6  bigger bounded repeats {0,4},{2,4} over nullable bodies
  G7  a nullable loop whose EXIT is followed by a second nullable loop at the
      SAME level, repeated up to 3 times (the S3 shape, generalised)
"""
import itertools, sys
out=[]
def add(p):
    if p not in out: out.append(p)

NUL = ["b*", "b*?", "b?", "b??", "b{0,2}", "b{0,2}?", "(?:b|)", "(?:|b)", "[bc]*", "[bc]*?", ".*?"]
# G1 multi-arm alternations with >1 nullable arm
for x, y in itertools.combinations(NUL[:8], 2):
    add("(?:(?:%s|%s|a)?)*" % (x, y))
    add("(?:(?:a|%s|%s)?)*" % (x, y))
    add("(?:(?:%s|a|%s)?)*" % (x, y))
    add("(?:(?:%s|%s|a|d)?)*" % (x, y))
# G2 nullable body under + / {1,n}
for n in NUL:
    for q in ("+", "+?", "{1,2}", "{1,3}", "{2,3}"):
        add("(?:(?:a|%s)?)%s" % (n, q))
        add("(?:(?:a|%s)%s)*" % (n, q))
# G3 lazy outer
for n in NUL:
    for q in ("*?", "+?", "{0,3}?", "{1,3}?"):
        add("(?:(?:a|%s)?)%s" % (n, q))
        add("(?:(?:%s|a)?)%s" % (n, q))
# G4 nested lazy/greedy alternation
for x, y, z in itertools.product(("*", "*?", "{0,2}", "{0,2}?"), repeat=3):
    add("(?:(?:(?:a|b%s)?)%s)%s" % (x, y, z))
# G5 classes and dot
for at in ("[a-c]", ".", "[^a]", "[ab]"):
    for q in ("*", "*?", "?", "??", "{0,2}", "{0,2}?"):
        add("(?:(?:a|%s%s)?)*" % (at, q))
        add("(?:(?:%s%s|a)?)*" % (at, q))
        add("(?:(?:%s%s)?)*" % (at, q))
# G6 bigger bounded repeats
for n in NUL[:8]:
    for q in ("{0,4}", "{0,4}?", "{2,4}", "{1,4}?"):
        add("(?:(?:a|%s)%s)*" % (n, q))
        add("(?:(?:a|%s)?)%s" % (n, q))
# G7 chains of sibling nullable loops after a K18 loop
K = "(?:(?:a|b*?)?)*"
for t1 in ("c*", "(?:c*)*", "c*?"):
    add("%s%s" % (K, t1))
    add("(?:%s%s)*" % (K, t1))
    for t2 in ("d*", "(?:d|)*"):
        add("%s%s%s" % (K, t1, t2))
        add("(?:%s%s%s)*" % (K, t1, t2))
        add("(?:%s)*%s%s" % (K, t1, t2))
print("\n".join(out))
