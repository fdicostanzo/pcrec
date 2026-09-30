#!/usr/bin/env python3
"""studies/hyb_reseed_cal/subjects.py — regenerate every subject the
[OPT-HYB-RESEED] calibration and timing tables name. Deterministic: the
same output on every run (fixed seeds, no clock).

usage: subjects.py OUTDIR

Families (1 MiB unless noted):
  gapG        a failing candidate `x` every G bytes, filler `y`
              (G in 1..1024); the crossover sweeps' subjects
  dense_sparse / sparse_dense   gap-2 candidates for half, then filler
  bursty      64 gap-2 candidates, then 4,096 filler, repeated
  advG        the alternating adversary: `xx` then G filler, repeated
  cjkG        (?<!日)本's failing candidate `日本` after G-1 filler `語`
  synth-1m / synth-64k-asc / synth-dense   I-114's three subjects
              (docs/dev/utf8_attrib_twin/I-114.md, same seeds)
  lka_sparse / lka_dense   `item(?= done)` prose: word streams in which
              `item` is rare / frequent and `item done` rarer still
  clampG      the clamped-family subjects for r1 sem F1 (units below,
              one per G bytes, filler `y`): see clamped.md

The lka_* pair and synth-* are seeded word/character streams; the lane
`reseed` scratch copies of lka_* were produced by an earlier seed, so the
2026-09-29 table's lka rows are the same RECIPE, a different realization.
"""
import os, random, sys

N = 1 << 20


def rep(unit, n=N):
    return (unit * (n // len(unit) + 1))[:n]


def gap(g, filler=b"y", cand=b"x"):
    return rep(filler * (g - 1) + cand)


def words(seed, vocab, weights, n=N):
    rng = random.Random(seed)
    out, size = [], 0
    while size < n:
        w = rng.choices(vocab, weights)[0]
        out.append(w); size += len(w) + 1
    return (" ".join(out)).encode()[:n]


COMMON = ["the", "and", "to", "in", "of", "is", "an", "one", "that", "be",
          "their", "this", "these", "by", "some", "for", "as", "was", "not",
          "two", "only", "but", "at", "which", "from", "all", "its", "have",
          "or", "has", "can", "also", "would", "other", "are", "into", "with",
          "more", "it"]


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "."
    os.makedirs(out, exist_ok=True)
    w = lambda name, data: open(os.path.join(out, name + ".bin"), "wb").write(data)
    for g in [1, 2, 3, 4, 6, 8, 12, 16, 24, 32, 48, 64, 128, 256, 1024]:
        w(f"gap{g}", gap(g))
    w("dense_sparse", gap(2)[:N // 2] + b"y" * (N // 2))
    w("sparse_dense", b"y" * (N // 2) + gap(2)[:N // 2])
    w("bursty", rep(gap(2)[:128] + b"y" * 4096))
    for g in [8, 16, 32, 64, 128, 256]:
        w(f"adv{g}", rep(b"xx" + b"y" * g))
    for g in [1, 2, 3, 4, 6, 8, 12, 16, 32, 64]:
        w(f"cjk{g}", rep(("語" * (g - 1) + "日本").encode()))
    # I-114's generators, verbatim seeds (docs/dev/utf8_attrib_twin/I-114.md)
    sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
    import gen114
    w("synth-1m", gen114.gen_mixed_1m())
    w("synth-64k-asc", gen114.gen_64k_ascii())
    w("synth-dense", gen114.gen_match_dense())
    # item(?= done): sparse = rare `item`, rarer `done`; dense = frequent both
    w("lka_sparse", words(7101, COMMON + ["item", "done"], [10] * len(COMMON) + [2, 2]))
    w("lka_dense", words(7102, COMMON + ["item", "done"], [2] * len(COMMON) + [40, 12]))
    # r1 sem F1: the clamped over-approximating family (clamped.md)
    for name, unit in (("aab", b"aab"), ("xabd", b"xabd"), ("abc", b"abc")):
        for g in [1, 2, 4, 8, 16, 64]:
            w(f"clamp_{name}_{g}", rep(unit + b"y" * (g - 1)))


if __name__ == "__main__":
    main()
