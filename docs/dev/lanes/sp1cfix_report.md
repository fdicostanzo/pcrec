# sp1cfix — review fixes for span_pick unit 1c

Lane sp1cfix (sonnet) for the memfn kit manager. Branch `lane/memfn-sp1cfix`, cut from `lane/memfn-sp1c` @ 3ecb647c7;
the findings are review 2026-11-04-r2 (`$PCREC_TMPDIR/scratch/memfn/sp1cfix/review.md`). Stage 1 stays byte-identical:
no emitted byte moved, no pcrec abi change, MF_SITE_ABI stays 23, no MF_CLASS_V move.

## What changed

- `memfn/src/window.c`: `kit_run_member` states its precondition (T_MASS_STRETCH is a strict, translation-invariant
  order) and its key space; translate's ranking refuses a pos of -1 (`kit_fail`) and, where C-pin fired, checks that
  `rank_pos[0]` is the run member minus the term offset; the comment is restated; the T_MASS_STRETCH basis names its
  pcrec pin; A-mass's comment says "position mass".
- `memfn/src/compose.c` (refusal message), `memfn/include/memfn.h` (two stale "cube mass" lines),
  `docs/design/memfn/integration.md` (Q-G2-13 row), `docs/design/memfn/span_pick.md` (ratchet end count).
- Tests: `tests/memfn/mass_check.c` + `run_finder.sh` (MASS_FLOOR 40 -> 41) + `tests/memfn/CLAUDE.md`;
  `tests/memfn/pres_pick_witnesses.tsv` (2 lines); `tests/memfn/decider_census.py`;
  `tests/mech/sabotages/S458_set_leads_tie_leads.sh`.

## Findings by id

Each plant was applied to the tree, shown, and REVERTED (`git checkout` of the file; the committed tree carries none).

