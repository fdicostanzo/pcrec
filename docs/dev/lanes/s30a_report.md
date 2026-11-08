# s30a — span_pick stage 3 unit 3.0a: the triple's tables, Table B's split, the asker fact retired

Lane s30a (opus), 2026-11-07. Kit request R-35, under Frank's stage 2-3 GO.
- Branch: lane/memfn-s30a, base 0fb486dbf.
- Worktree: worktrees/s30a.
- Design of record: docs/design/memfn/plan_frame.md rev 2.2, its 3.0a row.
- Binding rulings: reviews 2026-11-07 r12 and r13.

## Summary

3.0a is built kit-internal in the two commits R12 fixed. It has no seam change, no memfn.h edit and no
MF_SITE_ABI move.

**Commit 1 (§2.5.2-§2.5.3 + §2.6): the triple's tables, all in window.c.**
- The SUPPORT table (`wf_support`, exported as `wf_support_rows`).
- TABLE S (`table_s`, with rows ST-one, ST-none and ST-many).
- The renderer tables, each read through ONE accessor, `ren_find`:
  - skeleton `ren_skel`: E-find, and E-generic with its render order;
  - search `ren_search`: B-pair (with its loop-state slot), B-memchr, B-walk, B-hors;
  - stream `ren_stream`: S-restart twice (one row each for E-find and E-generic, sharing one text),
    S-shift and S-caller;
  - check `ren_check`: C-find, C-floor, C-caller;
  - fused `ren_fused`: B-fn, matched first.
- `wf_brows`, `wf_b_find`, `wf_b_render` and their two `_Static_assert`s retire. Every new table has a
  row-count successor.
- `d_hors_prepare` is split into a search half and a stream half.
- The libc union is now over all three pieces.
- The internal plan function `wf_plan_site` holds wf_prepare's selection and stores what the define
  renders. The floor reads its check, stream and skeleton rows.

**Commit 2 (§2.4): the asker fact retires.**
- `fd_find` takes the asker's frame. `fd_holds` gates slot FIND on the frame's RENDERABLE SET
  (`wf_renders`).
- Table S's ST-many is a named refusal raised after the gate (`?stream`).
- Deleted: `SF_ASKER_PAIR` (bit 15, retired) and `fd_stop.renders_pair`.
- The composer's `fd_renderers` rows become the search table's E-stmt rows (`wf_stmt_arm`).
  `select_arm`'s refusal is kept.
- FDROUTE prints `frame=`. `renderer_rows.tsv` is re-keyed to (frame, row, ren) with a `fused` column.
- rows_check gains §R's triples, §R's REFUSAL INVARIANT and the new §S (the support pin
  `stream_support.tsv` against `arm_fixtures --streams`).

Zero movers on every light witness. The heavy witnesses are written as jobs 500-509, not queued.

## Commits

