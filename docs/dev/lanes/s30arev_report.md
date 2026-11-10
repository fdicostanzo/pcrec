# s30arev — code review r1 s30a: the FIX-NOW and DOC sets (lane report)

Lane s30arev (opus), 2026-11-09, on `lane/memfn-s30a` in `worktrees/s30a` (start df23554a7). The review is
`docs/dev/reviews/2026-11-09-r1-s30a.md` (RULED: every disposition adopted as written, plus main's added FIX-NOW:
the "libc memchr supplies only one-shot" pin is re-attributed to the kit). Design of record: plan_frame.md rev 2.2 + D190.

## Summary

Every FIX-NOW and DOC item is done. Commits: a9e99b1ee (kit code and census), c8d54df7c (rows_check §S/§P and
the pin), a52ed4dcd (plan_frame §5, trace_format, mech rows), and the final commit (this report and the index line).
- **Zero emitted bytes moved, no abi event.**
  - The G2 window family is byte-identical, pre-fix vs post-fix, plain and traced, and so is its whole MFTRACE stream.
  - A sampled emit_sweep against base has 0 movers.
  - Finder form hashes are unchanged.
- **Plants measured by hand.** Seven plants, each classed SAME / SILENT-MOVE / LOUD:
  - B and C are SILENT-MOVE. rows_check §P hosts them, with §R's triples as the detector.
  - M is SAME, and §S is red on it.
  - A finding beyond the brief: F1 turns row R (S2993) from LOUD into a SILENT MOVE. Its mech suite was re-aimed from the harness to memfnfinder, measured red.
- **Gate jobs 500-509** cover the new tip. They pass their dry-runs and a scratch-queue `add --no-start`. None is queued.

## Item by item

- **F1 (+F15)**: commits a9e99b1ee, a52ed4dcd.
  - The ST-many refusal is raised in one place, `wf_plan_site` after Table E's walk, and only where Table E answers E-find (window.c:2316).
  - The one text is Table S's row `wf_srows[].why`. `wf_stream_refusal()` (kit.h:561) is the composer's reader of it (compose.c:1087).
  - `fd_find` keeps the refused pick and returns `FD_REFUSED` (kit.h:636). E-find's row then refuses (`e_find_holds`: holds || refused).
  - The F1 side note is in plan_frame §5 (R), and S2993's header is re-written from the measurement.
- **F2**: a9e99b1ee.
  - Disjoint key bits: `REN_FRAME (1u << 31)` (window.c:1788) with a `_Static_assert` on `FF_HORS`/`WF_ST_SHIFT`.
  - `ren_pick` returns 0 for FF_UNSTATED (window.c:1795), so a refusal does no lookup.
  - The named answer is `wf_renderable` (`WF_RENDERS_NOT/ONE/MANY`, kit.h:554). The gate reads it at finder.c:510.
- **F3 (guard only)**: a9e99b1ee.
  - `wf_tables_check` (window.c:2146) refuses an E-find search row with a predicate. It is called by `mf_art_begin` (compose.c:912).
  - Its trigger is noted: the first E-find search row with a predicate. The unification is a PLAN row.
- **F4**: a9e99b1ee.
  - The E-stmt `ren_search` rows hold only `.k`, `.arm` and `.basis`. The libc fact is read from the arm, and the unread cells are dropped.
  - `RC_CALLER` is dropped (RC_N 2). `RC_FLOOR.libc_runs` is now read by the one union `pieces_libc` (window.c:2202), for E-find and the floor.
  - plan_frame §2.6.2 says why C-caller is not a row.
- **F5**: a9e99b1ee.
  - `wf_tables_check` asserts that each fused row's key == REN_PICK(its declared search).
  - `b_fn_holds` no longer re-tests the pick (`wf_bx` lost `pick`).
