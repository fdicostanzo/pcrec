# r30b — [MEMFN] R-30: the pre-check asks the whole run alone (abi 92 -> 94)

Lane r30b, 2026-10-29, opus. Branch `lane/memfn-r30b` cut from main 1f5574fac (abi 92).
Charter: R-30 option A of `docs/dev/lanes/r30scope_report.md` (the kit manager's brief),
plus `r30b_rulings.md` (req_site_define edits allowed, listed here; none were needed).

## 1. The change

At an ALL_PRESENT pre-check whose layout carries the run's WINDOW part and the WHOLE-run
part (`pres_layout_check`: member 0, run longer than `MF_PRES_WINDOW`), the window part
is no longer defined or asked. The whole run's search does the work alone. It still scans
on the window's member byte, and each candidate's compare tests the window's bytes FIRST
(the "led" compare), then the rest of the whole run. This holds at the entry and at every
re-find, for any landmark, on both engines. Runs of 8 bytes or less, member-piece sites
and sites without a whole part are unchanged.

pcrec's statement is UNCHANGED: pcrec still states both parts (window `fn_ref 1`
`<p>_reqrun`, whole `fn_ref 2` `<p>_reqrun_whole`). The kit decides that the window is
implied. The rule is general, not a window special case. A FUNC run part `i` is IMPLIED
by a later FUNC run part `j` when all of these hold:
- `j`'s run contains `i`'s run at offset `d`, with equal bytes and masks;
- `j` scans on the same byte (`pj.plan_pos == pi.plan_pos + d`);
- `i` is not the site's `ret_pred`, so its position is never handed off.

An implied part is neither defined nor called (no note). The implying part's verify chain
leads with the implied slice.

Kit hunks:
- `memfn/src/precheck.c`, block "R-30: a run part another part implies":
  - `implied_by` (refuses under the lever, for `ret_pred`, and for non-FUNC runs) and `lead_of`.
  - `precheck_define` skips an implied part and prepares the led compare for its implier.
  - `precheck_use` skips an implied part.
- `memfn/src/runcmp.c`: `run_cmp_render_lead` / `run_cmp_prepare_lead`, and `rc_lead_term`
  (the slice as its own run term, rendered by the row table at `off + at`). The rest of
  the run is rendered by the existing rows with a `[lo, hi)` exclusion:
  - words row: a word wholly inside the lead is skipped;
  - bytes row: lead positions are skipped;
  - memcmp row: untrimmed (one call).
- `memfn/src/ofsskip.c`: `verify_chain` takes the `fn_in` and renders a led run when
  `lead_len`. `ofs_fn_define_lead` is a thin twin of `ofs_fn_define_at`. S279's anchor
  line (`run_cmp_render(art, t, "subject + cand", ...)`) is kept verbatim.
- `memfn/src/kit.h`: `mf_art.levers`, `fn_in.lead_at/lead_len`, and the new declarations.
- `memfn/src/compose.c` + `memfn/include/memfn.h`: `mf_lever` (§3).
- No `MF_SITE_ABI` / `MF_VOCAB` move. The kit journal entry is the kit manager's.

Example: case 7 (`https://www\.`... whole `https://www.`, window `s://www.`@3). Both
`rx_reqrun__body` and `rx_reqrun` are gone, and so are their calls at the entry and the
re-find. The whole run's compare is now:

    if (!memcmp(subject + cand + 4, "s://www.", 8) && rx_w8(subject + cand) == rx_w8("https://")) return cand;

K66's witness `(x?)([a-z]+)+eeeeeeee~#~#~#~#\1` (memcmp row):

    if (!memcmp(subject + cand + 8, "~#~#~#~#", 8) && !memcmp(subject + cand, "eeeeeeee~#~#~#~#", 16)) return cand;

## 2. Why it is never slower

The old shape was two scans, and both returned only "present or not":
- the window scan (memchr on the member byte, window compare at each candidate) up to
  the first window hit;
- then the whole scan (memchr on the same member byte, whole compare at each candidate)
  up to the first whole hit.

The whole run contains the window at a fixed offset, so every whole hit is also a window
hit. The window scan's verdict is therefore implied by the whole scan's. The new shape is
the whole scan alone. Its candidates are the same memchr hits as before. Per candidate:
- the window's compare comes first. A candidate the window rejects costs what it cost in
  the old window scan (one compare, at most);
