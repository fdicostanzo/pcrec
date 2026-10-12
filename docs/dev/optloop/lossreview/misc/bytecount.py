#!/usr/bin/env python3
"""lossreview/misc: byte-occurrence counts over a set's regenerated throughput
subjects, and the memchr-stop count each byte of a literal would cost.

    bytecount.py BENCHCOPY SET LITERAL_HEX      (SET utf8|litrun)

Prints: byte, occurrences over all throughput subjects (= the stops of a
memchr-for-that-byte scan that restarts after every hit), per literal
position. Subjects are the bench generators' output (sha-checked by manifest
byte-identity in the copy)."""
import os, sys, collections
root, st, hexlit = sys.argv[1:4]
d = os.path.join(root, "bench", st, "throughput")
cnt = collections.Counter(); n = 0
for f in sorted(os.listdir(d)):
    b = open(os.path.join(d, f), "rb").read(); n += len(b); cnt.update(b)
lit = bytes.fromhex(hexlit)
print("subject bytes", n)
seen = set()
for i, c in enumerate(lit):
    print("pos %d byte %02x (%s) stops %d%s" % (i, c, chr(c) if 32 <= c < 127 else "-", cnt[c], "  (dup)" if c in seen else ""))
    seen.add(c)
