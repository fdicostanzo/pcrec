# rq2 — [MEMFN] RQ-2: the second pick (`pcrec_find_pick2`, `mf_pred.plan_pos2`)

Lane rq2 (opus), 2026-10-09, branch `lane/rq2` off main d8c1b489.
Spec: integration.md §R4.9.11 RQ-2, Q-R9-3 RULED (a) (D155 item 3), §2.3 T7,
§R4.9.5 item 10 (KB, a site fact).

## 1. What was built

- **`pcrec_find_pick2(rate, bytes, mask, n, ka)`** (src/core/findings.c,
  beside `pcrec_find_run_scan_index`). It is a fourth PICK reader, not a new
  mechanism. It builds the candidate order `[n-1, ..., 0]` without `ka`
  (the scan reader's own order) and asks `pcrec_find_pick` once. A data tie
  and the NONE answer both go to the rightmost other position. It returns -1
  for n < 2. `mask` NULL means exact. It uses the scan reader's
  `PCREC_MAX_REQ_RUN_SCAN` abort guard.
- **`mf_pred.plan_pos2`** (`uint16_t`, appended LAST to `mf_pred`) and
  **`MF_NO_POS`** (0xFFFF) are in memfn/include/memfn.h, with
  **`MF_SITE_ABI` 8 -> 9**. See §3 for who owns this hunk.
- **The builders.** `ofs_pred_of` (src/gen/emit_dfa.c) is the one predicate
  builder the PRE site (`req_site_define`: window and K66 whole-run
  predicates) and the OFS site (`ofs_site_define`) share. It sets
  `plan_pos2 = pcrec_find_pick2(rate, term bytes, term masks, term length,
  plan_pos)` wherever the scan sits inside the RUN term. That is the only
  case where `plan_hint` names a RUN term. Nothing else states a real KB.
- **Allocators state "none".** `pcrec_memfn_site` and `pcrec_memfn_preds`
  (src/gen/memfn_sites.c) set `plan_pos2 = MF_NO_POS`, the same way the site
  allocator already sets `plan_hint = MF_NO_PRED`. Without this, an arena
  zero would read as a real position 0 (the "no silent defaults" rule).
  This covers the PRE gate/set-rest predicates and every non-PRE/OFS site.
- **The check.** `make test-memfn-pick2` (tests/memfn/run_pick2.sh +
  pick2_check.py, in TEST_SECTIONS, mech arm `pick2`). See §4.
- **Test-only probe.** `-DPCREC_PICK2_PROBE`: `pcrec_memfn_define` prints
  one `PICK2` line per predicate it hands the kit. It follows the
  `PCREC_SIMD_WITNESS` precedent: compiled out of every real build.

## 2. The distance rule, and its label

The design names a distance rule ("the rarest other position, with a
distance rule", §2.3 T7) but never states one. §R4.9.5 item 10 lists KB as a
site fact, and item 6 puts the KB SWEEP in tier U. The shipped rule is the
smallest one: **KB != KA**. Nothing else is imposed. Its label in place
(findings.c) is `UNMEASURED DEFAULT`.

- **Why this rule.** Under NONE it reproduces R-1's four timed cells exactly
  (memfnr4b_report.md §1): SELECT KA 4 -> KB 5, USER 0 -> 3, CAT 0 -> 2,
  it 0 -> 1. R-1's KB was the run's last (or first) byte, which is the
  rightmost-other tie rule.
- **What is deferred.** Adjacent bytes co-occur, so the product of their
  rates overstates a pair's rarity. A wider minimum distance is the KB
  sweep's question (RQ-4's slot), not this lane's (D149, "suspect tuning
  constants").
- **Under `-e utf8`.** The byte-rate resolves to NONE today
  (`--list-analysis default`: `byte-rate utf8 ... none`), so KB is
  positional: the rightmost other position among the cheapest cubes. pick2
  inherits whatever pick reads, U8-PICK's defect
  (docs/dev/lanes/u8pick0_report.md). It is NOT fixed here.

## 3. ABI: what moved, and the open ownership question

- **`PCREC_ARTIFACT_ABI` does not move** (it stays 71). No kit row reads
  `plan_pos2`, so no emitted byte moves at either SIMD setting (§4).
  `MF_SITE_ABI` is never emitted into an artifact (grep: it is set in
  `pcrec_memfn_site` and compared in `compose.c`, nothing more).
- **`MF_SITE_ABI` 8 -> 9 is a kit contract event.** Its readers, found by
  grep:
  - the number itself in memfn.h;
  - memfn/include/CLAUDE.md, updated;
  - `s->abi = MF_SITE_ABI` in memfn_sites.c, G2's `MF_SITE_ABI ± 1` cases
    and `compose.c`'s compare. These are symbolic and do not move.
  - No test pins the literal.
- **The number collides with R-13.** R-13 (lane/memfn-r13 @ 9f043b96, not
  on main) took 9 for the sink ops. Its memfn.h says "mf_pred.plan_pos2
  (RQ-2) is NOT in this bump: it lands with RQ-2", its vrun.c says "adding
  it is RQ-2's MF_SITE_ABI bump", and its report's Q-R13-3 leans "RQ-2's
  plan_pos2 at 10". So whichever lands second renumbers: "the next number at
  landing".
- **The ownership question, sent to main at lane start.** integration.md
  Q-R9-3 calls the field "a kit MF_SITE_ABI bump (folded into batch 1's one
  bump)", but the kit's R-13 handed it to RQ-2. I took the default I
  proposed: a contract-only memfn.h hunk (the field, the sentinel, the
  bump), with no kit logic touched. Consuming KB, the extra `and` in vrun.c's
  `cmask`, stays kit work. If main rules the field is the kit's to add, drop
  the memfn.h hunk and the one `p->plan_pos2 =` line plus the two allocator
  lines. `pcrec_find_pick2` and the check stand alone.
