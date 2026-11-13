# Lane b30b report: memfn plan_frame.md 3.0b, the seam with pcrec's asks

Lane b30b (opus), branch `lane/memfn-b30b`, cut from main a9fc6dbd8. Frank's build GO 2026-11-12.
Design of record: `docs/design/memfn/plan_frame.md` §5 3.0b, with the [s1d], [r1s1] and [r2s1]
revisions, §7 Q14-Q16, the two review Rulings sections, and D190.

## Summary

3.0b is built. `mf_wdecide` now takes the frame: the define hooks `def` and the CALL `mf_wcall`.
NONE answers the decision group only. DEFINE and EMIT also answer the frame part, which
`mf_define`/`mf_emit` would render. UNSTATED and every call above EMIT are refused. `mf_wreply` gains its
frame part, appended LAST: `framed`, `frame_row`, `method`, `search`, `stream`, `fused`, `plan_test[]`
and `stop_test`. MF_SITE_ABI goes 27 -> 28. MF_CLASS_V stays 9.

The kit holds an MF_TRACE AGREEMENT at every window define (`compose.c` `define_sel`, `window.c`
`wf_agree`). It re-derives the decision group through `decide`, builds the frame part from what the define
STORED (§4.1's field map), and compares the whole reply with `memcmp`. On a mismatch it refuses the
define, naming the first differing member.

pcrec's phase-1 callers ask framed or unframed as designed:
- ASK-1, `window_reply_ask`: FUNC, DEFINE.
- ASK-3: the `PCREC_CAND_TRACE` re-ask at `ofs_site_define`, compared whole, `asked-plan-differs`.
- ASK-5: the comments restated.
- ASK-6, `req_run_at`: NONE with no hooks; a refusal now fails the compile (the one pcrec hunk).

ASK-2 is void (K38-2).

The checks:
- The purity harness grew to 7874 exact checks: framed asks interleaved with defines, whole-reply
  memcmp, counting hooks, counting arena, and the call, opts and same-class fixtures.
- It also runs on the MF_TRACE driver, with exact E-func/E-generic define counts.
- G2 asks framed before every window render: (frame_row, stream) cells, text classes, reply-id
  resolution and the `table_name` population, all floored. A traced window-family pass runs against
  libpcrec_mftrace.a.
- A successor census probe has a compile-only check.
- 20 sabotage rows, S3078-S3097, every one shown red by plant. S686 is re-aimed.

No pcrec emitted byte moves: 100 spot compiles over 5 arms were identical to the base. The full
71-arm emit_sweep proof is queued as one box job for after 01:00.

## Built vs designed

Built as §5 3.0b's content, check, plant and sabotage-fate columns say. Where the text left a choice, I
took the reading that keeps every check able to fail:

1. **The agreement re-derives the decision on `ws`**, the define's own window site. On E-func and E-stmt
   the stored site is the legacy translation (`r->site`), which `decide` does not read. The frame part
   comes from the stored record (`site_rec` wplan/arm/fd_row/fn_pick), never through the plan function.
2. **E-stmt's search** is read through the arm-to-pick map (`wf_arm_pick`, the search renderer table's
   E-stmt rows) on both halves. `r->fd_ren` is NULL on a walked PF arm, so the re-base block's
   "`r->fd_ren`'s pick" could not be read there.
3. **A framed ask refuses wherever `mf_define` would refuse before selection**: unstated target,
   policy bits outside the kit's set, part/frame statements, `wf_check(site, 1)`, and denies that are not
   the art's (`framed_refused`).
4. **E-func's `stream`** is `ren_fused[RF_FN].stream`, the fused row's declared stream.
5. **The agreement runs after `row->define`**, because `fn_pick` (E-func's search, the `fn_rows` pick
   column) is written there.
6. **`plan_test`/`stop_test` are NONE on the fused rows** (E-find's B-fn, E-func's offset skip),
   following §4.1's field map and design line 669 ("the fused rows' [check] is their own").
   - G2's class keys on `fused == NO`.
   - It asserts a TABLE marker read only where the position's compare term is its own. A term shared by
     several positions is one byte compare and reads no table (sites 788 and 1274 are the witnesses).
   - It asserts no marker for any OWN position, everywhere.
