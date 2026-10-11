#!/usr/bin/env python3
"""gen_d160f.py DEFAULT_RXT OUT_DIR NAME MODE F_PCT -- a SCRATCH byte-level
prior in D160's shape ("rates follow the encoding's structure"): a `freq`
block that serves byte-rate under utf8.  ASCII keeps default.rxt's rows,
scaled to (100-F_PCT)% of the mass; the other F_PCT% is the non-ASCII mass,
split over characters of 2/3/4 bytes 40/50/10 (an assumption), then
  - every continuation byte 0x80-0xBF gets (total continuation mass)/64
    (it occurs in every non-ASCII character of every script);
  - every lead byte of a length class gets the class's lead mass divided by
    the number of leads it is spread over: MODE u = all leads of the class
    (30/16/5, 'script-neutral uniform'), MODE c = a CONCENTRATED 3/3/2 (real
    text uses few leads: Latin C3, Cyrillic D0/D1, kana/CJK E3-E9).
It is a TWIN-STUDY INSTRUMENT: the shares are the study's variable. Output
OUT_DIR/NAME.rxt, used as `--analysis NAME -I OUT_DIR`.
"""
import re, sys
dflt, out, name, mode, fpct = sys.argv[1:6]
f = int(fpct) / 100.0
src = open(dflt, encoding='utf-8').read()
asc = {int(m.group(1), 16): int(m.group(2)) for m in re.finditer(r'^\s+row ([0-9a-f]{2}) (\d+)$', src, re.M) if int(m.group(1), 16) < 0x80}
tot = sum(asc.values()); SCALE = 1_000_000
rows = {b: max(1, int(c * SCALE * (1 - f) / tot)) for b, c in asc.items()}
s2, s3, s4 = 0.4, 0.5, 0.1
cont_mass = f * (s2 * 1 + s3 * 2 + s4 * 3) * SCALE
for b in range(0x80, 0xC0): rows[b] = max(1, int(cont_mass / 64))
k2, k3, k4 = (30, 16, 5) if mode == 'u' else (3, 3, 2)
for b in range(0xC2, 0xE0): rows[b] = max(1, int(f * s2 * SCALE / k2))
for b in range(0xE0, 0xF0): rows[b] = max(1, int(f * s3 * SCALE / k3))
for b in range(0xF0, 0xF5): rows[b] = max(1, int(f * s4 * SCALE / k4))
o = ["analysis %s" % name, "    description SCRATCH D160-shaped byte prior (lrmisc): mode %s, non-ASCII mass %s%%" % (mode, fpct),
     "    freq", "        question How often does each byte occur in UTF-8 text with this structure?",
     "        reader byte-rate (docs/spec/findings.md §4)", "        analyzer authored: gen_d160f.py (scratch)",
     "        encoding ascii", "        serves byte-rate when utf8 via unigram"]
o += ["        row %02x %d" % (b, rows[b]) for b in sorted(rows)]
o += ["        provenance", "            source authored", "            retrieved 2026-10-11", "            attribution default.rxt ASCII rows; structural shares assumed, not measured"]
open(out.rstrip('/') + '/%s.rxt' % name, 'w', encoding='utf-8').write("\n".join(o) + "\n")
print(name, len(rows), "rows")
