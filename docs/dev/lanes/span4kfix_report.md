# span4kfix — R-45 plan B: the ruled code-round fixes and the re-cut raise

Lane span4kfix (opus), 2026-11-16, for the kit manager. Branch `lane/memfn-span4k`
(worktree `worktrees/span4k`), from tip `a9d13217c`. Review:
`docs/dev/reviews/2026-11-16-r27-memfn-span4k.md` (its RULED block, 14:45). Rulings
applied: `span4kfix_rulings.md` R1 (AX-1).

## Summary

Every FIX-NOW id of the ruled review is on plan B. Every DOC id is too. So is
ruling R1 (AX-1). Plan B is still at **0 movers**: the byte and utf8 corpora
compile the same as at `a9d13217c`. No emitted byte moved, so pcrec's `abi` does
not move. The kit's MF_SITE_ABI and MF_CLASS_V do not move either: no struct and no
signature changed in `memfn.h`, only comments.

The fix that matters most is SEAM-1. Before it, a refused ask could leave the
caller's rows half written. Now every check is made before the first write. Four
new sabotage rows (S3250-S3253) each plant one violation of a new header clause.
All four are DETECTED.

The raise is re-cut as ONE commit on `lane/memfn-span4k-raise`, over the final
plan-B tip. It carries READ-1, the kit's declining row. It has an in-tree witness:
a purity fixture at 33 positions, and sabotage row S3254 (DETECTED). On the combined
approximation tree (plan B + `lane/covs2afix` + the raise), runs of 33, 100 and
4095 positions are refused cleanly under ASan+UBSan.

## Fixes by id

- **TRI-1 / HOUSE-5** (`60b4662b5`): `wf_stated_offsets` (memfn/src/window.c) now
  counts on a stack bit set of `MF_WPLAN_MAX` bits. It has no heap allocation and
  no NULL path, so `mf_rows_need` is PURE, as declared. The alloc_check population
  absorbs 0: W1, W2, W3 and W4 are all diagnosed, and W5 passes.
- **MEM-1** (`36f30f724`): the plan's compare index is `uint16_t` end to end:
  `wf_dec.pterm`, `c_run`'s counter, and its allocation, which is sized by
  `sizeof`. A `_Static_assert(MF_WPLAN_MAX <= UINT16_MAX)` holds the width. The
  witness is a driver only (301 plan rows, no shared non-adjacent index). There
  is no in-tree row.
- **SEAM-1 (+ MEM-2 b/c, HOUSE-1)** (`4d00fccfe`):
  - The new `rows_hold(d, rows, framed)` makes every row-capacity check before any
    write.
  - `reply_of` and `reply_frame` are void and are called only after the checks.
  - The framed and NONE paths of `mf_wdecide` are now plain statements.
  - `wf_agree` reads `rows_hold`.
  - `ask_sel` (compose.c) checks presence and layout on the verdict before the
    proof is written.
  - The ALL_PRESENT `-1` zeroes `*out`.
  - Under MF_TRACE, an out-of-memory re-ask now has its own message.
- **HOUSE-2** (`4d00fccfe`): `proof_min_end` is now the one spelling of the
  minimum. Both `mf_rows_need` and kit_proof's R-short read it.
- **CHECK-2/3/4** (`ad5a89b26`):
  - Purity and d27_frame now fill every ask's rows with a 0xA5 sentinel first.
    - A refused ask must leave the sentinel untouched.
    - An answered ask's lists must be the caller's rows.
  - The deep compares now always compare contents, with no pointer-equality
    shortcut.
  - CHECK-2: a NONE reply must carry `plan_test == NULL`.
  - A new refusal fixture covers three cases:
    - a framed ask with no `plan_test`;
    - `plan_cap` one short;
    - `proof_cap` one short.
  - S1018, S1224, S3064 and S3086 are re-anchored to the SEAM-1 text. Their intent
    is unchanged, and all four are re-run DETECTED.
