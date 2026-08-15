#!/usr/bin/env python3
"""R23-semantics RANDOM grammar generator. Deliberately recursive and
unstructured, so it is not a family list at all: any nesting of loops,
alternations, options and bounded repeats over a small alphabet, biased hard
towards NULLABLE bodies (which is the only thing K17/K18 need) but with no
fixed skeleton. Usage: gen_rand.py SEED N > pats"""
import random, sys
seed, n = int(sys.argv[1]), int(sys.argv[2])
rng = random.Random(seed)
ATOM = ["a", "b", "c", "[ab]", "[a-c]", ".", "[^a]", "d"]
QUANT = ["*", "*?", "+", "+?", "?", "??", "{0,2}", "{0,2}?", "{0,3}",
         "{1,2}", "{1,2}?", "{2,3}", "{0,4}?", ""]

def gen(depth):
    r = rng.random()
    if depth <= 0 or r < 0.28:
        return rng.choice(ATOM) + rng.choice(QUANT)
    if r < 0.50:                                   # alternation, 2-4 arms
        k = rng.randint(2, 4)
        arms = [gen(depth - 1) for _ in range(k)]
        if rng.random() < 0.25:
            arms[rng.randrange(k)] = ""            # an EMPTY alternative
        return "(?:" + "|".join(arms) + ")" + rng.choice(QUANT)
    if r < 0.72:                                   # concatenation
        k = rng.randint(2, 3)
        return "(?:" + "".join(gen(depth - 1) for _ in range(k)) + ")" + rng.choice(QUANT)
    if r < 0.86:                                   # capturing group
        return "(" + gen(depth - 1) + ")" + rng.choice(QUANT)
    return "(?:" + gen(depth - 1) + ")" + rng.choice(QUANT)

out = set()
while len(out) < n:
    p = gen(rng.randint(2, 4))
    if rng.random() < 0.12: p = "^" + p
    if rng.random() < 0.08: p = p + "$"
    if 3 <= len(p) <= 120:
        out.add(p)
print("\n".join(sorted(out)))
