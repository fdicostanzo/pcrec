# sae1fix report — FIX-NOW set of the E1 review (lane sae1fix, sonnet, 2026-11-09)

Subject: branch lane/sae1 on top of c17a12722, review `docs/dev/reviews/2026-11-09-r3-sae1.md`
(manager rulings: every PROPOSED disposition adopted). DOC items are the manager's and were skipped.
No `memfn/` edit, no abi number moved (no emitted scaffolding changed), no merge of main.

## Fixes

| id | fix | where |
|---|---|---|
| CHECK-1 | the walking attempt's restored arms ride `PcrecMeasInherit.walk_arms` into each compound part's compile; `pf_derive_req_walk` reads them from the harness set, else from the inherited set. `PcrecEmitIn.harness` stays the harness entry's alone (no-compound / kit-proof are NOT passed to parts, as compile.c says). Premise: `^a\|abcd(?:\b)*efgh$` under the lever left the part stamp `6162636465666768@1`; now the part (`RX__Q_REQ_RUN`) is `65666768@2` and the artifact differs from the no-lever one | src/core/internal.h, src/core/compound.c, src/facts/facts.c |
| CHECK-2 | `[facts-arm]` gains 10 artifact (`-p rx --emit-main`) cells: top stamp under and without the lever on byte and utf8, plus the refusal cells (bad arm named alone, a prefix `emp` refused). The corpus reach floor and two-directional property stay PLAN (the review's [HARNESS-LEVERS] item) | tests/codegen/run_facts_checks.sh |
| CHECK-3 | m>=1 default and lever cells (`ab(?:\B){3}cd` 61626364@1 / 6364@0; `abcd(?:)+efgh`) plus S1910 (drops `all` at rmin>=1, detected) | same, tests/mech/sabotages/S1910_rep_unit_at_min1_not_all.sh |
| EMIT-2 / SLOT-1 | `rb_rep_unit_into` takes `pcrec_pd_unit()` at both m (the body is width 0), so the piece description matches `rb_init`'s identity; `req_pieces` is inert, no emitted C moves | src/facts/req.c |
| CONTRACT-1 | tuning §2.28¶3 now says a zero-iteration quantifier breaks contiguity only for a body that consumes something; a width-0 body's repeat does not | docs/spec/tuning.md |
| CONTRACT-3 | the req.c header and the A_EMPTY..A_LOOK case comment say BARE assertions cut; a quantified zero-width node is T2 row 1's; `restore=empty` restores the repeat, `zero` (lane sae2) the bare cuts | src/facts/req.c |
| CONTRACT-2 | `empty` is named in one place (walk_arms.def, unchanged) and plain A_EMPTY / width-0 repeats restore under it per the ruling; nothing added | n/a |
| CONTRACT-4 | ¶4a: the token replaces a `decline:`/`rate:` reason; a denied or absent fact lists its own reason, no token | docs/spec/facts_listing.md |
| CONTRACT-5 | the lever's error prints the bad name alone (`%.*s` with `strcspn`) | cli/main.c |
| SLOT-4 | `rb_rep_row` stops at the last row (`i < last`), which matches every repeat and is never restored, so the scan cannot run off the table whatever rows are added | src/facts/req.c |
| S1909 | plants CHECK-1 (compound.c drops the arms): detected by the `RX__Q_REQ_RUN` cells | tests/mech/sabotages/S1909_compound_part_drops_restored_arms.sh |

`src/facts/CLAUDE.md` names the two new rows. History-index line added to
docs/dev/history/claude_md/docs__dev__lanes.md.

## Checks run

- `make -j16` clean; `make strict` clean ("whole tree compiles clean with -Werror -Wshadow").
- `PCREC=build/pcrec bash tests/codegen/run_facts_checks.sh`: checks passed 11, failed 0 (all [facts-arm] cells).
- Plants by hand (sed of the SAB_BEFORE text, then run_facts_checks.sh, then `git checkout`): S1909 -> `[facts-arm]` FAIL naming `RX__Q_REQ_RUN [6162636465666768@1], want [65666768@2]`; S1910 -> FAIL naming the m>=1 cells. The matrix itself (VALIDATE_ONLY) accepts both rows' fields; the rows' real run is queued below.
- `bash tests/harness/run.sh tests/litscan/spanarms.rxt`: cases passed 62, failed 0.
- `make test-codegen` (first run, nice, ~25 min under box load): `run_group: 20/21 scripts passed`, `*** [Makefile:726: test-codegen] Error 1`; my filtered grep did not keep WHICH script, so it is UNIDENTIFIED and may or may not be this change (the facts check passes 11/11 standalone). A full re-run writes /var/tmp/pcrec-pcrec/scratch/sae1fix/codegen.log (detached; completion line `run_group:`), and queue job `206-main-sae1fix-codegen` reruns it with the last 40 lines kept.

## STATE AT HANDOFF

- Rulings file `docs/dev/lanes/sae1fix_rulings.md` was empty at every checkpoint; no entry applied.
- Queue: CANCELLED (not yet started) `main-sae1-axes`, `main-sae1-ident`, `main-sae1-mech`; RE-QUEUED on the fix commit as `201-main-sae1-ident-2`, `203-main-sae1-axes-2` (after `main-sae1-maketest`), `204-main-sae1-mech-2` (rows S1905-S1910, after axes-2). `main-sae1-census` and `main-sae1-maketest` stay queued: they run the lane tree at start, so they include this fix if it is committed first (it is); census is unaffected (answers and emitted default C unchanged).
- OWED: WHICH codegen script is red (read `grep -nE 'FAIL|run_group:' /var/tmp/pcrec-pcrec/scratch/sae1fix/codegen.log`; triage whether it is mine), verdicts of those jobs, `make test-codegen` log at the path named below.
