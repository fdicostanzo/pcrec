# Lane clss1: [CLS-TREE] S1, the kit in src/ (report)

**Lane:** clss1, opus, engine tier, implementation. **Branch:** `lane/clss1`,
from `main` at `fdcf3e00`. **Charter:** `docs/design/cls_tree_design.md` §6,
the S1 row, as updated by D131. **Date:** 2026-09-29.

## 1. Summary

The kit is in `src/gen/clskit.{c,h}`, and no emitter calls it. No artifact
moves, there is no abi event, and nothing is caller-visible. It has five
parts:

- **The seven leaf forms.** `CUBES` is tier 1 only, per CT-1.
- **The sectioning DP.** It is a size optimizer only (D131 item 2), with
  K's λ = 4 as table data. It is integer Q16, so a selection is
  bit-reproducible across boxes.
- **The whole-set forms** `P3` (TS = 10), `P2` and `B1`.
- **The shared byte atom table** ([OPT-CLSPACK], D131 item 6).
- **The D131 `--tune` class-form selection.** It is one first-match table,
  `ROWS`: eight rows, each with a name, a one-line predicate, its
  positions, its form and a deny ordinal. The predicates are a closed tag
  set evaluated by one exhaustive switch.

Each form has a C emitter that produces a `static inline int FN(unsigned cp)`.
Every emitted matcher answers correctly for every unsigned `cp`, not only
for code points up to 0x10FFFF.

`tests/clskit/` is a new `make test` section, `test-clskit`, with three
checks:

- **The differential.** Every emitted form is compiled under the harness's
  `-Werror` GENCFLAGS and compared against a reference on all 1,114,112
  code points plus three beyond. The populations are the 312 uprops sets,
  the K53 twelve, the 41 corpus byte classes and the 226 proptest sets. The
  composition law is checked on all 146 proptest compositions.
- **A census.** Every form must have been emitted at least once.
- **A C-vs-study cross-check** of sectionings at four λ, whole-set bytes,
  the atom count and every table choice.

It is green: **5 passed, 0 failed; 8,451,676,390 code-point checks and
325,320,704 law checks, 0 mismatches; 1,686 sectionings, 23,640
selections, 0 disagreements, 3 exact ties.**

**ONE DESIGN POINT PROVED WRONG IN CODE AND IS STOPPED (§3).** D131's
byte-comparing predicates were calibrated on MEASURED object bytes. The
compiler can only read the DP's MODEL bytes, and the model runs about 13%
low for `K`. So the `0`/`+1` row picks `P3` on 2 of the K53 twelve, where
the ruled evidence says 12. I implemented the table as ruled and did not
invent a fix. A ruling request with three options went to the manager
mid-lane, and it is repeated in §3.

## 2. What landed

| file | what |
|---|---|
| `src/gen/clskit.h` | the kit's API: `ClsLeaf`, `ClsSection`, `ClsKit`, `ClsForm`, `ClsAtomTable`, `ClsDeny`, `ClsRow`, `ClsSelectIn`, `ClsChoice`, and the entry points |
| `src/gen/clskit.c` | `LEAF` (the fit windows and the size/op model per leaf, as data), `PLACE` (the ruled placements, one home), `cube_of`, `page64_price` (O(k)), `section_best` + `pcrec_clskit_partition` (the DP), `intern_records` (the ONE dedup for pages, blocks and atoms), `build_pages` (P2/P3), `pcrec_clskit_whole_bytes`, `pcrec_clskit_atoms`, `ROWS` + `pred_holds` + `pcrec_clskit_select`, and the emitters |
| `tests/clskit/` | `run_clskit_tests.sh`, `populations.py`, `clskit_driver.c`, `checker_main.inc`, `crosscheck.py`, `CLAUDE.md` |
| `Makefile` | the `test-clskit` target; `TEST_SECTIONS` and `.PHONY` entries |
| `tests/mech/run_sabotage_matrix.sh` | the new arm `clskit`, registered in the vocabulary before its rows (R31 C11) |
| `tests/mech/sabotages/S360..S363` | the four S1 sabotage rows (§5) |
| CLAUDE.md | entries in `src/gen/`, `tests/` and `tests/clskit/` (new); a note in `studies/cls_tree_study/` that `make test` now imports six of its modules as the reference |

### 2.1 The table, as it ships

