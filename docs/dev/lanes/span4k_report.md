# span4k — R-45 plan B: the window-span carrier, the kit's per-extent working state, witness row (a)

Lane span4k (opus), 2026-11-16, for the kit manager. Branch `lane/memfn-span4k`
(worktree `worktrees/span4k`), base main `a66bf0877`. Design:
`docs/design/memfn/r45_reply.md` rev 4 at `fee80b67b` (§0, §1, §2, §5, §7;
§3/§4 are not this lane's). Rulings applied: main's four (other-sites-at-32,
cover-ask-storage, caller-storage, row-memory: all YES, from the brief) and
`span4k_rulings.md` R1 and R2.

## Summary

Plan B is built at **zero movers**: `emit_sweep.py` against `a66bf0877`, all 22
streams, 0 movers, both before and after the reach raise. The kit contract moves
**MF_SITE_ABI 29 -> 30** and **MF_CLASS_V 10 -> 11**. pcrec's `abi` does not move:
no emitted byte moved. Each per-position fact a span states, and each plan list a
window reply carries, is now a COUNTED LIST in storage the host owns.
`mf_class.proven[]` is now `proof_n`/`proof`. The kit's window working state is
sized by each alternative's stated extent and allocated per decision.
`MF_WREACH` (and so `MF_MAX_FWD`) is 4096 (R1).

Two STOP-rule findings went to the manager and were ruled in R1:
- The raise of `MF_WSPAN_POS` to 4095 and the retirement of
  `MF_MAX_SPAN_POS`/`MF_MAX_AHEAD` are HELD. They are one commit on the child
  branch `lane/memfn-span4k-raise` (R2).
- Witness row (b) WAITS ON main's stage-2 B5 text.

Witness row (a) is built: `run_proof.sh` plant S3242.

## Pieces

| piece | state | where |
|---|---|---|
| Carrier: `mf_wspan` lists (`set`, `table_ref` pointers; `len`/`core_lo`/`core_len` uint16) | DONE | `memfn/include/memfn.h:719` (struct end) |
| Carrier: `mf_wreply` lists (`plan`, `plan_term`, `plan_test` pointers, NULL `plan_test` on NONE; `nplan`/`run_len` uint16) | DONE | `memfn.h:1819` |
| `mf_rows`, `mf_rows_need`, the `rows` parameter of `mf_ask`/`mf_wdecide` | DONE | `memfn.h:1604`, `:1615`, `:1633`; `compose.c:1201`, `:1215`; `window.c:2820` |
| `mf_class.proven[]` -> `proof_n`/`proof`; refusals R-out, R-cap, R-short; `mf_run_reply` widened | DONE | `memfn.h:1326`, `:1409`; `compose.c:412` `kit_proof_open`, `:452` `kit_proof_close`, `:461` `kit_class_same` |
| `MF_MAX_FWD` decoupled = `MF_WREACH`; `MF_WMAX_SPAN` its own literal 32 (25 DERIVED + 7 UNMEASURED slack) | DONE | `memfn.h:333`, `:679` |
| `MF_WREACH` 64 -> 4096 (R1; it is a refusal bound only) | DONE, 0 movers | `memfn.h:695` |
| The kit's working state per extent: `wf_alt.p` and `wf_dec.poff/pterm` (`wf_extent`, allocated in `decide` from the art arena or the ask's heap), `struct wf_plan`'s off/set/core/table/grp + key (`plan_of`), `wf_fpart.plan_test` (the framed ask's heap), `find_groups`' stack array gone; `WF_NPOS` is now only a ceiling | DONE | `window.c:322`, `:335`, `:1273`, `:1427`, `:1832`, `:2775` |
| pcrec callers respelled (allocation from `cx->arena`; `pcrec_memfn_rows`; B5 reads `proof` within `proof_n`, all ones outside) | DONE | `src/gen/memfn_sites.c:183`, `:566`; `known.c:418`, `:601`, `:606`, `:657-663`; `emit_dfa.c:1469`, `:6912-6957`, `:7162`, `:7719`, `:7736` (`wreply_same`, PCREC_CAND_TRACE), `:7778`, `:8512`, `:8926`, `:11600`, `:16347` |
| Witness row (a): the kit row. Plant `end = last_s + 1`; R-short must refuse BY ITS MESSAGE through `mf_define`. The control is the unplanted define of a terms site and a window site | DONE, RED by message | `tests/memfn/run_proof.sh` S3242 + `plant_want`; `tests/memfn/proof_check.c` family A, two "R-short control" accepts |
| Witness row (b): the pcrec row | **WAITS-ON main B5**, unbuilt | spec below |
| HELD raise: `MF_WSPAN_POS` 4095 + retirement of `MF_MAX_SPAN_POS`/`MF_MAX_AHEAD` | ONE commit `0234da0e9` on `lane/memfn-span4k-raise`, NOT merged (R2) | validation below |

