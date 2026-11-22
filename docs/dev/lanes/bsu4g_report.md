# Lane bsu4g: R-47 unit U4 part 1, G2-V unit and whole with guard pages, plants (a) and (b)

## STATE AT HANDOFF

STATE: delivered, validation OWED (two queued box jobs)

Branch lane/bsu4g, cut from lane/memfn-k1108 at ad3c8f1c2 (U3 at abi 112 on this branch; U4 moves no emitted byte, so no abi event). The design of record is docs/design/memfn/block_span.md rev 4.2, §10.2's G2-V unit and G2-V whole rows and sabotage rows (a) and (b).

Rulings file docs/dev/lanes/bsu4g_rulings.md: empty at every checkpoint (read at launch, before each commit and before this report). No entry was applied.

No file under memfn/src/, src/, cli/ or lib/ changed. The premise test held (IN-LANE RUNS).

Commits (lane/bsu4g):
- f85412bb3: G2-V unit and whole (memfn/tests/g2_vspan.py and three C files under memfn/tests/g2/), run_g2_win.sh section V.
- 20d61219b: plants S3525 (a) and S3526 (b), mech suite `g2v` in tests/mech/run_sabotage_matrix.sh.
- b79157ee6: the C4 allowlist rows for the two rows, the memfn/tests CLAUDE.md line (two bullets' detail moved verbatim to NOTES.md for the 12 KB limit), fault lines line-buffered in both drivers.
- the report commit.

OWED: `736-kit-bsu4g-test` (key kit-bsu4g-test) and `737-kit-bsu4g-mech` (key kit-bsu4g-mech), queued as my last act. No process of mine runs past the handoff.

Shared files were touched by appended rows or one localized hunk only (bsu4p runs in parallel): c4_allowlist.tsv (4 rows at the end), run_sabotage_matrix.sh (one vocabulary entry and one case arm, `g2v`), memfn/tests/CLAUDE.md (one bullet added, two shortened) and NOTES.md (two moved paragraphs).

## G2-V UNIT

The check is `memfn/tests/g2_vspan.py unit`, run by `memfn/tests/run_g2_win.sh` as its section V (also `run_g2_win.sh --v` alone, the mech suite `g2v`).

**The generator** (`memfn/tests/g2/g2_vspan_gen.c`, the only file that calls the kit) renders each case of the space as a REPORT window site: one alternative, NPOS = k + 1 positions of one set, every position core and verify-YES, stated as ONE span. It renders each case twice, each on its own art:
- at x86-64-v3 with a sink that offers the bracket ops. This is the text under test. Its file-scope text goes, inside the target's region, into `vsites.c` with a one-call wrapper of the selector `g2vu<ID>_mf1_vs0`;
- at the portable target under the lever `span-head=0`. This is §10.1's k SOURCE: the loop `J = LO; for (; J < END;`, k = END - LO.

One span, not g2_win_gen.c's 128-position spans: with 128-position spans a D-hors stop's window is cut at 128, and a stated k 1000 read k 127 (measured on the prototype). pcrec states a stretch up to 4095 as one span at width 4095.

**The space** (python, seeded `g2vu|20261122`):
- sets of 1..8 random byte ranges in both polarities, two each (32);
- 4 random sets of bytes >= 0x80, and `[\x80-\xbf]`;
- `[0-9a-f]`, `[0-9]`, `\w`, `[aeiou]`;
- the empty set `[^\x00-\xff]`;
- six 255-member sets: `[^\n]` and `[^\xHH]` at 0x00, 0x7f, 0x80, 0xff and a random byte;
- single-byte-removed sets: six bases, each less its highest, lowest and a random member, written `(?!\xHH)BASE`;
- each set at two byte-rate regimes. `dense` makes the stop set common, so the site routes D-hors (T-vwin). `rare` routes R7w's walk (T-vscan). The k values are the rung edges 16, 17, 31, 32, 33, 63, 64, 65, 999, 1000 plus two random interior k (dense), and 16, 17, 24, 31, 32, 33, 63, 64, 65 plus one random (rare).

That is 1,430 cases, of which 1,216 render V.

**What the runner reads off the texts, never the kit's tables:**
- LO and K from the head-0 loop;
- the row (a `_sh[256]` shift table means D-hors);
- B = 32 where K >= 32, else 16.

It holds the kit's own numbers in its `__w32` text to these: `p = S + C + LO`, the loop's `i + B < K`, and the final `p + (K - B)`. It prints both and fails on a disagreement. It also requires exactly 1 selector call in the walk and 1 `__w32` call in the selector.

**The control.** The class is written in the TEST as a regex string. The bytes handed to the kit are derived from the same written spec by set arithmetic. Before anything runs, they are held equal to `re`'s reading of the class (a disagreement is the test's own fault). The expected answer of every window is `all(re.fullmatch(cls, bytes([b])) ...)` over the window's bytes: the kit's set and nibble tables are never read.

