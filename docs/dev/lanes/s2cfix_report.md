# Lane s2cfix — review 2026-11-06 r9 (memfn-s2c, CODE) FIX-NOW and DOC items

Branch `lane/memfn-s2c`, worktree `worktrees/s2c`. The deliver block is `docs/dev/lanes/s2cfix_deliver.txt`. The
review is `docs/dev/reviews/2026-11-06-r9-memfn-s2c.md`, with its "## Rulings" section, the critic texts and
`verify.md` in its sibling directory.

## Summary

Every FIX-NOW and DOC item of review r9 is applied, under the kit manager's four choices.

- **G4 FOLD.** `mf_form_hash(id)` is now one hash over the site text of every instance of the id, in table
  order, joined by a newline.
  - walk, libc, pair and rc-memcmp have a single instance, so their hashes are unchanged.
  - settest becomes `68dc869d44ec0026` and rc-words `3e58ff9dd5712452`. These are new hashes and nothing read
    them yet.
- **EMIT-3.** `vcls.py` now counts the c2 sites by lowering shape. Over 292 sites: case 156, pair 79, range 53,
  other 4. The `{X,x}` case pair is the majority, so the instance stays. `link.py` refuses a non-majority
  instance and tags a class with no majority `lower-bound`.
- **SLOT-17.** The ver-3 cards state `gate_e6` as `-`. The gate lives in the new kit policy table
  `memfn/data/policy.tsv` (`gate_default_e6 30000`). The slot's plan reads it from there, and the draft
  publishes the resolved value.
- **G1, the gate of the fix.**
  - The answer gate runs the TIMED `_time` as well as `_gate` on every subject. Each subject also gets a
    SENTINEL twin: a hit at the last byte, or the last candidate passing.
  - The gate prints its population (arms, pools, subjects, timed calls), and `run.py` asserts it against the
    plan.
  - The gate runs on every launch and on `ctl`.
  - The dry run writes a per-job MANIFEST, and `run` verifies it before timing anything. The caches are keyed
    by their inputs.
  - Sabotage row (l3) S2934, which halves only the timed loop, is DETECTED.

The slot harness now reads its facts from one place each:
- the card facts from the cards and the policy table;
- the plan from a frozen `plan.tsv`;
- "which jobs ran" from the finalized run record;
- the deps from the dry run's own `cell_text.tsv`.

The S2d job scripts are committed under `docs/design/memfn/span_cards/slot/jobs/`. Readiness waits for an
upstream job to END, not to be green. No emitted pcrec byte moves: an emit_sweep spot found 0 movers.

**State at handoff.** The validation is complete (§Validation). Nothing was queued and no timing was run. The
scratch gate jobs 470-474 and the S2d job dir are updated (§Gate jobs). To resume, read this report and the r9
table in span_cards §R1.3.

## Fixes by finding id

Commits:
- `b706bbf29`: kit side (formhash fold, RUNCMP guard, fixtures, check C, policy table, S2933).
- `94d6a16a5`: the slot harness, the spec hunks, the §R1.3 r9 table.
- `d62a6309e`: the design text, `slot/jobs/CLAUDE.md`, J9 readiness, the draft gate.
- `e1737b0a0`: HOUSE headers, guards and documentation drift.
- The report commit.

