# Lane bsu4p: R-47 unit U4, second half (T-table pins, the rest of C18, routing leg, plants c-f)

## STATE AT HANDOFF

STATE: delivered, validation OWED (two box-queue jobs, keys below)

Branch lane/bsu4p, cut from lane/memfn-k1108 at ad3c8f1c2. Checks only: no file under src/, cli/, lib/ or memfn/ changed, so no emitted byte moves and no abi event (the premise held: no memfn/src edit was needed).
Rulings file docs/dev/lanes/bsu4p_rulings.md: empty at every checkpoint; no entry applied.
Premise test (cells 1-4 at x86-64-v3, flags `-p rxa --features all -fmemfn-simd=x86-64-v3 --window-search-width=W`): `[0-9a-f]{16}` at 32 and 4095 reads 0 selector calls / 0 `__w32` calls; `{17}` reads 1 / 1 at both. Absent, absent, present, present, as expected.

OWED keys: kit-bsu4p-test, kit-bsu4p-mech (see OWED RUNS).

## T-TABLE PINS

`tests/memfn/span_pins.py` (new), called from C18's main (`simd_floor_check.py`) so the one `checks passed` line and the `simdfloor` mech arm score it.
- 20 cells, a literal list in the file (cells 1-20 of block_span.md §10.2, widths and flags as the table). Cells 17-20 render at the default layer and at x86-64-v3 (one cell each). Count rule as ruled: "present" = 1 selector call `rxa_mf<h>_vs\d+(rxa_mf<h>_s, rxa_mf<h>_c)` in the walk and 1 `__w32(rxa_mf<h>_s, rxa_mf<h>_c)`; "absent" = 0 and 0; read off the rendered text, never off window.c. Cells 17/18 use pcrec-harness `--harness=span-head=8`, 19/20 `--memfn=span-loop`.
- The control shares no source with the table: the §10.1 k source. Per cell, the finder row and frame from the traced build's `MFTRACE FDROUTE` record, k from the head-0 compile's loop text (END - LO), the predicate (D-hors 16..1000, R7w 24..64, E-find) applied in the check. Each cell is red if its row/k is not the literal the design names (reach, K35), if the text count is not the literal, or if the predicate and the literal disagree. For cells 17-20 the predicate holds (V's own row would take the stretch) and the expectation is 0, which is what makes plant (e) a witness.
- `run_simd_floor.sh` builds `build/libpcrec_mftrace.a` and links a traced CLI for it (`--trace`), plus `build/pcrec-harness` (`--harness`).
- Floor: 20 cells (not 11 patterns). Clean run: all 20 cells read as the design says (row/k: D-hors 15/16/1000/1001, R7w 23/24/64/65, D1 26, PAIR 26, D1w 26, D-hors 20).

## C18 AMENDMENT

The U4 part of block_span.md §10.2's amendment, in `tests/memfn/simd_floor_check.py`:
- NAMED gains an optional fourth column (targets). The three span witnesses `[0-9a-f]{17}` (HORS k16, B16), `[0-9]{25}` (R7w k24, B16), `[0-9a-f]{41}` at width 4095 (HORS k40, B32) are NAMED at x86-64-v3 only (R71-1); at x86-64 they are skipped, not read as "NOT a mover".
- Literal floor `SPAN_NAMED_FLOOR = 3` span SIMD FUNCs, each witness holding exactly one `<p>_mf<h>_vs0` selector (always_inline head). Clean: 3 / 3.
- Controls (2)-(4) are mech rows (PLANTS): S3534 `__w32` outside the bracket, S3535 a non-admitted level name, S3536 a selector that does work.
- Found while building S3535: `HELPER` saw the width-64 name but the per-level stats did `next(...)` over the admitted levels and crashed (ANOMALY, no count scraped). Fixed (an unadmitted width is named by the lint, never a crash).
- U3 already had the head family, `_b` name form, -O0 rule and control (1) (S3515, S3516, S3517).

## ROUTING LEG

`tests/memfn/routing_shape.py`: the FUNC population adds the NAME rule `_mf\d+_vs\d+$` and the V head family `static inline __attribute__((always_inline[, unused])) int <fn>(const unsigned char *<s>, size_t <c>)`, read with the forwarded argument list `<s>, <c>`. The rule is today's code (routed through `<fn>__body` defined above with the same parameters, one call, the called level defined above, no directive in a work body): V reuses `selector_body`. `check` counts V FUNCs with the offset-skip ones.
Seven selftest shapes (`VCONTROLS`, in `selftest()` and so in libc_census's controls, each also holding its FUNC count): routed (OFF) and one call to its level (ON) pass; selector does work, drops a parameter, helper below, level not defined above and unrouted are red. 21 of 21 controls PASS (`python3 tests/memfn/routing_shape.py`). On real artifacts of `[0-9a-f]{17}` (SIMD-off and x86-64-v3) it counts 1 FUNC and no violation.
Side effect, re-pinned: the census's `funcs` (run_libc_census.sh, full tier) rises 141 -> 281 because V selectors are now counted; floor re-pinned AT the measure (K35), `make test-memfn-stamps` 36/0.

## SPAN-SEED WIRING

Per block_span.md §10.1's table, what was wired in this lane:
- C18 / simdfloor: its corpus population already includes the `.rxt` (emit_sweep's enumeration); NAMED and floors as above.
- The identity gate (G-4) and the deny arm's DIFFER rows were wired at U2/U3 (`span_vector_identity.py`; `memfn_arm.py`'s span-vector rows). Their floors read the same 28 / 20 / 31 here, verified by plant (d) below. `DIFFER_PINS` in `scripts/emit_sweep.py` holds the `--memfn=no-span-vector` cells at 28 / 20 / 0 / 0 already (U2); nothing in this lane moved them, so no edit.
- NEW here: `span_pins.py` reads the 41 patterns of `tests/memfn/span_seed.rxt` with `pcrec --list-source` (not a copied list) at widths 32 and 4095 at x86-64-v3, counts V sites by the k source per site, counts selector calls per site in the shipped text, prints both and fails on any disagreement, floored 28 / 31. Clean: 28 = 28 and 31 = 31, every site agreeing.
- G1's population (§9.4, U6) and the T-table pins' own cell list (they do not read SPAN-SEED) need nothing.

## FLOORS

- C18 `FLOORS`, pinned AT the measure (5700 corpus patterns x 2 engines + the named): x86-64 (74, 74, w16 74); x86-64-v3 (105, 105, w32 105). The v3 figure decomposes as 74 + 28 (span_seed's V sites at the default engine) + 3 (the span NAMED witnesses). The x86-64 floor was 55 in the file (a stale pin from before the corpus grew); the measure there is 74 with no V mover, so it was re-pinned too. Say so if that is out of scope.
- `funcs` 141 -> 281 (ROUTING LEG).
- SPAN-SEED 28 / 31 and the 20 cells and `SPAN_NAMED_FLOOR` 3 are literals in the code.
- `DIFFER_PINS`: unchanged, floors verified (see SPAN-SEED WIRING).

## PLANTS

Mech rows S3530-S3536, all `SAB_FILE=memfn/src/window.c`, each with a REACH probe (REACH_ONLY: 7 of 7 REACHED). DETECTED in the matrix at 72fae9e65 (`run_sabotage_matrix.sh S3530..S3536`, log scratch/bsu4p/logs/plants.log), and the leg each plant is rejected by was read off a scratch-tree run:

| row | plant | matrix | rejected by (read) |
|---|---|---|---|
| S3530 (c) | T-vwin lower bound becomes 15 (`WF_VWIN_LO - 1`; a literal edit of the constant would fail the `_Static_assert` at build, so the predicate is edited) | DETECTED simdfloor 5 fail | pin cells 1-2 ("pcrec failed to render": the renderer's K >= 16 refusal) |
| S3531 (d) | the span-vector deny ignored (the table's option column reads NULL) | DETECTED axesmemfn 12 fail | memfn_arm.py span-vector DIFFER rows, @default and @simd, byte and utf8: "WITNESS ... did not differ under the deny" |
| S3532 (e) | V's rows walked before T-lever / T-force (enum order) | DETECTED simdfloor 36 fail | pin cells 17-20: "1 selector call(s) in the walk" (literal 0), at both layers |
| S3533 (f) | T-vscan keyed on pick FF_WALK | DETECTED simdfloor 1 fail | pin cell 15 alone: "1 selector call(s) ... (literal 0, 0)" |
| S3534 ctl (2) | `__w32`'s head outside the bracket | DETECTED simdfloor 32 fail | leg (c)'s byte count ("inserted 1740 bytes, SIMD_GUARDED_BYTES 0x659") |
| S3535 ctl (3) | helper named at width 64 | first run ANOMALY (a crash in C18, fixed in the next commit); after the fix rejected by the exclusivity lint ("guard lint: helper ...__w64 is no admitted level") in a scratch-tree run; the matrix re-run is OWED (kit-bsu4p-mech) | the lint |
| S3536 ctl (4) | selector call line gains `!= 0` | DETECTED simdfloor 158 fail | the routing leg: "(d) ...: a line that is not one call" |

Note on (d): "ignored at SIMD-off" is the one deny path: the table has a single option column read at every layer, so the plant ignores it at every layer; the default-layer DIFFER cell is the one the design names, and it is red. Note on (e): under the plant the head-0 harness compile (the k source) also renders V, so the pin cells' k-source leg reads k 0 as well; both the text count and the k source go red.

## IN-LANE RUNS

- `make strict`: green. `make test-memfn-arch`: 32 / 0 (c4_allowlist rows for the six new rows' SAB_REACH).
- `bash tests/memfn/run_simd_floor.sh` (the named file `make test-memfn-simdfloor` runs), at the tip with the stats fix: checks passed 22846, failed 0 (log scratch/bsu4p/logs/clean.log; the earlier run at 72fae9e65: 22846 / 0).
- `make test-memfn-stamps`: 36 / 0 with `funcs` 281.
- `python3 tests/memfn/routing_shape.py`: all 21 controls PASS.
- Plants: matrix as in PLANTS; scratch-tree runs (`--every 40`) for the rejecting leg, one per row.
- NOT run in-lane: `make test` (queued).

## OWED RUNS

Queued per RUNS.md, non-timing, after the commit that carries this report:
- `kit-bsu4p-test`: `make test` on the tree through scripts/perfrun. Includes simdfloor (pins and census), stamps, arch, claudemd size, the rows census.
- `kit-bsu4p-mech`: S3530-S3536 plus the U2/U3 rows (S3515 S3516 S3517 S3518 S730 S693), readiness `after kit-bsu4p-test`. S3535 must read DETECTED (its matrix verdict is owed after the fix).

## CHARTER VS COMMITTED

- 20 T-table pin cells: tests/memfn/span_pins.py (DONE).
- SPAN-SEED per-check wiring and floors: span_pins.py census 28 / 31; C18, identity gate, deny DIFFER rows already carry the `.rxt` (DONE; DIFFER_PINS unchanged on purpose).
- The rest of C18: NAMED three, per-target column, floor, FLOORS re-pin (DONE); controls (2)-(4) = S3534-S3536 (DONE, S3535 matrix verdict OWED, kit-bsu4p-mech).
- Routing leg: routing_shape.py name rule, head family, 7 selftest shapes (DONE).
- `DIFFER_PINS` floors: verified unchanged (DONE, no edit); C18 `FLOORS` re-pin (DONE).
- Plants (c)-(f): S3530-S3533 (DONE; matrix DETECTED; legs read).
- Owed runs: kit-bsu4p-test, kit-bsu4p-mech (OWED, queued as the last act).

Findings for the manager to file: (1) C18's per-level stats crashed on an unadmitted width (fixed here). (2) The `x86-64` FLOORS pin was stale (55 vs measure 74) before this lane. (3) A literal edit of `WF_VWIN_LO` to 15 breaks the build via bsu3fix's `_Static_assert`; design §10.2's plant (c) is therefore edited at the predicate.
