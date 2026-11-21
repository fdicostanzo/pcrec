# CRITIC POP: memfn-bspan3 (r69, design re-check of block_span.md rev 3)

## Fix ledger
- F-2 (population 3 bench / 0 corpus; k 31 each): LANDED-WRONG (POP-1: counts right, bench-row attribution wrong)
- F-3 counts/floors (41 patterns, 28 / 31): LANDED-RIGHT (recomputed: 41 distinct, floors 28 at w32, 31 at w4095, exact)
- F-17 (82 routed cells of 710's grid): LANDED-RIGHT (recomputed 66 + 16 = 82 on the real kind at w4095; 48 unrouted)
- F-18 cells part (12 pin cells): LANDED-WRONG (POP-2: frame cell cannot discriminate; cell count is patterns, not cells)
- F-19 (section 11 examples, utf8): LANDED-WRONG (POP-3: utf8 sentence covers hex only; W>32 row lacks W-1 on R7w)

## Findings

### POP-1 (CONFIRMED, doc, trivial effort, blast radius section 0.1 only) bench-row attribution in the population table is wrong. r68 F-2.
Section 0.1's table puts "(bounded/hex32, loglines/hex32-id)" on the row for `[0-9a-f]{32}` and gives `\b[0-9a-f]{32}\b` no bench id.
R/population/spancensus2_bench_own.tsv: line 41 `bench/bounded/patterns/hex32.rx` = `[0-9a-f]{32}` (window:31); line 175 `bench/loglines/patterns/hex32-id.rx` = `\b[0-9a-f]{32}\b` (window:31); line 53 dig-exact-32 = `\d{32}`.
So hex32-id is the `\b` pattern; as written the table implies 4 bench rows (two for row 1) against "3 bench sites". The counts themselves recompute exactly: 3 patterns, fd D-hors / D-hors / R7w, frame E-find, k 31, at w32 and w4095 (6 compiles). Fix: move "loglines/hex32-id" to row 2.

### POP-2 (CONFIRMED, check-power + doc, effort one cell, blast radius section 10.2 pins) the "frame" pin cell cannot discriminate, and "12 cells" counts patterns. r68 F-18.
Cell: `[0-9a-f]{20}[g-z]{20}` at width 32 ("E-stmt: absent"). Measured (site.py, kit table facts): at w32 fd row = R7w, frame = E-stmt, no span loop; its stretches are k 20 and 19 (the w4095 run of the same pattern). With the frame column DELETED from T-vscan the cell still reads absent (R7w needs k >= 24; 20 and 19 fail) and T-vwin needs D-hors (the row is R7w). So the plant "drop the frame test" does not flip the cell: it guards nothing. A cell that does: any E-stmt site with fd R7w and a stretch of 24..64, e.g. `[0-9a-f]{33}` at w32 (measured: fd R7w, frame E-stmt; a 32-position stretch, so only the frame column refuses it), or `[0-9]{65}` at w32 (fd R7w, E-stmt; already in the seed list but not as the frame cell). Brow cells DO discriminate: `ab[0-9]{26}` (D1, E-find, k 26) and `[xy][0-9]{26}` (PAIR, E-find, k 26) at w32 and w4095: V 0 only because brow != R7w (k 26 is inside 24..64). Once-per-site cell reached: at w4095 loops k 20, k 19, both inside 16..1000, one V.
Count: the note says 12 cells = 8 bound + 4. The listed (pattern, width) cells are 4 (hex 16/17 x w32,w4095) + 2 (hex 1001/1002 x w4095) + 4 (dig 24/25 x 2 widths) + 2 (dig 65/66 x w4095) = 12 bound cells, plus brow 2 (x2 widths = 4 if both) + frame 1 + once 1 = 16-18 cells. "8 bound" counts patterns. The pin patterns number 11 (matches SPAN-SEED). State which unit (pattern or cell) the floor 12 is.
Reached: all 22 (pattern, width) runs compiled rc=0 with the stated fd row and k (hex 16: k 15 absent; 17: k 16 V; 1001: k 1000 V; 1002: k 1001 absent; dig 24: k 23 absent; 25: k 24 V; 65: k 64 V at w4095; 66: k 65 absent).

### POP-3 (CONFIRMED, doc, trivial) section 11: the -e utf8 sentence is incomplete, and the "W > 32" row's R7w bound lacks the W-1 clause. r68 F-19.
(a) Section 11 says "Under -e utf8 the hex sets are WALK (R7w), so the hex family moves only at {25}..{32} there." Reproduced (hex {17} k16 V 0, {24} k23 V 0, {25} k24 V 1, {26}, {32} V 1, {33} E-stmt). But the sentence names only hex and the mover list above it names `[^\n]{17}..` and others without a utf8 caveat. Measured under `-e utf8` at w32: `[a-f]{17}` and `[aeiou]{17}` are R7w (k16: V 0, so they too move only at {25}..{32}); `[^\n]{17}` is E-stmt with no stretch at all (never moves); `[A-Za-z0-9_-]{17}` and `\w{20}`/`\w{25}` stay D-hors (V 1). Fix: say the moves follow the finder row, and list `[a-f]`, `[aeiou]` with hex and `[^\n]` as non-mover under utf8.
(b) Row `--window-search-width=W > 32`: "R7w with 24 <= k <= 64" has no W bound, while the D-hors clause has min(1000, W-1). Measured at W = 64: `[0-9]{64}` R7w k 63 V 1; `[0-9]{65}` E-stmt, no stretch; `[0-9a-f]{64}` k 63 V 1, `{65}` E-stmt. So R7w's bound is min(64, W-1) as well.

### POP-4 (SUSPECTED, design/doc, small) U2b's probe grid cannot see the known differing k > 31 shapes; section 2's list of differing sets omits `\w{501}` at w4095. r68 F-14 / SIZE-3.
r68 size.md:23 and sound.md:60 name `\w{501}` at width 4095 as differing from today (2 lines; sound.md) and 710's word500 is a routed cell. Section 2 lists only `\w{17}`, `\w{20}`, `\w{32}`; section 2.1's grid is `cls{17..32}` at width 32 only (recomputed: 160 patterns, 128 eligible, 32 non-movers: exact), and the real-population leg runs the 3 bench patterns at w4095 (k 31). So no U2b leg covers a k > 31 window cell at SIMD-off; the known positive at k 500 is not carried. What would confirm: build the wrapped `\w{501}` at w4095 and diff `rxa_search` at -fno-memfn-simd (r68's hand-built result is 2 lines; not reproduced here, the wrapper is unbuilt). Fix: add `\w{501}` (w4095) to U2b as a second known positive, or state that the census is k 16..31 only.

## PROBED-AND-HELD

- Section 0.1: 3 bench patterns recomputed at w32 and w4095 (6 compiles): fd D-hors / D-hors / R7w, frame E-find, k 31 each. Corpus 0 V sites: r68 SIM-1's `(?:ab|ba|aa|bb){24}c` is D1 (not routed), cross-checked by r68 verify V2; not recompiled (counted by r68).
- SPAN-SEED: enumerated from the text: 3 bench + 11 pins + 30 slice = 44, dedup by text = 41 (3 coincide: `[0-9a-f]{17}`, `[0-9]{25}`, `[0-9a-f]{32}`); 82 compiles (41 x w32, w4095), all rc=0; V-site count by trace fd row + frame + k, first eligible stretch per site: 28 at w32, 31 at w4095, both exactly the floors (the slice's 26 = 6x3 + 4x2; +2 bench; +3 pins at w4095: {1001}, [0-9]{65}, first stretch of {20}[g-z]{20}).
- Section 2.1 U2b grid: 160 patterns (10 classes from confirm.py CLASSES x n 17..32, w32) compiled; 128 eligible (96 window = 6 x 16, 32 scan = 4 x 8), 32 non-movers (scan classes k 16..23), classes' kinds match SITE_EXPECT, every pattern E-find, k = n-1. `\w{20}` (the floor witness) is in the grid and eligible.
- Section 6 F2: 130-cell grid (10 classes x 13 k, pattern cls{k+1}) at w4095 on the real kind: 82 routed (66 D-hors window + 16 R7w scan = 6 x 11 + 4 x 4), 48 not; zero kind mismatches vs SITE_EXPECT, all E-find, k = repeat count - 1 in 130/130.
- Section 3.3: `x[0-9]{26}` default D1 (V 0), under --memfn=no-fd-d1 D1w E-find k 26 (V 0, as the table says).
- Plant (b) witness `[0-9]{25}`: lo=1 end=25 k=24 on a 25-entry plan, so its stretch ends at the pattern end; `[0-9a-f]{32}` lo=0 end=31 (the probe is the 32nd entry), as the note says.
- Section 11 mover examples at w32: `[0-9a-f]{17..32}`, `\w{17,25,32}`, `[^\n]{17,25,32}`, `[0-9]{25,32}`, `[A-Z]{25,32}` move; `[0-9a-f]{16}`, `[0-9]{24}`, `{33}` (E-stmt), `ab[0-9]{26}`, `[xy][0-9]{26}` do not; `[0-9a-f]{n}` utf8 sentence true for hex.
- r68 diff: verify.md V2 (D1 k=48 at w4095), V3 (D1w k=26), V14 (hex{20} utf8 R7w k 19), SIM-1 (3 sites), SIZE-2 (3 sites 0 instruction diffs, `\b` one: padding), MEAS (`\w{20}` 24, `\w{32}` 26 lines, 0 on hex17/dig25/hex32/\d32/num65), V8/V12 (47 lines; 47 of 130), F2 9/9: all agree with rev 3's published numbers. The one mismatch is POP-1; `\w{501}` is POP-4.
- Compile count: 82 + 160 + 130 + 19 extras = 391 of the 400 cap (no gcc compiles).

CRITIC COMPLETE

