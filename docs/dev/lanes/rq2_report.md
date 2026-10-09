# rq2 — [MEMFN] RQ-2: the run ranking (`pcrec_find_run_rank`); the `plan_pos2` field HELD

Lane rq2 (opus), 2026-10-09, branch `lane/rq2` off main d8c1b489.
Spec: integration.md §R4.9.11 RQ-2, Q-R9-3 RULED (a) (D155 item 3), §2.3 T7,
§R4.9.5 item 10 (KB, a site fact).

## 0. Where it landed, and why it changed shape mid-lane

The lane first built the brief as written. That build had three parts:
- `pcrec_find_pick2`, the rarest position other than KA, with a distance
  rule;
- `mf_pred.plan_pos2` and `MF_NO_POS` in memfn.h, with `MF_SITE_ABI` 8 -> 9;
- the PRE/OFS builder stating KB, and the allocators stating "none".

That build is commits 1b9f40b9..dc0cd366. It validated green (§4.1).

Main then **HELD the memfn.h hunk**. Frank is weighing a general interface:
pcrec states the FACT, an ordered array of the run's candidate positions
rarest first with their rates, and the kit takes 1, 2 or N, with the
distance rule moving to the kit. Main's instruction was: build the
pcrec-side READER generally, unit-check it, and do not wire a field until
the shape is confirmed.

So at the branch tip (4dc78dfb onward):
- memfn.h, the builder line, both allocator lines, memfn/include/CLAUDE.md
  and the integration.md RQ-2 row are back to main's text;
- `pcrec_find_pick2` is replaced by `pcrec_find_run_rank`;
- the check is renamed `make test-memfn-rank`.

Main's earlier ruling (take the default memfn.h hunk) arrived in the same
batch and is superseded by the HOLD.

## 1. What is built

- **`pcrec_find_run_rank(rate, bytes, mask, n, pos, mass)`** sits in
  src/core/findings.c beside `pcrec_find_run_scan_index`. It ranks every
  position of a run rarest first by PICK's own cost, the cube mass
  `cube_mass`, and returns each position's mass beside it (`mass` NULL:
  not wanted).
  - **Order.** The ranking is a stable insertion over the scan reader's
    candidate order `[n-1, ..., 0]`, so ties go to the rightmost under both
    arms and `pos[0]` IS `pcrec_find_run_scan_index`'s answer.
  - **pick and pick2.** pick is `pos[0]`. pick2 under the old rule is the
    first entry != KA, which for every PRE predicate is `pos[1]` (§4).
  - **Bound.** `n <= PCREC_MAX_REQ_RUN_SCAN` (32), with the scan reader's
    own abort guard. A kit-facing cap (`MF_RANK_MAX`) would be a declared
    limit of the field, not of this reader.
  - **Callers.** It has no caller in a default build, so it emits nothing
    and moves no artifact.
- **The probe.** `-DPCREC_RANK_PROBE` is a test-only build, on
  `PCREC_SIMD_WITNESS`'s precedent. Its hook in `pcrec_memfn_define` prints,
  for every RUN-scanning predicate of every PRE/OFS site handed to the kit:
  - the term's bytes and masks;
  - the scanned position;
  - the ranking under the compile's own `pcrec_find_byte_rate`.
- **The check.** `make test-memfn-rank` (tests/memfn/run_rank.sh +
  rank_check.py, in TEST_SECTIONS, mech arm `rank`).

## 2. The distance rule (for when the field is shaped)

- **Under the HOLD it is not pcrec's.** The ranking is the fact; the
  distance rule belongs to its consumer.
- **The rule the first build used.** It is recorded because main accepted
  it before the HOLD. The rule is `KB != KA` inside the same RUN term, with
  the rightmost tie. Its label was `UNMEASURED DEFAULT`, the smallest rule
  the design's unstated "with a distance rule" admits.
- **R-1's cells.** Under NONE that rule reproduces R-1's four timed cells
  exactly (memfnr4b_report.md §1): SELECT 4 -> 5, USER 0 -> 3, CAT 0 -> 2,
  it 0 -> 1.
- **What the ranking already gives.** The ranking reproduces them too:
  `pos[1]` is the rightmost cheapest other position.
- **What is left for the kit.** A wider minimum distance is §R4.9.5 item
  10's KB sweep. Adjacent bytes co-occur, so a product of their rates
  overstates a pair's rarity.
- **`-e utf8`.** The byte-rate resolves to NONE
  (`--list-analysis default`: `byte-rate utf8 ... none`), so the ranking is
  by cube size, then positional. That is U8-PICK's defect
  (u8pick0_report.md), inherited and NOT fixed here.

## 3. ABI

- **At the tip, no stamp of any kind moves.** `PCREC_ARTIFACT_ABI` stays
  71 and `MF_SITE_ABI` stays 8; memfn.h is main's text.
- **For the eventual field.** An appended field plus its sentinel is a kit
  `MF_SITE_ABI` bump to "the next number at landing". R-13
  (lane/memfn-r13 @ 9f043b96) took 9 for its sink ops, so the field takes
  10 if R-13 lands first. It is not a pcrec abi event: `MF_SITE_ABI` is set
  in `pcrec_memfn_site` and compared in `compose.c`, and it never reaches
  an artifact. The literal is pinned by no test.
- **What the first build showed.** Wiring `plan_pos2` moved no emitted
  byte at either SIMD setting (§4.1), because no kit row reads it.
