#!/usr/bin/env python3
"""segment_sym.py [MAXLEN] -- the island's FORWARD and BACKWARD character
segmentations agree (ucp_design.md s3.5).  Forward: the stage-4 decoder at
each position; an ill-formed start consumes ONE byte as the pseudo-character
BOTTOM.  Backward: pcrec's repaired back_step (walk over continuation bytes
to the nearest non-continuation byte, which must decode to a character
whose length is EXACTLY the run walked), else BOTTOM consumes one byte.
Exhaustive over every string up to MAXLEN (default 5) from a boundary-byte
alphabet.  Controls, in the failing direction: the UNREPAIRED back_step
(utf8_design.md s5.2's first body) and a forward decoder that skips a whole
truncated run instead of one byte must each DISAGREE somewhere."""
import itertools, sys
sys.path.insert(0, __file__.rsplit("/", 1)[0])
from bottom_model import dec   # the one decoder, not a copy
A = [0x41, 0x80, 0x97, 0x9F, 0xA0, 0xA9, 0xBF, 0xC0, 0xC2, 0xC3, 0xDF, 0xE0, 0xE2, 0xE6, 0xED, 0xEF, 0xF0, 0xF4, 0xF5, 0xFF]
def fwd(b, skip_run=False):
    out, i = [], 0
    while i < len(b):
        r = dec(b, i)
        if r: out.append((i, i + r[1])); i += r[1]
        else:
            j = i + 1
            if skip_run:
                while j < len(b) and b[j] & 0xC0 == 0x80: j += 1
            out.append((i, j)); i = j
    return out
def bwd(b, unrepaired=False):
    out, p = [], len(b)
    while p > 0:
        q = p - 1
        while q > 0 and b[q] & 0xC0 == 0x80: q -= 1
        r = dec(b, q)
        if unrepaired and b[q] & 0xC0 != 0x80:
            r2 = dec(b + b"\x80\x80\x80", q); ok = r2 is not None
            n = r2[1] if ok else 0
            if ok and q + n >= p: out.append((q, p)); p = q; continue
        if r and q + r[1] == p: out.append((q, p)); p = q
        else: out.append((p - 1, p)); p -= 1
    return out[::-1]
MAX = int(sys.argv[1]) if len(sys.argv) > 1 else 5
n = bad = cb1 = cb2 = 0
for L in range(MAX + 1):
    for t in itertools.product(A, repeat=L):
        b = bytes(t); n += 1
        f = fwd(b)
        if f != bwd(b): bad += 1; print("DISAGREE", b.hex(), f, bwd(b)) if bad < 5 else None
        if f != bwd(b, unrepaired=True): cb1 += 1
        if fwd(b, skip_run=True) != bwd(b): cb2 += 1
print("#strings %d (alphabet %d, len 0..%d): forward==backward on all but %d" % (n, len(A), MAX, bad))
print("#control unrepaired back_step disagrees on %d; control run-skipping forward disagrees on %d" % (cb1, cb2))
