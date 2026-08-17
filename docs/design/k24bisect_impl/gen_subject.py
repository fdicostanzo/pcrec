#!/usr/bin/env python3
# Generates the case-(c) subject exactly as tests/bench/compare/compare.sh's
# embedded subject-generation script does: same rng seed (1729), same
# rand_lower() draws for cases (a) and (b) consumed FIRST (to land at the
# same point in the rng stream before drawing (c)'s buffer -- the three
# cases share one random.Random(1729) instance in compare.sh, in this
# order), then purge_words() on the (alpha|beta|gamma|delta|epsilon) word
# list. Bit-for-bit identical to compare.sh's c_alt_absent.bin. Run once;
# the bisect probe caches the result and skips regeneration.
import random, sys, os

outdir = sys.argv[1]
MB = 1024 * 1024
LOWER = b"abcdefghijklmnopqrstuvwxyz"

def rand_lower(rng, n):
    return bytes(rng.choices(LOWER, k=n))

def purge_words(buf, words):
    passes = 0
    while passes < 200:
        passes += 1
        s = bytes(buf)
        any_hit = False
        for w in words:
            idx = s.find(w)
            while idx != -1:
                any_hit = True
                mid = idx + len(w) // 2
                target_letter = w[len(w) // 2:len(w) // 2 + 1]
                for repl in LOWER:
                    if bytes([repl]) != target_letter:
                        buf[mid] = repl
                        break
                s = bytes(buf)
                idx = s.find(w, idx + 1)
        if not any_hit:
            break
    else:
        raise RuntimeError("purge_words: did not converge after 200 passes")
    return buf

rng = random.Random(1729)
n = 8 * MB

# (a) draw, consumed and discarded -- keeps the rng stream position
# identical to compare.sh's, which draws (a) then (b) then (c).
_ = rand_lower(rng, n)

# (b) draw + its (never-taken, ~1e-8 odds) needle-collision fixup loop.
buf_b = bytearray(rand_lower(rng, n))
needle = b"needleXYZW"
s = bytes(buf_b)
if needle in s:
    while needle in bytes(buf_b):
        idx = bytes(buf_b).find(needle)
        buf_b[idx] = LOWER[(LOWER.index(buf_b[idx]) + 1) % 26]

# (c) the actual subject this probe measures against.
words = [b"alpha", b"beta", b"gamma", b"delta", b"epsilon"]
buf = bytearray(rand_lower(rng, n))
purge_words(buf, words)
with open(os.path.join(outdir, "c_alt_absent.bin"), "wb") as f:
    f.write(buf)

print("subject generated:", os.path.join(outdir, "c_alt_absent.bin"), len(buf), "bytes")
