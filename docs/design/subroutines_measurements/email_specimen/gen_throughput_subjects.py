#!/usr/bin/env python3
"""gen_throughput_subjects.py -- three 1MB throughput subjects, deterministic."""
import os

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "throughput")
os.makedirs(OUT, exist_ok=True)

TARGET = 1024 * 1024

# (a) valid addresses separated by spaces
addr = b"user.name@sub.example.com "
buf = (addr * (TARGET // len(addr) + 1))[:TARGET]
with open(os.path.join(OUT, "a_valid_addrs.bin"), "wb") as f:
    f.write(buf)

# (b) no '@' at all
line = b"the quick brown fox jumps over the lazy dog 1234567890 "
buf = (line * (TARGET // len(line) + 1))[:TARGET]
with open(os.path.join(OUT, "b_no_at.bin"), "wb") as f:
    f.write(buf)

# (c) one long atom run (no @, no dots, no spaces -- pure atom-class bytes)
buf = (b"a" * TARGET)
with open(os.path.join(OUT, "c_long_atom_run.bin"), "wb") as f:
    f.write(buf)

for fn in ("a_valid_addrs.bin", "b_no_at.bin", "c_long_atom_run.bin"):
    p = os.path.join(OUT, fn)
    print(fn, os.path.getsize(p))