**Witness row (b) spec** (r45_reply.md §1, R3-5):
- Kind and id: a mech row, id from S3243-S3249.
- Pattern: `[0-9a-f]{32}` with nothing after it, an after-UNSTATED cover at the
  default width 32 (`k` = 32, `last_s` = 31).
- `SAB_FILE` `memfn/src/compose.c`: the same cut as S3242,
  `long end = last_s + 1;`, giving range end 32, below `k`.
- `SAB_FILE2`: delete the R-short check, by its message text "the proof range
  ends before the statement's following offset".
- Expected: B5's named internal error by its text, "the kit's proof range ends
  at offset %d, before the cover's after-context at %d". This text exists only
  in main's stage-2 B5 (`pcrec_cover_proof_diff` in `src/gen/known.c`), which is
  in no tree today.
- REACH: the clean build emits `RX_DFA_SCAN "cover"` for the pattern and the
  after side is unstated.

**HELD raise (child commit `0234da0e9`).** It touches:
- `memfn.h`: `MF_WSPAN_POS` is its own literal 4095; `MF_MAX_SPAN_POS` and
  `MF_MAX_AHEAD` are deleted.
- `window.c`:
  - `wf_legacy` keeps `WF_LEGACY_POS` = `MF_MAX_TERM` (DERIVED: `legacy_ok`
    admits at most `MF_MAX_TERM` non-full positions, and a grouped stretch is
    spelled, so it is non-full).
  - D-hors: `_Static_assert(MF_MAX_SPAN_POS < 256)` is replaced by a shift
    capped at 255. A shorter shift is safe, and the table is unchanged at
    every window of 255 or fewer positions.
- `d27_frame.c`: its own `KPOS` 32 (a kase is copied by value).
- S526: back to its pre-k382mech DETECTED shape (C14 stride). Lowering
  `MF_MAX_TERM` no longer lowers the span bound. It has NOT been re-measured
  by mech.

The commit does not build on `lane/memfn-span4k` alone: pcrec's `known.c:347`,
`known.h:27` and S1131 read `MF_MAX_SPAN_POS`, and covs2afix's A1 removes all
three.

## Readers changed

Found by grep for every changed name (`proven`, `mf_ask(`, `mf_wdecide(`, `->set[`/`table_ref` writers, `plan_test`, `MF_MAX_FWD`, `MF_WREACH`, `MF_WPLAN_MAX`, `MF_WSPAN_POS`, `MF_MAX_SPAN_POS`, `pcrec_memfn_wspan`).
- Kit: `memfn/src/compose.c` (`term_prove` :380, `kit_last_stated` :394, `kit_proof_open` :412, `kit_proof_close` :452, `kit_class_same` :461, `kit_class` :472, `ask_sel` :1155, `mf_rows_need` :1201, `mf_ask` :1215, `define_sel` :1235 and its MF_TRACE re-ask ~:1378); `memfn/src/kit.h` (`kit_proof_st`, prototypes, ~:600-630); `memfn/src/window.c` (above, plus `wf_plan_class` :3957, `wf_stated_offsets` :3988, `wf_agree` :2901 deep compare); `memfn/src/presence.c` (7 casts widened, :187-262); `memfn/src/formhash.c` (`fh_work.sp_set/sp_table`). `gate.c:627` (`j < MF_WSPAN_POS`) is a clamp, still true, unchanged.
- pcrec: listed in Pieces (memfn_sites.c/h, known.c, emit_dfa.c).
- Tests:
  - Kit tests: `tests/memfn/proof_meta.h`, `proof_run.c`, `proof_check.c`,
    `proven_check.c`, `mass_check.c`, `run_decide_check.c`, `arm_fixtures.c`,
    `d27_frame/d27_frame.c`, plus the R-short witness in `run_proof.sh`.
    `d27_frame.c` retires the `plan_test` past-nplan check (a counted list has
    no past) for `plan_test_range`, and its whole-reply memcmps become deep
    compares (`rsame`/`rsame_n`).
  - G2: `memfn/tests/g2/g2_win.h` (`G2W_NPROOF` gone, `g2w_site.nproof`),
    `g2_win_gen.c` (`rows_for`, `wreply_same_n`, `class_same`, past-nplan check
    retired, `to_kit` points at G2's own lists), `g2_win_run.c`,
    `g2_pres_gen.c`.
  - Probe: `docs/design/memfn/span_pick/probe/probe.c`, which
    `run_link_checks.sh` compiles.
- Plants re-anchored, intent unchanged:
  - `run_proof.sh` S1224;
  - `memfn/tests/run_g2_win.sh` S1407 and S3092;
  - mech S1018, S1083, S1148, S1224, S3086 and S3097.
  - Every mech row's anchor count was compared against `a66bf0877` (1,307
    rows). Only these six moved. S3083 and S3094 were kept by keeping their
    line.
