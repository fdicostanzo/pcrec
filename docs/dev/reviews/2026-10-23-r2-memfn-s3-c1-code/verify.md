# verify.md — rerun of CONFIRMED findings (crit-memfn-s3-c1, tree ae83da9d4)
Scratch: /tmp/claude-1001/crit-memfn-s3-c1/verify/. Counts = distinct subject-byte reads inside the E-find block
(rx_mf1_s[...] rewritten to a dedup-counting macro, consecutive same-address reads counted once), find-all loop
over the subject; old arm read from source (run-counter loop reads each byte once, ~1.0).

| id | file | claim | rerun | verdict |
|---|---|---|---|---|
| emit F1 | emit | same-set windows lose the run-count scan edge; E-find re-tests run bytes | see F1 section below | VERIFIED |

## emit F1
Command: `pcrec -p rx --features all [--memfn=no-wf-find] -o X.c --pattern P`; instrumented copy compiled with gcc -O2 and driven
over a 64 KB English subject (first 21447 B only: APPROACH.md is 21 KB, not 64 KB) and a 64 KB random-run subject
(runs 1..k-1 of set members separated by a space; no match possible).
- Old (`--memfn=no-wf-find`) emits `RX_DFA_SCAN_EDGE "range"` with a `scan_run_length` loop (`\d{6}` read: each byte read once, run counter, no re-read). New emits `memfn forms=none`, cover E-find (walk@0 + left-to-right verify + `c++`, or D-hors shift loop); the same `RX_DFA_SCAN_EDGE` define is still printed in the new file but the new search function has no run counter (it is a stamp only).
- Tests per subject byte, NEW:

| pattern | English (21 KB) | dense short runs (1..k-1) |
|---|---|---|
| `\d{6}` | 1.005 | 2.500 |
| `\w{8}` | 0.969 | 1.151 |
| `[0-9a-f]{8}` | 0.199 | 1.130 |
| `[a-z]{16}` | 0.638 | 1.943 |

  Old is ~1.0 by construction on all. So: on English the new loop is at or below the old (D-hors shift wins), on dense short-run subjects it is 1.1x to 2.5x of old reads (the critic's 6x was k=16 digits; `\d{16}` not rerun here, the mechanism is the same: D-one c+1 re-reads). Wall-clock not measured (counts only). Claim as a counted-ops statement VERIFIED; magnitude is shape-dependent and smaller for the four named patterns than the critic's k=16 table.

## emit F3 / slot F1 (non-case-pair multi-member stops: memchr -> scalar walk)
Command: `pcrec -p rx --features all [--memfn=no-wf-find] -o X.c --pattern P`, count `memchr(` in the whole emitted file
(old keeps it in a helper, not in rx_search); raw: verify/f3b.out. Observed NEW vs OLD memchr count:
`ab(?=[Qq])` 0 vs 1; `[xq]abc` 0 vs 1 (new loop: `while (!(s[c]==113||s[c]==120)) c++`, old memchr on `a`); `[\x80-\xff]q`/`x`/`j` 0 vs 1;
`[^\x00-\x7f]e` 0 vs 1; `[\x00-\x08]z` 0 vs 1; `the[qx]` 0 vs 1; `ab[qj]cd` 0 vs 3; `ee[qj]ee` 0 vs 1; `e[qj]e` 0 vs 1.
Controls keep memchr in both: `[A-Z]x`, `[0-9]x`, `\dz`, `[XYZ]q`, and `[a-]x`, `[:a]q` (stop is the single literal; NOT movers).
Magnitude not timed. VERIFIED for all 9 of the critic's probes and for slot F1; `[a-]x`/`[:a]q` are controls, not losses.

## emit F2 / slot F2 (SIMD: caseless + context loses vrun)
Command: same with `-fmemfn-simd`, read `RX_MEMFN_FORMS` (raw: verify/f2.out). NEW none vs OLD `vrun@w32+w16` for
`(?i)\bthe\b`, `(?i)\bhello\b`, `(?i)\bthe`, `(?i)the\b`, `(?i)abc(?=d)`, `(?i)[0-9]hello`, `(?i)abc[xy]`, `\b(?i:foobar)\b`, `(?i)foo[0-9]bar`.
Controls `(?i)hello`, `(?i)foobar` keep vrun in both; `(?i)ab\d` none in both. VERIFIED (wake-rate ratios 2-17x not rerun).
Pin lowering (DIFFER_PINS 20->9, 15->10): not rerun (needs sweeps); the claim is read from scripts/emit_sweep.py only -> not checked.

## slot F6
`(?<=[Qq])ab`: NEW RX_DFA_SCAN "unanchored", OLD "unanchored" (memchr). Counterfactual `(?<=q)ab`: NEW "cover". So cover is lost only
for the two-member context stop, and it is not a regression vs old (same artifact as old). VERIFIED as stated ("missed win, not a regression").

## trade F2 (make test-axes memfn arm), STATIC
`build/pcrec --list-axes` memfn section lists `wf-find` (line 218) and `wf-hors` (219). tests/axes/memfn_arm.py:232 asserts
`set(spelling) == {k[0] for k in MEMFN_CLASS}` (non-`--measure` mode); MEMFN_CLASS (line 68) has zero `wf` keys (grep 0);
`git diff --stat c3ea619c3 ae83da9d4 -- tests/axes` is empty. VERIFIED statically: the population check must fail. Not run (no make).
Caveat: assumes read_memfn_section feeds every memfn row (it builds `spelling` from all rows) and the arm is on by default in test-axes.

## slot F7 / F8 (spec)
- registry.md:174 names "E-find" and "the kit refuses a REPORT site"; registry.md:175 names `HORS_MIN`; tuning.md:969 names "D-hors". VERIFIED.
- Over-promise: registry.md:174 promises two memchr streams for bit-apart bytes and SIMD kernels for such windows; `ab(?=[Qq])` gets a byte walk and `\b(?i:foobar)\b` gets no vrun (reruns above). VERIFIED.
- F8: memfn/src/window.c:1575 `d_hors_holds` also declines `dx->whi < 0`; registry.md:175 states only mass >= HORS_MIN and >= 2 positions. VERIFIED (design-doc side not read).

## slot F6 aside: other slot CONFIRMED (F3, F4, F9, F11, F12): not rerun (not in priority list). F12: not checked.

## house (cites only)
| id | check | verdict |
|---|---|---|
| F1 | window.c:1377-1384 (translate into e->L), 1572 (d_hors_holds writes dx->wlo/whi via `hors_window(.., &dx->wlo, &dx->whi)`), 1640-1650 (translate into b->fn) exist | VERIFIED (const cast of dx not seen in the 1572 lines I printed; the writes through dx are) |
| F3 | compose.c wplan branches at 963-1261 (16 hits incl. 1261 `r->wplan ? r->cls.includes : r->arm->includes`) | VERIFIED |
| F4 | wf_b_search header 2397-2398 mentions `hit`, signature (rc,b,p,d,byte) has none; kit.h:254/767/795 and window.c:1857 say "preview art"/"preview's own" | VERIFIED |
| F5 | wf_find_expr at 2503 has no header comment (2498-2502 is the previous function); `w->hors` appears 4 times in the span, critic says three | VERIFIED (minor miscount) |
| F6 | fd_find at finder.c:918; PAIR row finder.c:304; `.step` read at 1154 | VERIFIED (not read in depth) |
| F7 | window.c:1783 WF_WHY_MAX=320; 1820 "the kit manager's R2 ruling"; compose.c:1048 "D172 S3" in a message | VERIFIED |
| F8 | internal.h:3849-3855 kit_proof INERT comment; compose.c select_arm early `return NULL` for REPORT at 276-283 | VERIFIED |
| F2, F10 | stack numbers (-fstack-usage) and Table B flag restatement not rerun | NOT RERUN |

## trade F1, F3-F5 (cites only)
- F1: `grep -rn no-wf-find tests/axes scripts/emit_sweep.py Makefile` -> one hit, a COMMENT at scripts/emit_sweep.py:451; no functional use. PARTLY: the "finds nothing" is true for use, not literally. (54 files under tests+scripts do mention it, the hand-picked witnesses.)
- F3: read_588.py: `sample_fails` appended at 229 (dropped rows) and 244 (stratum gmean) only; per-row/cell FAILs go elsewhere. VERIFIED by read.
- F4: pick_588.py:110 prints "movers N, generatable N, picked N" per stratum; sums 391/804 not recomputed. VERIFIED (cite), figures not rechecked.
- F5: git log c3ea619c3..ae83da9d4 order (newest first): ae83da9d4, d190e3a70 (C1 commit), 8671624a4 (job 605 RESULT), ..., b5b85aeac; so 8671624a4 is older than d190e3a70. VERIFIED (b5b85aeac is lower down, i.e. earlier than 605; the critic's "605 precedes the C1 commits" is true for d190e3a70, and b5b85aeac is the S3 commit named in the report, not a C1 fix: PARTLY on the second commit id).
