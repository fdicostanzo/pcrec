#!/usr/bin/env python3
"""p910 P10 witnesses (RECONSTRUCTED after the run from the files' measured
shapes; same structure and lengths, different random bytes). argv[1] = out dir.
e-* for email-owasp (required byte '@'), i-* for moment-iso8601 ('-').
  late-at / late-at-miss   60,000 class bytes then a matching / failing tail
  regret-19k / regret-30k  N class bytes, a byte that kills the attempt, then
                           ~1 MiB of letters/space/,/. without the req byte:
                           the attempt dies just after (19,800 ~ 1.2x the
                           checkpoint) or well after the checkpoint
  ok / short-noat(-dies) / empty   short subjects
"""
import os, random, sys
o = sys.argv[1]; r = random.Random(910)
L = b"abcdefghijklmnopqrstuvwxyz"; WS = b" \t\n\x0b\x0c\r"
def rnd(al, n): return bytes(r.choice(al) for _ in range(n))
def filler(n): return rnd(L + b" ,.", n)
W = {
    "e-late-at": rnd(L, 60000) + b"@example.com",
    "e-late-at-miss": rnd(L, 60000) + b"@example.c",
    "e-regret-19k": rnd(L, 19800) + b" " + filler(1068377 - 19801),
    "e-regret-30k": rnd(L, 30000) + b" " + filler(1078577 - 30001),
    "e-ok": b"john.doe@mail.example.org",
    "e-short-noat": rnd(L, 40),
    "e-short-noat-dies": rnd(L, 10) + b" x",
    "e-empty": b"",
    "i-late": rnd(WS, 60000) + b"2024-01-02T03:04:05Z",
    "i-late-miss": rnd(WS, 60000) + b"2024-01-02T03:04:05Q",
    "i-regret-30k": rnd(WS, 30000) + b"x" + filler(1078577 - 30001),
    "i-ok": b"  2024-W05-3",
}
for k, v in W.items():
    open(os.path.join(o, k + ".bin"), "wb").write(v)