- Design-tier doc readers, FLAGGED, not edited (stale sentences, not contract
  breaks, r45_reply.md §5 (h)):
  - `docs/design/kit_proof.md` (35 hits, e.g. `:781-782` the old
    `MF_MAX_FWD`/`proven[]`);
  - `docs/design/cover_cap.md` (21);
  - `docs/design/memfn/span_runs_sheet.md` (7);
  - `docs/design/ctx_span.md` (4, e.g. `:263`, `:1429-1433`);
  - `docs/design/memfn/window_site.md` (4);
  - `docs/design/memfn/part_d.md` (3);
  - `docs/design/stream/approach.md` (2);
  - `plan_frame.md`, `window_contract.md`, `run_pos_set_stage3_readiness.md`
    and `docs/dev/kvcensus.md` (1 each).
  - The historical probes `docs/dev/kvcensus/kvprobe.c:103` and
    `docs/dev/lanes/r33_sim/probe.c:106` call the old `mf_ask`/`mf_wdecide`.
    Nothing builds them.
  - `docs/spec/` has none (D80: no caller-observable change, no spec hunk).
- Docs updated: `memfn.h` comments, `memfn/include/CLAUDE.md` (MF_CLASS_V 11,
  MF_SITE_ABI 30), `memfn/CLAUDE.md` (stack peak re-read), and
  `memfn/docs/journal.md`.

## abi

- `MF_SITE_ABI` 29 -> 30 and `MF_CLASS_V` 10 -> 11: kit-contract events, both
  in this branch. `MF_VOCAB` is unchanged.
- pcrec `abi` is unchanged: there are zero movers (below).
- The held child moves no number of its own. It is MF_SITE_ABI 30's raise,
  unreleased.

## Validation

- `make` and `make strict` are clean on each commit.
- Identity: `scripts/emit_sweep.py --ref a66bf0877 --bin build/pcrec`, 7,071
  argv patterns and 465 composition files, 22 streams, **0 movers**. It ran
  twice: at `97c49ee4b` (plan B plus the working state) and at `52ee04995`
  (after `MF_WREACH` 4096).
- Plan-B tip `52ee04995`:
  - `make test-codegen`, `test-registry`, `test-rxtsource` and
    `test-memfn-link` rc 0. The R-28 peak is `wf_parts_prepare` 3,488 B, then
    `kit_class_same` 3,312 B, both under 4 KB.
  - `test-memfn-g2`: 70,358,672 passed / 0 failed (window, traced window and
    presence families included).
  - `test-memfn-finder` rc 0.
  - `test-memfn-d27frame`: 6,937,301 checks, 0 failed, floors held; the
    control and empty runs go red.
  - `memfn/tests/run_g2_win.sh --plants`: 38/38 RED. S1400's red is "does not
    compile warning-free", as before this lane.
  - `tests/memfn/run_proof.sh --plants`: S1221, S1224, S1225, S1419, S1408 and
    S3242 RED.
  - `tests/memfn/run_arch_blind.sh`: 17/0.
  - No `*** [test-...] Error` line in any log.
- Earlier tips (the same code, before the reach raise):
  - `test-memfn-g2`: 70,358,672 passed / 0 failed.
  - `test-memfn-finder` rc 0.
  - `test-memfn-d27frame`: 6,937,301 checks, 0 failed, floors held; the
    control and empty runs go red.
  - `run_g2_win.sh --plants`: all 38 RED.
  - `run_proof.sh --plants`: S1221, S1224, S1225, S1419, S1408 and S3242 RED.
    S3242 is red by its message: "A accept span 0 BOUNDED: refused:
    mf_define: the proof range ends before the statement's following offset".
  - `tests/memfn/run_arch_blind.sh`: 17/0.
- Mech, the re-anchored and window rows: S1018, S1148, S1224 and S3097
  DETECTED (`f4ccc3d28`); S1083 DETECTED (memfnfinder 6 failed); S3083, S3086
  and S3094 DETECTED (`97c49ee4b`). No anomaly remains (S1083's first plant
  left a dangling `else`, fixed to `if (0)`).
- Held child, validated per R2 in the scratch detached worktree
  `worktrees/span4k-try`:
  - The tree was plan-B tip `52ee04995` merged with `lane/covs2afix`
    (`7983d4798`); 5 doc/tsv conflicts were taken from our side, for the
    build only. Then `0234da0e9` was cherry-picked.
  - `make strict` clean, `make test-codegen` rc 0.
  - `emit_sweep --ref` the unraised merge `f3b6f1756`: 22 streams, **0
    movers**.
  - The worktree was removed with `scripts/wtprune --apply --force`.
  - OWED to the combined branch: its suites beyond codegen, and mech S526.
- Not run (per the brief): full `make test`, box-queue jobs, timing and cloud.

## STATE AT HANDOFF

- Branch `lane/memfn-span4k` at its tip; the lane commits this report there.
  Child `lane/memfn-span4k-raise` = one commit on the plan-B tip, NOT merged
  (R2). Main takes it on the combined branch after covs2afix.
- Rulings file: last entry applied is **R2**. R1 and R2 are both applied.
- Witness row (b) WAITS-ON main's B5. It is not a lane debt (R1).
- OWED: none
