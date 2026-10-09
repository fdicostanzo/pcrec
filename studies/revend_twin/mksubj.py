#!/usr/bin/env python3
"""[OPT-REVEND] hand-twin subjects (STUDY; deterministic, seeded).

    mksubj.py REPO OUTDIR

Writes, under OUTDIR:
  pool_byte.hex  every quoted subject of tests/assertions/*.rxt and
                 tests/base/*.rxt (the end_window.rxt subjects among them),
                 plus hand edge subjects (empty, lone/double newline, tails
                 with and without a final newline), one hex line each
  pool_utf8.hex  tests/utf8/*.rxt subjects plus multibyte / ill-formed edges
  long.hex       ~1 MiB synthesized bodies x tails: matching, non-matching,
                 trailing-newline, no-tail (for the identity sweep)
  t-*.bin        the timing bodies: the bench's three t-tail-*-1m SHAPES
                 (its manifest's descriptions, NOT its bytes), t-1m-like
                 (ends "[20\\n"), and a 16 KiB+1 whitespace near-miss
"""
import os, random, re, sys, glob

repo, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)

ESC = {"n": b"\n", "t": b"\t", "r": b"\r", "f": b"\f", "v": b"\v",
       "\\": b"\\", '"': b'"', "0": b"\0", "e": b"\x1b", "a": b"\x07"}

def decode(q):
    o = bytearray(); i = 0
    while i < len(q):
        c = q[i]
        if c != "\\":
            o += c.encode("utf-8"); i += 1; continue
        d = q[i + 1]
        if d == "x":
            o.append(int(q[i + 2:i + 4], 16)); i += 4
        elif d in ESC:
            o += ESC[d]; i += 2
        else:
            raise ValueError(d)
    return bytes(o)

def harvest(globs):
    subs = []
    rx = re.compile(r'^(?:m|n|ms|ns)\s+"((?:[^"\\]|\\.)*)"')
    for g in globs:
        for f in sorted(glob.glob(os.path.join(repo, g))):
            for line in open(f, encoding="utf-8", errors="surrogateescape"):
                m = rx.match(line)
                if not m: continue
                try: subs.append(decode(m.group(1)))
                except Exception: pass
    return subs

def write_hex(name, subs):
    seen = set(); n = 0
    with open(os.path.join(out, name), "w") as f:
        for s in subs:
            if s in seen: continue
            seen.add(s); n += 1
            f.write(s.hex() + "\n")
    print(f"{name}: {n} subjects")

edges = [b"", b"\n", b"\n\n", b"a", b"a\n", b"a\n\n", b"aa\nb", b"123", b"123\n",
         b"x 42", b"x 42\n", b"x 42\n\n", b"42\nx", b"   ", b"   \n", b" \n ",
         b"\n   ", b"end of file   ", b"end of file   \n", b"\t\v\f\r\n",
         b".txt", b"a.txt", b"a.txt\n", b"saved to report.txt", b"x\nsaved to report.txt\n",
         b"report.TXT", b"report.txt.", b"a.txt b.txt", b"abc$", b"word", b"word\n",
         b"wo rd", b"a=b=c", b"x=1\ny=2", b"a@b", b"ab@cd\n", b"total 20250614",
         b"[20\n", b"aaa", b"aaab", b"aab\n", b"b", b"zz9z", b"99z\n", b"\x00\n",
         b"\xff\xfe", b"a\xff", b"\xffa\n"]
write_hex("pool_byte.hex", edges + harvest(["tests/assertions/*.rxt", "tests/base/*.rxt"]))

u8edges = [b"", b"\n", "αβγ".encode(), "αβγ\n".encode(), "x αβγ".encode(),
           "日本語".encode(), "日本語 \n".encode(), "a ".encode(), "a \n".encode(),
           "naïve.txt".encode(), "файл.txt\n".encode(), "x  ".encode(),
           b"a\xce", b"a\xce\n", b"\xb1\xb1", b"ab\x80", "α\x80".encode("utf-8", "surrogateescape"),
           b"\xce\xb1\xce", "𝔸𝔹".encode(), "𝔸𝔹\n".encode(), "end   ".encode()]
write_hex("pool_utf8.hex", u8edges + harvest(["tests/utf8/*.rxt"]))

# a ~1 MiB prose-like body (the census's mksubj.py vocabulary, its own seed)
rnd = random.Random(20261009)
words = ["alpha", "beta", "gamma", "delta", "the", "of", "and", "item", "42", "7",
         "log", "error", "warn", "file.txt", "path/to", "x=1", "done", "user", "id"]
body = bytearray(); col = 0
while len(body) < (1 << 20) - 64:
    w = rnd.choice(words).encode(); body += w; col += len(w)
    if col > 60: body += b"\n"; col = 0
    else: body += b" "; col += 1
body = bytes(body[:(1 << 20) - 64])
if body.endswith((b" ", b"\n")): body = body[:-1] + b"."

tails = {
    "t-tail-digits-1m": b"\ntotal 20250614",
    "t-tail-txt-1m":    b"\nsaved to report.txt",
    "t-tail-space-1m":  b"\nend of file   ",
    "t-1m":             b"\n[20\n",
}
for name, tail in tails.items():
    open(os.path.join(out, name + ".bin"), "wb").write(body + tail)
ws = bytes(rnd.choice(b" \t\n\r\f\v") for _ in range(16383)) + b" "
open(os.path.join(out, "t-trim-nearmiss-16k.bin"), "wb").write(ws + b"x")

longs = [body + t for t in (b"", b"\n", b" 4242", b" 4242\n", b"\nsaved to report.txt",
                            b"\nsaved to report.txt\n", b"\nend of file   ", b"\nend of file   \n",
                            b" end.", b"\n\n")]
longs.append(ws + b"x"); longs.append(ws)
write_hex("long.hex", longs)