- **New sabotage rows** (`4afc8adbc`, `1a9590764`), one per new clause:
  - S3250: the framed ask writes rows, then refuses.
  - S3251: the NONE reply carries `plan_test`.
  - S3252: the reply's lists are in kit storage.
  - S3253: an R-cap refusal writes rows.

  The cloud mech shard table is regenerated to hold them (`1775d48c9`). It was made
  with `--measured --slots 30 --waves 3`. `cloud_mech_check` passes with 1311 ids.
- **EMIT-1 = READ-4** (`14a0b0c2a`): B5's compare loop (`pcrec_cover_proof_diff`,
  src/gen/known.c) is now bounded by the count, `max(LO + proof_n, k + 1)`,
  clipped at `MF_MAX_FWD`. It no longer runs to `MF_MAX_FWD` itself.
- **SEAM-2** (`14a0b0c2a`): `pcrec_memfn_rows` takes a `PcrecRowsPart`
  (PROOF / PROOF_CEILING / PLAN) and allocates only that part. The callers in
  emit_dfa.c and known.c name the part they read.
- **HOUSE-4** (`14a0b0c2a`): `pcrec_memfn_wspan` refuses a length outside
  `0..MF_WSPAN_POS` through `pcrec_ctx_fail`. It does so before it sizes or casts
  anything. The two comments in known.c (`cc_fits`, `cover_window`) are respelled.
- **SEAM-3 = READ-5** (`69a32a7bf`): a supersession note on the retired carrier
  in each of these:
  - window_site.md
  - plan_frame.md §2.2 (and its `plan_test` row)
  - window_contract.md
  - kit_proof.md (its table and §4.2)
  - run_pos_set_stage3_readiness.md
  - span_arms.md
  - docs/dev/kvcensus/kvdfa.py
- **SEAM-4** (`69a32a7bf`): new header comments in memfn.h:
  - `mf_rows_need` is PURE. It has a `max(1, ..)` floor, and its answer suffices
    but is not exact (see Validation).
  - `mf_ask` writes nothing to rows when it returns -1.
  - `mf_wdecide` refuses a NULL list.
  - The proof is defined on the proof rows.
- **SEAM-5** (`69a32a7bf`): MFTRACE `ASK` now carries `proof_n=N`, recorded in
  memfn/docs/trace_format.md "The ask (mf_ask)".
- **SEAM-6 / MEM-3 residue** (`69a32a7bf`): one header line each, on `mf_defined`
  (the art owns its counted list) and `mf_ask`.
- **Review copy** (`d919af327`): the review is copied unchanged to
  `docs/dev/reviews/2026-11-16-r27-memfn-span4k.md` (+ dir) and indexed.
- **AX-1, ruling R1** (`910765545`): `docs/dev/lanes/r33_sim/probe.c` `wr_json` now
  passes caller storage to `mf_wdecide`, with 6 args, as
  `tests/memfn/run_decide_check.c` does. The proof is in Validation
  (`make test-memfn-d3floor`).

  **Census of tree-wide callers** of the changed seam signatures, from
  `git grep` over the whole tree:
  - `mf_wdecide` / `mf_ask`: src/gen (emit_dfa.c 7, known.c 1); memfn/tests/g2
    (g2_pres_gen.c, g2_win_gen.c); tests/memfn (arm_fixtures, d27_frame,
    proof_check, proven_check, run_decide_check);
    docs/design/memfn/span_pick/probe/probe.c; docs/dev/lanes/r33_sim/probe.c;
    docs/dev/kvcensus/kvprobe.c.
    - All are at the new arity except two.
    - r33_sim/probe.c is fixed here.
    - kvprobe.c is still 4-arg. It is also stale on older fields
      (`mf_pred.window_stated`, `move_back`, retired before this branch), so it
      does not build on plan B's base either.
    - kvprobe.c is LEFT UNTOUCHED: no build or suite reads it, and an arity fix
      alone would not make it build. It is listed for the kit manager.
  - `pcrec_memfn_rows`: src/gen only (emit_dfa.c 7, known.c 1, memfn_sites.c/h),
    all updated with SEAM-2.
  - `mf_rows_need`: compose.c, memfn_sites.c, g2_pres_gen.c, g2_win_gen.c,
    arm_fixtures.c, d27_frame.c, span_pick/probe.c. Its signature is unchanged.
  - Every other match is prose (reviews, lane reports, design docs, sabotage
    headers).
