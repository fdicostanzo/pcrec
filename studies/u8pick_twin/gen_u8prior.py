#!/usr/bin/env python3
"""gen_u8prior.py DEFAULT_RXT OUT_DIR -- a SCRATCH structural UTF-8 prior for
`--analysis u8prior -I OUT_DIR` (the experiment behind the report's fix sketch).

NOT a measured prior and NOT derived from any bench subject (the K35 trap: a
control sharing a source with what it controls).  Construction, all stated
assumptions:
  - ASCII code points: default.rxt's own byte rows, scaled to 80% of the mass.
  - the other 20%: split EQUALLY across five script blocks (Latin-1 Supplement
    letters, Cyrillic basic, Hiragana, Katakana, CJK Unified common block) and
    UNIFORM within each block.
"""
import re, sys
src = open(sys.argv[1], encoding='utf-8').read()
ascii_rows = {int(m.group(1), 16): int(m.group(2))
              for m in re.finditer(r'^\s+row ([0-9a-f]{2}) (\d+)$', src, re.M) if int(m.group(1), 16) < 0x80}
tot = sum(ascii_rows.values())
blocks = [(0xC0, 0xFF), (0x410, 0x44F), (0x3041, 0x3093), (0x30A1, 0x30F6), (0x4E00, 0x9FFF)]
SCALE = 1_000_000
rows = {}
for cp, c in ascii_rows.items():
    rows[cp] = max(1, c * (SCALE * 80 // 100) // tot)
share = SCALE * 20 // 100 // len(blocks)
for lo, hi in blocks:
    n = hi - lo + 1
    for cp in range(lo, hi + 1):
        rows[cp] = max(1, share // n)
out = ["analysis u8prior", "    description SCRATCH structural UTF-8 prior (u8pick0): ASCII default prior at 80%, five script blocks equal-share at 20%",
       "    cpfreq", "        question How often does each Unicode code point occur in this exemplar?",
       "        reader byte-rate (docs/spec/findings.md §4)", "        analyzer authored: gen_u8prior.py (scratch)",
       "        encoding ascii", "        serves byte-rate when utf8 via encode-utf8"]
out += ["        row U+%04X %d" % (cp, rows[cp]) for cp in sorted(rows)]
out += ["        provenance", "            source authored", "            retrieved 2026-10-09",
        "            attribution default.rxt ASCII rows; script-block shares assumed, not measured"]
open(sys.argv[2].rstrip('/') + '/u8prior.rxt', 'w', encoding='utf-8').write("\n".join(out) + "\n")