- **No spec hunk.** `mf_pred` is the kit's internal contract, not a caller-
  observable surface (D80): no entry, flag, stamp, limit or diagnostic moved.

## 4. Validation

### Light, done

| gate | result |
|---|---|
| `make` / `make strict` | clean (gcc 15.2, at the final HEAD) |
| `make test-memfn-pick2` | 9 passed / 0 failed, ~7 s plus the probe build |
| emit_sweep `--variant all`, SIMD off, at 1b9f40b9 vs d8c1b489 | LIGHT_OFF |
| emit_sweep `--extra=-fmemfn-simd` at 1b9f40b9 vs d8c1b489 | LIGHT_ON |
| memfn sections, test-codegen | GATES |

1b9f40b9 is the first commit that carries every byte-reachable change. The
later commits add only the `#ifdef PCREC_PICK2_PROBE` hook, tests and docs.
The heavy chain re-runs both sweeps at its own HEAD.

**The check's populations** (whole corpus: 4,396 distinct patterns plus 9
named, three arms). Every predicate's `plan_pos2` equals the brute force:
1,248 run predicates and 4,643 others.

| population | measured | floor |
|---|---|---|
| run-PRE | 1,111 | 1,000 |
| run-OFS | 137 | 120 |
| run-byte (byte + vm arms) | 879 | 800 |
| run-utf8 | 369 | 330 |
| masked | 142 | 120 |
| prior-not-rightmost | 365 | 320 |
| data-tie (real rate) | 128 | 100 |
| norun | 4,643 | 4,000 |

The brute force shares no code with pcrec:
- it enumerates each cube's members itself;
- it reads the rate from the `--list-analysis default` listing's `freq`
  section;
- it takes NONE where the resolution row has no digest.

**Hand plants.** Each plant ran in a `git archive` copy of 1ec226b9 and was
scored by its own tree's `run_pick2.sh`. All seven are red.

