# rps3 — [RUN-POS-SET] stage 3, pcrec half of set S2 (lane report)

Lane rps3 (opus), branch `lane/rps3` from main `f066e84ee`. GO: Frank 2026-11-11 and
2026-11-12 23:45 (S2 build go, both halves, one landing). Kit contract:
`lane/memfn-pdesign:docs/design/memfn/part_d.md` rev 4 §9 items 1-9.

## STATE AT HANDOFF

- STATE: delivered-with-owed. The pcrec half is BUILT on the branch and byte-identical to
  main on every artifact (the interim domain below), `make strict` clean, `test-registry`
  green standalone (`bash tests/registry/run_registry_tests.sh`, every block "checks failed: 0").
- The suites, the emit_sweep and the REACH_ONLY run are QUEUED as one box-queue batch
  (owner rps3, OWED below), because the box was held by the kit's 591 gate.
- Two questions to main are OPEN (sent 2026-11-13, no reply before handoff): (1) how the
  stage-3 domain goes live (leaning: a `#if MF_SITE_ABI >= N` in `pf_derive_req_walk`, or the
  landing flips two lines by hand); (2) whether 2a's `rr_alt` rule (1) and the step-0 census
  are this lane's (NOT built: waiting on the scope ruling).
- No rulings file was named in the brief.
- Every commit leaves a buildable, green-on-today's-kit tree.

## CHANGES

**The representation (stage 3 U-a, U-c, U-e; D187).** A run position is the BYTE SET every
match holds there: `RbRun.pos[]` and `ReqRun.pos[]` are arena-owned 32-byte sets by pointer
(the memo's §1 U-a fix (4)), replacing `bytes`/`mask` and `whole`/`whole_mask`. One
constructor (`rn_put`) refuses a set outside the walk's DOMAIN (`rn_admits`: at most
`pos_set` members and, while the cube clause holds, one cube). Information is
`8 - ceil(log2 |S|)` (`pcrec_req_info`, the ranking's and the floor's unit; a cube's is its
mask's popcount, so no exact or cube run moves). The alternation affix is the per-position
UNION (`rb_pd_join`), `rn_hull_mask` deleted. The content-order tie row keys on the covering
cube first, so ties between cube runs are the old order exactly. A covering cube is a
reader's private spelling (`pcrec_req_cube`, D187 add. 1). Readers moved to sets (memo §2.1's
table, every row): `pcrec_req_pick`, `pcrec_run_pin`, `pf_derive_req_walk`'s floor, the
renderer `pf_hex`, `req_note_run`, `req_pres_spans` (`wpos_bits`), `pf_window_of` +
`walk_proves` (subset-of-set, §9 item 1: R never stops at a position for its shape),
`ofs_test_pos_in_set`, `req_whole_holds_byte`, `req_landmark_hit_ppm`, `req_run_in_cover`,
`req_set_leads_own`, `req_rest_own_sig`; `OfsTest.run_mask` (never set) and
`run_mask_or_null` deleted. findings.c: `pcrec_find_run_scan_index` reads sets through two new
primitives `pcrec_find_pos_mass` / `pcrec_find_pos_pick` (S1 primitive list updated);
`pcrec_find_seq_mass` deleted (its one reader moved).