- **No spec hunk.** The reader is internal, and no entry, flag, stamp,
  limit or diagnostic moved (D80).

## 4. Validation

### 4.1 The first build (1b9f40b9: the field wired)

| gate | result |
|---|---|
| `make` / `make strict` | clean |
| `make test-memfn-pick2` | 9/0: 1,248 run predicates and 4,643 others all equal a brute-force second pick |
| emit_sweep `--variant all` vs d8c1b489 | SWEEP_OFF |
| emit_sweep `--extra=-fmemfn-simd` vs d8c1b489 | SWEEP_ON |
| memfn sections (pick2, manifest, deleg, arms, forms, arch, link, rows, stamps, guarded, g2) | all rc 0 |
| test-codegen | GATES_CODEGEN |

There were seven hand plants against pick2: positional, tie-leftmost,
mask-ignored, distance-dropped, builder-unset, allocator-unset, and
NULL-mask. All seven were red (17 to 3,597 predicates).

### 4.2 The tip (the ranking)

| gate | result |
|---|---|
| `make` / `make strict` | clean |
| `make test-memfn-rank` | 9 passed / 0 failed, ~7 s plus the probe build |
| hand plants (§4.3) | PLANTS |

The emitted bytes are unchanged by construction, since the reader has no
default-build caller. The heavy chain re-runs both sweeps at its own HEAD.

**The check's populations** cover the whole corpus (4,396 distinct
patterns plus 9 named) at three arms (byte, `-e utf8`, `--engine=vm`).
Every ranking, positions and masses, equals the brute force for all 1,248
runs. Every PRE predicate scans rank[0] (1,111 of 1,111, asserted).

| population | measured | floor |
|---|---|---|
| run-PRE | 1,111 | 1,000 |
| run-OFS | 137 | 120 |
| run-byte (byte + vm arms) | 879 | 800 |
| run-utf8 | 369 | 330 |
| masked | 142 | 120 |
| prior-not-positional | 653 | 590 |
| data-tie (real rate) | 252 | 225 |

- **OFS.** 137 of 137 OFS predicates also scan rank[0]. This is reported,
  not asserted: the OFS scan member is chosen by the offset selection,
  which happens to agree today. A consumer that wants KB "rarest other
  than the scan" must still be told KA (`plan_pos`) and must not assume
  KA == rank[0].
- **Independence.** The brute force shares no code with pcrec. It
  enumerates cube members itself and reads the rate from the
  `--list-analysis default` `freq` section, taking NONE where the
  resolution row has no digest.

### 4.3 Hand plants against the ranking

Each plant ran in a `git archive` copy of 4dc78dfb and was scored by its
own tree's `run_rank.sh`.

PLANT_TABLE

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
  4. emit_sweep `--variant all` vs d8c1b489;
  5. emit_sweep `--extra=-fmemfn-simd`;
  6. recursion identity;
  7. mech VALIDATE_ONLY;
  8. solo mech for every row anchored in an edited file: S266 S287 S294
     S301 S308 S311 S312 S314 S325 S326 S329 S460 S461 S526 S571 S678.
     S526 is harmless now that memfn.h is main's. The verdict is
     `== mech run COMPLETE` in `build/land/mech.log`.

## 5. Sabotage row plan (count only; ids from main; none from S706-S730)

**FIVE rows, all on arm `rank`.** The unstable-insertion plant duplicates
tie-leftmost, so it is not a row.

1. The rate is ignored (positional).
2. The candidate order is reversed (ties go leftmost).
3. The mask is ignored.
4. The masses are not returned.
5. One position is left unranked.

Each anchor is a single line of `pcrec_find_run_rank`. The rows are not
written: the manager allocates ids, and the anchors go in with them. When
a field is wired, add one row on the builder line, with the field's own
check.

## 6. Files

- src/core/findings.c, findings.h: `pcrec_find_run_rank`.
- src/gen/memfn_sites.c: the `PCREC_RANK_PROBE` hook.
- tests/memfn/run_rank.sh, rank_check.py: the check.
- Makefile: `test-memfn-rank` in TEST_SECTIONS and the help list.
- tests/mech/run_sabotage_matrix.sh: arm `rank`.
- CLAUDE.md updates: src/core, src/gen, tests/memfn, tests/mech.
- NOT touched at the tip: memfn/, docs/design/memfn/integration.md. The
  RQ-2 row and §2.3 T7 still name `pcrec_find_pick2`/`plan_pos2`, and main
  edits them when the shape is ruled.

## 7. For the shape decision

- **The full ranking costs nothing per site.** The reader is O(n²) over at
  most 32 positions at compile time. The probe shows that every PRE/OFS
  RUN-scanning predicate has one.
- **Two fields carry the shape.** The ranking plus `plan_pos` (KA) are
  enough. `rank_pos[]`/`rank_ppm[]` map onto `pos[]`/`mass[]`, where mass is
  ppm summed over the cube's members (a pair counts both).
- **Field init.** A field set by `ofs_pred_of` alone needs an explicit
  "none" from the allocators (`pcrec_memfn_site`, `pcrec_memfn_preds`), as
  the first build did. Otherwise arena zeros read as a one-entry ranking.
- **The kit.** Its `site_check` may want to refuse a stated ranking that is
  not a permutation of `0..run_len-1`.
