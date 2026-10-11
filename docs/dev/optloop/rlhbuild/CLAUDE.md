# docs/dev/optloop/rlhbuild/ — [REQ-HANDOFF-L1] as built (lane rlhbuild, 2026-10-11)

Identity and timing instruments for the built row family: the landmark-K
facts, the byte-landmark entry handoff and the forward scan's re-entered
handoff (NEXT row `handoff`). The reading is `docs/dev/lanes/rlhbuild_report.md`.
Every timing here is SCRATCH TIER (one box, pinned core, interleaved); the
official verdict is a bench run (D144 add. 4).

Re-uses `../et1twin/etdrv.c` (identity + timing driver), `../et1twin/p2drv.c`
(libpcre2-8 side), `../et1twin/gen_adv.py` (kvq, sfx64) and
`../rlhtwin/gen_adv.py` (ipv6, ipv4; dotted4 takes ipv4's) by path.

## Files

- `build.sh` — per cell, the variants `base` (main's pcrec), `new` (the lane's),
  `deny` (`-fno-req-handoff`), `newm` (new with the byte gate's generic kit
  loop rewritten to memchr at BOTH sites, `mkmemchr.py`: the R-15 delta,
  SCRATCH, never the lane's text) and `p2` (libpcre2-8). Cells: ipv6, ipv4,
  dotted4, sfx64, kvq, and the K-admission cells hostile (`a.{1,50000}z`),
  hcolon (`[a-y]\d{0,150}:`, declined) and hcolon_in (`[a-y]\d{0,100}:`,
  admitted).
- `mkmemchr.py` — the memchr rewrite above (asserts what it rewrote, by count).
- `gen_hostile.py` — landmark-dense subjects for the K-admission cells
  (z-dense, colon-dense; 4 KiB .. 1 MiB) plus 200 small adversarial ones.
- `ident.sh` — base against new / deny / newm / p2 per cell, find-all plus
  every startpos (etdrv `ident`); `ident.txt` its output.
- `time.sh` — pinned interleaved timing (throughput, search_short);
  `times.tsv` raw, `summarize.py` / `times_summary.txt` the reading.
