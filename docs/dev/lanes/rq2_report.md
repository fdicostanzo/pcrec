# rq2 — [MEMFN] RQ-2 / D157: the position ranking (`mf_pred.rank_*`)

Lane rq2 (opus), 2026-10-09, branch `lane/rq2` off main d8c1b489.
Spec: integration.md §R4.9.11 RQ-2 and Q-R9-3 RULED (a) (D155 item 3).
**Superseded in shape by D157** (Frank, 2026-10-09, via the manager): pcrec
states the FACT, a ranked array, rather than a second position plus a
pcrec-chosen rule.

## 0. Path through the lane (the rulings, in order)

1. **First build (1b9f40b9..dc0cd366).** The brief as written:
   - `pcrec_find_pick2`, a second position chosen by a pcrec rule;
   - `mf_pred.plan_pos2` and `MF_NO_POS`, `MF_SITE_ABI` 8 -> 9;
   - the PRE/OFS builder and the allocators stating it.

   It validated green, zero movers at both SIMD settings (§4.1). Main first
   ruled "take the default memfn.h hunk".
2. **HOLD.** Main held the field and asked for the general reader instead:
   a ranking of the run's positions by the prior, with the same tie rule.
   - 4dc78dfb reverted the wiring and replaced pick2 with
     `pcrec_find_run_rank`.
3. **D157, GO** (c6aace93 onward). Wire the ranked array, appended LAST in
   `mf_pred`:
   - `rank_n` (0 = no facts);
   - `rank_pos[MF_RANK_MAX]`;
   - `rank_ppm[MF_RANK_MAX]`.

   `MF_RANK_MAX` is a declared limit with its derivation stated, and entries
   past `rank_n` are unspecified and never read. pcrec's scalar pick (KA,
   `plan_pos`) is unchanged, and `MF_SITE_ABI` moves to the next number at
   landing.
   - The rule that chooses positions from the ranking is NOT pcrec's. The
     first build's rule is dropped from pcrec and noted as the kit's
     choice.
   - Wording rule: describe the fields as facts only.

## 1. What is built (at the tip)

- **`pcrec_find_run_rank(rate, bytes, mask, n, pos, mass)`**
  (src/core/findings.c, beside `pcrec_find_run_scan_index`). It orders
  every position of a run by PICK's own cost, the cube mass, lowest first,
  and returns each position's mass beside it.
  - **Order.** A stable insertion over the scan reader's candidate order
    `[n-1, ..., 0]`: ties go to the rightmost position under both arms,
    and `pos[0]` is the scan reader's answer.
  - **Bound.** `n <= PCREC_MAX_REQ_RUN_SCAN`, guarded by the scan reader's
    own abort.
- **The contract** (memfn/include/memfn.h, `MF_SITE_ABI` 9). Appended LAST
  in `mf_pred`: `uint8_t rank_n`, `uint16_t rank_pos[MF_RANK_MAX]`,
  `uint32_t rank_ppm[MF_RANK_MAX]`, with `#define MF_RANK_MAX 32` beside
  `MF_MAX_TERM`. The comment states facts only:
  - the RUN term's positions, ordered by pcrec's prior rate, lowest first,
    ties to the higher offset;
  - each position's rate in ppm, summed over the position's members, under
    the compile's byte-rate or else the uniform rate;
  - the count;
  - 0 = no facts;
  - entries past `rank_n` are unspecified and never read.
- **`MF_RANK_MAX` 32, derived.** The longest RUN term pcrec hands the kit is
  bounded by the run analysis's own truncation bound,
  `PCREC_MAX_REQ_RUN_SCAN` (32):
  - the PRE window is at most `PCREC_MAX_REQ_RUN_EMIT` (8);
  - the K66 whole run is at most 32;
  - the OFS pinned stretch is at most the window.

  `_Static_assert(MF_RANK_MAX >= PCREC_MAX_REQ_RUN_SCAN)` sits where pcrec
  fills the array, so a ranking is never truncated and `rank_n` is the
  whole run length. Measured over the corpus, the longest run term is
  PRE 32 and OFS 8, so the bound is reached exactly.
- **The builder.** In `ofs_pred_of` (src/gen/emit_dfa.c), the PRE (window
  and K66 whole run) and OFS predicate builder: where the scan sits inside
  the RUN term, `ofs_pred_rank` fills `rank_*` from the reader under
  `pcrec_find_byte_rate(cx)`. `plan_hint`/`plan_pos` are unchanged. Every
  other predicate keeps the arena's `rank_n` 0, which is the stated "no
  facts" value, so no sentinel is needed.