7. **(U)'s fixture site.** Neither the generic purity sites nor `n = "n - 1"` split DEFINE from EMIT.
   The fixture that does is `pur_pf_site`: one one-byte span on a STMT/ASSIGN site whose miss leaves,
   with an expression-statement `on_miss`. The PF memchr row serves it at DEFINE and declines it at USE
   (its contract: a jump or a braced block). So mf_define renders E-stmt and mf_emit E-find.
8. **(AD)'s population** adds that PF site to the purity STMT sites. The PF row reads `s`, `n`, `lo` and
   `result` as identifiers only, so a gate that reads a spelling beyond its class moves its frame row.
   Every purity STMT site alone is served by rows that accept every class, so AD's plant there moves
   nothing.
9. **The traced purity pass's control**, planted as designed (E-func declined in `e_legacy_holds`):
   - purity stays at 7874 checks, plain and traced, and no define refuses;
   - only the counts move: E-func 81 -> 0, E-generic 8 -> 89.
   So the exact pins are what catch the K35 shape. No fixture edit was needed.
10. **The successor probe's tree argument** is the env var `PROBE_TREE`. The jobs' first argument is the
    boxqueue mode (`--dry-run`/`--ready`), so a positional tree would collide.
11. **purity_rows.tsv's new rows** carry patterns for Table E (`E_*`), the renderer rows (`R[KBSCF]_*`),
    the support rows (`support:PICK`) and Table S (`ST_*`). The control print now also prints each site's
    STMT EMIT replies and the PF site's.
    - 18 of the new rows are REACH.
    - 12 are UNREACHED with reasons. They are picks no purity site makes (WALK, HORS, LIBC_BACK, the
      bounded PF arms); G2's window family carries them. ST-many never holds, by construction.
12. **F's text** (`asked-plan-differs`): mech cannot assert a failure text. So the row's mech verdict is
    the candoracle suite's red. The text was verified by hand at the build: all 11 failing witnesses
    print `CANDORACLE asked-plan-differs`, none a refusal. The row's header records this.
13. **The decider census** gains `wf_arm_pick` and `wf_frame_of` (T-FRAME), and `wf_agree` as excluded
    (it decides nothing). HITS 61 -> 67 and MEMBER_COUNT 67 -> 70, with their reasons in the file.

Not built here (owed, see Owed runs): the D27 spec-first author's seam-contract tests (a cell outside
this worktree), and `reach_equal.py` under the MF_TRACE kit on both layers (a box job).

Also in this lane:
- I changed the manager-written `docs/dev/lanes/b30b_deliver.txt`'s `owed:` field from `none` to
  `kit-b30b-gate`. The brief asks for an `OWED:` line naming the queue key, which `owed: none` forbids.
  lanecheck now checks that the key is named and queued, a stricter check than `none`.
- `memfn/include/CLAUDE.md` was within 5 bytes of its 12 KB limit. Its MF_SITE_ABI 20-22 history moved
  verbatim to `memfn/NOTES.md` (not include/NOTES.md: C16 scans every non-CLAUDE.md file there).
- `tests/memfn/CLAUDE.md`'s purity detail moved to `tests/memfn/NOTES.md` "Purity harness".

## MF_SITE_ABI 28

`memfn.h` MF_SITE_ABI 27 -> 28, with its history entry. The readers were found by grep:
- `memfn.h`'s own comments (FRAME, the reply's doc, the call enum);
- `memfn/include/CLAUDE.md` line 4, which was stale at 25/8 and now reads 28/9;
- the symbolic readers, which recompile unchanged;
- the probe (successor below).

Every other "MF_SITE_ABI 27" hit is a historical "since 27" citation and stays.

MF_CLASS_V stays 9. pcrec's artifact abi does not move, because no emitted byte moves.

