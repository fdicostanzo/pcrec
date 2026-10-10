#!/usr/bin/env python3
"""docs/dev/optloop/et1twin/gen_adv.py -- adversarial subjects per cell for
the identity check, aimed at the reverse-inner tactic's own edges rather
than at the bench's text: landmark-dense runs, overlapping and adjacent
occurrences, starts clipped by search_from, P runs longer than P's bound,
landmarks with an empty starts(j), verifies that fail after a non-empty
starts(j), and the subject's first/last bytes.

    gen_adv.py CELL BENCH OUTDIR [COUNT]

Deterministic (seeded by the cell name). Writes OUTDIR/adv_NNNN.bin."""
import os, random, sys

cell, bench, out = sys.argv[1], sys.argv[2], sys.argv[3]
count = int(sys.argv[4]) if len(sys.argv) > 4 else 400
r = random.Random("et1twin-" + cell)
os.makedirs(out, exist_ok=True)


def ipv6():
    hexd = "0123456789abcdef"
    toks = [lambda: "".join(r.choice(hexd) for _ in range(r.randint(1, 6))), lambda: ":",
            lambda: "::", lambda: r.choice(" g\nG-.x"), lambda: "fe80::1", lambda: "2001:db8:0:0:1:0:0:1",
            lambda: ":".join("".join(r.choice(hexd) for _ in range(r.randint(1, 5))) for _ in range(r.randint(2, 9)))]
    return "".join(r.choice(toks)() for _ in range(r.randint(0, 40))).encode()


def kvq():
    toks = [lambda: "".join(r.choice("abz_09") for _ in range(r.randint(1, 40))), lambda: '="',
            lambda: '"', lambda: "=", lambda: "\\", lambda: '\\"', lambda: r.choice(" -.:\n"),
            lambda: 'key="v"', lambda: 'a="x\\"y"', lambda: "_" * r.randint(1, 34)]
    return "".join(r.choice(toks)() for _ in range(r.randint(0, 30))).encode()


def sfx64():
    pat = open(os.path.join(bench, "bench/altwide/patterns/sfx-64.rx")).read().strip()
    words = pat[3:-1].split("|")
    stems = [w[:-3] for w in words]
    toks = [lambda: r.choice(words), lambda: r.choice(stems), lambda: "ing", lambda: "in", lambda: "g",
            lambda: "".join(r.choice("abcdefghijklmnopqrstuvwxyz") for _ in range(r.randint(1, 6))),
            lambda: r.choice(" \n.-"), lambda: r.choice(stems)[r.randint(0, 2):] + "ing",
            lambda: r.choice(stems) + "inging"]
    return "".join(r.choice(toks)() for _ in range(r.randint(0, 25))).encode()


gen = {"ipv6": ipv6, "kvq": kvq, "sfx64": sfx64}[cell]
for i in range(count):
    open(os.path.join(out, "adv_%04d.bin" % i), "wb").write(gen())