| id (constituents) | fix | where |
|---|---|---|
| **G1** (CHECKS-1, -2, -5, SLOT-2, HOUSE-9) | (1) `drv gate` calls `_time` and requires its count to equal the planted one; a SENTINEL subject per subject makes a short timed loop miss even on miss-only or p0 subjects. (2) The population line `== s2 GATE ok: A arms, P pools, S subjects, T timed calls, 0 misses` is asserted against the plan in `run.py gate`; an arm with no length is a miss. (3) Gated on all 7 launches and on ctl. (4) `RUNDIR/<job>/manifest.tsv` holds the run id and the sha-256 of the frozen plan, fx, libpcrec.a, ctl, placement.tsv, cell_text.tsv and L1-L7. `run` and `screen` verify it first. (5) fx is cached as `fx.<sha of its inputs>`; artifacts and subjects are cached by their inputs' sha; `ctl` refuses inputs other than the ones it was built from. Sabotage (l3) S2934. | slot `drv.c`, `gen.c`, `slot.h`, `run.py`, `link.py`, `art.py`; span_cards §3.2 |
| **G2** (SLOT-15) | `plan.key_form` reads (form, cls) from the KEY. The render uses it, and an Arm that disagrees refuses with `KEY-ARM MISMATCH`. The compare is against the hash of the instance the key names. Sabotage (g2) S2935. | `plan.py`, `link.py`; §3.2 |
| **G3** (SLOT-1, SLOT-16, CONTRACT-2 record part) | The dry run freezes `RUNDIR/plan.tsv`, and a later dry run that differs refuses. `finalize` copies plan/floor from that frozen plan. Cells files start with a `#run_id` line. `est.py` reads the record's jobs, plan and floor, and refuses: cells of a never-ran job, a ran job missing a planned cell, another run's cells, an id that disagrees with its columns, a base that is not `plan.base_of`'s. Input errors exit 2. `est.py selftest` plants each of these. Sabotage (g3) S2936. | `est.py`, `record.py`, `run.py`, `plan.py`; §3.5 |
| **G4** (EMIT-1, SLOT-6, HOUSE-2) | FOLD (ruled), described in the Summary. Check B requires FORM to equal the fold computed independently with `--hash-text` over the instances' `--site-text`. Fixtures are per instance (CHECKS-6). Mech row S2933. | `memfn/src/formhash.c`, `kit.h`, `memfn/include/memfn.h`, `tests/memfn/arm_fixtures.c`, `finder_check.py`; §2.4 |
| **G5** (EMIT-2, SLOT-7, HOUSE-1, CONTRACT-6) | `link.py` writes `RUNDIR/<job>/cell_text.tsv` (arm, form, cls, instance hash, fold hash, tags), and the draft's deps come from it; a fold that differs between jobs refuses. The record carries `box`, `isa`, `libc`, `gcc` and `rules`. The header reads them, and none is a literal any more. A REFUSED outcome writes no draft (exit 3). | `link.py`, `est.py`, `record.py`; §3.5, §3.8 |
| **G6** (SLOT-3, HOUSE-3, CONTRACT-5 vocab) | `record.py window` writes the window facts idempotently. It runs at every job's start and at finalize, and refuses another run id, commit or box. The declared CAUSE table maps green, failed, wait-timeout, cancelled (declined-j1b only for J2p under `j1_verdict b`) and none (never-queued); an unknown state refuses. | `record.py`, `run.py`; §3.5 |
| **G7** (HOUSE-4, -6, -7, SLOT-8, CONTRACT-2 odd gate) | `plan.py` reads the estimator, lengths, launches, rounds, unit and gate from the ver-3 cards and `policy.tsv`. The null base takes its run, mask or members from its class instance's `--facts`. `CAND_STRIDE` and `POOL_BYTES` are plan.py's alone and passed with `-D`. The miss-text members come from the find forms' facts. The half gate, bimodal and drift use doubled comparisons (`measures.md` §3.5¶2, ¶4, ¶6). | `plan.py`, `link.py`, `est.py`, `run.py screen`, `gen.c`, `slot.h` |
| **G8** (HOUSE-8 parts) | An unknown landing refuses, as does a landing without a gap. The git return code is checked (`code_commit`, `main_tree`). The commit must be a hex object name. | `link.py`, `run.py`, `record.py` |
| **W1** (SLOT-5) | Job scripts committed: `slot/jobs/` (480 prep, 481-486, 489 J9, `common.sh`, `window.env.example`). Each `--dry-run` compares its queued copy with the tree's. `expect groups=N` comes from `plan.py groups` (J1 9, J2 3, J2p 7, J3 6, J4 5, J5 3). | §3.3, §9 S2c/S2d |
| **W2** (SLOT-4, CONTRACT-5) | `ready_after` waits for upstream END. Every timing job answers 77 once prep ended non-green. J2p answers 77 when J1 ended non-green. J3 runs after J2 AND J2p. J9 waits for prep to end and for each job to end (or never be queued). | `slot/jobs/`; §3.3 |
| **W3** (SLOT-12) | `Waiter` bounds the job's TOTAL waiting time. | `run.py`; §3.3 |
| **CONTRACT-1** | `measures.md` §3.4¶1 names the producer's rules as an input, and the new §3.5¶8a puts their home in the record's `run` key `rules`. `record.py` writes `rules kit-grid@3`, and `est.py` refuses any other owner. The data form (`unless:<run-key>=<value>`, base column) is PLANNED; trigger: the next producer (S2g). | spec, `record.py`, `est.py` |
| **CONTRACT-3** | §2.1¶1 `partial`: one clause for format 2 pointing at §3.5¶12 row 3. | spec |
| **CONTRACT-4** (a)-(c) | §3.4¶2a: L = 7, else refuse (`plan.py` refuses too). §3.5¶12 row 1: an absent unit refuses. §3.4¶14a: W, u_l and E positive (`est.py` refuses otherwise). (d), (e) NOTED as ruled. | spec, `plan.py`, `est.py` |
| **CONTRACT-6** | No draft on REFUSED (with G5). | `est.py`; §3.8 |
| **EMIT-3** | Majority lowering shape (ruled), described in the Summary; vcls `shape` lines. | `vcls.py`, `vcls.out`, `plan.shape_majority`, `link.shape_tag`; §3.2 |
| **EMIT-4** | RUNCMP guard `arm == &runcmp_arm`; settest is stated as a leaf render with row NULL. | `formhash.c`; §3.2 entry table |
| **EMIT-5** | PLAN with trigger (a `pair` cls `fn` instance). | §3.2 |
| **SLOT-9** | vcls.out is STAMPED with the sweep's sha-256 `b88599f6…` and commit `71cad723e`; counts unchanged. The census0 fold is PLANNED; trigger: S2f's census0 re-run. | `vcls.py`, `vcls.out`; §3.2 |
| **SLOT-10** | Design sentence fixed: the walk plans `one` only. | §2.5 |
| **SLOT-11** | Enter card note: `die1` holds for kinds 1-5; kind 6 REPORT has no die (the fixture's note states it). Kind 5 NOTED. | §2.4 |
| **SLOT-13** | The bound and trigger are per (launch, arm): max 5 draws per arm in this lane's dry runs, launch sums 2-17. The trigger has not fired. | §3.2 |
| **SLOT-14** | gen.c's subject comment fixed (verify bases draw their class instance's p0 subjects). | `gen.c` |
| **SLOT-17** | RULED POLICY; `memfn/data/policy.tsv`. | §2.4, §6 |
| **CHECKS-3** | The card guard resolves every named `kit:form.<id>` against the FORM rc-0 set; the count is pinned EXACTLY (`CARD_FORMDEP_COUNT = 17`). | `finder_check.py` |
| **CHECKS-4** | `rename_idents` counts renames, and check B requires `renamed > 0` per instance. | `arm_fixtures.c`, `finder_check.py` |
| **CHECKS-6** | R-MS3 rename/edit/foldedit fixtures for all 10 instances. | same |
| **CHECKS-7** | NOTED (red either way); untouched. | — |
| **HOUSE-5 / SLOT-18** | `j1_rule.py` imports est's primitives; the pad range constants are labelled D149. | `j1_rule.py`, `link.py` |
| **HOUSE-10** | Removed: `placement_ok`, the duplicate `names`, `SIB`, `arm.events`, `nhit`. `tp` is a `with` block. est reads the record's `jobs`. | slot |
| **HOUSE-11** | `MAIN` is derived from git. `QUIET_LOAD`, `QUIET_HOLD` and `QUIET_POLL` are labelled. `sabotage.sh` uses `tests/lib/timeout_bin.sh`. The doubled conditional is fixed. The duplicated quiet gate stays NOTED (as ruled). | `run.py`, `sabotage.sh` |
| **HOUSE-13** | Function headers: formhash.c's nine, `run_cmp_row` (and kit.h's side-effect wording), `hash_text_mode`, the fact writers. | `formhash.c`, `runcmp.c`, `kit.h`, `arm_fixtures.c` |
| **HOUSE-15** | Usage and header block (`--site-parts`, `--hash-text`), `tests/memfn/CLAUDE.md`, `memfn/src/CLAUDE.md` (a fold per id, heap; at its 12 KB limit, so the line stays short), slot CLAUDE.md env inputs, `screen RUNDIR RUN_ID`, sabotage.sh's verb, run.py exit codes. | as named |
| **HOUSE-17** | drv.c messages on every exit; a partially read NFILE says it recalibrates; gen.c guards `gap == 0` and `L >= CAND_STRIDE`. | `drv.c`, `gen.c` |
| HOUSE-12, -14, -16 | PLAN (as ruled; HOUSE-16's `class_measure` goes with SLOT-9's fold). vcls.py's missing `__main__` guard (part of HOUSE-16) is fixed. | — |