| # | row | positions | predicate | form | deny |
|---|---|---|---|---|---|
| 0 | `atom-shared` | all | byte set, ≥ 11 byte-class sites share an atom table of ≤ 64 atoms | ATOM | `CLSD_ATOM` |
| 1 | `byte-kit` | −2, −1 | byte set (every member ≤ 0xFF) | K | `CLSD_BYTE_KIT` |
| 2 | `byte-table` | 0, +1, +2 | byte set | B1 | `CLSD_BYTE_TABLE` |
| 3 | `size-page3` | −2, −1 | bytes(P3) < bytes(K) | P3 | `CLSD_SIZE_PAGE3` |
| 4 | `speed-page2` | +2 | mid gate and bytes(P2) ≤ bytes(B1) | P2 | `CLSD_SPEED_PAGE2` |
| 5 | `speed-bitmap1` | +2 | mid gate and bytes(B1) < bytes(P2) | B1 | `CLSD_SPEED_BITMAP1` |
| 6 | `mid-page3` | 0, +1, +2 | mid gate: K ≥ 16 sections and bytes(P3) ≤ 1.26 × bytes(K) | P3 | `CLSD_MID_PAGE3` |
| 7 | `kit` | all | always | K | none, and undeniable |

Rows 3-7 are D131 item 1, verbatim. `+2`'s "else as `0`" is row order and
not a special case. With rows 4-5 not firing, or denied, row 6 answers `+2`
exactly as it answers `0`. The cross-check exercises that path.

Rows 0-2 are my reading of D131 items 4-6: the kit's byte forms at the
size-leaning positions only; the default byte form stays a table; the atom
table is the default from about 11 sites. **Two readings to confirm:**

1. I put the atom row first at EVERY position, the size-leaning ones
   included. That is clsfit's own proposal for `−2`/`−1`, since the atom
   table is also the smaller form at N ≥ 16 (§1.7.3 item 3).
2. The byte "table" form is `B1`, the kit's general whole-span bitmap. It
   is not a special 32-byte per-site bitmap. For a byte set, `B1` is at
   most 32 bytes and usually less.

### 2.2 Choices on the populations (no deny)

| population | −2 / −1 | 0 / +1 | +2 |
|---|---|---|---|
| K53 twelve | K ×12 | **K ×10, P3 ×2** (L, Xan) | K ×10, P2 ×2 |
| 312 uprops | K 308, P3 4 | K 307, P3 4, B1 1 (the one uprops set whose members are all ≤ 0xFF) | K 307, P2 4, B1 1 |
| 41 byte classes (atom table offered, N = 41, 40 atoms) | ATOM ×41 | ATOM ×41 | ATOM ×41 |
| 41 byte classes, atom row denied | K ×41 | B1 ×41 | B1 ×41 |

The **bold** cell is §3's problem. clsfit's evidence, on measured bytes, is
P3 ×12 at `0`, P2 ×12 at `+2`, and 9/312 uprops sets at `0`.

## 3. STOPPED: the table's byte predicates read MODEL bytes, and the model under-reads K

The ruled table compares `bytes(K)` with `bytes(P3)`, `bytes(P2)` and
`bytes(B1)`. clsfit's evidence (`cls_tree_design.md` §1.7.4) used MEASURED
object bytes. For K, it read `sweep_k53.tsv` `total`, which is the
`.text + .rodata` of a compiled `.o`. A compiler cannot compile its own
candidate to measure it. It has the DP's model: exact rodata plus the
study's per-form `.text` constants (`kit.py` `TEXT_BYTES`).

Those constants are the SYNTHETIC-slope route, where gcc shares code between
identical sections, so they are a best case. The study's own calibration
says the OLS route reads about 2× higher. The whole-set forms' models are
exact, because they are rodata plus one measured `.text` constant.

Measured with the study's own code, K53 twelve, λ = 4:

| set | K model | K measured | P3 | P3 / K model | P3 / K measured |
|---|---:|---:|---:|---:|---:|
| L | 3,621 | 4,196 | 4,249 | **1.17** | 1.01 |
| ^L | 3,671 | 4,201 | 5,136 | 1.40 | 1.22 |
| C | 3,916 | 4,469 | 5,488 | 1.40 | 1.23 |
| ^C | 3,954 | 4,506 | 5,297 | 1.34 | 1.18 |
| Cn | 3,844 | 4,450 | 5,472 | 1.42 | 1.23 |
| ^Cn | 3,930 | 4,466 | 5,472 | 1.39 | 1.23 |
| Xan | 3,984 | 4,513 | 4,641 | **1.16** | 1.03 |
| ^Xan | 4,022 | 4,583 | 5,528 | 1.37 | 1.21 |
| Xwd | 4,221 | 4,818 | 5,545 | 1.31 | 1.15 |
| ^Xwd | 4,175 | 4,866 | 5,736 | 1.37 | 1.18 |
| Unknown | 3,828 | 4,430 | 5,432 | 1.42 | 1.23 |
| ^Unknown | 3,866 | 4,466 | 5,241 | 1.36 | 1.17 |

On every set, measured minus model for K is a near-constant 530-690 B. That
is the matcher's dispatch tree and prologue. The model omits it
(`DISP_BYTES = 0`, "inside the measured slopes") because the synthetic
arms' dispatch was charged to their slopes. Consequences:

- **`0`/`+1`:** z_mid = 1.26 on model bytes admits `P3` on 2/12 (L, Xan),
  against 12/12 in the ruled evidence.
- **`+2`:** it inherits the gate, so it gives `P2` ×2, not ×12.
- **`−2`/`−1`:** "the smaller of K and P3" leans to K as well. On measured
  bytes it is also K ×12, so this position does not move.

**Recommendation (a).** Add ONE per-matcher dispatch/prologue text term to
K's byte ESTIMATE used by the selection predicates. It could be a constant,
or about 30 B per section fitted from `sweep_k53.tsv` λ = 4 as measured
minus model. It would be its own ruled data cell in `PLACE`. The DP's
choices do not move, because the term is added after the sectioning is
chosen, so the study cross-check does not move either.

Alternatives:
- **(b)** Restate z_mid on model bytes. 1.45 reproduces 12/12, but it
  hides the bias in a placement.
- **(c)** Recalibrate the DP's own text model. That moves sectionings and
  needs a study change.

Nothing calls the kit, so nothing moves whichever is ruled. Sent to the
manager mid-lane, 2026-09-29.

## 4. Deviations from the study and the design, each deliberate

1. **The DP is integer (Q16).** The study's is floating point. `log2` for
   BSEARCH's op weight is an integer squaring routine (`log2_q16`), because
   a libm `log2` is not a promise of bit-identical digits across boxes, and
   the artifact must not depend on the box. The cost is 3 exact TIES among
   1,686 sectionings, all on proptest sets. Each is two BSEARCH sections of
   64 and 44 intervals whose order the float DP broke by rounding. The
   cross-check prices both under the study's own model and counts a 1e-6
   agreement as a tie (a `TIE` line), never as silent agreement.
2. **BSEARCH emits its loop inline in the leaf.** The study emits one
   shared `cls_bsearch` helper. A matcher is then self-contained, with no
   per-artifact prelude a caller must remember. At λ = 4, BSEARCH is chosen
   rarely.
