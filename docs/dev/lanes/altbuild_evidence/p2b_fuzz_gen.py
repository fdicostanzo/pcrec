"""p2b_fuzz_gen.py SEED N OUT.tsv -- stage 2b's random differential against
libpcre2 (lane altbuild, 2026-11-06). Writes N random alternation patterns,
each with every subject over {a,b,c,d} up to length 3 plus a few longer
ones, as rows for docs/dev/lanes/altrev2_evidence/probe.py (libpcre2 10.46
via ctypes against pcrec `-p rx`, span and every capture compared).

The grammar is built to reach the owner's rules and every adjacency row:
branches of 1-4 items over a small alphabet, so equal widths, shared
prefixes and shared tails are common; items are a letter, a class, an
optional or repeated letter (a repeat contributes no head), `\\K` and
`\\b` (zero-width, read through; `\\K` writes), a capture (writes), a
lookahead with or without a capture, and a nested alternation; a pattern
may continue with a letter or a backreference."""
import itertools, random, sys

LET = "abcd"
def item(r, depth):
    k = r.random()
    if k < 0.45: return r.choice(LET)
    if k < 0.55: return r.choice(["[ab]", "[cd]", "[ac]", "[bd]", "[abc]"])
    if k < 0.62: return r.choice(LET) + r.choice(["?", "+", "*", "{2}"])
    if k < 0.67: return "\\K"
    if k < 0.71: return "\\b"
    if k < 0.78: return "(" + r.choice(LET) + ")"
    if k < 0.82: return "(?=" + r.choice(LET) + ")"
    if k < 0.84: return "(?=(" + r.choice(LET) + "))"
    if k < 0.90 and depth < 2: return "(?:" + alt(r, depth + 1) + ")"
    return r.choice(LET)

def branch(r, depth):
    return "".join(item(r, depth) for _ in range(r.randint(0 if r.random() < 0.08 else 1, 4)))

def alt(r, depth):
    n = r.randint(2, 6)
    bs = [branch(r, depth) for _ in range(n)]
    # bias toward shared prefixes / tails, the factoring rules' food
    if r.random() < 0.4:
        p = r.choice(LET)
        bs = [p + b if r.random() < 0.8 else b for b in bs]
    if r.random() < 0.3:
        t = r.choice(LET)
        bs = [b + t if r.random() < 0.8 else b for b in bs]
    return "|".join(bs)

def pattern(r):
    p = "(?:" + alt(r, 0) + ")"
    k = r.random()
    if k < 0.3: p += r.choice(LET)
    elif k < 0.4 and "(" in p.replace("(?:", "").replace("(?=", ""): p += "\\1?"
    return p

def main():
    seed, n, out = int(sys.argv[1]), int(sys.argv[2]), sys.argv[3]
    r = random.Random(seed)
    subs = [""] + ["".join(t) for L in (1, 2, 3) for t in itertools.product(LET, repeat=L)]
    subs += ["abcd", "dcba", "aabb", "abab", "xabcx"]
    seen = set()
    with open(out, "w") as f:
        f.write("# p2b_fuzz_gen.py seed %d n %d\n" % (seed, n))
        while len(seen) < n:
            p = pattern(r)
            if p in seen: continue
            seen.add(p)
            for s in subs:
                f.write("byte\t%s\t%s\n" % (p, "hex:" + s.encode().hex() if s == "" else s))

main()
