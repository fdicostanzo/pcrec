#!/usr/bin/env python3
"""slotarms subject generator: gen_subj.py OUT  (writes OUT/subj/pc_<name>, bytes only).

nm*  no-match subjects: all 'a' (no digit, so no pattern's start set is ever hit)
e0   empty subject
m<family>-L<L>  64 KiB subjects with EXACTLY one match per L bytes: each L-byte unit is
     the family's match then 'a' filler, so the matches are disjoint and no match
     can straddle a unit (family w2: match 'Da', w5: match 'DDDDa'; D = digit).
Deterministic (no randomness): the same bytes on every box.
"""
import os, sys
TOTAL = 65536
FAM = {"w2": b"7a", "w5": b"7777a"}
out = os.path.join(sys.argv[1], "subj")
os.makedirs(out, exist_ok=True)
def put(name, data):
    with open(os.path.join(out, "pc_" + name), "wb") as f:
        f.write(data)
put("e0", b"")
for n, name in ((8, "nm8"), (64, "nm64"), (1024, "nm1k"), (TOTAL, "nm64k")):
    put(name, b"a" * n)
for fam, m in FAM.items():
    for L, tag in ((8, "8"), (64, "64"), (1024, "1k")):
        unit = m + b"a" * (L - len(m))
        assert len(unit) == L
        put("m%s-L%s" % (fam, tag), unit * (TOTAL // L))