One item is not this lane's: the accepted process change (the harness-fidelity lens row in the skill's lens
table and critics.md) belongs to the manager. Main's and the kit's skill files are outside this worktree's
scope.

## Sabotage

All rows go red when planted and green when reverted. The control is the unplanted copy: green J2 dry run and
green `est.py` self-test.

| row | finding | plant | detector | result |
|---|---|---|---|---|
| S2933 (mech, `memfnfinder`) | G4 | `mf_form_hash` folds the canonical instance only | check B: `mf_form_hash(settest/rc-words) ... is not the fold` | hand-plant RED (finder_check 1062 passed / 2 failed), reverted GREEN (1064/0); log `scratch/memfn/s2cfix/plant2933.log` |
| (l3) S2934 slot | G1 | `_time` loop over `n / 2` (gate loop untouched) | gate SENTINEL: `GATE MISS ctl ... SENTINEL: found 1 ... timed 0, planted 1` | DETECTED |
| (g2) S2935 slot | G2 | plan.py builds the libc row's Arm with walk's form | `KEY-ARM MISMATCH kit.find_byte.libc` | DETECTED |
| (g3) S2936 slot | G3 | est's never-ran cross-check disabled | est self-test `leftover cells of a never-ran job WRONG` | DETECTED |
| (j), (j2), (k), (l1), (l2) | S2c's | unchanged plants | (l1)/(l2) now first caught by the sentinel subject (regexes widened to the new message; l2 still requires found = timed = planted) | DETECTED |