| plant | where | `make test-memfn-pick2` |
|---|---|---|
| positional (pick2 ignores the rate) | findings.c | RED, 347 predicates |
| tie to leftmost (candidate order ascending) | findings.c | RED, 427 |
| mask ignored (every candidate a byte) | findings.c | RED, 17 |
| distance rule dropped (KA a candidate) | findings.c | RED, 1,248 (KA is always the cheapest) |
| `ofs_pred_of` stops setting `plan_pos2` | emit_dfa.c | RED, 1,248 |
| `pcrec_memfn_preds` stops stating `MF_NO_POS` | memfn_sites.c | RED, 3,597 |
| the builder passes NULL masks | emit_dfa.c | RED, 17 |

### Heavy, OWED (armed detached, gated on `worktrees/rq2/.lift`)

- **Waiter:** `build/land/waiter.sh` (one, `nohup setsid`). It polls
  `.lift`, then execs `build/land/chain.sh` at whatever HEAD the branch has.
- **Trailer:** `build/land/trailer.log`. Completion line:
  `== CHAIN DONE`.
- **Stages:**
  1. build;
  2. `scripts/perfrun --label rq2 -- build/land/test.log`, read with
     `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'` and the perfrun note;
  3. strict;
  4. emit_sweep `--variant all` at the chain's HEAD vs d8c1b489;
  5. emit_sweep `--extra=-fmemfn-simd`;
  6. `tests/codegen/run_recursion_identity.sh` (no abi move expected);
  7. mech VALIDATE_ONLY;
  8. solo mech for every row anchored in an edited file or quoting
     `ofs_pred_of`: S266 S287 S294 S301 S308 S311 S312 S314 S325 S326 S329
     S460 S461 S526 S571 S678. The verdict is `== mech run COMPLETE` in
     `build/land/mech.log`.

## 5. Sabotage row plan (count only; ids from main; none from S706-S730)

**SIX rows, all on arm `pick2`.** The NULL-mask plant duplicates the
mask-ignored one (both 17), so it is not a row.

1. pick2 ignores the rate (positional).
2. Data ties go leftmost.
3. The mask is ignored.
4. KA is admitted as a candidate (the distance rule dropped).
5. `ofs_pred_of` drops the `plan_pos2` assignment.
6. `pcrec_memfn_preds` drops the `MF_NO_POS` statement.

Each anchor is a single line in §1's files. The rows are not written: the
manager allocates ids, and the anchors go in with them.

## 6. Files

- src/core/findings.c, findings.h: `pcrec_find_pick2`.
- src/gen/emit_dfa.c: `ofs_pred_of` states KB.
- src/gen/memfn_sites.c, memfn_sites.h: `MF_NO_POS` at allocation; the
  `PCREC_PICK2_PROBE` hook.
- memfn/include/memfn.h: `plan_pos2`, `MF_NO_POS`, `MF_SITE_ABI` 9.
- tests/memfn/run_pick2.sh, pick2_check.py: the check.
- Makefile: `test-memfn-pick2` in TEST_SECTIONS and the help list.
- tests/mech/run_sabotage_matrix.sh: arm `pick2`.
- CLAUDE.md updates: src/core, src/gen, memfn/include, tests/memfn,
  tests/mech.
- docs/design/memfn/integration.md: RQ-2 row marked BUILT.

## 7. For the kit (R-13 follow-up)

- vrun.c's `cmask` can AND a second compare at `plan_pos2` wherever
  `plan_pos2 != MF_NO_POS`. On a RUN-term predicate pcrec always states it
  for `run_len >= 2`.
- Today it is a SPEED fact: a reader that ignores it stays exact.
- The kit's `site_check` may want to refuse a stated `plan_pos2` that
  equals `plan_pos` or is past `run_len`. G2's zero-initialized predicates
  carry 0 there, not `MF_NO_POS`, and nothing reads it yet.
