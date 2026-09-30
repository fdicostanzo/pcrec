#!/usr/bin/env python3
"""[PF-KNOW] the two match-dense synthetic subjects of results/twins.md and
the sparse `secrets.bin` (the capability t-1m text with one token every
4 KB).  Deterministic (seeded); writes into the directory given.

    python3 gen_dense.py OUTDIR [/path/to/pcrec-bench/bench/capability/throughput/t-1m.bin]
"""
import os, random, sys

A = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
U = "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"

def tok(rng, n, al=A): return "".join(rng.choice(al) for _ in range(n))

def token(rng, k):
    if k == 0: return "github_pat_" + tok(rng, 82, A + "_")
    if k == 1: return "https://hooks.slack.com/services/T" + tok(rng, 8) + "/B" + tok(rng, 10) + "/" + tok(rng, 24)
    return "AKIA" + tok(rng, 16, U)

def main():
    out = sys.argv[1]; os.makedirs(out, exist_ok=True)
    # secrets_dense.bin: 6,000 tokens, " x " between (seed 11)
    rng = random.Random(11); parts = []
    for i in range(6000): parts.append(token(rng, i % 3)); parts.append(" x ")
    open(os.path.join(out, "secrets_dense.bin"), "w").write("".join(parts))
    # sshd_dense.bin: 60,000 lines `sshd[N]: word` (same rng, continued)
    lines = ["sshd[%d]: %s\n" % (rng.randint(1, 99999), tok(rng, rng.randint(3, 12))) for _ in range(60000)]
    open(os.path.join(out, "sshd_dense.bin"), "w").write("".join(lines))
    # secrets.bin: the bench's t-1m with one token per 4 KB (seed 7)
    if len(sys.argv) > 2:
        rng = random.Random(7); b = open(sys.argv[2], "rb").read(); o = bytearray(); pos = 0; i = 0
        while pos < len(b):
            o += b[pos:pos + 4096]; pos += 4096
            o += (" " + token(rng, i % 3) + " ").encode(); i += 1
        open(os.path.join(out, "secrets.bin"), "wb").write(o)

if __name__ == "__main__":
    main()