- **The probe.** `-DPCREC_RANK_PROBE` is a test-only build, on
  `PCREC_SIMD_WITNESS`'s precedent. It prints each predicate's `rank_*` as
  handed to the kit by `pcrec_memfn_define`, plus the run term's bytes,
  masks and `plan_pos`.
- **The check.** `make test-memfn-rank` (tests/memfn/run_rank.sh +
  rank_check.py, in TEST_SECTIONS, mech arm `rank`).

## 2. Points for main

- **D157** is recorded here as ruled. Main writes the decisions.md entry.
- **NONE (no byte-rate, `-e utf8` today).** The ranking is still stated:
  each rate is MASS's NONE answer (the uniform rate, i.e. the member
  count), and the order is by cube size, then positional.
  - **Why not `rank_n` 0 under NONE.** It would need a reader to test the
    rate pointer, which the findings seam forbids outside the primitives
    (D126 Q4; `tests/findings` structural rule).
  - **U8-PICK.** The positional order under `-e utf8` is U8-PICK's defect
    (u8pick0_report.md), inherited and not fixed here.
- **pcrec has no selection rule over the ranking.** The first build's rule
  (and its UNMEASURED-DEFAULT label) is withdrawn from pcrec; any rule is
  the kit's choice (D157).
- **OFS.** 137 of 137 OFS predicates scan `rank_pos[0]` today, which is
  observed, not asserted. The OFS scan member is chosen by the offset
  selection, so `plan_pos` remains the scanned position's statement.

## 3. ABI

- **pcrec.** `PCREC_ARTIFACT_ABI` does not move (71): no emitted byte moves
  (§4).
- **The kit contract.** `MF_SITE_ABI` 8 -> 9 is a kit contract event
  ("the next number at landing").
  - **Collision.** R-13 (lane/memfn-r13 @ 9f043b96, not on main) also takes
    9 for its sink ops, so whichever lands second renumbers.
  - **Readers, found by grep:**
    - the define in memfn.h;
    - memfn/include/CLAUDE.md, updated;
    - memfn/CLAUDE.md's layer note, updated;
    - the symbolic `s->abi = MF_SITE_ABI` and G2's `MF_SITE_ABI ± 1`
      cases, which do not move;
    - `compose.c`'s compare, which does not move.

    No test pins the literal, and it never reaches an artifact.
- **Size.** `mf_pred` grows by 1 + 64 + 128 bytes (plus padding) per
  predicate. It is arena-allocated, never an automatic (C10).
- **No spec hunk.** `mf_pred` is the kit's internal contract, not a
  caller-observable surface (D80).

## 4. Validation

### 4.1 Earlier states (for the record)

- **1b9f40b9 (plan_pos2 wired).**
  - emit_sweep `--variant all` vs d8c1b489: 90 cells, 0 movers,
    0 asymmetric.
  - emit_sweep `--extra=-fmemfn-simd`: 22 cells, 0 movers.
  - `make strict`, `test-codegen` (15/15) and every memfn section were
    green.
  - The `--variant all` run printed `VARIANTS: FAILED`, but only on REACH
    and TAG FLOOR violations in the `lowsize`/`lowboth` cells, IDENTICAL
    on side a (main d8c1b489) and side b. That is a pre-existing stale
    variant pin on main, not this lane's. rq3's chain saw the same verdict.
    It is flagged for main and not re-pinned here, since this lane moves
    no population.
- **Hand plants.**
  - Against pick2: seven, all red.
  - Against the ranking reader at 4dc78dfb: positional, tie-leftmost,
    mask-ignored, unstable-insertion, mass-dropped and last-unranked, all
    six red (142 to 1,248 rankings each).

### 4.2 The tip (c6aace93+; logs `build/light/sweep2_off.log`, `sweep2_on.log`, `trailer2.log`)

| gate | result |
|---|---|
| `make` / `make strict` | clean |
| `make test-memfn-rank` | 11 passed / 0 failed |
| emit_sweep (all streams) vs d8c1b489, SIMD off | 0 movers, 0 asymmetric on every stream; argv 5,431 at full reach, composition 108 artifacts; self-check passed (83 s) |
| emit_sweep `--extra=-fmemfn-simd` vs d8c1b489 | 22 of 22 cells: 0 movers, 0 asymmetric; self-check passed (102 s) |
| builder-level hand plants (§4.3) | 4 of 4 red |