**The windows** (driver `memfn/tests/g2/g2_vspan_drv.c`), per V case:
- 3 all-member windows;
- the staircase: one non-member at each position (every position up to K 65; beyond that, the block edges near both ends plus 16 random positions);
- 24 random windows with 1..3 bytes from the whole byte space;
- SWEEPS: every byte value 0..255 at position 0, K-1, B-1 and B.

Each window runs twice, flush against a PROT_NONE page at each end (GUARD PAGES). Every 97th window's FNV-1a hash is printed by the driver and recomputed by the runner, so the window the driver built is the window the runner described (12,846 checked).

**Result** (`bash memfn/tests/run_g2_win.sh --v`, log $PCREC_TMPDIR/scratch/bsu4g/v1.log): 1,177,900 windows x 2 placements, 610,819 of them false, **0 wrong**, 0 faults.

## G2-V WHOLE

The check is `memfn/tests/g2_vspan.py whole`, in the same section V.

**The population: 84 patterns**, each compiled by build/pcrec at -fno-memfn-simd and at -fmemfn-simd=x86-64-v3, at --window-search-width 32 and 4095. That gives 336 artifacts.
- `cls{n}` for 8 classes (`[0-9a-f]`, `[0-9]`, `[^\n]`, `[\x80-\xbf]`, `[aeiou]`, `\w`, `[A-Z]`, `[+.0-9]`) at n 16, 17, 24, 25, 32, 33, 41, 65, 66;
- `[0-9a-f]{1001}`, `[^\n]{1000}` and `[0-9a-f]{300}`;
- mixed patterns:
  - two stretches: `[0-9a-f]{20}[g-z]{20}`, `[0-9]{30}[a-f]{30}`, `[^\n]{40}[0-9]{20}`;
  - a stretch beside non-core positions: `\b[0-9a-f]{32}\b`, `\b\w{40}\b`, `\b[0-9]{25}`;
  - a literal run beside a stretch: `abc[0-9]{30}`, `[0-9a-f]{30}xyz`, `[0-9a-f]{25}\.[0-9]{25}`.

