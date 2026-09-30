#!/usr/bin/env python3
# I-114's deterministic subject generators (lane reseedtwin, copied verbatim
# from the reseed lane scratch; docs/dev/utf8_attrib_twin/I-114.md).
import random

SEED = 20260927

def gen_mixed_1m(seed=SEED):
    """~1 MiB mixed subject: ASCII prose with 'a'/'x'-bearing words, a
    minority of accented Latin words, and a CJK-word minority."""
    rng = random.Random(seed)
    ascii_words = ["the","quick","brown","fox","jumps","over","lazy","dog",
                   "cat","apple","exit","axiom","next","index","excess",
                   "extra","annex","exam","text","context","example"]
    latin_extra = ["café","déjà","naïve","élan","exposé","protégé"]
    cjk_words = ["日本語","東京都","本州","京都府","本日","日本"]
    out, size, target = [], 0, 1_000_000
    while size < target:
        r = rng.random()
        if r < 0.85:   w = rng.choice(ascii_words)
        elif r < 0.95: w = rng.choice(latin_extra)
        else:          w = rng.choice(cjk_words)
        out.append(w); out.append(" ")
        size += len(w.encode("utf-8")) + 1
    return "".join(out).encode("utf-8")[:target]

def gen_64k_ascii(seed=SEED+1):
    """64 KiB pure-ASCII subject: frequent 'x' (~8%), rare 'a' (~0.5%),
    zero 'é'/CJK (impossible in ASCII)."""
    rng = random.Random(seed)
    letters = "bcdfghijklmnopqrstuvwyz "  # no 'a', no 'x'
    out, size, target = [], 0, 65536
    while size < target:
        r = rng.random()
        if r < 0.08:    ch = "x"
        elif r < 0.085: ch = "a"
        else:           ch = rng.choice(letters)
        out.append(ch); size += 1
    return "".join(out).encode("ascii")[:target]

def gen_match_dense(seed=SEED+2):
    """200 KB match-dense synthetic: repeats of 'ax', 'éx' (utf-8), '日本',
    '本', '日' so all three lookaround patterns get frequent real matches."""
    rng = random.Random(seed)
    units = ["ax", "éx", "日本", "本", "日", "x", "a"]
    out, size, target = [], 0, 200_000
    while size < target:
        b = rng.choice(units).encode("utf-8")
        out.append(b); size += len(b)
    return b"".join(out)[:target]

if __name__ == "__main__":
    import sys, pathlib
    outdir = pathlib.Path(sys.argv[1] if len(sys.argv) > 1 else ".")
    (outdir / "synth-1m.bin").write_bytes(gen_mixed_1m())
    (outdir / "synth-64k-asc.bin").write_bytes(gen_64k_ascii())
    (outdir / "synth-dense.bin").write_bytes(gen_match_dense())