- a candidate the window passes pays the rest of the run, as the old whole scan's compare
  did.

The worst case is dense candidates that pass the window and fail the rest. There the new
shape pays one more compare per candidate than the old whole scan. The old shape, though,
also walked those candidates in the window scan before the whole scan began, unless the
window's first hit came early. Measured below: no case moved up in instructions.

## 3. The test-only lever

`--harness=pres-window` (build/pcrec-harness only; `#ifdef PCREC_HARNESS` in
`cli/main.c`) sets `PcrecHarnessOptions.pres_window`. `src/gen/memfn_sites.c` then calls
`mf_lever(job->mf, "pres-window")` before the first define. The kit's `implied_by`
answers "not implied" under it, so the old form comes back byte for byte (the census's
lever arms check this over the corpus: nothing may move vs main).

`mf_lever` is a harness-only kit entry, like `mf_reach` and the retired `mf_preview`. It
refuses an unknown name, and it refuses after the first define. There is no
`options.def` row and no public deny, per the brief's flag. The lever is:
- an `INTERNAL_ARMS` member of `tests/axes/run_axes.sh` (the old form's answers over the
  whole corpus);
- on the G7 lever fence's allowlist (`tests/compound/run_lever_fence.sh`) for
  `tests/memfn/run_presence.sh`, the only test that names it.

pcrec-side hunks:
- `src/core/internal.h:177-187`: the `pres_window` bit and its comment.
- `cli/main.c:1436`: the `--harness=pres-window` spelling.
- `src/gen/memfn_sites.c:161-166`: the `mf_lever` call, and a loud failure on refusal.
- `src/gen/emit_dfa.c:55`: `PCREC_ARTIFACT_ABI 94`.

No `req_site_define` edit was needed (the rulings allowed one).

## 4. abi readers (92 -> 94; 93 is trailgc's, landing first)