**THE INTERIM DOMAIN.** `PCREC_MAX_REQ_RUN_POS_SET` stays 2 and `PF_WALK_POS_CUBE` (facts.c)
is `true`: today's kit refuses any run position that is not a byte or a cube (K-1), and a set
union makes new non-cube positions (`cat|dog`), so the branch states exactly today's runs.
MEASURED with the domain flipped in a scratch build (`--emit-facts`, today's kit):
`\d{3}-\d{4}` states `[30-39][30-39][30-39]2d[30-39]...@3`, `[a-z]{8}`, `xy/users\d+`
(`78792f7573657273[30-39]`), `\w+@example\.com`, `GET /[a-z]+ HTTP` all render facts and
stamps; `[α-ω]foo`, `(?i)αβγ`, `abc[α-ω]defg` (utf8) and `cat|dog` are REFUSED by today's
kit (`mf_define: the derived run part's find is not at the run reply's scan position`), the
K-1 refusal Part D removes. The limits row's text says the ruled reason is superseded and
names the landing's flip (128, cube clause lifted).

**part_d §9, item by item.**

| item | done/blocked | where |
|---|---|---|
| 1 R by role, `pf_window_of` subset-of-set, `wpos_bits` | done (pcrec side) | emit_dfa.c `walk_proves`, `pf_window_of`; witness `xy/users\d+` OWED after the kit (today's kit reads R by shape: with the domain flipped it measured `RX_DFA_PREFILTER "handoff"`, `REQ_WHY "emitted"`, i.e. F11's mover, until Part D) |
| 2 the decline: the one TESTED predicate | done | emit_dfa.c `req_run_tested`/`req_run_tested_cx`; readers `req_site_define` (P1 `gate_need` on the tested run), `req_landmark_k` (new: K of the head member on a decline; used by `req_handoff_k`, `req_handoff_applies`, `pf_handoff_applies`, the shadow's landmark), `req_handoff_vm_run` (entry/attempts rows), `req_landmark_hit_ppm`. `PF_REQ_LANDMARK_MAXOFF` stays the pre-kit fact; it is RE-READ through `req_landmark_k`, not moved. The head-vs-`req_byte` check: see STOP note below |
| 3 nothing to render | done | new `req-admit` row `untestable` (`req_untestable_applies`), `_REQ_WHY "untestable"`; `--list-axes` gains one row (req-admit 4; set-leads 5, emitted 6) |
| 4 scan-less run; two comments | done | `req_note_run`/`req_note_scan` read `has_scan`; `emit_req_handoff_rest` names the run only where tested |
| 5 lead reader | done | `req_pres_head(lead=true)` reads the tested predicate |
| 6 shadow retirements | done | emit_dfa.c `req_run_wide`: no `leads`/`rlead`/`dominated`/`rdom` record on a run with a non-cube position; `tests/memfn/run_pres_picks.sh` comment |
| 7 version events | OWED to the landing | `MF_SITE_ABI`/`MF_CLASS_V` are the kit's; pcrec abi 105 -> 106 rides the landing (no byte moves on this branch, so no bump here) |
| 8 spec hunks | done | match_api §6.3.7¶5, ¶6 example, ¶7 rows 1 and 3, ¶7a spelling, ¶8 token, ¶11 landmark; tuning §2.28¶1/¶4/¶5/¶7, §2.29¶1/¶4/¶8/¶10, §2.30¶4, §2.39¶1/¶3, §2.41¶1/¶7a; limits.md §3.4a¶4; facts_listing.md §4.1.2¶1. The `--list-axes` memfn-section floor (+1 for the kit's deny row) is OWED with the kit's row |
| 9 pins and floors | OWED to the landing | all kit-dependent (`--memfn=no-run-verify-wide` DIFFER_PINS, D3 floor, D27 witnesses) |
| R-41 `head_max` unbounded name | done, guarded | `req_site_define`: `#ifdef MF_HEAD_MAX_UNBOUNDED` (the name is a GUESS: the kit has not declared it); `tests/memfn/c10_presence.tsv`'s `(a+)+zq` row OWED |

**STOP note (item 2, the head-vs-`req_byte` check).** §9 lists the check among the readers
that switch to the predicate, i.e. it would be enforced on a decline. On a decline the head is
the kit's P3 set pick while `req_byte` (derived before the kit replies) is pcrec's pick over
the run's EXACT positions where one is the scan index's, so the two can differ on a declined
run that has an exact position, and the check would then be an internal error. Built instead:
the check holds where NO run is stated (today's meaning), and on a decline K is read from the
head member itself (`req_landmark_k`), which is the check's reason (the landmark whose K the
handoff subtracts). Asking main to confirm.

**Sabotage rows re-anchored (7, same faults):** S280, S3048, S329, S448 (now two sites, BEFORE2
is the "compared exactly" half), S451, S453, S456 (the plant now stores the INTERSECTION, empty
where the branches differ, which the constructor refuses). No new rows: the decline's witnesses
(one plant on `req_run_tested`) can only red after Part D (OWED).

**Other files:** `tests/codegen/run_encoding_checks.sh` (REQ_WHY's closed set gains
`untestable`), `src/core/limits.def` (two rows' text, the bits unit comment),
`tests/findings/structural_check.py`.

## OWED

- QUEUED batch (`scripts/boxqueue batch --owner rps3`, stages file `worktrees/rps3/build/STAGES.rps3`:
  strict, codegen, registry, rxtsource, memfndeleg, startset, compound, reach, sweep; verdicts by
  `scripts/monread rps3`; each stage waits for the one before it to go green): `make test-codegen test-registry test-rxtsource
  test-memfn-deleg test-startset test-compound`, verdict by
  `grep -E '\*\*\* \[(Makefile:[0-9]+: )?test-'`; `REACH_ONLY=1 bash
  tests/mech/run_sabotage_matrix.sh S280 S3048 S329 S448 S451 S453 S456`;
  `python3 scripts/emit_sweep.py --ref f066e84ee` over every stream but `dumps` (expected
  movers: NONE; movers file `$PCREC_TMPDIR/scratch/rps3/sweep_movers.tsv`). The `dumps`
  stream is excluded because its delta is intended and MEASURED by hand against main's binary:
  `--list-axes` gains `req-admit 4 untestable` and renumbers set-leads/emitted to 5/6 (nothing
  else moves); `--list-limits` changes the text of `PCREC_MIN_REQ_RUN_BITS` and
  `PCREC_MAX_REQ_RUN_POS_SET` only (values unchanged).
- At the joint landing (needs lane/memfn-partd): flip the domain (`PCREC_MAX_REQ_RUN_POS_SET`
  128, `PF_WALK_POS_CUBE` false, or the `#if` main rules); pcrec abi 105 -> 106 with every
  reader by grep; confirm `MF_HEAD_MAX_UNBOUNDED` is the kit's name and move c10's `(a+)+zq`
  row; §9 item 9's pins; the `--list-axes` memfn floor; the decline witnesses + one plant on
  `req_run_tested`; the stage-3 mover census (memo §3's witnesses, by class) and D186's
  per-regime evidence; `make test`, `make test-axes`, mech; the `xy/users\d+` witness
  (`run-pinned`, offsets `0*,1,..,7`).
- NOT BUILT pending main's ruling: 2a's `rr_alt` rule (1) and the step-0 independent census.