| id | done | evidence |
|---|---|---|
| F1 | window.c: precondition + key-space comment on `kit_run_member`; translate refuses a -1 with `kit_fail("window family: the run ranking lost position K of N (the T_MASS_STRETCH tie row must be a strict order)")` and stops the ranking at K (never casts -1 to 65535) | Plant `T_MASS_STRETCH` -> `TIE_EXCHANGE`: `zq.*(?i)hello world` and `q(?i)aaaa` now refuse with "ranking lost position 5 of 8" / "2 of 5" (several other patterns refuse earlier, at req_run_member's pin); before the fix the review measured rank 0, 65535, 0, 65535. Reverted |
| F2 | where `d->pinned`, a loud `kit_fail` when `rank_pos[0] != d->member - w->off[hint_at]`; window.c's comment now "the plan term's least-mass position" (the 1c row is NOT amended) | Plant: rank walk broken in translate (first answer xor 1). `(?i)enzyme -fmemfn-simd` with the check DISABLED: rc 0, emitted C differs (the formerly silent move); with the check: refused (rc 1, "the memfn kit refused the window family's phase-1 ask"). Reverted. Unplanted input: 1620 compiles byte-identical vs base (Validation) |
| F3 | integration.md Q-G2-13 row gains the pspans exception ("MF_SITE_ABI 23, D187, span_pick 1c"); compose.c message now "(... a rendered term may state one, Q-G2-13, a presence fact may not, D187, MF_SITE_ABI 23)" | test-memfn-finder `NORMAL ... outside its mask` still passes (the match text is unchanged) |
| F4 | memfn.h `mf_wreply.run_stated` ("PICK's position mass") and `mf_pres_picks.run_scan` ("its set's mass"); window.c A-mass | grep: no "cube mass" / "cube's mass" left under memfn/ |
| F5 | span_pick.md §Staging: stage 1 ends at 3 or 4 (R20 2, R25 1, R22 0-1; R24 reads 0), "restated against roadmap §5's current recipes" | the ratchet-log line in roadmap §5 is main's / the kit manager's (not mine) |
| F6 | `pres_pick_witnesses.tsv`: `scan 1 2 - x.*(?i)ab1def` and the same at `-e utf8`; expected position 2 hand-derived (the only exact, 1-member position is the least mass; masked 'a','b','d','e','f' have 2) | run_pres_picks.sh: 69 passed, 0 failed (28 witness lines). Plant: `run_at` ignores the mask (set = the run byte alone): both new lines go RED (the used column differs, rc 1 on the layout check), and the comparator plants still discriminate. Reverted |
| F7 | mass_check NORMAL: a span violating at the LAST position (`'A','B','c'` under mask DF) must be refused; MASS_FLOOR 41 | Plant `run_cmp_sat` loop bound `j < 1`: "FAIL: NORMAL a violation at the LAST position is refused: got 0, want 1", mass 40 passed, floor FAIL. Reverted (41/41 after) |
| F8 | S458's `SAB_REACH` probe now carries `--memfn=no-window-search` | Plant (`<` -> `<=` on the set-leads line): `é@ -e utf8` has `memchr(...,64,` x0 at default flags and x0 planted (the probe was vacuous); with the deny flag clean x0, planted x1. `REACH_ONLY=1 ... S458`: REACHED. Reverted |
| F9 | decider_census.py BACKSTOP: dead `< sm`, `> c)` replaced by `< b.mass`, `< after->mass`; a third plant copies kit_run_member's loop | census: 39 hits (floor 30), 0 outside a member; the new plant `ms < b.mass ||` turns it red (4 stray hits); 57 checks / 0 failed |
| F10 | the T_MASS_STRETCH basis: "equals pcrec_find_run_scan_index's tie until pcrec reads the kit's member; a change is a pcrec findings change in the same commit (req_run_member and pres_layout_check pin it)" | by grep |
| F11 | not mine (PLAN, main's) | |
| F12 | not mine (PLAN, folds into 1d) | |
| F13 | NOTED | |

## Validation

Light, in the lane; the heavy loops ran under `scripts/boxlock run` (labels sp1cfix-spot, sp1cfix-cmp). Code final at
3fa12133d; sections ran AFTER it.

| check | command run | result |
|---|---|---|
| build / strict | `make -j8`; `make strict` | clean; "whole tree compiles clean with -Werror -Wshadow" |
| finder | `make test-memfn-finder` (run_finder.sh) | rc 0; 1976 passed, 0 failed; `mass checks passed: 41`, `ok mass: 41 cases passed >= floor 41` |
| rows | `make test-memfn-rows` | rc 0; census 57/0 (backstop 39 hits, 0 outside) |
| G2 | `make test-memfn-g2` | rc 0 (17:45-17:52, after the last code commit); `checks passed: 70358652`, `checks failed: 0`; no `*** [test-` line in any section log |
| anchors | `python3 -I scripts/m6read_check_sab_anchors.py` | 1102 rows, all anchors resolve |
| pres picks | `bash tests/memfn/run_pres_picks.sh` | 69 passed, 0 failed |
| byte identity | `scratch/memfn/sp1cfix/cmp.py`: frozen base build (7b671bc2c) vs this tree, 405 patterns (bench list, p588, pzzz, pextra, the 4 F2/F6 patterns incl. `(?i)enzyme`) x default, `-e utf8`, `--engine=vm`, `-fmemfn-simd`; rc + stdout + stderr | 1620 compiles, 0 differ |
| reach smoke | `reach_equal.py --limit 300`, base vs this tree's MF_TRACE build, the same 4 arms | `LIMITED rc=0 keys=120 differ=0` (rc 3 = clean smoke run) |
| mech reach | `REACH_ONLY=1 tests/mech/run_sabotage_matrix.sh S458` | REACHED |

Not run: make test, the full identity sweep, mech for real, test-axes (the gates).

## Gate jobs

Prepared, NOT queued, `$PCREC_TMPDIR/scratch/memfn/sp1cfix/jobs/`: copied from sp1c's with keys `kit-sp1c2-*`,
`TREE=worktrees/sp1cfix` (prio 390-399), the frozen base builds and pattern files read from `scratch/memfn/sp1c/`
(`SB=` in common.sh), the memfn section's finder floor text 41. Every `--dry-run` exits 0 and each was ACCEPTED by
`PCREC_BOXQUEUE_DIR=.../sp1cfix/bqtest scripts/boxqueue add --no-start FILE` (scratch queue only).

| job | what |
|---|---|
| 390-kit-sp1c2-strict | make; make strict |
| 391-kit-sp1c2-memfn | rows, finder, link, g2, arms, stamps, deleg, manifest, findings, registry |
| 392-kit-sp1c2-reach | MF_TRACE build; reach_equal 18 arms |
| 393/394/395-kit-sp1c2-ident1..3 | emit_sweep 67 + 2 identity arms, 23 per shard |
| 396-kit-sp1c2-test | make test alone via perfrun |
| 397/398/399-kit-sp1c2-mech..mech3 | the 54 rows for real (same list as sp1c: window.c and compose.c are edited again, S458 changed; shard 1 declares `unreached: 2`) |

## OWED

- Everything under Gate jobs (queue by the manager).
- The roadmap §5 ratchet-log line for F5 and the F11/F12 plan rows: main's.
- No journal entry was added (the kit manager's file).

## STATE AT HANDOFF

Commits on `lane/memfn-sp1cfix` (see `git log`): a191bd40b (F6 witness), 3fa12133d (fixes F1-F5, F7-F10), the report.
No emitted byte moved; MF_SITE_ABI 23 unchanged; pcrec abi unchanged. No plant is left in the tree.
