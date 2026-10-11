#!/usr/bin/env python3
"""docs/dev/optloop/rlhtwin/gen_adv.py -- adversarial subjects per cell for
the one-byte handoff's identity check, aimed at the handoff's own edges:
the landmark at exactly K / K+1 bytes after a can-begin run (the c - K
boundary), landmark-dense runs, start-set runs longer than K before a
landmark (the attempt that must begin below c - K is NOT a match), the
landmark as the subject's first/last byte, and, for the re-entered form
(h2), many dead landmarks between matches so the restart point fires
repeatedly. ipv6 keeps et1twin's token set (same seed) and adds these.

    gen_adv.py CELL OUTDIR [COUNT]

Deterministic (seeded by the cell name). Writes OUTDIR/adv_NNNN.bin."""
import os, random, sys

cell, out = sys.argv[1], sys.argv[2]
count = int(sys.argv[3]) if len(sys.argv) > 3 else 400
r = random.Random("rlhtwin-" + cell)
os.makedirs(out, exist_ok=True)
hexd = "0123456789abcdef"


def hx(lo, hi):
    return "".join(r.choice(hexd) for _ in range(r.randint(lo, hi)))


def ipv6():
    toks = [lambda: hx(1, 6), lambda: ":", lambda: "::", lambda: r.choice(" g\nG-.x"),
            lambda: "fe80::1", lambda: "2001:db8:0:0:1:0:0:1",
            lambda: ":".join(hx(1, 5) for _ in range(r.randint(2, 9))),
            lambda: hx(4, 4) + ":", lambda: hx(5, 9) + ":" + hx(1, 4),      # K / beyond-K edge
            lambda: "12:34:56", lambda: ":" * r.randint(2, 9),
            lambda: ":".join(hx(1, 4) for _ in range(r.randint(7, 9)))]
    return "".join(r.choice(toks)() for _ in range(r.randint(0, 40))).encode()


def ipv4():
    def octet():
        return str(r.choice([r.randint(0, 9), r.randint(10, 99), r.randint(100, 255),
                             r.randint(256, 999), r.randint(1000, 99999)]))
    toks = [octet, lambda: ".", lambda: "..", lambda: r.choice(" a\n-:x0"),
            lambda: ".".join(octet() for _ in range(r.randint(2, 6))),
            lambda: "192.168.1.17", lambda: "10.0.0.256", lambda: "1.2.3",
            lambda: "0" * r.randint(1, 6) + ".", lambda: "255.255.255.255",
            lambda: "v1.2.3-rc.4", lambda: "." * r.randint(2, 7),
            lambda: str(r.randint(1000, 9999)) + "." + octet()]   # digits beyond K before '.'
    return "".join(r.choice(toks)() for _ in range(r.randint(0, 40))).encode()


gen = {"ipv6": ipv6, "ipv4": ipv4}[cell]
for i in range(count):
    open(os.path.join(out, "adv_%04d.bin" % i), "wb").write(gen())
