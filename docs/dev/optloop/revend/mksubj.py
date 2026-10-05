#!/usr/bin/env python3
"""[OPT-REVEND] deterministic 1 MiB prose-like subjects (SCRATCH tier, NOT the
bench's t-1m): words, digits, punctuation, a newline about every 60 bytes,
seeded.  Writes <dir>/{nomatch,match}.bin:
  nomatch  ends in 'end.'   (no `\\d+$`, `\\w+$`, `\\s+$` match at the end)
  match    ends in ' 4242' / 'tail' variants chosen per pattern by the driver
"""
import random, sys, os
d = sys.argv[1]
rnd = random.Random(20261005)
words = ["alpha", "beta", "gamma", "delta", "the", "of", "and", "item", "42", "7",
         "log", "error", "warn", "file.txt", "path/to", "x=1", "done", "user", "id"]
out = bytearray(); col = 0
while len(out) < (1 << 20) - 64:
    w = rnd.choice(words).encode()
    out += w; col += len(w)
    if col > 60:
        out += b"\n"; col = 0
    else:
        out += b" "; col += 1
body = bytes(out[: (1 << 20) - 64])
os.makedirs(d, exist_ok=True)
for name, tail in (("nomatch", b" end."), ("match_digits", b" 4242"),
                   ("match_word", b" tail"), ("match_ws", b" end.   "),
                   ("match_txt", b" see log.txt")):
    open(os.path.join(d, name + ".bin"), "wb").write((body + tail)[: (1 << 20)])
