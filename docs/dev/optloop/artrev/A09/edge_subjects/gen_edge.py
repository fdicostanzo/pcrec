#!/usr/bin/env python3
"""A09 edge subjects for loglines_level_context (rvA09): token soup built from
fragments of the pattern's literals, so level words, keyword words, word-boundary
neighbours, newlines and >200-byte gaps occur densely. Deterministic (seed 9).
Usage: gen_edge.py OUTDIR"""
import random, sys, os
out = sys.argv[1]
rng = random.Random(9)
LEV = [b"ERROR", b"FATAL", b"CRIT"]
KW = [b"timeout", b"timed out", b"refused", b"denied", b"unreachable"]
NEAR = [b"ERRO", b"RROR", b"ERRORS", b"xERROR", b"_ERROR", b"9FATAL", b"FATALx", b"CRITICAL", b"CRI",
        b"FATA", b"C", b"E", b"F", b"EE", b"CC", b"FF", b"CRITCRIT", b"ERRORERROR",
        b"timeouts", b"xtimeout", b"timed  out", b"timedout", b"timed", b"time", b"refuse", b"denie",
        b"unreachabl", b"d", b"r", b"t", b"u", b"de", b"re", b"ti", b"tim", b"un", b"timed o", b"timed ou"]
SEP = [b" ", b" ", b" ", b"\n", b":", b"-", b"_", b"[", b"]", b"\t", b"\xe9", b"\x00", b".", b"  ", b"\n\n", b"=", b"0"]
FILL = [b"a", b"xyz", b"Closed", b"Error", b"error", b"Code", b"Field", b"session", b"INFO", b"WARN", b"DEBUG"]
def tok():
    r = rng.random()
    if r < 0.18: return rng.choice(LEV)
    if r < 0.33: return rng.choice(KW)
    if r < 0.55: return rng.choice(NEAR)
    return rng.choice(FILL)
def soup(n, sep_p=0.85, longgap=False):
    b = []
    L = 0
    while L < n:
        t = tok()
        if longgap and rng.random() < 0.05:
            t = b"x" * rng.choice([150, 195, 199, 200, 201, 205, 250])
        b.append(t); L += len(t)
        if rng.random() < sep_p:
            s = rng.choice(SEP); b.append(s); L += len(s)
    return b"".join(b)[:n]
os.makedirs(out, exist_ok=True)
k = 0
def w(data):
    global k
    open(os.path.join(out, "e-%03d.bin" % k), "wb").write(data); k += 1
# hand-placed shapes: start/end of subject, exact 200 boundary, adjacency
w(b"ERROR timeout")
w(b"ERROR timeout\n")
w(b"xERROR timeout ERROR denied")
w(b"ERROR:" + b"y" * 194 + b" timeout")      # gap 200 incl. sep
w(b"ERROR " + b"y" * 194 + b" timeout")
w(b"ERROR " + b"y" * 195 + b" timeout")
w(b"ERROR " + b"y" * 193 + b" timeout")
w(b"FATAL\ntimeout FATAL refused")
w(b"CRIT timed out")
w(b"CRIT timed  out timed out")
w(b"CRITtimeout CRIT timeoutx CRIT unreachable")
w(b"ERROR FATAL CRIT denied")
w(b"E")
w(b"C")
w(b"FATA")
w(b"ERROR")
w(b"refused ERROR")
w(b"ERROR ERROR " + b"z " * 120 + b"denied")
w(b"\xe9ERROR denied\xe9")
w(b"ERROR denied" * 30)
w(b"ERROR " + b"q" * 300 + b" ERROR timeout")
for i in range(40):
    w(soup(rng.randint(5, 120)))
for i in range(30):
    w(soup(rng.randint(120, 600), longgap=True))
for i in range(8):
    w(soup(rng.randint(4000, 20000), sep_p=0.6, longgap=True))
# truncated literals at the very END of the subject (bounds of any look-ahead
# verification; exact-size buffers make ASan see a one-byte over-read)
for stem in [b"", b"x ", b"ERROR timeout ", b"ERROR ", b"\n"]:
    for t in [b"FAT", b"FA", b"FATA", b"CRI", b"CR", b"ERRO", b"ERR", b"T", b"O", b"tim", b"timed o", b"unreach", b"ERROR timed", b"ERROR timeou"]:
        w(stem + t)
# the .{0,200} bound exactly: gaps 199..202 between level end and keyword start,
# for every level and keyword, alone and with a later in-bound keyword
for lev in LEV:
    for kw in KW:
        for gap in (199, 200, 201, 202):
            mid = b" " + b"y" * (gap - 2) + b" "
            w(lev + mid + kw)
            w(b"x " + lev + mid + kw + b" " + lev + b" " + kw)
print(k, "subjects")
