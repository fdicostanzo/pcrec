#!/usr/bin/env python3
"""[OPT-REVEND] Q1 subjects: mksubj_q1.py PATTERNS.tsv OUTDIR
For each pattern row x {1m,64k} x {long,short,non,nl}: a prose body (the
revend_twin body recipe, own cut to size) + the row's tail. nl only for eol=1.
Tail tokens: @Q<n> = n 'q', @A<n> = n 'a', @B<n> = n 'b'. Writes
OUTDIR/<name>.<size>.<kind>.bin and OUTDIR/index.tsv (name size kind file)."""
import os, random, re, sys
tsv, out = sys.argv[1], sys.argv[2]
os.makedirs(out, exist_ok=True)
rnd = random.Random(20261009)
words = ["alpha", "beta", "gamma", "delta", "the", "of", "and", "item", "42", "7",
         "log", "error", "warn", "file.txt", "path/to", "x=1", "done", "user", "id"]
def prose(n):
    b = bytearray(); col = 0
    while len(b) < n:
        w = rnd.choice(words).encode(); b += w; col += len(w)
        if col > 60: b += b"\n"; col = 0
        else: b += b" "; col += 1
    b = bytes(b[:n])
    return b[:-1] + b"." if b.endswith((b" ", b"\n")) else b
bodies = {"1m": prose((1 << 20) - 1100), "64k": prose((1 << 16) - 1100)}
def tail(t):
    t = re.sub(r"@([QAB])(\d+)", lambda m: {"Q": "q", "A": "a", "B": "b"}[m[1]] * int(m[2]), t)
    return re.sub(r"\\(n|x[0-9a-f]{2})", lambda m: "\n" if m[1] == "n" else chr(int(m[1][1:], 16)), t).encode("latin1")
idx = open(os.path.join(out, "index.tsv"), "w")
for line in open(tsv):
    if line.startswith("#") or not line.strip(): continue
    name, eol, pat, tl, ts, tn = line.rstrip("\n").split("\t")
    kinds = {"long": tail(tl), "short": tail(ts), "non": tail(tn)}
    if int(eol): kinds["nl"] = tail(ts) + b"\n"
    seen = {}
    for sz, body in bodies.items():
        for k, t in kinds.items():
            if t in seen.values() and k == "short" and sz == "1m":
                pass  # short == long is kept: the cell is just reported twice
            f = f"{name}.{sz}.{k}.bin"
            open(os.path.join(out, f), "wb").write(body + t)
            idx.write(f"{name}\t{sz}\t{k}\t{f}\n")
    seen = None
