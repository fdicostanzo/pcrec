#!/usr/bin/env python3
"""[START-LANDING] exhaustive short subjects for one artifact (STUDY).

    mksubj.py ART.c PREFIX ENC OUT.hex [MAXSUBJ]

The alphabet is one representative byte per byte class of the artifact's
FORWARD machine (`<p>_forward_byte_class[256]`, read from the emitted text),
plus, under utf8, whole tokens: a 2-, 3- and 4-byte character, a lone
continuation byte, a truncated lead and 0xFF (the ill-formed cases the
landing guard exists for). Every string over the alphabet up to the longest
length whose total stays under MAXSUBJ (default 40000) is written, one hex
line each: a machine-derived, pattern-specific exhaustive pool (E9's shape).
"""
import itertools, re, sys

art, P, enc, out = sys.argv[1:5]
cap = int(sys.argv[5]) if len(sys.argv) > 5 else 40000
src = open(art).read()
m = re.search(r"%s_forward_byte_class\[256\] = \{([^}]*)\}" % re.escape(P), src)
toks = []
if m:
    cl = [int(x) for x in m.group(1).replace("\n", " ").split(",") if x.strip()]
    seen = {}
    for b, c in enumerate(cl):
        if c not in seen: seen[c] = b
    reps = sorted(seen.values())
    # prefer printable reps where a class has one (readability only)
    for c in list(seen):
        for b in range(0x20, 0x7f):
            if cl[b] == c: seen[c] = b; break
    reps = sorted(seen.values())
    toks = [bytes([b]) for b in reps]
else:
    toks = [bytes([b]) for b in b"a1 _\n"]
if enc == "utf8":
    toks = [t for t in toks if t[0] < 0x80] + [b"\xc3\xa9", b"\xe2\x82\xac", b"\xf0\x9f\x98\x80", b"\x80", b"\xc3", b"\xff"]
# keep the alphabet small enough for length >= 4
while len(toks) > 9:
    toks = toks[::2] + [t for t in toks[1::2] if t[0] >= 0x80][:2]
L, tot = 0, 1
while tot + len(toks) ** (L + 1) <= cap:
    L += 1; tot += len(toks) ** L
with open(out, "w") as f:
    for n in range(L + 1):
        for w in itertools.product(toks, repeat=n):
            f.write(b"".join(w).hex() + "\n")
print("%d tokens, length <= %d, %d subjects" % (len(toks), L, tot))
