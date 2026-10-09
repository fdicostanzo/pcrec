#!/usr/bin/env python3
"""[OPT-REVEND] revision 2 timing subjects: mksubj_r2.py OUTDIR

The bench tail stand-ins of mksubj.py rebuilt on a body with NO ".txt"
anywhere before the tail (panel X7: the old body's vocabulary contained
"file.txt", which let a pre-check find an early hit; "file.txt" becomes
"file.dat" here), plus:
  t-tail-spacenl-1m  "\\nend of file   \\n": `\\s+$`'s TIE cell (both seeds
                     reach s*, the anchored run decides);
  w-<name>.bin       the widest DFA-routed bound `[a-z]{0,4096}\\z`
                     (8192 already falls back to the VM): match ~1 KB,
                     ~4 KB (the bound), none (empty match at n);
  v-60000-*.bin      the same tails for `[a-z]{0,60000}\\z`, which is
                     VM-routed (DFA overflow): context only, W1 alone.
Writes OUTDIR/<name>.bin and OUTDIR/index.tsv (pattern-row subject)."""
import os, random, sys
out = sys.argv[1]; os.makedirs(out, exist_ok=True)
rnd = random.Random(20261009)
words = ["alpha", "beta", "gamma", "delta", "the", "of", "and", "item", "42", "7",
         "log", "error", "warn", "file.dat", "path/to", "x=1", "done", "user", "id"]
body = bytearray(); col = 0
while len(body) < (1 << 20) - 64:
    w = rnd.choice(words).encode(); body += w; col += len(w)
    if col > 60: body += b"\n"; col = 0
    else: body += b" "; col += 1
body = bytes(body[:(1 << 20) - 64])
if body.endswith((b" ", b"\n")): body = body[:-1] + b"."
assert b".txt" not in body
subs = {
    "t-tail-digits-1m": body + b"\ntotal 20250614",
    "t-tail-txt-1m": body + b"\nsaved to report.txt",
    "t-tail-space-1m": body + b"\nend of file   ",
    "t-tail-spacenl-1m": body + b"\nend of file   \n",
    "t-1m": body + b"\n[20\n",
}
ws = bytes(rnd.choice(b" \t\n\r\f\v") for _ in range(16383)) + b" "
subs["t-trim-nearmiss-16k"] = ws + b"x"
wbody = body[:(1 << 20) - 4200]
for k, t in (("m1k", b"\n" + b"q" * 1000), ("m4k", b"\n" + b"q" * 4000), ("none", b"\nab!")):
    subs["w-" + k] = wbody + t
for k, t in (("m1k", b"\n" + b"q" * 1000), ("m50k", b"\n" + b"q" * 50000), ("none", b"\nab!")):
    subs["v-" + k] = body[:(1 << 20) - 51000] + t
for name, b in subs.items():
    open(os.path.join(out, name + ".bin"), "wb").write(b)
rows = {
    "tail-digits-eol": ["t-tail-digits-1m", "t-tail-txt-1m", "t-tail-space-1m", "t-1m"],
    "tail-word-eoz": ["t-tail-digits-1m", "t-tail-txt-1m", "t-tail-space-1m"],
    "tail-space-eol": ["t-tail-digits-1m", "t-tail-txt-1m", "t-tail-space-1m", "t-trim-nearmiss-16k", "t-tail-spacenl-1m"],
    "tail-ext-lower-txt": ["t-tail-digits-1m", "t-tail-txt-1m", "t-tail-space-1m"],
    "tail-dotstar-txt": ["t-tail-digits-1m", "t-tail-txt-1m", "t-tail-space-1m"],
    "wide-4096": ["w-m1k", "w-m4k", "w-none"],
    "wide-60000-vm": ["v-m1k", "v-m50k", "v-none"],
}
with open(os.path.join(out, "index.tsv"), "w") as f:
    for r, ss in rows.items():
        for s in ss: f.write(f"{r}\t{s}\t{s}.bin\n")
