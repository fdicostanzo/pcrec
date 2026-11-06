# s2c report: span_pick stage 2 unit S2c, the producer (kit request R-35)

Lane s2c (opus), branch `lane/memfn-s2c`, base `ea5d54abf`, 2026-11-06. Design of record: `docs/design/memfn/span_cards.md`
rev 1.3 (this lane's first commit). STATE: delivered. Validation COMPLETE for every check the brief allowed this lane
to run. The gate suites (strict on the queue, the kit sections, make test, mech) are OWED as prepared, unqueued box-queue jobs.

## Summary

- Commits: `4cc755a15` (rev 1.3), `2ab3b0ce4` (spec hunks + harness WIP), `c53d457f6` (formhash entry table, kit-grid@3, check C
  guard, S2930-S2932, J1/J5), `e21633081` (slot CLAUDE.md, movers.py, sabotage fixes), and the report commit.
- No emitted pcrec byte moves. A bounded `scripts/emit_sweep.py` spot against base `ea5d54abf` (159 patterns: 150 sampled from
  the S2b corpus plus the J1/J5 fixtures; streams c-default, c-vm, emit-ir, facts) gave **movers=0, asymmetric=0** on all four
  streams (`emit_sweep: DONE rc=0`). Nothing reaches the seam. `runcmp.c` only gains a lookup (`run_cmp_row`) that formhash
  reads; no text changes.
- Every job's dry run is green under run id `s2c-dry`: J1, J2, J2p, J3, J4, J5 (Validation). The slot-local sabotage rows
  are 5 of 5 DETECTED. The S-rows S2930-S2932 each went red when planted by hand and were reverted.
- **Two deviations need main's ruling** (Built, "Readings and deviations"):
  1. §3.2's "3 of 4 phases" constraint is now read against each object's real `.text` alignment.
  2. `walk-set` is folded into `walk`.
- The placement screen ran on a loaded box: load ~7.8, with the queue job `462-kit-s2a-ident1` running. It printed the unit noise
  as 8.56 %, OVER the 1.5 % half gate. This tests the mechanism only. It is not a quiet-box reading, and the window's own
  quiet gate is what matters.

## Rev 1.3 text fixes

Commit `4cc755a15`: review r7's READY-1..9, marked `[rev1.3 <id>]`, with the §R1.3 table. Each fix is in the section the
table names:
- READY-1: §3.8, the strip's output path and the KS_TEXTSRCS hook; also §8.2.
- READY-2: §3.5 and §3.6, the run record's two writes, with J9 finalizing via `boxqueue state`.
- READY-3 and READY-9: §9's S2c row.
- READY-4: the contradictory separability sentence deleted.
- READY-5: §3.4 step 1 (a)/(c) and §3.5 (b), the three compares.
- READY-6: §3.8, counting the `.pre` view's cell lines.
- READY-7: NOTED in §3.5 Outcomes.
- READY-8: §3.2, `s2c-dry` and the re-draw order.

`docs/design/memfn/CLAUDE.md`'s rev line follows. The commit message records the sabotage letter to id map:
- (m) S2930
- (n) S2931
- (o) S2932
- slot-local rows (j), (j2), (k), (l1), (l2) run through `slot/sabotage.sh`.

## Built

- **formhash** (`memfn/src/formhash.c`, `kit.h`): ONE entry table plus ONE renderer path, `fh_render`, which reaches each form
  through the kit's own selection. An instance whose facts reach another row is refused, never hashed.
  - Ids: `walk`, `libc` (hashes unmoved: `bc7b2e02f06fe955`, `d7672e87c1dd6d97`), `pair` (`b866902a13e46ba1`), `settest`
    c1/c2/cn, `rc-words` w1/w2/w3, `rc-memcmp` l1. The canonical instances are c2, w2 and l1.
  - Entry points: `mf_form_entry_at/of`, `mf_form_shape_of`, `mf_form_row`, `mf_form_hash_cls`, `mf_form_site_split`
    (the helper and the site body separately; the slot harness renders a cell TU from them).
- **arm_fixtures.c**: hash_mode prints `FORM` and `FORMCLS` lines, R-MS3's rename and edit lines, and has the modes
  `--site-text`, `--site-parts`, `--hash-text`, `--facts`.
- **finder_check.py**: check B resolves every instance against `FORM_IDS` (instance floor 10, pairwise distinct, R-MS3 per id).
  Check C's card guard (a card with a `kit:form.` dep has `form` as its first dim) runs over every card table, floored at 17.
- **kit-grid@3** (`memfn/data/cards/kit-grid.tsv`): `find_byte` (unit walk; slope 64Ki/256Ki/1Mi; `twin-per-arm;bimodal-test`),
  `find_hit`, `verify_cmp`, `enter`, each with gate 30000.
- **Spec**: `docs/spec/measures.md` gains §2.2¶5, §3.4 (the estimator, steps 1-8) and §3.5 (gates, the NULL rule, the
  bimodal test, drift, the run record, the three-copy compare, the first-match outcome table). There is NO §2.2¶3 hunk.
  `docs/design/measure_sets.md` and `span_pick.md` get their `[s2]` lines.
- **The slot harness**: `docs/design/memfn/span_cards/slot/`, files listed in its CLAUDE.md.
  - Built: plan, generator, driver, link (per-launch pads seeded by (run id, job, l, arm, draw); bounded re-draw of 64;
    cell-text check; linked-text equality arm vs twin; fixed `ctl` executable with sha `c17c56ed...b201`), run (dry/run/screen),
    est, record, j1_rule.
  - J1 and J5 whole-artifact arms (`art.py`, `enter/fixtures.tsv`, `j1/`), built by a sub-lane under my brief and reviewed here.
  - Also `sabotage.sh` and `movers.py`.
- **J5 fixtures** (entry NONE). Rule: a census0 corpus unit of that kind whose CHOSEN alternative has that entry and at least
  2 non-FULL verify positions; python `re` semantics must be the same; the shortest pattern wins.
  - kind 1: `(?i:select)\d+x`
  - kind 3: `(?i)(hello|help)`
  - kind 4: `(?i)(ca)t\1`
  - kind 5: `(?m)^\bfoo\b$` (not row-1)
  - kind 6: `(?i)abc` (REPORT: a pass candidate is a match)
  - **UNREACHED, reported and not forced**: PARKED for kinds 1 and 3 (each verifies only the stop, so no FAIL candidate
    exists), RESEED for kinds 1 and 3 (never chosen), and PARKED/RESEED for kinds 4-6 (stated by no corpus unit).
- **J1**: the bench's `wild-waf-crs-942270-union-select` and `wild-secrets-username-password-pair`. I read
  username-password-pair as plan.md's "query-string pair", from O-117's movement on the qs texts.
  - Patterns are read from the bench checkout at run time, sha-256 pinned, never copied.
  - Subjects are generated pcrec-side (`j1/subjects.py`) in two shapes, `mixed` and `qs`, with two regimes, `throughput`
    (1 MiB) and `short` (1,024 records): 8 cells.
  - Widths are 32/64/128/256/512 plus the twin `128#b`. The PAIR declaration `wa = 128, wb = 128` is asserted to occur
    exactly once per artifact.
- **Verify classes** (fix the verify cls boundaries from T-CMP / T-SETTEST: what and why). `slot/vcls.py` over the S2b
  sweep's row-1 sites (`vcls.out`). Classes are measured on the site text the kit renders, not on the pattern's set:
  - settest by COMPARE count: c1 (48 sites), c2 (290), cn (7, with `\w` at 7 compares).
  - rc-words by WORD count D(L) = ceil(L/W): w1 10, w2 49, w3 1.
  - rc-memcmp: l1 (one load, L in {1,2,4,8}), 2 sites.
  - Why: the compare/word count is what T-SETTEST and T-CMP's rows actually cost per candidate. census0's "short<=8 /
    setN by members" was S2b's reading of the pattern side and splits sites that render the same text. No rc-overlap and
    no rc-bytes site exists on row 1, so neither has a class.
- **Readings and deviations (for main's ruling)**:
  1. **Placement phases.** gcc 15.2's generic tuning aligns tight loops to 32 (`.p2align 5`), and some artifact objects
     to 64. An arm's function then cannot take 4 phases mod 64.
     - `link.py` reads each object's `.text` alignment A and requires min(3, 64/A) distinct phases over the 7 launches,
       plus arm and twin differing mod 64 in every launch where A < 64.
     - At A = 64 there is one phase, so neither constraint can apply: it is recorded, not re-drawn.
     - I did NOT add `-falign-functions` or `-mno-align-tight-loops`, because the cells time the declared target's default
       code. This changes §3.2's "3 of 4" premise for most arms (2 phases at A = 32), so main should rule on it or on a flag.
     - Phases seen: J2 `2`; J2p `1`; J4 `1,2,3`; J1 and J5 `1,2`.
  2. **`walk-set` folded into `walk`.** Its site, the composer's FIND over `{X,x}` through pcrec's table, renders the
     walk's text byte for byte, so the hash decides it is one form (§2.4). The plan carries no walk-set keys (J2 byte,
     J3 alt).
  3. **Per-arm draw index.** The draw index d is per (launch, arm). The per-launch constraint is repaired twin by twin in
     link order. The cross-launch constraint re-draws the failing arm in the latest launch that still has draws (READY-8's
     "from launch 7 down").
  4. **Verify-row form hashes.** Cells are checked against their (form, cls) instance hash. `mf_form_hash(id)` is the
     canonical class.

## Sabotage

| letter | id / runner | plant | result |
|---|---|---|---|
| (j) | slot/sabotage.sh | pad seed ignores launch and draw | DETECTED: `link: REFUSED: J2 launch 7 arm kit.find_byte.walk: 64 draws, the cross-launch constraint ...` |
| (j2) | slot/sabotage.sh | twin padded onto its arm's phase | DETECTED: `... arm kit.find_byte.walk#b: 64 draws, the per-launch constraint (arm and twin differ mod 64) still fails` |
| (k) | slot/sabotage.sh | walk rendered from libc's entry row | DETECTED (rc 3): `CELL-TEXT MISMATCH ctl: site text d7672e87c1dd6d97, form hash of ('walk', None) bc7b2e02f06fe955` |
| (l1) | slot/sabotage.sh | libc's hits planted as another byte | DETECTED: `GATE MISS kit.find_hit.libc.periodic.one.256 ... found 0 ..., planted 4096` |
| (l2) | slot/sabotage.sh | find wrapper returns each hit one byte late | DETECTED: `found 4096 sum 2148007936 ..., planted 4096 sum 2148003840` (count kept, positions moved) |
| (m) | S2930 | `pair` entry rendered as the walk | red by hand (after a rebuild of libpcrec.a): `form instances hash one text: walk - = pair -` |
| (n) | S2931 | verify_cmp@3 dims `cls;form;pass` | red by hand: `card verify_cmp@3 names a kit:form. dep but its first dim is 'cls', not form` |
| (o) | S2932 | format-2 header in memfn/data/sets/ | red by hand: `values_digest 5c77acf469930b8b, recomputed b3ea024ae0fe2fbb` |

Notes on the table:
- The control (the unplanted copy's J2 dry run) is green.
- (l2): the wrapper is shared, so every find arm misses. The runner matches the miss by its shape: found = planted, sum differs.
- S2930-S2932 pass VALIDATE_ONLY (3 definitions valid). Every plant was reverted; `git status` was clean on memfn/ and tests/ afterwards.

## Validation

- `make strict`: rc 0, after all code changes.
- `make test-memfn-finder`: rc 0, `checks passed: 3235, checks failed: 0`. `check C: 17 cards with a kit:form. dep`.
  Every FORMCLS instance resolves; the ids are pairwise distinct; R-MS3's rename (hash kept) and one-instruction edit (hash
  moves) hold per new id. UNREACHED is printed only for the later forms (V1, W64, NONE, dispatch-twin).
- **Dry runs** under `s2c-dry`, RUNDIR `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/dry` (logs `dry.<JOB>.log`):
  - Each prints the ctl sha, `placement:`, the launch-1 gate (`0 misses`) and `would run`.
  - Gates: J2 4 arms, J2p 19, J3 18, J4 35, J5 15, J1 48.
  - Every cell TU's site-text hash equals its key's form hash (`cell-text:` line).
  - All six rc 0. Draws per launch, and the phases mod 64 the objects' alignment allows:

    | job | draws | phases |
    |---|---|---|
    | J1 | 5,5,5,5,6,2,4 | 1,2 |
    | J2 | 5,3,1,2,1,2,0 | 2 |
    | J2p | 0,0,0,0,0,0,0 | 1 (every J2p object is 64-aligned, so the constraints cannot bind there: deviation 1) |
    | J3 | 8,17,14,6,7,8,8 | 2 |
    | J4 | 12,11,12,8,15,9,14 | 1,2,3 |
    | J5 | 4,1,2,2,0,0,0 | 1,2 |

  - Groups: J1 9, J2 3, J2p 7, J3 6, J4 5, J5 3.
- **Placement screen** (`run.py screen`): x_l [1000000, 1000161, 999797, 1141840, 670404, 954498, 1040157], giving
  `noise_e6 85643 (8.564 %)` vs the half gate 15000 → OVER, on a box at load ~7.8 with a queue job running.
  - It shows the screen computes and prints; it is not a quiet reading.
  - Recommendation: run the screen as the first step of the cleared window, or as a quiet-gated job, before J1.
- **Run record dry runs** (`/var/tmp/pcrec-pcrec/scratch/memfn/s2c/recdry`), on synthetic J1 cells:
  - `j1` writes verdict a / b / c.
  - `ready-j2p` gives: absent → 75, (a) → 0, (b) → 77, (c) → 0.
  - `finalize` writes the sections run, jobs, plan, floor, j1_cells in order. J2p under (b) is `never-ran declined-j1b`; failed
    and wait-timeout jobs are `never-ran` with their cause.
- **emit_sweep spot**: 0 movers (Summary). Log: `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/emit/sweep.log`.
- **movers.py smoke** (5 patterns): base pass 0 movers. The self pass refuses `--measures=zen4-grid3` (unknown set), which is
  correct until S2e adds the set.
- No timing run beyond the screen. Nothing ran 19:00-01:00. No make test, no mech.

## Gate jobs

Prepared, NOT queued, in `/var/tmp/pcrec-pcrec/scratch/memfn/s2c/jobs/` (`common.sh`). Each `--ready` calls
`/var/tmp/pcrec-pcrec/scratch/memfn/s2a/jobs/hold.sh` first. Every `--dry-run` is green.
- `470-kit-s2c-strict`
- `471-kit-s2c-sections`: 12 sections, the memfn sections plus knowledge, compound, codegen and registry.
- `472-kit-s2c-test`: make test via perfrun.
- `473-kit-s2c-mech`: 13 rows, from `rows_for.sh` over the changed files plus S2932: S267 S285 S443 S444 S445 S573 S793
  S797 S1545 S1547 S2930 S2931 S2932.
- `474-kit-s2c-slotsab`: slot/sabotage.sh, no clock.

**S2d window jobs**: prepared, NOT queued, in `jobs/s2d/`. `common.sh` holds `RUN_ID=""` and `FROZEN=""`, which main fills
when the window is cleared; every dry run refuses while they are empty.
- `480-kit-s2d-prep`: every job's slot dry run under the window's run id, so the timing jobs only time. Not timing.
- `481-kit-s2d-J1`
- `482-kit-s2d-J2`
- `483-kit-s2d-J2p`: its `--ready` is `record.py ready-j2p`, which returns 77 under (b).
- `484-kit-s2d-J3`: follows J2p green, or J2 when J2p was cancelled.
- `485-kit-s2d-J4`
- `486-kit-s2d-J5`
- `489-kit-s2d-J9`: `record.py finalize` over the queue's end states.

The timing jobs (J1-J5, J2p) are `idle-ok` and quiet-gated by run.py. A filled test copy dry-ran green for J2, J2p, J3, J4
and J9. J1 and J5 needed prep in that RUNDIR first, which the refusal names.

## Charter-vs-committed checklist

| §9 S2c item | committed |
|---|---|
| formhash entry table + renderer entry (§3.2) | yes, `c53d457f6` (formhash.c, kit.h) |
| kit-grid@3 cards | yes, kit-grid.tsv ver 3 (4 cards) |
| check C's deps guard on card rows | yes, finder_check.py, floor 17, observed 17 |
| measures.md §3.4-3.5 + §2.2¶5, NO §2.2¶3 | yes, `2ab3b0ce4`; no ¶3 hunk |
| measure_sets lines | yes, `2ab3b0ce4` (+ span_pick [s2] lines) |
| arm_fixtures `ids[]` + check_hash resolve list gain every new id | yes (FORM/FORMCLS lines, FORM_IDS) |
| slot: driver, subject generator | yes, drv.c, gen.c, slot.h |
| slot: per-launch linking + placement, run id in seed, bounded re-draw | yes, link.py (deviation 1 on phases) |
| slot: ctl | yes (fixed executable, sha checked) |
| slot: the estimator | yes, est.py |
| slot: j1_rule.py | yes |
| slot: the run record's writer | yes, record.py |
| slot: sabotage.sh | yes, 5/5 DETECTED |
| slot: movers.py | yes (run by S2e) |
| verify cls boundaries from T-CMP / T-SETTEST, what and why | yes, vcls.py/vcls.out; Built |
| dry runs of every job, `s2c-dry` | yes, J1 J2 J2p J3 J4 J5 green |
| placement screen, unit noise printed under the half gate | printed; OVER on a loaded box (not a quiet reading) |
| check C card guard over every card table (17) | yes |
| R-MS3 fixtures per new id; ids pairwise distinct | yes (finder 0 failed) |
| every cell's site-text hash = its key's form hash | yes (cell-text line on every dry run) |
| run record two writes dry-run (j1, ready-j2p absent/a/b/c, finalize) | yes |
| sabotage (j),(j2),(k),(l),(m),(n),(o) | yes; (l) as l1 + l2; S2930-S2932 |
| no emitted pcrec byte moves | yes, emit_sweep spot 0 movers |
| gate jobs (strict, sections, test, mech) + S2d J1-J5 + J2p | prepared, not queued |
| CLAUDE.md for every added file | yes, slot/CLAUDE.md, span_cards/CLAUDE.md, memfn and tests/memfn CLAUDE.md |