| sha | content |
|---|---|
| 8bb9db959 | commit 1: §2.5.2-§2.5.3 + §2.6. Names BASE 0fb486dbf and the sabotage id range S2982-S2993 |
| b5d1f8dd4 | commit 2: §2.4 |
| (this report's commit) | report and history index line |

Sabotage ids follow the design's letter order:
- (A)-(D) are S2982-S2985.
- (K)-(R) are S2986-S2993.

S2981 is the highest id in use. S2982 and above appear on no branch or worktree, except as plan_frame.md's
own sentences that name the numbers.

## Zero movers (evidence)

- **Byte identity, light sample.** Base binary (build/pcrec at 0fb486dbf) vs HEAD:
  - 12 patterns: the renderer_rows witnesses, `..`, `#`, `a[Xx].b`, `x[ab]{3}y`, `\d+-\d+`, `abcdef`.
  - 4 arms: default, `-fmemfn-simd`, `--memfn=no-fd-d1`, `--engine=vm`.
  - Result: 48/48 SAME at commit 1 and 48/48 SAME at commit 2.
  - The full emit_sweep over all 67 identity arms is jobs 501-503.
- **G2 window family** (`run_g2_win.sh`): 10444 passed, 0 failed, at both commits. The census holds
  (window-search=1294, wf-floor=541, pf_walk=17, ofsskip=31, ...).
- **Form-id hashes unchanged** (`run_finder.sh`, finder_check 1108/0, whole suite 3316/0, both commits).
  Check C reports "33 format-2 form-bearing rows checked, 0 stale".
- **REACH equality.** The new tables print no REACH; old Table B's walk printed none either. The full
  equality run is job 504: 18 arms, no `--map`, no gone set.
- **decider_census.py green:**
  - commit 1: 81/0, HITS 48, MEMBER_COUNT 60;
  - commit 2: 83/0, HITS 50, MEMBER_COUNT 61, all hits inside members.
- **rows_check:**
  - §R green: 14 declared triples, 11 witnessed, 55 FDROUTE records over 11 distinct triples.
  - §S green: 6 rows, 1 ruling ledger read.
  - 243/0. Three triples have no witness (UNREACHED), as at base.
- **Goal 4 grep** (`renders_pair|SF_ASKER_PAIR` in memfn/, src/ and tests/, outside the history ledgers
  finder_history.md, journal.md and responses.md): empty.
- **Landing-time basis witness** (§2.5.2): job 504's `basis.py`. Over BASE's traced text, `_sh[256]`
  appears iff the trace prints FDROUTE `ren=B-hors`. See Deviations 8.

## Sabotage rows

All rows were planted and reverted by hand on this tree. Every row is RED except (Q).

| row | id | form | plant | measured |
|---|---|---|---|---|
| (A) | S2982 | mech, memfnfinder | B-pair's search row serves no pick | `mf_form_hash(pair) does not resolve`; 9 instances resolve, under the floor of 10 |
| (B) | S2983 | hand (rows_check) | an (E-stmt, PAIR) row with no arm, replacing the E-stmt LIBC_BACK row | rows_check red: the R7w/pf_walk witness printed (E-find, PAIR, B-pair); D1c's witness lost its triple |
| (C) | S2984 | hand (rows_check) | the gate removed from fd_holds | rows_check red: `foo\|bar\d` printed (E-find, PAIR, B-pair); pcrec's include check fired on the mismatch_inplace witness |
| (D) | S2985 | census in-script plant | a second renderer list spelled over `ren_search[` | backstop red, 2 stray hits (runs in every census run) |
| (K) | S2986 | G2 window plant | the HORS SHIFT cell set to 0 | RED: "a dense window renders no D-hors table" |
| (L) | S2987 | G2 window plant | S-restart's text resumes `C += 2` | RED: 334 driver failures |
| (M) | S2988 | hand (rows_check §S) | LIBC admits MASK | RED: "support row LIBC: pin yes/no/no, kit yes/yes/no" (the only observation, as designed) |
| (N) | S2989 | G2 window plant | E-generic's S-restart row deleted (keys 0) | RED: "no-window-search: a DFA_SCAN site not on the floor" |
| (O) | S2990 | mech, memfnfinder | the gate unscoped (PRES rows gated too) | RED: "a presence span no routed PRES row decides", "fd-P0: PRES decided []" |
| (P) | S2991 | G2 window plant | B-pair's loop-state slot emptied | RED: the family does not compile |
| (Q) | S2992 | mech, DECLARED UNDETECTED | the libc union over search and stream only | no byte moves; finder green. See Deviations 1 |
| (R) | S2993 | mech, harness | PAIR feeds RESTART and SHIFT | RED: the witnesses fail to compile (rc 1); §R's invariant fired: "REFUSED naming Table S's ST-many refusal" |

G2 plants S1423, S1427, S1428 and S1543 are KEPT VERBATIM: the split moved their lines whole. Each was
re-run and is RED, as are S1422, S1425 and S1429. S686 is 3.0b's. Every mech anchor was checked
(SAB_BEFORE count = SAB_COUNT). VALIDATE_ONLY passes for S2982, S2990, S2992 and S2993.

## Checks run

All runs were niced on the box, light only:
- `make -j2` and `make strict` (clean) at both commits.
- The 48-compile identity sample (above).
- `run_g2_win.sh` at both commits.
- The plants listed above.
- `run_finder.sh` at both commits, and under (A), (O) and (Q).
- `run_rows.sh` at both commits, and under (B), (C), (M) and (R).
- `decider_census.py` with plants.
- Traced witness compiles under (A), (B), (C) and (R), using rows_check's traced build.
- `check_claudemd_size.sh --all`.
- The mech anchors, and VALIDATE_ONLY.

No make test, mech, emit_sweep or box job was run.

## Validation jobs written (not queued)

The job files are in /var/tmp/pcrec-pcrec/scratch/memfn/s30a/jobs/, with shared settings in `common.sh`.
Every job's `--dry-run` exits 0. Every `--ready` honours s2a's hold.sh. The 500-509 prefixes are
placeholders for the kit manager.

| job | key | what | after |
|---|---|---|---|
| 500-kit-s30a-strict | kit-s30a-strict | make; make strict | - |
| 501..503-kit-s30a-ident1..3 | kit-s30a-identN | emit_sweep, all 67 identity arms, base binary vs HEAD (ident.sh, 23/22/22) | strict, ident1, ident2 |
| 504-kit-s30a-reach | kit-s30a-reach | BASE's MF_TRACE build (git archive), HEAD's; reach_equal.py at 18 arms over corpus + 4 patterns files; then basis.py | ident3 |
| 505-kit-s30a-test | kit-s30a-test | make test via perfrun | reach |
| 506-kit-s30a-plants | kit-s30a-plants | run_g2_win.sh --plants (26, each must be red) | test |
| 507..509-kit-s30a-mech1..3 | kit-s30a-mechN | mech, 62 rows (mech.sh): rows_for.sh union + every memfnfinder row; gate is unexpected 0, anomalies 0 | plants, mech1, mech2 |

## Deviations from plan_frame.md

1. **(Q) has no detector.** The design names emit_sweep on `--memfn=no-fd-d1 abcdef` and the reply-class
   pin. Neither moves:
   - pcrec includes `<string.h>` on its own, and `RX_MEMFN_LIBC` reads `none` on both sides.
   - pcrec reads `libc_free` only in `cand_class_eq`, which compares ask against define over one plan.
   - `arm_fixtures --query` reads libc only as `memchr(`/`memcmp(`, and the run compare loads words by
     `memcpy`.

   Committed as S2992, declared UNDETECTED with its reason. A detector would need an independent libc
   reading that counts `memcpy(`, plus a B-walk fixture with a run term. That is a check change; I did not
   invent it.
2. **(B) and (C) do not refuse the compile.** A composer site whose PAIR has no E-stmt arm falls through
   `select_arm` to the window family's E-find row, which renders it with B-pair. So the observation is a
   moved triple, red in rows_check §R's witness check, not §R's refusal-invariant message. The invariant is
   built, and it does fire on (R).
3. **(B)'s plant replaces the E-stmt LIBC_BACK row.** A one-line added row would break the pinned row
   count (`_Static_assert`). The arm-less (E-stmt, PAIR) row therefore takes that row's place.
4. **No mech arm runs rows_check or the census.** (B), (C) and (M) are hand plants recorded here, as lane
   sp1e did. (D) is a census in-script plant. (K), (L), (N) and (P) are G2 in-script plants, run by job 506.
5. **MEMBER_COUNT is 61, not 59, and HITS is 50.** The renderable set (`wf_renders`) and the composer's
   accessor (`wf_stmt_arm`) are functions holding `ren_find(`, so they are members. The design allows a
   build to re-derive both numbers from its map.
6. **§S reads the ruling's ledger at 067aca4df with `git show`.** That commit is on lane/memfn-k1107 and
   not on main. Until the kit branch, which contains it, lands, a checkout without the object turns §S red.
7. **Rows with no 3.0a reader, and one name collision.**
   - C-caller has no 3.0a reader. S-caller is read through Table S's streams(E-stmt).
   - E-func has no fused row: its search is 3.0b's `fn_rows` pick column.
   - The check row named "C-floor" shares T-VERIFY's row name. It does not match run_purity_reach.sh's
     population pattern.
8. **The basis witness is partial.** Its HORS half is automated (`_sh[256]` iff `ren=B-hors`, job 504). The
   other half ("B-walk, B-pair, B-memchr and floor sites resume C++ and declare no mask") has no stable
   textual test for "a mask variable", so it is not mechanized. The floor's `C++` holds by construction:
   both S-restart rows share one text, and (L) shows it reaches both.
9. **Smaller readings.**
   - `mf_wdecide` calls `decide` directly; that is the plan function's decision half.
   - The plan stores the stream ROW, not a stream value (R8: no unread output).
   - FDROUTE's `frame=` key is appended last on the line.
   - The E-stmt rows' ids are their arms' ids, so `ren=` bytes do not change.
   - The gate's decline traces as `PRED_FALSE`, like every other `fd_holds` decline.

## Charter-vs-committed checklist

| charter item (plan_frame.md §5, 3.0a) | committed |
|---|---|
| search renderer table + renderable set (slot FIND only) | yes: `ren_search`, `wf_renders`, the gate in `fd_holds` (b5d1f8dd4) |
| SF_ASKER_PAIR, renders_pair deleted; select_arm's refusal kept | yes (b5d1f8dd4) |
| support table, Table S (ST-one, ST-none, ST-many) | yes (8bb9db959); ST-many is a refusal after the gate (b5d1f8dd4) |
| skeleton, search and stream rows with loop-state slots; check rows; fused rows; wf_brows/wf_b_find/wf_b_render retired; wf_floor_expr reads its stream row | yes (8bb9db959) |
| one lookup accessor per table | yes: one over all of them, `ren_find` |
| support pin, rows_check §S, arm_fixtures --streams, SOURCE column | yes (b5d1f8dd4) |
| internal plan function computing what the define renders (no 3.0b outputs) | yes: `wf_plan_site` (8bb9db959) |
| census rows + narrowed backstop shapes | yes, at both commits |
| finder history row; renderer_rows.tsv re-keyed + fused; FDROUTE frame= | yes (b5d1f8dd4) |
| CLAUDE.md lines; reader-table restatements (R14) | yes: memfn/src, memfn/tests, tests/memfn CLAUDE.md; window_site, units_inventory, span_pick T-STREAM, span_cards, trace_format, formhash comments |
| `_Static_assert` successors | yes, one per new table |
| G2 plant re-aims | KEPT VERBATIM (S1423, S1427, S1428, S1543), each red |
| sabotage rows (A)-(D), (K)-(R) | yes, 12 rows in the forms above; (Q) UNDETECTED (Deviations 1) |
| witnesses: identity, G2, hashes + check C, REACH, census, §R/§S, Goal 4 grep, basis | light ones green here; identity, REACH and basis written as jobs 501-504 |
| heavy runs (make test, emit_sweep per arm) | written as jobs, not queued (the brief) |
| commit order R12 | yes: commit 1 = §2.5.2-§2.5.3 + §2.6, commit 2 = §2.4 |
