#!/usr/bin/env python3
"""Generate the patterns that are supposed to make a path-sensitive closure
memo blow up, so the design note's cost claim is a measurement and not a hope.

Families:
  nest<N>      (?:(?: ... (?:a*)* ... )*)*        — N nested nullable stars
  nestlazy<N>  the same with lazy inner quantifiers (K17/K18's own shape)
  chain<N>     (?:a*|b*)(?:a*|b*)...              — N sibling nullable loops
  bounded<N>   (?:a*|b*){N}                       — the entry's named worry
  altnest<N>   (?:a|b*?)? nested N deep, K18's diverging shape scaled up
  wide<N>      (?:a1*|a2*|...|aN*)*               — one loop, N nullable arms

Usage: gen_adversarial.py > adversarial.txt
"""
import sys


def nest(n, inner="a*", lazy=False):
    q = "*?" if lazy else "*"
    s = inner
    for _ in range(n):
        s = "(?:%s)%s" % (s, q)
    return s


out = []
for n in range(1, 13):
    out.append(("nest%d" % n, nest(n)))
    out.append(("nestlazy%d" % n, nest(n, "a*?", lazy=True)))
for n in range(1, 13):
    out.append(("chain%d" % n, "".join("(?:a*|b*)" for _ in range(n))))
for n in (2, 4, 8, 12, 16, 20, 24, 32, 48, 64):
    out.append(("bounded%d" % n, "(?:a*|b*){%d}" % n))
for n in range(1, 11):
    s = "a"
    for _ in range(n):
        s = "(?:%s|b*?)?" % s
    out.append(("altnest%d" % n, s + "*"))
for n in (2, 4, 8, 16, 32, 64):
    out.append(("wide%d" % n,
                "(?:" + "|".join("[%s]*" % chr(ord('a') + (i % 26)) for i in range(n)) + ")*"))
# K18's own diverging family, nested
for n in range(1, 9):
    s = "(?:a|b*?)?"
    for _ in range(n):
        s = "(?:%s|c*?)?" % s
    out.append(("k18nest%d" % n, s + "*"))

for name, p in out:
    print(p)
    print("# %s" % name, file=sys.stderr)