**The check's populations** cover the whole corpus (4,396 distinct
patterns plus 9 named) at three arms.
- Every RUN-scanning predicate's ranking (`rank_n`, positions, rates)
  equals the brute force: 1,248.
- Every other predicate carries `rank_n` 0: 4,643.
- Every PRE predicate scans `rank_pos[0]`: 1,111.

| population | measured | floor |
|---|---|---|
| run-PRE | 1,111 | 1,000 |
| run-OFS | 137 | 120 |
| run-byte (byte + vm arms) | 879 | 800 |
| run-utf8 | 369 | 330 |
| masked | 142 | 120 |
| prior-not-positional | 653 | 590 |
| data-tie (real rate) | 252 | 225 |
| norun (`rank_n` 0) | 4,643 | 4,000 |

The brute force shares no code with pcrec. It enumerates cube members
itself and reads the rate from the `--list-analysis default` `freq`
section, taking NONE where the resolution row has no digest.

### 4.3 Builder-level plants (tip)

Each plant applied to the tip's builder, the probe rebuilt, the check run:

| plant | verdict |
|---|---|
| builder never called (`rank_n` 0 everywhere) | red: 1,248 rankings differ; 1,111 PRE `rank_pos[0]` mismatches |
| `rank_n` one short | red: 1,248 rankings differ |
| no rates stated (`rank_ppm` 0) | red: 1,248 rankings differ |
| positional order (rate ignored) | red: 879 rankings differ; 391 PRE mismatches |

The plants script is `build/plants.sh`, output `build/plants2.out`.

### 4.4 Heavy, OWED (armed detached, gated on `worktrees/rq2/.lift`)

- **Waiter:** `build/land/waiter.sh` (one, `nohup setsid`). It polls
  `.lift`, then execs `build/land/chain.sh` at the branch's HEAD.
- **Trailer:** `build/land/trailer.log`. Completion line:
  `== CHAIN DONE`.
- **Stages:**
  1. build;
  2. `scripts/perfrun --label rq2 -- build/land/test.log`, read with
     `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` and the perfrun note;
  3. strict;
  4. emit_sweep `--variant all` vs d8c1b489. Expect the same pre-existing
     side-a/side-b floor verdict and 0 movers.
  5. emit_sweep `--extra=-fmemfn-simd`;
  6. recursion identity;
  7. mech VALIDATE_ONLY;
  8. solo mech for every row anchored in an edited file: S266 S287 S294
     S301 S308 S311 S312 S314 S325 S326 S329 S460 S461 S526 S571 S678.
     The verdict is `== mech run COMPLETE` in `build/land/mech.log`.

## 5. Sabotage row plan (count only; ids from main; none from S706-S730)

**SEVEN rows, all on arm `rank`:**
1. The reader ignores the rate (positional order).
2. The reader's candidate order is reversed (ties go to the lower offset).
3. The reader ignores the mask.
4. The reader drops the masses.
5. The builder stops calling `ofs_pred_rank`.
6. The builder states `rank_n` one short.
7. The builder states no rates.

Each anchor is one line of `pcrec_find_run_rank` or `ofs_pred_rank`. The
rows are not written: the manager allocates ids.

## 6. Files

- src/core/findings.c, findings.h: `pcrec_find_run_rank`.
- src/gen/emit_dfa.c: `ofs_pred_rank` and its `_Static_assert`; the one
  call in `ofs_pred_of`.
- src/gen/memfn_sites.c: the `PCREC_RANK_PROBE` hook.
- memfn/include/memfn.h: `MF_RANK_MAX`, `rank_n`/`rank_pos`/`rank_ppm`,
  `MF_SITE_ABI` 9.
- tests/memfn/run_rank.sh, rank_check.py: the check.
- Makefile: `test-memfn-rank` in TEST_SECTIONS and the help list.
- tests/mech/run_sabotage_matrix.sh: arm `rank`.
- CLAUDE.md updates: src/core, src/gen, tests/memfn, tests/mech,
  memfn/include, memfn.
- docs/design/memfn/integration.md: the RQ-2 row marked superseded by D157
  and BUILT.