The final run is `slot/sabotage.sh` → **8 DETECTED, 0 MISSED of 8 rows**, log
`/var/tmp/pcrec-pcrec/scratch/memfn/s2cfix/sab2.log`.

G5-G8 have no answer-level plant. Their refusals are exercised by the record-step witness (§Validation) and
`est.py selftest` (6 cases: complete; leftover never-ran cells; missing cell; other run id; wrong base; id vs
launch column).

## Validation

Everything below ran in the worktree or under `/var/tmp/pcrec-pcrec/scratch/memfn/s2cfix/`. No timing, no queue,
no `make test`, no mech.

- `make`: rc 0.
- `make strict`: rc 0, "whole tree compiles clean with -Werror -Wshadow".
- `make test-memfn-finder`: rc 0. finder_check 1064 passed, 0 failed; check C 17 cards; overall 3272 passed, 0
  failed (`finder2.log`).
- `gnutimeout 300 bash tests/registry/limits_check.sh`: rc 0, 39 passed, 0 failed.
- `make test-spec-history`: rc 0, 187 + 11 passed, 0 failed. `scripts/spec_toc.py` was rerun on measures.md.
- `slot/sabotage.sh`: 8 DETECTED, 0 MISSED (§Sabotage).
- Slot dry runs, J1, J2, J2p, J3, J4, J5 under run id `s2c-dry` in one RUNDIR: all rc 0 (`dryall2.log`).
  - Every launch is gated, for example J4 `35 arms, 35 pools, 560 subjects, 560 timed calls, 0 misses` × 7.
  - Cell-text checks: J2 4, J2p 18, J3 18, J4 28 TUs, all equal to the hash of the instance the key names.
  - The ctl sha is identical across jobs.
  - Groups: J1 9, J2 3, J2p 7, J3 6, J4 5, J5 3.
- S2d job `--dry-run`s: all 8 rc 0 with a test `window.env` (run id s2c-dry, FROZEN = HEAD).
  - `expect groups` as above.
  - A stale copy refuses (rc 1).
  - `--ready` with nothing queued: J2 75 (waits on prep); J9 75 (waits on prep).
- Record steps on a dry-run record:
  - `ready-j2p`: absent 75 / a 0 / b 77 / c 0.
  - `window` with another run id refuses (2).
  - `j1` writes the verdict.
  - `finalize` maps green, failed, cancelled→declined-j1b, wait-timeout, none→never-queued; an unknown state
    (`pending`) refuses (2).
  - `est.py draft` on a REFUSED record writes no draft (exit 3).
  - On a synthetic FULL run, the draft is written (38 rows, 826 cells, gate resolved to 30000 on the cards), and
    `build/pcrec --list-measurements=draft.tsv` reads it (rc 0).