- **Not this lane's**:
  - HOUSE-3, MEM-3 and SEAM-7 U2-U5 are PLAN.
  - The design-doc edits for MEM-3, SEAM-6 and HOUSE-3 in `r45_reply.md` §5 are
    OWED to `lane/memfn-r45`. That file is not on this branch. This lane does not
    owe them.

## Raise

`lane/memfn-span4k-raise` is ONE commit over the final plan-B tip. The tip is named
in STATE AT HANDOFF.

**What it carries:**
- The old raise (`2794f4696`, re-applied clean):
  - `MF_WSPAN_POS` goes from 32 to 4095.
  - `MF_MAX_SPAN_POS` and `MF_MAX_AHEAD` are retired.
  - `WF_LEGACY_POS` is retired.
  - The D-hors shift is capped at 255.
  - d27_frame KPOS.
  - S526 is re-aimed.
- **READ-1**, the kit's declining row contract. `run_part_terms` (window.c) refuses
  two kinds of derived run part:
  - a scan stretch of over `MF_RANK_MAX` positions ("a derived run part whose scan
    stretch is over MF_RANK_MAX positions (its ranking has no spelling)");
  - more than `MF_MAX_TERM` terms ("a derived run part of more than MF_MAX_TERM
    terms").

  Both refusals come before any ranking entry or term is written. The
  `MF_WSPAN_POS` comment names this row.
- **The witness** (arm_fixtures `pur_long_run_fixtures`): an ALL_PRESENT presence
  RUN span with its derived run part. At 32 positions it defines. At 33 it must be
  refused by the stretch rule, named in the error. Sabotage row **S3254** removes
  the stretch rule. It is DETECTED (memfnfinder 3 fail).
  - Planted by hand with both rules removed, the fixture goes red too. The define
    then fails later, at `rank_n > MF_RANK_MAX` in the translated vocabulary. It
    is not the stretch refusal.
  - So the later check refuses AFTER `run_rank` has already written past
    `rank_pos[MF_RANK_MAX]`. That is the review's READ-1: a write past the
    arrays at 33 positions, past the heap block at 100 or more. Without the
    stretch rule, the define still refuses, but only after memory is corrupted.
    The fixture tells the two apart by the error text.

**On the combined approximation tree** (`worktrees/span4kfix-try`): the fixed
plan-B tip (`d919af327`) + `git merge lane/covs2afix` + the raise. Two conflicts
were resolved:
- known.c `cc_fits`'s comment: covs2afix's text, with this lane's no-overrun
  sentence.
- Docs/index files: taken from covs2afix.

Results:
- `make` builds clean. `make strict` is clean. `make test-codegen` passes.
- The purity fixtures: 13270 passed, 0 failed.
- S3254 DETECTED. S526 (re-aimed) DETECTED (memfnforms 1 fail).
- The review's `verify/longrun.c` under `-fsanitize=address,undefined`:
  - 32 positions: defines.
  - 33, 100 and 4095 positions: refused by the stretch rule, with no sanitizer
    report.
  - A many-byte variant: defines at 20 and 31; at 33, 40 and 70 it is refused by
    the term rule.
- Movers against the unraised merge, with 18 long-run patterns added to the
  review's corpus/edge/hand lists:
  - byte: 0 movers (277 SAME, 3 BOTHFAIL).
  - utf8: 0 movers (276 SAME, 4 BOTHFAIL).
  - At `--window-search-width=4095`: 22 DIFF and 1 RCDIFF. All are runs of 20 or
    more positions now admitted. Expected: that is the raise doing its job under
    a caller who widens the window. The RCDIFF is `[0-9a-f]{4095}`.

**What the raise needs from MAIN** (main's half, same landing, on main's combined
branch; not built here):
- **READ-2**: the per-bound asserts for other-sites-at-32 (`req_pres_spans`,
  `pf_window_of`), and a pcrec name for the reach-64 bound.
- **CHECK-1**: a BUILD-REFUSED witness row for the emit_dfa.c K38-2 assert. After
  the S526 re-aim, that assert has no witness.
- **READ-3**: main's stage 2 (PLAN).

## Validation

Box: dev box, gcc 15.2, `nice`, -j4. There was no full `make test`, no queue job
and no timing.

- **Plan B** at `d919af327` (the fix commits; later commits: the shard table, the
  AX-1 probe, the purity re-pin):
  - All exited 0: `make strict`, test-codegen, test-registry, test-rxtsource,
    test-resource, test-kitproof, test-spec-history, test-claudemd-size,
    test-doc-lint, test-memfn-link, test-memfn-manifest.
  - Also exited 0: test-memfn-g2, -stamps, -arms, -deleg, -arch, -forms,
    -reach, -targets, -rows, -guarded, -simdfloor, -d27region, -d27frame,
    -rank, and run_arch_blind.
  - The verdict is make's `*** [..test-X] Error` lines. There is ONE: test-memfn-finder
    (see the purity pin note below).
  - test-resource: 42 checks pass. The allocation-failure injector's four
    witnesses hold: nothing is silently absorbed.
- `fx --purity`: 13268 passed, 0 failed.
- `make test-memfn-d27frame`: PASS, 8564177 checks.
- Anchors: all resolve (1311 rows).
- **Sabotage rows**, all DETECTED:
  - S3250: memfnfinder 21 fail.
  - S3251: 21 fail.
  - S3252: 4583 fail.
  - S3253: 13 fail.
  - S3086: 1889 fail.
  - S1018: 2469 fail.
  - S1224: 203 fail.
  - S3064: g2pres 52448 fail.

  The memfnfinder rows were re-run after the purity re-pin (`33e389ccf`), and all
  are still DETECTED.
- **0 movers** against `a9d13217c`: byte 259 SAME / 3 BOTHFAIL, utf8 258 SAME /
  4 BOTHFAIL.
- **AX-1**: `make test-memfn-d3floor` exits 0 on `33e389ccf`. It builds the
  traced r33_sim probe.
- **Notes:**
  - `mf_rows_need` over-asks on translated routes. Purity sites 2, 3, 7, 8 and 10
    answer with `proof_n` 10-11 where the need is 12-13. The refusal fixture
    accepts both outcomes. The header now says "suffices", not "exact".
  - The alloc_check populations are higher than on main (W1 2523 vs 861). That is
    plan B's per-extent working state; none of them is absorbed.

- **test-memfn-finder** was RED at `d919af327`: its EXACT purity pin read 7874,
  but the run made 13268 checks. That count is the CHECK-2/3/4 checks this lane
  added (the base `a9d13217c` reads 7874). The pin is raised in `33e389ccf`, with
  its reason in the comment. On `33e389ccf`, `make test-memfn-finder` exits 0.
- **The raise does not build on plan B alone**, by design. As with the old raise,
  plan B's known.h/known.c still read `MF_MAX_SPAN_POS`, and `lane/covs2afix`
  removes those reads. So the raise is validated only on the combined tree. On
  the combined tree rebuilt on the final fix tip (`33e389ccf` + covs2afix + the
  raise):
  - `make`, `make strict`, `make test-codegen` and `make test-memfn-finder` all
    exit 0, with purity at 13270 == 13270.
  - S3254 and S526 are DETECTED.

## STATE AT HANDOFF

- plan B: `lane/memfn-span4k` tip = the commit that adds this report. Its parent,
  `33e389ccf`, is the last fix. The kit manager's reply names the hash.
- raise: `lane/memfn-span4k-raise` is ONE commit whose parent is that plan-B tip.
  The reply names the hash.
- rulings: R1 (AX-1) applied; last applied R1
- `worktrees/span4kfix-try` removed (wtprune --force)
- OWED: none