The out-of-build reader is `docs/design/memfn/span_pick/probe/probe.c`, R-33's probe successor:
- Its wrappers are declared by `__typeof__` of `mf_art_begin`/`mf_define`/`mf_emit`.
- `tests/memfn/run_link_checks.sh` compiles it `-fsyntax-only -Werror` on every run.
- Control: the predecessor's six-parameter `art_begin` fails with "conflicting types". The predecessor
  `r33_sim/probe.c` no longer compiles against 28, as the design predicted.

The directory holds `probe.c`, `build.sh`, `collect.py` and `sim.py` (copies), and `sweep.sh`/`rp.sh`
(copies of jobs 240/241 with `SIM` this directory and the tree in `PROBE_TREE`). `span_pick/CLAUDE.md`'s
Re-run section names them.

## The pcrec hunk

`src/gen/emit_dfa.c` `req_run_at` (ASK-6):
- It asks the cover site with `MF_WCALL_NONE` and `def` NULL.
- A refusal sets `refused`, and after `done:` restores the trace state, it fails the compile:

      internal error: the memfn kit refused the `@` table's cover-row phase-1 ask (src/gen/emit_dfa.c, req_run_at)

- Before 3.0b a refusal silently dropped the REQ_RUN `@`.
- Plant row (AG) S3097 (`call` 0) refuses every cover-routed pattern with a REQ_RUN run (`zqxzqx`,
  `hello world`, `abc[de]fghij`) and compiles `a.*zqxzqx` (no cover route).

The other pcrec edits are ASK-1 (`window_reply_ask`: FUNC frame, the define's hooks, DEFINE), ASK-3 (the
`PCREC_CAND_TRACE` re-ask in `ofs_site_define`) and ASK-5 (the `wr` comment, naming `req_run_at` among
its readers).

## Sabotage rows

20 rows, S3078-S3097 in letter order. They were free at 07bc1f198; the highest id taken was S3077. Each
was verified red by plant on a scratch copy:
- the fixture rows by `arm_fixtures --purity` plain and traced;
- the G2 rows by `g2_win_gen` against a planted kit;
- F and AG by a planted pcrec.

| id | row | home | detector | measured red |
|---|---|---|---|---|
| S3078 | E | mech, memfnfinder | traced purity (the agreement) | plain 3, traced 2028 failed |
| S3079 | E2 | mech, memfnfinder | traced purity (agreement vs stored record) | plain 0, traced 2025 |
| S3080 | F | mech, candoracle | ASK-3 `asked-plan-differs` | 11/90 witnesses, all that text |
| S3081 | G | mech, memfnfinder | counting hook (table_name) | 1554 |
| S3082 | H | mech, memfnfinder | whole-reply memcmp; control moves | plain 88, traced 1323 |
| S3083 | I | mech, memfnfinder | opts fixtures (REPORT / no-fd-d1) | 10 |
| S3084 | J | G2 plant | reply-id resolution | 1198 gen failures |
| S3085 | S | mech, memfnfinder | call 0 answers -1 | 11 |
| S3086 | T | mech, memfnfinder | NONE frame part zero | 11 |
| S3087 | U | mech, memfnfinder | EMIT vs mf_emit (PF site) | 2 |
| S3088 | V | mech, memfnfinder | counting hook, six stated (member) | 11 |
| S3089 | X | G2 plant | impossible cell MASK | 1134 |
| S3090 | Y | G2 plant | method R7w picks WALK, search PAIR | 355 |
| S3091 | Z | G2 plant | fused FN iff `_ofsskip` | 352 |
| S3092 | AA | G2 plant | form class (E-find/E-generic) | 3295 |
| S3093 | AB | G2 plant | table_name population, plan_test | 61 |
| S3094 | AC | mech, memfnfinder | counting arena | 194 |
| S3095 | AD | mech, memfnfinder | same-class fixture (PF site) | 2 |
| S3096 | AF | G2 plant | table_name population, stop_test (af_walk) | 32 |
| S3097 | AG | mech, codegen (reach probe) | ASK-6 loud refusal | compile refused on cover patterns |