**Subjects** (11,280, every artifact of a pattern runs on all of that pattern's subjects):
- the cards' six regimes (hit-dense, near-miss, random, short-subject, miss-heavy, not-warm; 700 bytes, 3,000 for patterns over 200 positions);
- the forced near-miss staircase: for EVERY stretch position, the witness with that position failing, both as the whole subject (the first window) and after a match. That is 10,440 subjects, so the 1001-position pattern gets all 1,000 indices;
- edges: a match alone, one byte short, empty, and two matches then a near-miss.

**The control:** python `re.finditer` over the same pattern string. The driver (`memfn/tests/g2/g2_vwhole_drv.c`) runs the find-all, restarting at the match end, and prints the count and an FNV-1a hash of `start,end;` per (artifact, subject, placement). The runner compares the count and the hash.

**V sites are counted by §10.1's k source.** The script builds the traced harness from the tree under test (`tests/memfn/mk_mftrace_lib.sh` over LIB, then `cli/main.c -DPCREC_HARNESS`). It reads `MFTRACE FDROUTE` for the row and frame, and k off the head-0 lever compile's loops. C-own means the loop's test reads no table. The predicate (frame E-find; D-hors 16..1000, R7w 24..64; the first eligible stretch per site) is applied in the script. Beside it is the kit's own answer: the sites whose walk calls a selector, and at SIMD-on one `__w32` call per V site (0 at SIMD-off). A disagreement is a failure; there were 0 over 336 artifacts.

**Result** (same log): 90,240 find-all runs, both placements, **0 wrong**, 0 faults; 6,659 matches over the V-site patterns. Section V's whole wall is about 13 s (336 gcc -O2 compiles on 6 threads).

## GUARD PAGES

Both drivers map [PROT_NONE page][data][PROT_NONE page] and run every input twice. A SIGSEGV/SIGBUS handler prints the faulting byte's offset from the input's first byte and which guard it hit, then exits 3. The runner reports it as a failure naming the case, subject and placement.

**UNIT.** The window is exactly the stretch: S[C + LO] .. S[C + LO + K - 1], with C = 3 and S = window - C - LO.
- **Low placement:** the window's first byte S[C + LO] is the first byte after the low guard page. A read of **S[C + LO - 1]** (or anything below it) faults. This proves the V function never reads below p = S + C + LO, on every one of the 1,216 renderings, at both rungs.
- **High placement:** the window's last byte S[C + LO + K - 1] is the last byte before the high guard page. A read of **S[C + LO + K]**, one byte past the stretch, faults. This proves the final block `p + (K - B)` and every loop trip stay inside [p, p + K) on every rendering, D-hors and R7w alike. This is §4.2's over-read argument, checked: the loop's trips read [p + i, p + i + B) with i + B < K, and the final block reads [p + K - B, p + K).

**WHOLE.** The subject is s[0] .. s[n - 1].
- **Low placement:** s[0] is the first byte after the low guard page, so **s[-1]** is proven unread by the whole find-all (the walk, the bound, V and the verify). For V this reaches the stretch's lower end where the stretch starts at the candidate (D-hors, LO 0) and the candidate is at 0: plant (c)'s K = 15 case (bsu4p's).
- **High placement:** s[n - 1] is the last byte before the high guard page, so **s[n]** is proven unread. For V, the stretch's last byte is s[n - 1] only where the stretch ends at the PATTERN's end and a match sits flush at the subject's end. That holds for the R7w walk (`[0-9]{25}`: stretch [1, 25) after the stop at 0) at every width and layer. On D-hors the stretch [0, k) is followed by the probe at k, which the hoisted bound keeps in bounds, so the byte past a D-hors stretch is s[c + k] < n, never the guard.
- Measured on plant (b), whole alone: `[0-9]{25}` at width 32, SIMD-on, the 700-byte hit-dense subject (28 back-to-back matches, the last flush with the end), high placement: **FAULT reading s[700], high-guard**. That is exactly s[n].

## PLANTS

Both are mech rows with a REACH witness ([MECH-REACH]), suite `g2v` (`run_g2_win.sh --v`: unit and whole, about 30 s). Ids S3525 and S3526 are from the brief's range; S3527-S3529 are unused.

- **S3525, plant (a)**, `tests/mech/sabotages/S3525_vspan_nibble_table_drops_member.sh` (708's `nib_drop`):
  - the plant: in `vs_w32_block`, the nibble-table loop skips the stretch set's HIGHEST member;
  - REACH: `[0-9a-f]{17}` at x86-64-v3, expecting `    return rx_mf1_vs0__w32_b(p + (16 - 16));`, the same function's line after the anchored loop. REACHED;
  - in-lane DETECTION: **DETECTED**, `g2v:2444fail/1613pass` ($PCREC_TMPDIR/scratch/bsu4g/mech1.log). A hand run of the unit alone on a planted kit: 206,972 wrong window answers, every one a window holding the dropped byte (for example `[\x02-\x34]` k 1000: "the kit says 0, re says 1").
- **S3526, plant (b)**, `tests/mech/sabotages/S3526_vspan_final_block_reads_past.sh` (708's `past`):
  - the plant: the final block is written `p + (K - B + 1)`;
  - REACH: the design's witness `[0-9]{25}`, expecting `    return rx_mf1_vs0__w32_b(p + (24 - 16));`. REACHED;
  - in-lane DETECTION: **DETECTED**, `g2v:1258fail/369pass` (mech1.log);
  - whole ALONE on a planted tree (a `git archive` copy built in scratch, $PCREC_TMPDIR/scratch/bsu4g/plantB): the end-guard FAULT above, `[0-9]{25}`, s[700]. Unit alone faults too: its high placement is flush with the stretch's end on every rendering.

**FINDING for the design text (block_span.md §10.2, plant (b)'s row).** The row says that on HORS "the byte past the stretch is the probe, in bounds, so the plant is benign there". That is true of the READ, but the plant is not benign in ANSWERS on D-hors where K is a multiple of B. The loop's last trip then ends at K - B, and the shifted final block [p + K - B + 1, p + K + 1) leaves byte K - B untested. At K = B (k 16, 32) that byte is the stretch's first.

Measured (whole alone on plant (b)): `[0-9a-f]{17}` at both widths answers 1 match on a stair-first subject where re finds 0, before the end-guard fault. The check is not weakened (the plant is caught twice). Only the row's sentence is too broad. Proposed text: "benign in its reads on HORS (the probe); it still misanswers where B divides K, which G2-V whole's staircase catches".

## POPULATIONS

Every floor is a literal in `memfn/tests/g2_vspan.py`, measured on this box at seed 20261122, less about 10% (K35).

| population | measured | floor |
|---|---|---|
| unit V renderings, vwin (D-hors) B 16 | 192 | 172 |
| unit V renderings, vwin B 32 | 576 | 518 |
| unit V renderings, vscan (R7w) B 16 | 138 | 124 |
| unit V renderings, vscan B 32 | 310 | 279 |
| unit vwin reaches each k of 16, 17, 31, 32, 33, 63, 64, 65, 999, 1000 | each | 1 each |
| unit vscan reaches each k of 24, 31, 32, 33, 63, 64 | each | 1 each |
| unit V cases per set kind: ranges / neg / high / named / full255 / removed | 304 / 304 / 95 / 76 / 114 / 323 | 273 / 273 / 85 / 68 / 102 / 290 |
| unit empty-set cases (each refused by the kit, counted) | 22 | 19 |
| unit windows (x2 placements) | 1,177,900 | 1,060,000 |
| unit false windows | 610,819 | 549,000 |
| whole V sites by the k source, vwin B 16 / B 32 / vscan B 16 / B 32 (per pattern x width) | 35 / 20 / 19 / 13 | 31 / 18 / 17 / 11 |
| whole mixed patterns x widths with a V site | 8 | 7 |
| whole subjects / staircase subjects | 11,280 / 10,440 | 10,150 / 9,400 |
| whole matches over V-site patterns | 6,659 | 5,990 |

**Populations that are 0, printed and not floored (K35):**
- **The empty set never reaches V.** The kit refuses an empty-set window site at its define ("no Table E row serves this frame"), so the nibble test's empty-set table is unreachable from any site. All 22 empty-set cases are refused as expected and counted as passes.
- **A literal run beside a stretch never reaches V.** In every probed pattern (`abc[0-9]{30}`, `[0-9a-f]{30}xyz`, `=[0-9a-f]{30}`, `[0-9a-f]{25}\.[0-9]{25}`, ` [^\n]{30}`, `e[0-9a-z]{30}`, `[^\n]{40}\n`, at both widths) the literal is D1's stop (memchr), and V is keyed on D-hors/R7w. The three "lit" patterns stay in WHOLE for their answers, with 0 V sites. This is a design-text observation: §10.2's "a literal run plus a stretch" is a site kind with no V population at today's routing. The mixed V population is the two-stretch and word-boundary kinds (8 pattern x width cells).
- Sets of one or two members route D1 or PAIR, never V, so they are left out of the unit's space (the random ranges always hold two or more bytes).

## IN-LANE RUNS

All logs are in $PCREC_TMPDIR/scratch/bsu4g/.
- **Premise test:** `build/pcrec -p rxa -fmemfn-simd=x86-64-v3 --pattern '[0-9a-f]{17}'` gives 1 walk call `rxa_mf1_vs0(rxa_mf1_s, rxa_mf1_c)` and 1 `return rxa_mf1_vs0__w32(rxa_mf1_s, rxa_mf1_c);` in the selector. The existing `run_g2_win.sh` before any edit: checks passed 27,376, failed 0 (win_base.log, 216 s).
- **The file the suite runs, standalone:** `bash memfn/tests/run_g2_win.sh --v` (section V alone): checks passed 2,830, failed 0, 27 s (v1.log).
- **The full window family with section V:** `bash memfn/tests/run_g2_win.sh` (what `run_g2.sh` section 4w runs): see win_full.log; the result is in my handback message. The traced pass (`G2W_TRACE=1`) skips section V by design.
- **Mech, in-lane:**
  - `REACH_ONLY=1 bash tests/mech/run_sabotage_matrix.sh S3525 S3526`: 2 of 2 REACHED (reach1.log);
  - `bash tests/mech/run_sabotage_matrix.sh S3525 S3526` under `scripts/boxlock run`: 2 of 2 DETECTED, `== mech run COMPLETE: 2 rows (unexpected: 0, undetected: 0, unreached: 0, anomalies: 0, oracle-skipped: 0)` (mech1.log).
- **`make test-memfn-arch`:** 32 passed, 0 failed, after the C4 rows.
- **`make strict`:** clean.
- **Not run in-lane:** full `REACH_ONLY` over every row. No memfn/src or src/ file changed, so no strategy fires in a new place (BOILERPLATE's trigger does not apply). The existing rows' detection is in the OWED mech job.

## OWED RUNS

Queued by `scripts/boxqueue add` as my last act (non-timing, no window ask). Job scripts: $PCREC_TMPDIR/scratch/bsu4g/jobs/.
- **`736-kit-bsu4g-test`** (key kit-bsu4g-test): `make -j16`, then `scripts/perfrun --label bsu4g -- $PCREC_TMPDIR/scratch/bsu4g/maketest.log`, with TMPDIR set. The verdict is make's `*** [...test-` lines. It includes test-memfn-g2, whose `run_g2_win.sh` now runs section V (about 30 s more).
- **`737-kit-bsu4g-mech`** (key kit-bsu4g-mech), ready after kit-bsu4g-test. DETECTION of 36 rows:
  - my S3525 and S3526;
  - U2's S730 S689 S3280 S693 S690 S694, S3276-S3279, S3281-S3285, S2982, S3500, S3501, S3510;
  - U3's S3515-S3518, S1852, S3170, S3198, S699-S703, S723, S724, S728.
  - Expected last line: `== mech run COMPLETE: 36 rows (unexpected: 0, undetected: 0, ...)`.

**CHARTER VS COMMITTED** (each TASK bullet and its artifact):
- G2-V unit: a new section of `run_g2_win.sh` at x86-64-v3 arts, over the full generated space and the rung-edge and interior k, with the python re control on the class written in the test, PROT_NONE at both ends, and literal floors per rung and per row. DONE: `memfn/tests/g2_vspan.py` `unit`, `g2/g2_vspan_gen.c`, `g2/g2_vspan_drv.c`, `run_g2_win.sh` section V.
- G2-V whole: `cls{k+1}` and mixed patterns, SIMD-on and SIMD-off, find-all at widths 32 and 4095, re over the six regimes plus the staircases (every index, first window and after a match), PROT_NONE at both ends, floors per site kind by the k source. DONE: `g2_vspan.py` `whole`, `g2/g2_vwhole_drv.c`. The "literal run plus a stretch" kind has V population 0 (POPULATIONS), so its floor is not set.
- Plant (a), caught by G2-V unit, mech row with REACH: DONE, S3525, DETECTED in-lane.
- Plant (b), caught by G2-V whole's end guard page, witness `[0-9]{25}`, mech row with REACH: DONE, S3526, DETECTED in-lane; whole-alone fault at s[n] shown.
- The report says exactly which byte each guard page proves unread: DONE (GUARD PAGES).
- The two owed box jobs: QUEUED (OWED RUNS); their verdicts are OWED to the manager (kit-bsu4g-test, kit-bsu4g-mech).
- Not mine (bsu4p's): the T-table pins, the rest of C18, the routing leg, SPAN-SEED's per-check wiring, DIFFER_PINS, FLOORS, plants (c)-(f).
