#!/usr/bin/env python3
"""gen_d160.py DEFAULT_RXT OUT_DIR NAME S2 S3 S4 -- a SCRATCH prior shaped like
D160's ruling ("authored from UTF-8 STRUCTURE, script-neutral"): ASCII keeps
default.rxt's own rows; the rest of the mass is split by SEQUENCE LENGTH only,
S2/S3/S4 in basis points of the total for 2-/3-/4-byte characters, then EQUALLY
across the lead bytes of that length (C2-DF, E0-EF, F0-F4) and uniformly
within a lead's continuation space (sampled code points, valid scalars only).
So every continuation byte 0x80-0xBF is common (it occurs in every non-ASCII
character) and no script is named.

It is a TWIN-STUDY INSTRUMENT, not a candidate for src/findings/default.rxt:
the shares are the study's variable (three settings are run), the sampling of
3-/4-byte leads is a stand-in for 'uniform within the lead'. Output:
OUT_DIR/NAME.rxt, used as `--analysis NAME -I OUT_DIR`.
"""
import re, sys
dflt, out, name, s2, s3, s4 = sys.argv[1:7]
s2, s3, s4 = int(s2), int(s3), int(s4)
src = open(dflt, encoding='utf-8').read()
asc = {int(m.group(1), 16): int(m.group(2)) for m in re.finditer(r'^\s+row ([0-9a-f]{2}) (\d+)$', src, re.M) if int(m.group(1), 16) < 0x80}
tot = sum(asc.values()); SCALE = 1_000_000
rows = {}
am = SCALE * (10000 - s2 - s3 - s4) // 10000
for cp, c in asc.items(): rows[cp] = max(1, c * am // tot)
def spread(mass_bp, cps):
    per = max(1, SCALE * mass_bp // 10000 // len(cps))
    for cp in cps: rows[cp] = rows.get(cp, 0) + per
spread(s2, list(range(0x80, 0x800)))
for L in range(0xE0, 0xF0):
    base = (L & 0xF) << 12
    cps = sorted({base + (i * 53) % 4096 for i in range(256)})
    cps = [c for c in cps if not 0xD800 <= c <= 0xDFFF and c >= 0x800]
    spread(s3 // 16, cps)
for L in range(0xF0, 0xF5):
    base = (L & 0x7) << 18
    cps = sorted({base + (i * 4099) % 262144 for i in range(64)})
    cps = [c for c in cps if 0x10000 <= c <= 0x10FFFF]
    spread(s4 // 5, cps)
assert len(rows) <= 65536
o = ["analysis %s" % name, "    description SCRATCH D160-shaped structural UTF-8 prior (lrmisc): shares by sequence length %d/%d/%d bp" % (s2, s3, s4),
     "    cpfreq", "        question How often does each Unicode code point occur in this exemplar?",
     "        reader byte-rate (docs/spec/findings.md §4)", "        analyzer authored: gen_d160.py (scratch)",
     "        encoding ascii", "        serves byte-rate when utf8 via encode-utf8"]
o += ["        row U+%04X %d" % (cp, rows[cp]) for cp in sorted(rows)]
o += ["        provenance", "            source authored", "            retrieved 2026-10-11", "            attribution default.rxt ASCII rows; length shares assumed, not measured"]
open(out.rstrip('/') + '/%s.rxt' % name, 'w', encoding='utf-8').write("\n".join(o) + "\n")
print(name, len(rows), "rows")
