# d27fix — the D27 author's findings on kit 3.0b's framed ask (lane d27fix, opus, 2026-11-13)

Branch `lane/memfn-d27fix`, base main 32514791a. Charter:
`/var/tmp/pcrec-pcrec/scratch/memfn/s1owed/d27author/findings_and_rulings.txt` (the kit manager's rulings on D27 author
s1d27's findings F1-F5 and ambiguities A1-A7). The contract is `docs/design/memfn/plan_frame.md` §2.2-§2.3 and
`memfn/include/memfn.h`.

## Summary

Lane d27fix fixed the four kit defects (F1-F4), wrote the spec text for F5 and A1-A7, and adopted the author's
tests as the kit family `tests/memfn/d27_frame/`. The family is wired into `make test` as `test-memfn-d27frame`,
quick tier plus control and empty runs, and has an opt-in full tier, `-full`.

- **Kit fixes:** `memfn/src/window.c`, plus a shared predicate in `memfn/src/kit.h` used by `generic.c`. Five new
  sabotage rows, S3120-S3124, one per fix, all red by hand. They are detected by a new mech arm, `memfnd27frame`.
- **ABI:** no reply-struct change and no reader of `plan_test` outside the kit's own tests, so there is no
  MF_SITE_ABI move. It stays 28.
- **Emitted bytes:** none move. pcrec states no lever, and the fixes change only replies and refusals. Box gate
  job `kit-d27fix-gate` proves it, queued as the lane's last act.
- **Not a ruling:** one driver change, N1 below, is the adopting lane's own reading. It is flagged for the kit
  manager.

## Findings and fixes

| finding | root cause | fix (window.c unless named) |
|---|---|---|
| F1 | `translate`'s pinned-run ranking used the art's run options, which carry the `run-tie-left` lever. A verify-NO member deliberately ignores the lever: `run_member` takes the stretch row's tie (`KIT_RUN_EXACT_AROUND`, plan_frame §2.5). So under the lever, ranking and member disagreed on a tie, and the loud RQ-2 check fired. | `member_opts(d, r)` (:932) is the one home of the member's options. A PINNED run ranks under its member's tie (:1554), so the lever moves the ranking exactly where it moves the member, K38-1's RQ-2 ruling. Separately, `wdecide_framed` turns any set art error into -1 with a zeroed reply: never 0 with the error set. |
| F2 | The EMIT ask asked only the define half. `mf_emit`'s use refuses a NOP ASSIGN with a stated `result_decl` on the statement frames. | `emit_use_refused` (:2614) over a declared row list `nop_decl_rows` (E-find, the floor, `generic`). The predicate `kit_nop_decl` (`kit.h` :208) is shared with the two renderers that refuse, `generic.c` :427 and window.c :3304, so the ask and the refusals cannot drift apart. |
| F3 | `mf_emit` places no `mf_locals` between its define and its use, so a `decl_point` 1 site always refuses at the use. The ask answered 0. | Under EMIT, `decl_point` 1 answers -1 (:2642). |
| F4 | `plan_test` followed the C-table rule alone. A position E-find tests inside a run compare (C-run's group, `grp`) reads no table. | `test_of` answers TABLE only where `grp[k] < 0` (:2499); the MF_TRACE agreement's held reply reads the same (:2770). `stop_test` keeps the C-table-only reading, since the find tests the stop. Readers of `plan_test`, by grep: window.c's agreement, `memfn/tests/g2/g2_win_gen.c` and `tests/memfn/arm_fixtures.c` (purity). There are none under `src/`, `cli/` or `lib/`, so there is no ABI move. |
| F5 | spec only | §2.3 observable table (below). |

**The agreement and EMIT.** The traced agreement (`wf_agree`) re-asks at the define. It now asks with `use` 0, the
define half only, because the use refusals happen after the define, at `mf_emit`'s use.

**Re-aimed existing checks.** Each still detects its fault at the new code:
- S3006 (rank asks the member directly) is re-anchored to the one-line `kit_run_decide(d->rate, ro, ...)` call.
- G2 plant S3096 is re-aimed to the stop's C-table-only line.
- The purity row `+C-member(verify-NO)` is re-anchored.
- `g2_win_gen.c`'s plan_test rule accepts OWN at grouped positions.

## Spec text

- **`docs/design/memfn/plan_frame.md`:**
  - A status-block note says the lane's text is marked `[d27fix Fn]`/`[d27fix An]` and replaces older text it
    contradicts.
  - §2.2 contract line 2: A1 (sink-capability refusals excluded; the ask assumes a full sink) and F2/F3 (EMIT
    includes the use half: `decl_point` 1, and the NOP-ASSIGN-declared refusal on E-find/floor/`generic`).
  - Line 4's range list names `decl_point` 1 under EMIT (F3).
  - The Purity paragraph drops the layer (A5: the reply describes the OFF variant). The fenced defect path answers
    -1, never 0 with the error set (F1, A3), and the lever's green reach to that path is closed (F1).
  - §2.3's plan_test rule gives OWN inside a run compare (F4). `stop_test` uses C-table's rule alone (F4) and is
    NONE on E-generic (A2).
  - The observable table covers FN on E-func as `<fn_name>`/`<fn_name>__body` (F5); the run-compare OWN, the HORS
    skip's one verified position (A4) and the pinned stop's offset; and stop_test's text checked only on WALK
    (A7).
  - `mismatch_inplace` is spelled as the trace spells it, three places (A6).
  - §4.1: the agreement's re-ask is the define half (F2, F3).
- **`memfn/include/memfn.h`:**
  - `mf_wreply`'s `plan_test`/`stop_test` doc follows F4/A2.
  - The `mf_wdecide` -1 causes list gains the poisoned art (A3), EMIT's `decl_point` 1 and the use refusals, and
    the sink exclusion (A1).

## The adopted family

`tests/memfn/d27_frame/` was adopted verbatim in fbe34357e, then changed only where a ruling changes a reading. Each
change is logged in its CLAUDE.md table:

- (a) `rule_plan_test`: on E-find a shared-`plan_term` position may answer OWN; the text checks decide which (F4).
- (b) Population `plan_test_TABLE_in_run_compare` renamed `_shared_term`, with new population
  `plan_test_OWN_offered_in_run_compare`. Floors re-measured: 3400/110/340/1420 from minima 3783/122/377/1580 (F4).
- (c) `obs_plan_test_own_text` allowances: the stop's offset whose offer the find reads, and one D-hors probe offset
  (F4, A4).
- (d) **N1, not a ruling, for the kit manager:** `facts_at` on a PARKED alternative with reseed 0 meets the
  verify-YES spans only. This fixed one seed-3 case, 17342, that predates this lane's kit changes. The author's
  reading met every span. Ask the kit manager to rule whether the reply's PARKED meet is correct as the kit renders
  it.
- (e) New check `no_fenced_defect_refusal`: no define/emit refusal text contains "run ranking" (F1). It is the
  detector for S3120/S3121.

**Wiring:**
- `tests/memfn/run_d27_frame.sh` runs the quick tier (gcc -O2, seeds 1-3 plain plus seed 1 traced) with a passes
  floor of 6,500,000. It then runs the control, which must be red in all 4 runs with no silent family, and the
  empty run, which must break floors in all 4 runs.
- `make test-memfn-d27frame` is in TEST_SECTIONS after d27region. `make test-memfn-d27frame-full` is the opt-in
  full tier: gcc, clang, gcc ASan+UBSan, floor 19,500,000.
- CI shard table row: shard 11, ESTIMATE 90 s.

**Runtime and cap.**
- Quick section: about 1 min on the dev box (7700X), about 15 s of it driver time.
- Full tier: 1m39s.
- Parallelism cap: 1, a serial driver.

**Verdicts:**
- Full tier: 20,709,012 passed, 0 failed, floors held. This run predates check (e).
- Quick tier with (e): 6,983,024 passed, 0 failed.
- Control: 45/45 families red in each plain run, 50/50 traced.
- Empty: floors broken in all 4 runs.

## Part D overlap

Lane partd (Part D, `part_d.md` §2.1 item 3, the F26 direct translation) moves `translate`'s RQ-2 ranking into a
shared function, which still ranks "with the art's tie (the lever included)", and keeps translate's member check
for family sites.

That is exactly the reading F1 found wrong for PINNED runs. When Part D lands on this fix, the shared function must
take the run options (`ro`) from its caller, and the pinned caller passes the member's tie (`member_opts`).
Otherwise F1 returns.

Three things re-target there with it:
- S3006's anchor.
- S3120, whose plant removes the `if (d->pinned) ro.tie = ...` line.
- S3121's second file.

Sabotage ids: Part D's branch holds S3100-S3119, so this lane took S3120-S3124. Neither branch's rows collide.

## Identity and movers

No pcrec emitted byte moves:
- pcrec states no lever, so F1's ranking is unchanged without one.
- F2-F4 change only replies and refusals of the ask. The define path refuses nothing new, because the use refusals
  sit at `mf_emit`'s use as before.

The proof is box gate job `kit-d27fix-gate`
(`/var/tmp/pcrec-pcrec/scratch/memfn/d27fix/593-kit-d27fix-gate.sh`). It runs emit_sweep with BASE 32514791a and REF
the lane's code tip (named in the job), both built FRESH from `git archive` in the job's scratch, over 71 arms: the
67 declared identity arms plus 4 CPU-target arms, with tgt-generic checked as generic == plain. Movers declared:
none. Its verdict is owed (below).

## Checks

All validation ran in the worktree on the dev box, under `nice`.

| check | verdict |
|---|---|
| `nice make -j8` | green |
| `make strict` | green (20 s) |
| `make test-codegen` | first run RED, TT-9: the new `tests/memfn/run_d27_frame.sh` was in neither sanitizer list. Fixed: added to `tests/lib/san_excluded.txt` as NO-C-RUN, the same shape as `run_d27_region.sh`. Rerun green: 0 failed, 21/21 scripts, 211 s |
| `make test-memfn-arch` | green (9 s) |
| memfn quick families: finder (purity reach with the re-anchored row), arms, rows, rank, forms, reach, stamps, link, deleg, manifest, targets, d27region | all green |
| `make test-memfn-d27frame` (new) | green, 57 s |
| `make test-ci-shards`, `test-claudemd-size` | green |
| `python3 -I scripts/m6read_check_sab_anchors.py` | green, all 1280 rows' anchors resolve |
| `CLAUDEMD_ROOT=<worktree> scripts/check_claudemd_size.sh --all` | green |
| G2 window family (`memfn/tests/run_g2_win.sh`) | plain 11,266/0, traced 5,670/0; plants S3093, S3096 RED |

Sabotage rows S3120-S3124 (`SAB_SUITES="memfnd27frame"`), each planted by hand and run through the quick tier
(`scratch/memfn/d27fix/plants.sh`), all red:

| row | fault | checks failed (first families) |
|---|---|---|
| S3120 | pinned rank ignores the member tie | 71: ask_sets_no_error, no_fenced_defect_refusal, refuse_iff_define_refuses |
| S3121 | framed ask answers on a poisoned art (+ the tie line) | 101: + poisoning_ask_answers_refusal |
| S3122 | EMIT ask ignores the NOP decl | 952: refuse_iff_emit_refuses |
| S3123 | EMIT ask admits decl_point 1 | 411: refuse_iff_emit_refuses |
| S3124 | run compare answers TABLE | 2410: obs_plan_test_table_text_runcmp, trace_no_internal_error, ... |

G2 window: plain 11,266 passed / 0 failed; traced 5,670 / 0. G2 plants S3093 and S3096 still RED. The mech matrix's
own run over the rows is owed to the cloud (mechrows).

## Owed runs

- Box gate job `kit-d27fix-gate`: emit_sweep, BASE 32514791a vs REF the lane's code tip, both fresh git-archive
  builds, 71 arms, no movers declared. Queued; verdict unread by the lane.
- Cloud `make test`, `test-axes`, `ubsan`, `asan` on the lane tip.
- Cloud mechrows over S3120 S3121 S3122 S3123 S3124, plus the re-anchored S3006 (arm `memfnd27frame` is new; the
  by-hand plants above are the lane's evidence until then).

The cloud kinds are left for the kit manager to dispatch (the lane never pushes).

## STATE AT HANDOFF

OWED: kit-d27fix-gate (box); cloud test, axes, ubsan, asan; cloud mechrows S3120 S3121 S3122 S3123 S3124 S3006

Code complete and committed. The deliver file's `owed:` line was `any`, which lanecheck reads as a queue key; the
lane changed it to `kit-d27fix-gate`, the key the brief names (its own commit). For the kit manager: rule N1
(the adopted family, driver change (d)).

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| F1 fix: ask and define both succeed under the lever; ask never 0 with the error set | window.c `member_opts` + pinned tie, err guard; S3120, S3121 |
| F1 root cause, Part D overlap reported | sections above |
| F2 fix: EMIT ask refuses the NOP-decl use | `emit_use_refused`, `kit_nop_decl`; S3122 |
| F3 fix: EMIT refuses decl_point 1; line 4 names it | window.c :2642; plan_frame line 4; S3123 |
| F4 fix: OWN inside a run compare; readers grepped; ABI decided | `test_of` + agreement; readers kit-only, no MF_SITE_ABI move; S3124 |
| F5, A1-A7 spec text; memfn.h -1 list (A3) | plan_frame.md (tags `[d27fix ..]`), memfn.h |
| adopt tests as tests/memfn/d27_frame/, quick tier in make test | fbe34357e verbatim; `test-memfn-d27frame` |
| driver changed only per ruling, each logged | d27_frame/CLAUDE.md table (a)-(e); N1 flagged as NOT a ruling |
| green with floors; control and empty red | Adopted family verdicts above |
| runtime and parallelism cap named | ~1 min quick section, 1m39s full; cap 1 |
| sabotage row per kit fix, next free ids, arch-free prose; make test-memfn-arch | S3120-S3124; test-memfn-arch in Checks |
| gate job: emit_sweep vs fresh git-archive base, BASE/REF named, queued last | 593-kit-d27fix-gate.sh; queued |
| validation list | Checks |
| report sections, OWED line, CLAUDE.md files, history index | this file; tests/memfn, d27_frame CLAUDE.md; history index entry |
