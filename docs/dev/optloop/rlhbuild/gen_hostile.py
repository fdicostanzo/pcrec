#!/usr/bin/env python3
"""docs/dev/optloop/rlhbuild/gen_hostile.py -- the K-admission cells'
subjects: landmark-DENSE text, where the landmark recurs far closer than K
(Frank's `a.{1,50000}z` over z-dense text, and the DFA-route witnesses
`[a-y]\\d{0,N}:` over ':'-dense digit text). Sizes 4 KiB .. 1 MiB so a time
per byte that does not grow with n is the linearity reading; plus small
adversarial subjects for identity.

    gen_hostile.py OUTDIR

Deterministic. Writes OUTDIR/{z,colon}-NNNNk.bin and OUTDIR/adv_NNNN.bin."""
import os, random, sys

out = sys.argv[1]
os.makedirs(out, exist_ok=True)
r = random.Random("rlhbuild-hostile")


def zdense(n):
    b = bytearray()
    while len(b) < n:
        b += r.choice([b"z", b"zz", b"a", b"x", b"za", b" ", b"azz"])
    return bytes(b[:n])


def colondense(n):
    b = bytearray()
    while len(b) < n:
        b += r.choice([b":", b"1", b"23", b"a1:", b"b", b"::", b" ", b"q9"])
    return bytes(b[:n])


for kib in (4, 64, 1024):
    open(os.path.join(out, "z-%04dk.bin" % kib), "wb").write(zdense(kib * 1024))
    open(os.path.join(out, "colon-%04dk.bin" % kib), "wb").write(colondense(kib * 1024))
for i in range(200):
    f = zdense if i % 2 else colondense
    open(os.path.join(out, "adv_%04d.bin" % i), "wb").write(f(r.randint(0, 300)))