- **Re-aimed:** S686 (`fn_rows[]` BODY swap) onto the BODY rows' new text with the pick column.
- **Anchors:** `m6read_check_sab_anchors.py` resolves all 1257 rows. Each mech row's SAB_BEFORE matches
  exactly once. VALIDATE_ONLY passes all 13 new mech rows. Every existing G2 plant still applies.
- **Cloud mech shards:** re-derived by `make cloud-reweight KIND=mech`; cloud-check 16/0. The new rows
  carry ESTIMATE weights.

AF's population is 24 B-walk sites whose stop marker is read, as the design measured. The 3 non-B-walk
E-find sites that read the stop's marker (sites 121, 336, 760) are all HORS with the stop NOT in
`plan[]`. Their path is B-hors's probe (`d_hors_head`, `hl` the stop's offset), which §2.3 already names,
so this is not a finding.

## Identity and movers

- **Spot check (box rule):** 100 single compiles, base a9fc6dbd8 against HEAD, over 5 arms:
  - the arms: default, `--engine=vm`, `-fmemfn-simd`, `--memfn=no-window-search`,
    `-fmemfn-simd=x86-64-v3`;
  - the patterns cover ASK-1 (DFA prefilter offset-skip), ASK-6 (cover-routed REQ_RUN `@`) and E-find.
  - Result: **0 differ** in `.c`, `.h` and rc.
- **The full proof** is the job `kit-b30b-gate` (`scratch/memfn/b30b/jobs/gate.sh`, dry-run green; queued as 591 by the lane, CANCELLED by the kit manager before it started because a stale emit_sweep TAG floor on main would have reddened it; the kit manager merges main into this branch, re-bases BASE/REF and re-queues it):
  - emit_sweep base a9fc6dbd8 (`scratch/memfn/b30b/base/build/pcrec`, git archive) against HEAD on all
    71 arms: the 67 declared identity arms (default, each `--memfn=no-X`, `--engine=vm`, both SIMD
    layers) plus 4 CPU-target arms (tgt-generic as the direct generic == plain check);
  - every arm must be identical, with no declared movers;
  - then the 14 new or changed mech rows and the 7 G2 plants.
- **If any byte moves, the job is red**, and per the brief the lane's claim of no movers is void.

## Checks

Run in the tree at fac1dc6b0 plus this commit (`scratch/memfn/b30b/val/chain.sh`, logs beside it, 2026-11-12/13):

| check | verdict |
|---|---|
| `nice make -j8` | rc 0 |
| `make strict` | rc 0 (20 s) |
| `make test-codegen` | rc 0 (217 s) |
| `make test-memfn-finder` (run_finder.sh: purity 7874, traced counts E-func 81 / E-generic 8, census, reach rows) | rc 0, 18040 passed / 0 failed (74 s) |
| `make test-memfn-rows` | rc 0 |
| `make test-memfn-link` | first run RED: C16 flagged the new `memfn/include/NOTES.md` (no SPDX/provenance; every non-CLAUDE.md file under include/ and src/ is in C16's scope). Fixed by moving that history into `memfn/NOTES.md` (outside C16's scope; the check left unchanged). Re-run rc 0, 12 passed / 0 failed, including `[probe]` |
| `make test-memfn-targets` | rc 0 |
| `make test-memfn-arms` | rc 0 |
| `make test-memfn-g2` (quick, with the new traced window pass) | rc 0, 70,358,670 checks / 0 failed (586 s) |
| `python3 -I scripts/m6read_check_sab_anchors.py` | rc 0 (1257 rows) |
| `CLAUDEMD_ROOT=worktrees/b30b scripts/check_claudemd_size.sh --all` | rc 0 |
| spot identity, base vs HEAD, 100 compiles over 5 arms | 0 differ |

## Owed runs

### STATE AT HANDOFF