3. **The whole-set forms are priced by BUILDING their tables** (at most
   17,408 pages), not by an O(k) formula. `pcrec_clskit_whole_bytes` and the
   emitter call one `build_pages`, so the price and the emitted table cannot
   disagree (the study's §8 PAGE64 lesson). The DP's own PAGE64 section
   price is still O(k), as the study's is.
4. **Row denies are kit-internal ordinals (`ClsDeny`), not public
   `PCREC_NO_*` bits.** A public flag is caller-visible, and S1 promises
   nothing caller-visible. D129 Q2's `-fno-cls-kit` is the calling stage's
   mapping.
5. **`ClsSelectIn.kit`** (optional) lets a caller that already ran `K` skip
   a second DP. The cross-check exercises both paths: deny 0 recomputes,
   every other deny passes the kit in.
6. **An out-of-range `tune` reads as `balanced`**, as `tune.c`'s own rows
   do, so the table always answers.
7. **Atom numbering is first occurrence over bytes 0..255.** The study
   sorts a Python `set`, whose order is not deterministic. Only the atom
   COUNT is compared: 40 on both sides for N = 41.

## 5. Sabotage rows S360-S363 (arm `clskit`)

Each row ran as its own invocation, `PROCS=1 CC=gcc-16 bash
tests/mech/run_sabotage_matrix.sh S36N`, sequentially, at tree `52d63c9f`.
All four read `== mech run COMPLETE: 1 rows (unexpected: 0, undetected: 0,
unreached: 0, anomalies: 0, oracle-skipped: 0) ==`. Logs are in the lane's
scratch as `/tmp/claude-clss1/mech_S36N.log`.

**Numbering.** Main's highest S-id is S336. ucpu2 is adding rows upward
from there, so this lane took S360 upward as instructed. `clskit` is a new
arm word, registered in the vocabulary block and the dispatch before the
rows that name it.

| row | plant | detector | result |
|---|---|---|---|
| S360 | the dispatch tree's seam test `cp < BASE` one too high, so each right-hand section's first member is refused | the differential | **DETECTED**, `clskit:3fail/2pass` |
| S361 | `cube_of` keeps only its O(k) spill budget and drops the exact containment loop (`{0,4,5}` over span 6 passes the budget) | the differential (the cross-check also moves) | **DETECTED**, `clskit:4fail/1pass` |
| S362 | `intern_records` compares half of each record, so page leaves agreeing in their low 32 bits collapse | the differential | **DETECTED**, `clskit:4fail/1pass` |
| S363 | the mid gate drops its section-count conjunct, so a row fires on a false predicate | the cross-check alone, as predicted: every form stays a correct matcher | **DETECTED**, `clskit:1fail/4pass` |

## 6. Validation

| check | command | result |
|---|---|---|
| strict | `make strict CC=gcc-16` | **clean** ("whole tree compiles clean with -Werror -Wshadow") |
| the new section | `PROCS=4 bash tests/clskit/run_clskit_tests.sh` (what `make test-clskit` runs) | **checks passed: 5, failed: 0**. Differential: 591 sets, 8,451,676,390 checks, 0 mismatches. Law: 146 × 2, 0 mismatches. Cross-check: 1,686 sectionings, 23,640 selections, 8 rows, atoms 41/40, ties 3, disagreements 0. Census: every leaf and whole form emitted (LEAF ALL 131,975 / RANGES 14,813 / MASK64 20,694 / CUBES 16,849 / BITMAP 4,490 / PAGE64 5,543 / BSEARCH 2,779; FORM K 5,910 / P3 591 / P2 591 / B1 453 (138 skipped over 40 KB) / ATOM 41) |
| bare-number scan | `bash tests/registry/limits_check.sh` | **35 passed, 0 failed.** The kit's numbers are table data, not `#define`s |
| codegen | `make test-codegen CC=gcc-16` | **11/12 scripts passed.** The one red, `run_inline_capability.sh` (`FAIL: nm could not read arm_a.o (no rx_search symbol)`), is PRE-EXISTING and darwin-only: it reproduces identically with main's own `build/pcrec` (`PCREC=/Users/fdicostanzo/pcrec/build/pcrec`). The kit cannot reach it, because nothing calls the kit |
| mech | one id per invocation (§5) | **S360-S363 all DETECTED**, 0 unexpected, 0 anomalies |

**Identity.** Nothing under `src/` changed except the two new files, and no
existing function calls into them (`grep -rn clskit src/ cli/ lib/` finds
only `clskit.c`/`.h`). No artifact byte can move.

**OWED, the full suite.** It is the manager's to schedule, because ucpu2
holds the heavy slot:

    cd <tree> && make -j4 CC=gcc-16 && nohup caffeinate -s make -k test CC=gcc-16 > build/clss1_make_test.log 2>&1 &

The verdict is make's `*** [test-X] Error` lines. `test-clskit` adds about
3-4 minutes (Mac, `PROCS=4`), most of it the study's Python DP in the
cross-check.

## 7. For the manager

1. **Rule §3's quantity.** I recommend (a).
2. **Confirm §2.1's two byte-tier readings:** the atom row at every
   position, and `B1` as the byte table form.
3. **`make test` now imports six study modules** as the reference. The
   study's CLAUDE.md says so. studies/CLAUDE.md's "never built or tested
   by make" stays true of the study's OWN targets, but its reference code
   is now load-bearing.
4. **The next stage:**
   - S3 (`A_WCLASS`) needs nothing from here.
   - S4 calls `pcrec_clskit_select` + `pcrec_clskit_emit_*` per distinct
     set. It wires `tune` from the job, maps `ClsDeny` to `-fno-cls-kit`,
     and owes the abi ritual.
   - S2 builds the artifact's atom table from its byte-class sites.