- `est.py selftest`: 6 cases, 0 wrong.
- emit_sweep spot against the lane base `79c5e91e5`: 159 patterns (S2c's pattern file), streams c-default, c-vm,
  emit-ir, facts. **movers=0, asymmetric=0** on every stream, `emit_sweep: DONE rc=0` (`emit/sweep.log`).
- Old-hash readers, by grep: `206d9992…` and `8957c3f8…` occur only in the r9 review's own record files.

## Gate jobs

Scratch `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/jobs/`; nothing queued.
- 470 strict, 472 test: unchanged.
- 471 sections: its comment now says check C is exact 17 with resolved deps. The section list is unchanged, so
  the population is unchanged (12).
- 473 mech: `IDS` gains S2933, so **N 13 → 14**. The comment names the slot-local rows (l3) S2934, (g2) S2935,
  (g3) S2936.
- 474 slotsab: rows `j j2 k l1 l2 l3 g2 g3`, **`expect rows=8`** (was 5), regex `^(j|j2|k|l1|l2|l3|g2|g3)  DETECTED `.
- `--dry-run` of 471, 473 and 474: rc 0.
- `jobs/s2d/` now holds copies of the committed `slot/jobs/` (W1/W2) and a `window.env` with RUN_ID and FROZEN
  empty. Main fills it when the window is cleared; until then every dry run refuses, by design.

## Charter-vs-committed checklist

- [x] G1 (FIX-NOW; the gate of the fix): timed entry gated with a sentinel, population asserted, every launch,
  manifest, caches keyed; S2934 DETECTED
- [x] G2 (FIX-NOW): the key names the text; S2935 DETECTED
- [x] G3 (FIX-NOW): frozen plan, record-driven est, run-id cells, cross-checks; S2936 DETECTED
- [x] G4 (FIX-NOW, FOLD): fold hash, per-instance fixtures; S2933 red/green
- [x] G5 (FIX-NOW): cell_text deps, box facts, no draft on REFUSED
- [x] G6 (FIX-NOW): window facts at every job, CAUSE table
- [x] G7 (FIX-NOW): cards and policy as the one home, null base from facts, one CAND_STRIDE, doubled gates
- [x] G8 (FIX-NOW): landing refuses, git return code checked
- [x] W1 (FIX-NOW + §9 text): job scripts committed, `expect groups` from the plan
- [x] W2 (FIX-NOW): readiness by END; J3 after J2 and J2p; J2p 77 on a non-green J1; J9 waits for prep
- [x] W3 (FIX-NOW): total wait bounded
- [x] CONTRACT-1 (DOC, FIX-NOW; PLAN data form): §3.4¶1, §3.5¶8a, `rules` key
- [x] CONTRACT-3 (DOC): §2.1¶1 `partial`
- [x] CONTRACT-4 (a)-(c) (DOC): §3.4¶2a, §3.5¶12 row 1, §3.4¶14a; (d)/(e) NOTED
- [x] CONTRACT-6 (DOC): no draft on REFUSED
- [x] EMIT-3 (FIX-NOW, majority shape): vcls shapes, link refusal/tag; instance stays (case 156/292)
- [x] EMIT-4 (FIX-NOW): RUNCMP guard; settest leaf render in formhash and §3.2
- [x] EMIT-5 (PLAN): trigger stated in §3.2
- [x] SLOT-9 (FIX-NOW stamp; PLAN fold): vcls.out stamped; fold trigger in §3.2
- [x] SLOT-10 (DOC): §2.5
- [x] SLOT-11 (DOC): §2.4 enter note
- [x] SLOT-13 (DOC + ruling): per (launch, arm), §3.2
- [x] SLOT-14 (DOC): gen.c comment
- [x] SLOT-17 (RULED POLICY): `memfn/data/policy.tsv`, cards `-`, §2.4/§6
- [x] CHECKS-3 (FIX-NOW): deps resolved, count exact
- [x] CHECKS-4 (FIX-NOW): renamed > 0 required
- [x] CHECKS-6 (FIX-NOW with G4): per-instance fixtures
- [x] CHECKS-7 (NOTED): untouched
- [x] HOUSE-5 / SLOT-18 (FIX-NOW): j1_rule imports est; pad range labelled
- [x] HOUSE-10 (FIX-NOW): dead code removed
- [x] HOUSE-11 (FIX-NOW part): timeout_bin, labels, MAIN derived; duplicated gate NOTED
- [x] HOUSE-13 (FIX-NOW): function headers
- [x] HOUSE-15 (FIX-NOW): usage and CLAUDE.md drift
- [x] HOUSE-17 (FIX-NOW): messages and guards
- [x] HOUSE-12, HOUSE-14, HOUSE-16 (PLAN): unchanged, except vcls.py's `__main__` guard
- [x] Design text marked `[rev1.3 r9-<id>]` with the §R1.3 r9 table; spec hunks cite sections only
- [x] Gate jobs 470-474 counts and the S2d job dir (W1/W2) updated; nothing queued