OWED: kit-b30b-gate (box; to be re-queued BY THE KIT MANAGER after merging main and re-basing BASE/REF; the lane's 591 was cancelled by the manager: emit_sweep zero movers on 71 arms + mech S3078 S3079 S3080 S3081 S3082 S3083 S3085 S3086 S3087 S3088 S3094 S3095 S3097 S686 + G2 plants S3084 S3089 S3090 S3091 S3092 S3093 S3096); cloud for the kit manager: test, axes, ubsan, asan, mechrows S3078,S3079,S3080,S3081,S3082,S3083,S3085,S3086,S3087,S3088,S3094,S3095,S3097,S686

Also owed, to the kit manager:
- **The D27 spec-first author** for 3.0b's seam contract (`mf_wdecide`, `mf_wcall`, `mf_wreply`'s
  frame part, from §2.2-§2.3 alone). It needs a cell outside this worktree (`scripts/mk_d27_cell.sh`).
- **`reach_equal.py` under the MF_TRACE kit, both layers** (`--arms` with the default and
  `-fmemfn-simd`). This is the agreement's corpus carrier, a boxqueue job.
- **The full `make test-memfn-g2-full`/`make test`.** The traced window pass is in run_g2.sh's `win`
  unit at about 26 s, inside the quick budget.
- **The ledger and journal:** `memfn/docs/responses.md` (the R-35 3.0b done entry) and
  `memfn/docs/journal.md`, both kit-manager files.

## Charter-vs-committed checklist

| charter item (§5 3.0b content / brief) | committed |
|---|---|
| §2.2-§2.3 seam: `mf_wdecide(art, site, def, call, out)`, `mf_wcall`, frame part appended last | memfn.h, window.c (dc1ab8e76) |
| `reply_of`'s frame part; the define's record (§4.1: `fn_pick`) | window.c `wf_frame_of`/`reply_frame`, kit.h, ofsskip.c |
| MF_TRACE agreement at every window define, whole memcmp, stored frame part | compose.c `define_sel`, window.c `wf_agree` |
| frame-part outputs moved from 3.0a: fused, plan_test, stop_test, ids, E-func search (pick column), E-stmt arm map, allocator | window.c, ofsskip.c, compose.c `kit_legacy_arm` |
| S686 re-aim onto the BODY lines | tests/mech/sabotages/S686_* |
| ASK-1, ASK-3, ASK-5; ASK-2 void; ASK-6 loud | src/gen/emit_dfa.c |
| purity: framed asks interleaved, whole memcmp, hex control, counting hook (six), counting arena + counted populations, same-class fixture, PURITY_FLOOR re-pinned (7874), purity_rows.tsv rows | tests/memfn/arm_fixtures.c, run_finder.sh, purity_rows.tsv, run_purity_reach.sh |
| traced purity pass, E-func/E-generic counts exact (81/8), its control | run_finder.sh; control recorded above |
| traced window-family pass against libpcrec_mftrace.a, green on base first, runtime measured | run_g2.sh, run_g2_win.sh (`G2W_TRACE`); base green (0 failures), HEAD green, 26 s |
| mf_wcall fixtures (S, T, U) | arm_fixtures.c `pur_call_fixtures` |
| G2 framed ask, cell tally + floors + impossible cells, text classes, table_name population (stop-below-TABLE 40, stated-hook-no-offer 4642), AF tally (24) with the 3 others' paths printed, reply-id resolution | g2_win_gen.c, g2_win.h, run_g2_win.sh |
| successor probe + jobs + compile-only check + span_pick CLAUDE.md | docs/design/memfn/span_pick/probe/, run_link_checks.sh |
| 20 sabotage rows S3078-S3097, each red | tests/mech/sabotages/ (13), run_g2_win.sh PLANTS (7) |
| §3's package: readers, CLAUDE.md, trace_format, comments | memfn/include, memfn/src, tests/memfn, memfn/tests CLAUDE.md; trace_format.md; window.c |
| D27 author | OWED (cell outside this worktree) |
| reach_equal.py under MF_TRACE, both layers | OWED (box job) |
| one box job after 01:00 | written + dry-run (jobs/gate.sh); queued 591, cancelled by the kit manager, re-queue owed to the manager |
