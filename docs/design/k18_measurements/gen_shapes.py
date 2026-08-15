#!/usr/bin/env python3
"""Generate patterns in the K17/K18 SHAPE SPACE, densely.

The K17 entry's own post-mortem is that the general fuzzer needed four
independent draws to land together and hit the class at ~1e-4. A design note
that has to tell one candidate repair from another cannot afford that rate, so
this generator does not sample the base tier — it samples only the ingredients
the two bugs are made of, and it samples them exhaustively at small sizes:

  * nullable quantifiers, greedy and lazy: * *? {0,n} {0,n}? ?? ?
  * alternations with a nullable arm, in both preference orders
  * `?`-wrapped groups (K18's outer shape) and bare groups (K17's)
  * capturing and non-capturing, since K18's family diverges either way
  * one and two levels of nesting, under an outer `*` or `+`

Usage: gen_shapes.py [max] > shapes.txt
"""
import itertools
import sys

QUANT = ["*", "*?", "+", "+?", "?", "??", "{0,2}", "{0,2}?", "{1,2}", "{1,2}?"]
ATOM = ["a", "b", "[a-c]", ".", "[^a]"]

inners = []
for at, q in itertools.product(ATOM, QUANT):
    inners.append(at + q)

# level-1 bodies: an alternation of a plain atom and a quantified atom, both
# orders, plus a concatenation control (K18's own control list says
# concatenation does NOT diverge, so it belongs here as a live negative).
bodies = []
for x in ("a", "a+", "[a-c]"):
    for inner in inners:
        bodies.append("%s|%s" % (x, inner))
        bodies.append("%s|%s" % (inner, x))
        bodies.append("%s%s" % (x, inner))

WRAP = ["(?:%s)", "(%s)", "(?:%s)?", "(%s)?", "(?:%s)??", "(?:%s)*", "(?:%s){0,2}"]
OUTER = ["*", "+", "*?", "+?", "{0,3}", "{1,3}"]

out = []
seen = set()
for body in bodies:
    for w in WRAP:
        mid = w % body
        for o in OUTER:
            p = "(?:%s)%s" % (mid, o)
            if p not in seen:
                seen.add(p)
                out.append(p)

lim = int(sys.argv[1]) if len(sys.argv) > 1 else len(out)
print("\n".join(out[:lim]))