## 7. Addendum: landing prep (lane rq2land, sonnet, 2026-10-09)

Three items for the manager, on `lane/rq2` after df095437. No `src/`
change; the RQ-2 code is untouched and zero-mover as §4.2 says.

### 7.1 Sabotage rows S731-S737 (arm `rank`)

Ids allocated by the manager (none in the kit's reserved blocks; the
highest on main and in every worktree was S730). One file each under
`tests/mech/sabotages/`, anchors copied from `git show HEAD:<path>` (each
occurs exactly once). All seven are solo **DETECTED** with their reach
witness live, `unexpected: 0`, about 25 s a row (the arm builds the probe
compiler and runs `rank_check.py`; log `build/s7/mech_rows.log`, scratch).

| id | file | plant | arm result | reach text it asserts |
|---|---|---|---|---|
| S731 | findings.c | `pcrec_find_run_rank` prices with `cube_mass(NULL, ...)`: the rate is ignored | 2 fail / 9 pass | SELECT order `4,2,0,5,3,1` and its masses |
| S732 | findings.c | candidate order reversed (`i = k`): ties go to the lower offset | 2 / 9 | all-tie utf8 order `5,4,3,2,1,0`, and the real-rate tie in `4,2,0,5,3,1` |
| S733 | findings.c | the mask ignored (`0xFF`): a cube position priced as one byte | 2 / 9 | `(?i)cat` masses `20286,59579,66067` |
| S734 | findings.c | `mass` filled with zeros: the order right, the rates dropped | 1 / 10 | SELECT masses |
| S735 | emit_dfa.c | `ofs_pred_rank(cx, t, p);` never called (`rank_n` 0 everywhere) | 2 / 9 | PRE order and the OFS order `4,5,1,0,7,6,2,3` |
| S736 | emit_dfa.c | `rank_n = run_len - 1` | 1 / 10 | the same two full position lists |
| S737 | emit_dfa.c | `rank_ppm[i] = 0` | 1 / 10 | PRE and OFS masses |

How the reach is built: nothing but a `-DPCREC_RANK_PROBE` compiler prints
the ranking (no artifact, answer or identity gate moves), so each row's
`SAB_REACH` builds that probe from the CLEAN tree into `$REACH_TMP` (about
3 s at `-j8`; the arm itself does the same on the sabotaged tree) and runs
`SELECT`, `(?i)cat` and `abcdefghijklmn` at the byte base plus `SELECT`
under `-e utf8`. `SAB_REACH_EXPECT` is the exact text that row's plant
moves ([MECH-REACH]: assert what moves), and `SAB_REACH_POP` holds the
three named witnesses in `rank_check.py`'s `NAMED` list. `VALIDATE_ONLY`
reads FIELDS OK for all seven and for the eight-id invocation the chain
uses. `tests/mech/CLAUDE.md`'s `rank` entry now names the ids.

### 7.2 The stale variant pins, measured