Found by grepping the tree for the number:
- `src/gen/emit_dfa.c:55`: the define.
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT=94` plus the transition narrative.
- `docs/spec/match_api.md`:
  - the guard block (`!= 94`, `(abi 94)`, `PCREC_RX_ABI_H 94`);
  - the rx_info table row;
  - §6¶17 "It is `94`".
- `docs/dev/history/abi_changelog.md`: the new 94 entry.
- `tests/mech/sabotages/S693_abi_not_bumped.sh`: BEFORE 94, AFTER `93 /* SABOTAGE S693 */`,
  re-aimed comment.
- `tests/codegen/run_recursion_identity.sh`: FILEPIN self-pinned to 38d3143d5, the abi
  commit.

If R-30 lands BEFORE trailgc, every reader above takes 93 instead.

Spec hunk: `docs/spec/tuning.md` §2.29¶4. The pre-check now searches the whole run, not
the window, scanned on the window's member. The window is tested first in each candidate
compare. No stamp value moves; the census confirms it (§5).

## 5. Movers (census vs 1f5574fac)

`docs/dev/lanes/r30b_evidence/census.py` follows lane s3's census shape (emit_sweep has
no abi normalization). It covers every distinct corpus pattern under its block's options.

Arms:
- c-default, c-utf8, c-vm, c-simd, c-vm-simd: judged both ways against the DECLARED
  population. That population is read from BASE's own artifact: BOTH-ASKS means BASE
  calls `rx_reqrun(` and `rx_reqrun_whole(`. Such an artifact must move, and only as
  declared:
  - no `rx_reqrun(` and no `rx_reqrun__body`;
  - `rx_reqrun_whole(` kept;
  - every `#define RX_` stamp line equal.
  Any other artifact must not move.
- lever and lever-vm: the harness binary under `--harness=pres-window` against BASE;
  nothing may move.
- ir and facts listings: nothing may move.

CENSUS_RESULT

## 6. Sabotage plants (S1543-S1548; S1549-S1559 unused)

Each plant was applied to a fresh archive of the lane tip and built (-j2, nice). Then two
checks were run:
- section D of `tests/memfn/run_presence.sh` (in `make test-memfn-finder`, mech suite
  `memfnfinder`);
- for the answer-moving plants, the K66 corpus file through the harness.

| row | plant | detector | result |
|---|---|---|---|
| S1543 | `implied_by` never answers: the window is asked again | memfnfinder (section D) | 18 FAIL |
| S1544 | the use skips EVERY non-`ret_pred` run part: the whole run is never asked | harness k66 + memfnfinder | harness 12 of 16 cases failed; section D 5 FAIL |
| S1545 | lead compared one byte right of its place | harness k66 + memfnfinder | harness 4 failed; section D 7 FAIL |
| S1546 | lead ignored: the run compared in its row's own order | memfnfinder | 7 FAIL |
| S1547 | the rest skips every word OVERLAPPING the lead | memfnfinder | 3 FAIL |
| S1548 | `mf_lever` accepts `pres-window` and sets nothing | memfnfinder | 9 FAIL |

All six are DETECTED. Notes:
- S1544 first read 0 FAIL in section D: section D matched `rx_reqrun_whole(` against the
  DEFINITION. Section D now reads the CALL
  (`rx_reqrun_whole(subject, subject_length, search_from)`).
- The negative control: section D against main's pre-R-30 binaries gives 10 FAIL.
- Each row's `SAB_REACH` probe is live on the tip and anchored once. `VALIDATE_ONLY`
  passes for S1543-S1548, S278 and S693. Each row's formal mech verdict is the staged
  job's (§8).

Not planted: "the window kept as a landmark (`ret_pred`) dropped anyway". A probe over
71 presence/handoff/k66/reqcube patterns found NO site with a window `ret_pred` beside a
whole part, so such a plant reaches nothing (K35). The `ret_pred` refusal in `implied_by`
is for correctness; no corpus population exercises it.

Re-aimed: S278's `SAB_REACH`. It grepped K66's whole compare
`if (!memcmp(subject + cand, "eeeeeeee~#~#~#~#", 16)) return cand;`, which is now the
led compare. Its intent is unchanged. It is the only reach probe on compare text that
moved (probed: S1421, S267, S279, S285, S449, S464, S571 all still reach).

## 7. Measurements

Method:
- instructions:u via perf_event_open, around the find-all region only;
- `taskset -c 7`, gcc -O2, 3 repeats (they agreed within 8 instructions);
- the driver is subtri's `drv.c` with the substitution part removed
  (`$PCREC_TMPDIR/scratch/r30b/meas/drv.c`);
- base = main 1f5574fac's pcrec, new = the lane tip;
- wall time UNMEASURED (not evidence); the official verdict is a bench run.

| case | subject | base | new | delta |
|---|---|---:|---:|---:|
| 7 url-tld-fix (find-all) | acc-main (sha256 a9b0a4cc..., 361,986,301 B) | 1,279,053,014 | 898,415,587 | -380,637,427 (x1.42) |
| K66 witness, near miss: window passes, first word fails | `Xeeeeeee~#~#~#~#\n` x 1M | 168,180,316 | 159,180,168 | -9,000,148 |
| K66 witness, near miss: scan byte + first word pass, window fails | `eeeeeeee~#~#X#~#\n` x 1M | 117,144,630 | 114,144,554 | -3,000,076 |
| K66 witness, no scan byte | `abcdefghijklmnop\n` x 1M | 1,594,119 | 1,594,119 | 0 |
| 7 pattern, near miss: window passes, first word fails | `Xttps://www.acme.com/\n` x 1M | 117,159,054 | 117,158,963 | -91 |
| 7 pattern, near miss: scan byte + first word pass, window fails | `https:/Xwww.acme.com/\n` x 1M | 78,126,758 | 76,126,724 | -2,000,034 |

Notes:
- Case 7: res 23,986 matches on both sides, and the span hash is identical per repeat.
  The saving equals subtri's attribution of the window pre-check (379M, 11.6%).
  reqvm1's 1,304.9M was the substitution run; this is find-all.
- The near-miss rows are the worst case of §2 (dense candidates). No row moved up. Two
  rows are a tie within the old shape's own cost:
  - the K66 "no scan byte" row: the old window scan found nothing and the whole scan was
    never asked;
  - the case 7 window-passes row (-91 instructions): the window's first hit ends the old
    window scan at once, so both sides pay one whole scan.

## 8. The staged heavy job (dry run only, NOT queued)

- File: `docs/dev/lanes/r30b_job_kit-r30b-heavy`.
- Proposed key: `NNN-kit-r30b-heavy`. The manager picks the priority number.
- Command: `scripts/boxqueue add --name NNN-kit-r30b-heavy docs/dev/lanes/r30b_job_kit-r30b-heavy`.
- The dry run passes (13 steps, 76 mech ids valid at run time, cap 14,400 s).
- Stages:
  - mechval, build, strict;
  - refbuild of 1f5574fac;
  - the census (§5, at -j16);
  - codegen, registry, rxtsource;
  - every memfn section;
  - axes_lever: `AXES=--harness=pres-window tests/axes/run_axes.sh`, the old form's
    answers over the corpus;
  - make test via `scripts/perfrun --label r30b`;
  - mech on the 76 rows: every row on a file R-30 touches (`tests/mech/rows_for.sh`),
    the six plants, S278, S449, S693;
  - reach.
- Expected wall: about 2.5 h (8,500-9,500 s). That is job 622's 9,400 s for 142 rows,
  scaled by this job's 76 rows and fewer stages. It is an estimate, not a measurement.

## 9. Light checks (box lock, `scripts/boxlock run --label r30b-checks`)

CHECKS_RESULT

## 10. Open questions / for the landing

- Commit 38d3143d5 carries the R-30 code and the abi event. The later WIP commit
  d33e0b848 touched `memfn/src/ofsskip.c` again: `verify_chain`'s restructure kept S279's
  anchor line verbatim. That restructure moves no emitted byte: 38d3143d5's build vs the
  tip compared 219 artifacts (the 71 presence/handoff/k66/reqcube patterns, case 7 and
  `(a)..(i)\9`, each at default/vm/utf8), and 0 differ. Even so, the landing may prefer to squash the lane into
  one commit and move the identity (B) FILEPIN to it.
- abi number: 94 assumes trailgc lands 93 first (§4).
- The `ret_pred` refusal has no corpus population (§6). File it if a landmark window
  beside a whole part ever appears.

## 11. Charter vs committed

| charter item | committed |
|---|---|
| drop the window part + its ask where the whole part is present (entry + every re-find, any landmark, both engines) | yes: precheck.c (define + use), census arms c-default/utf8/vm/simd/vm-simd |
| <=8-byte runs and member-piece sites unchanged | yes: no whole part means no implier; census "outside the declared population moved" = 0 required |
| whole-run compare tests the former window's word first | yes: the led compare (runcmp.c `_lead`, ofsskip.c verify_chain) |
| no public deny; a test-only lever via the existing harness mechanism | yes: `--harness=pres-window` + `mf_lever` (no options.def row) |
| pcrec's statement unchanged (req_site_define edits allowed, listed) | unchanged; pcrec-side hunks listed in §3 |
| abi 94, readers by grep, (B) self-pin, spec hunk | yes: §4; tuning.md §2.29¶4 |
| light checks via boxlock run | §9 |
| mover census vs 1f5574fac, every mover a declared both-asks artifact from a pcrec-side read | §5 |
| plants in S1543-S1559, each DETECTED | S1543-S1548, all DETECTED (§6); ret_pred plant not made (no population) |
| measurement: case 7 before/after, near-miss control, K66 witness, absolute deltas | §7 |
| STAGE one heavy job (dry run only) | §8, not queued |
| report + history index entry in the same change | this file + `docs/dev/history/claude_md/docs__dev__lanes.md` |
| CLAUDE.md files whose roles changed | cli/, memfn/src/, memfn/include/ |
| no merge, no push; lanecheck to DONE | yes |

## 12. Addendum (lane r30bfix, 2026-10-31): sections not run before delivery

Job 697 went red (triage: `r30btri_report.md`; no R-30 defect). These sections were NOT run
before delivery, and each was red at job 697 on a stale expectation:
- `test-codegen` (only via `tests/codegen/run_codegen_tests.sh`): `reqcube_check.py`'s k66 row
  still required the window's `rx_reqrun` block R-30 drops. The "71
  presence/handoff/k66/reqcube patterns" probe above was a byte comparison of two lane builds, not
  this check.
- `test-memfn-guarded`: the `simd-form` population floor (6) read 5.
- `test-compound`: the G7 lever fence's allowlist lacked the new plant S1548, which names the lever.

§9's `CHECKS_RESULT` placeholder was never filled in; the light checks' record is §8's staged job.
§4's abi numbering (92 -> 94) is superseded: lane r30bfix merged main 5c60e118c (abi 93) and
renumbered R-30 to 93 -> 94 (provisional). The fixes, the merge and the re-run jobs are in
`r30bfix_report.md`.