- **F6**: a9e99b1ee, a52ed4dcd.
  - `wf_stmt_row` (kit.h:579, window.c:2117) returns the E-stmt row, and `site_rec.fd_ren` (kit.h:263) carries it.
  - FDROUTE prints the row's `id` and `wf_frame_name(frame)` (compose.c:1145).
  - memfn/docs/trace_format.md has the FDROUTE hunk. No trace line moved (G2's MFTRACE stream is identical).
- **F8 + F9**: c8d54df7c, a52ed4dcd.
  - rows_check.py §P, with `PLANTS` (rows_check.py:584) and `run_plants` (:617), plants S2983 (B), S2984 (C) and S2988 (M) in a copy of the kit source, relinks, and runs the detector: §R's triple set for B and C, §S for M.
  - Each must go red, and each witness's class is printed.
  - The refusal invariant is now `refusal_named` (:316), scoped to row R.
  - plan_frame §5 B, C, M and Q are re-written from measurements. Q is UNDETECTED, and the text says so.
- **F11**: c8d54df7c. `support_faults` (rows_check.py:522) makes a duplicated search on either side a fault.
- **F12**: c8d54df7c.
  - The ledger allowlist is `LEDGERS` (:516): memfn/docs/responses.md and docs/dev/decisions.md.
  - A D-number provenance narrows the read to that decision's entry.
- **F13**: a9e99b1ee.
  - The census LIVE shapes are `REN_ROWS(ren_`, `keys &`, `wf_support[` and `wf_srows[` (decider_census.py:72).
  - Members: `wf_srows` and `wf_stream_refusal` added, `wf_stmt_arm` -> `wf_stmt_row`, and `wf_tables_check` excluded.
  - HITS 60, MEMBER_COUNT 64.
  - S2985 is re-aimed at a true byte copy (b1: `census_find2` called via `REN_ROWS(ren_search)`). It must produce exactly 2 strays. Census 90/0.
- **F18**: a9e99b1ee. `_Static_assert(WF_NEROWS == E_GENERIC + 1)` (window.c:1636).
- **Main's added item + F14 (DOC)**: c8d54df7c, a9e99b1ee.
  - The pin's LIBC/LIBC_BACK source is `RULING (D190, kit-stated line)`.
  - The pin header, the rows_check docstring, window.c's support comment (:2031) and plan_frame §5 (M) now say the sentence is the KIT's line, which D190 files. They no longer call it the owner's text.
  - `RULING_SOURCE` (rows_check.py:519) requires the decision id and whose words the line is.
- **F16 (DOC)**: a9e99b1ee. Comments only.
  - History narration and the retired-table names are removed from comments.
  - The B-* ids are said once to stay as trace-pinned ids (window.c:3254).
  - The remaining `rev`/`3.0a` mentions in memfn/src are design citations, not history.
- **plan_frame §5 B/C/Q text (DOC)**: a52ed4dcd. B and C are measured SILENT-MOVE (§P, the triple detector). Q is UNDETECTED (measured, S2992).
- **PLAN rows (main's to file; not filed here)**:
  - F7: the FUNC-form floor's open-coded loop.
  - F10: §R's invariant names Table S on only some refused compiles.
  - F17: `b_fn_holds` translates inside a predicate. Trigger: 3.0b, when fused rows grow.
  - The F3 unification (one context type per table). Trigger: the first E-find search row with a predicate.
  - A `memfnrows` mech arm. With it, S2983/S2984/S2988 could leave §P, and S2993 could add rows_check.
  - NEW from the measurements: `mismatch_inplace` LOUD under B/C (see Plants).

## Zero bytes

| witness | result |
|---|---|
| G2 window family (seed 20261022, 1500 sites), pre-fix df23554a7 vs tip, plain and -DMF_TRACE | sites IDENTICAL (20,787,703 bytes, both kinds), generator logs IDENTICAL, MFTRACE stderr IDENTICAL (164,135 lines, 3,106 FDROUTE) |
| emit_sweep, base 0fb486dbf's binary vs tip, `--streams c-default,c-vm --every 20 --jobs 2` | population 6394 per stream; movers 0, asymmetric 0 (c-default 5878 ok/516 refuse; c-vm 5879/515) |
| hand sample, 14 patterns x 7 arms, pre-fix binary vs tip | 98/98 SAME |
| finder form hashes, tests/memfn/run_finder.sh at tip | finder_check 1108/0; whole suite 3316/0 (s30a's figures) |

No header, layout or ABI number moved, and there is no abi event. Full identity is left to gate jobs 501-503.

## Plants measured

Method: each plant was applied to a git archive copy of the branch (scratch, never the worktree), built with
`nice make -j2`, then:
- 15 patterns x 4 arms were compiled by the planted pcrec and by the clean pcrec, and each pair was classed (SAME, SILENT-MOVE = rc 0 and different text, LOUD = refused).
- The detector was run on the planted copy.

| row | plant | class (of 60) | detector, measured | SAB_DOC_FIGURE |
|---|---|---|---|---|
| S2983 (B) | (E-stmt, PAIR) search row with no arm | SILENT-MOVE 9, SAME 51 | rows_check §R red (`foo\|bar\d` prints (E-find, PAIR, B-pair), not (E-stmt, R7w, pf_walk)); also `mismatch_inplace` LOUD | §P row (no mech file) |
| S2984 (C) | the renderability gate removed | SILENT-MOVE 9, SAME 51 (same moves as B) | as B | §P row |
| S2988 (M) | LIBC admits MASK | SAME 60 | §S red (LIBC yes/yes/no vs pin yes/no/no) | §P row |
| S2993 (R) | PAIR admits SHIFT | **SILENT-MOVE 12, SAME 48, LOUD 0** (s30a: LOUD) | memfnfinder 17fail/3295pass (form `pair` unresolved); rows_check 7 failed | written |
| S2990 (O) | gate unscoped to PRES (re-aimed) | LOUD 26, SAME 34 | memfnfinder 56fail/3227pass | written |
| S2992 (Q) | libc union drops the check (re-aimed) | SAME 60 | memfnfinder 0/3316: UNDETECTED as declared | written |
| S1079 | D1 declines for the composer (re-aimed) | SAME 60 | memfnfinder 6fail/3308pass | appended |

The in-script §P run in `run_rows.sh` reproduces B, C and M (rows_check 239/0 at tip).

## Gates refreshed

Jobs in /var/tmp/pcrec-pcrec/scratch/memfn/s30a/jobs/ read the worktree's HEAD, so they cover the tip.
- **common.sh**: a refresh note.
- **mech.sh**:
  - rows_for over this lane's changed files gives 44 rows, all within the existing 62.
  - The re-aims are noted, along with the move of S2983/S2984/S2988 to §P.
  - S2993's suite is now memfnfinder (read from its file).
- **505 (make test)**: adds a step that requires the three `plant S29(83|84|88) ... RED` lines from test-memfn-rows, and declares `expect plants=3`.
- **506 (G2 plants)**: the 26 G2 plant anchors still resolve once each (replayed).
- **501-504, 507-509, ident.sh, basis.py**: unchanged. They read HEAD.

Every job passes its own `--dry-run`, and `scripts/boxqueue add --no-start` succeeds against a scratch `PCREC_BOXQUEUE_DIR`. Nothing is queued.

## Checks run

All niced and single-process:
- `python3 -I scripts/m6read_check_sab_anchors.py`: all 1171 anchors resolve.
- The G2 plant anchor replay: 26/26 count 1.
- `bash tests/memfn/run_arch_blind.sh`: 17/0.
- `nice make strict`: clean.
- `tests/memfn/run_rows.sh`: 239/0.
- `decider_census.py`: 90/0.
- `tests/memfn/run_finder.sh`: 3316/0.
- The G2 identity witness, the sampled emit_sweep, and the hand sample.

`make test-codegen` was not run, because no tests/**/run_*.sh was added or renamed. Nothing else was run: no make test, no mech, no full identity sweep, no box job.

## Deviations

1. **S2993 (R) re-modelled.** This goes beyond the ruled set, but follows from F1 and was measured.
   - With the refusal raised only where Table E answers E-find, Table E's legacy-first order serves the site elsewhere. The plant became a SILENT MOVE: 12/60, nothing refused.
   - The corpus harness, its old suite, checks answers, which a correct other text leaves green. Its mech suite is now `memfnfinder`, measured red.
   - plan_frame §5 (R) and S2993's header are re-written accordingly.
   - A rows_check §P entry for R was not added: memfnfinder already detects it.
2. **The D190 ledger.**
   - The branch has no D190 (its decisions.md predates it).
   - The pin row keeps `@ memfn/docs/responses.md 067aca4df` as its ledger, with the source relabelled `RULING (D190, kit-stated line)`.
   - LEDGERS already allows docs/dev/decisions.md, so switching to `@ docs/dev/decisions.md D190` after the post-U2 re-merge is a one-cell change.
   - I proposed this to the kit manager and got no reply, so I built it as proposed.
3. **B/C side effect.** Under either plant, pcrec refuses the arm fixture `mismatch_inplace` in rows_check ("the memfn kit's text calls <string.h> functions the prologue did not include"). The clean tree is unaffected. This is recorded in plan_frame §5 (C) and offered as a PLAN observation.
4. **SAB_DOC_FIGUREs for S2983/S2984/S2988** live in this report and in the §P comment. These rows have no mech file.

5. **The deliver file gained one line**, `dirty-ok: docs/dev/artifact_size_log.tsv`. Lanecheck refused the tree for that file.
   - The file has been dirty since 2026-11-08 19:10 (a make test run before this lane started).
   - The brief says never to commit it, and discarding it is not this lane's call.
   - No other line of the deliver file changed.

## STATE AT HANDOFF

OWED: none. Nothing is queued or running. Branch lane/memfn-s30a is at the final commit of this lane. Gate jobs 500-509 are refreshed and wait for the kit manager to queue them.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| FIX-NOW F1+F15, F2, F3 guard, F4, F5, F6, F8, F9, F11, F12, F13, F18, the D190 re-attribution | yes (a9e99b1ee, c8d54df7c, a52ed4dcd) |
| DOC F14, F16, plan_frame §5 B/C/Q, F1 side note | yes |
| PLAN rows listed, not filed | yes (Item by item) |
| zero bytes, no abi event, with G2 / finder hashes / emit_sweep sample at -j2 | yes |
| every new or re-modelled plant measured by hand, classed, SAB_DOC_FIGURE written | yes (7 plants) |
| sab anchors, arch_blind, make strict | yes |
| make test-codegen (only if a run_*.sh was added) | not needed |
| jobs 500-509 refreshed, each --dry-run passes, not queued | yes |
| report + history index line, final commit | yes |