`scripts/emit_sweep.py --variant all` on main printed `VARIANTS: FAILED`
with 0 movers and identical sides, in the lowsize/lowboth cells only
(plain, lowdfa and lowthr had no violation; 71 violation lines over the four
cells in the lane's own run, `build/light/sweep_off.log`). The manager's
6973d7f5 re-pinned six reach floors and **no tag floor**, so main was
already red under the tag floors at the abi 70 commit, and RQ-3 moved the
cells again.

Method: `--variant lowsize --variant lowboth` with each revision against
itself (`--ref R --tree-rev R --no-self-check --emit-pins`, 146 s a
revision), then the per-pattern change between two variant binaries with a
scratch driver over the same corpus (4,387 distinct patterns, both bases:
c-default, c-vm, emit-ir-vm and the `emit-ir-auto` token).

| revision | what | the cells against the committed pins |
|---|---|---|
| c0a0b76a | decland's measurement (bbf3c1d9) | every tag equal to the pin |
| 32a1c91f, 9c181041 | decattr merge (abi 69), pre-R4e'.0b | identical to c0a0b76a |
| 82ff9432 | R4e'.0b, abi 70 | reach -2 on six streams, tags moved (byte: no-backreference -2, yes -5, no-size-cap +4) |
| d33d3899 | main just before RQ-3 | same as 82ff9432 |
| 631771b7 | RQ-3, abi 71 | reach moves again (lowboth/byte c-default -5, others -2), more tags |
| 5a8b233e | main now | same as 631771b7 |

**Cause, step 1 (82ff9432).** Each VM FUNC grew by +139..+184 B (the commit
message's own figure), which moves 9 distinct patterns across the LOWERED
caps (30000 VM code, 60000 emit): `(x?)([a-z]+)+S\d(?i:s)qz\1` over the
VM-code cap (30098 B; this is rq3tri's finding), seven `yes` ->
`no-size-cap` (`(a+)(a+?)`, `(?:aa|a)++ab`, `(?:a|aa)++ab`, `((a)(a))(a)`,
`(log|login|logout)$`, `(?!(?1))(a\Kb)c`, `(?=(?1))(a\Kb)c`) and `(ab|ac){2,4}?`
`yes` -> `yes-collapsed`.

**Cause, step 2 (631771b7).** RQ-3 adds `#define RX_SIMD_GUARDED_BYTES
0x0000000000000000ULL` to every artifact: a constant **+52 bytes**, on all 16
of 16 measured (pattern, engine, encoding) pairs, and the cap's quoted
"bytes of emitted code" moves by the same 52 (30098 -> 30150 for the reqcube
pattern). 18 more patterns cross: `(a{1,3}){64}`, `{65}`, `{66}` (refused at
c-default), `(\w*)(\W*)\2\1` (utf8), `(?1)a((?2))c(a+)b` (utf8),
`(?:(?:b?|a+){0,2})+`, `(?:(?:b{0,2}|a+){0,2})+`,
`^(?(DEFINE)(?<g>a+))(?&g)++ab$` (utf8), and ten `yes` -> `no-size-cap` /
`yes-collapsed`. Both steps are CAP CROSSINGS on the same text on both
sides, never movers. Reach counts are rows and the patterns are distinct, so
one pattern can carry -2 (the corpus lists it twice).

**Observation for the manager, not a ruling.** RQ-3 made the SIMD bytes
neutral to every length decision (D155 addendum 2) and the stamp it added
is itself ordinary text the caps count: the 52 B is the stamp line, not a
SIMD byte. Any future stamp shifts the lowered-cap cells the same way; the
re-pin is the cost each time, and the ladder this report records is the
procedure.

**The re-pin** is its own commit (8ec0e97a): the dated comment above
`VARIANT_PINS` carries the cause and the commands, and the four lowsize/
lowboth cells were pasted from `--emit-pins` of main 5a8b233e (its emitted
text is d8c1b489's) against itself, as a textual patch of the values so the
rest of the pprint-shaped block does not move. One thin-tag manifest left
(lowsize/byte `-fno-prefilter-collapse`, `no-size-cap` is now 104, above
THIN_TAG). `TRACE_VARIANT_RECORDS_FLOOR` was not re-measured (no `--trace`
in the chain). The patched block loads equal to the measured one on reach,
tags and manifest in all four cells.

**Validation of the re-pin:** `emit_sweep.py --ref d8c1b489 --tree-rev
8ec0e97a --variant lowsize --variant lowboth --no-self-check --jobs 8`
(floors applied, this lane's compiler against main): **`VARIANTS: CLEAN`**,
36 stream lines all `movers=0 asymmetric=0`, 124.5 s, no violation in any
of the four cells (`build/s7/sw_validate.log`). The chain's own
`--variant all` (the unchanged plain/lowdfa/lowthr cells) runs after the
lift.

### 7.3 Re-arm

- The old waiter, pid **762358**, was stopped with `scripts/safekill` before
  any edit (it was in its 30 s poll, `.lift` absent, `trailer.log` empty) and
  confirmed gone (`ps -p 762358` empty, no process naming
  `worktrees/rq2/build/land`).
- `build/land/chain.sh`: the solo mech list gained `S731 S732 S733 S734
  S735 S736 S737` (it stays one invocation, `PROCS=4`); everything else is
  unchanged, and `REV` is still `git rev-parse HEAD` at lift time, so it
  includes this report and the re-pin.
- ONE new detached waiter, `nohup setsid bash build/land/waiter.sh`, pid
  **880614** (pgid 880614), polling `worktrees/rq2/.lift` and then exec'ing
  `chain.sh`. `.lift` was not touched; the manager lifts after the kit's
  slot17 finishes. Completion: `build/land/trailer.log`, line `== CHAIN DONE`;
  the mech verdict is `== mech run COMPLETE` in `build/land/mech.log`.
