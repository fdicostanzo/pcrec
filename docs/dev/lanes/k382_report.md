# k382 — R-38 K38-2, THE SEAM EVENT (Parts A and B together)

Lane k382 (opus), branch `lane/memfn-k382`. It was cut from lane/memfn-k382a @ 37a6b36ed and
merged main d81ebd294 (K38-2a landed, plus [FEAT-FAMILIES] abi 99) at fc8538569.

- Design of record: `docs/design/memfn/span_runs_sheet.md` rev 1.3 (§2-§5, §5.1, §6), plus its
  §5.1 addendum `[k382]` written in this change.
- Owner's go (2026-11-11): "K38-2. let's finish it now."
- Sabotage ids taken from the reserved S3040-S3069: S3040 and S3041 (EMIT-3, G2 plants), S3042
  (mech), S3060-S3064 (G2 plants plus mech rows).

STATE: DONE

## Summary

pcrec now states the necessary run to the kit UNCUT, as one presence span in set form. The kit
derives the pre-check's ONE run part from that span and from its run decision. The decision's
reply (`mf_class.run`: scan plus verified extent) is answered by `mf_ask` and by `mf_defined`.

- pcrec cuts no window: `PCREC_MAX_REQ_RUN_EMIT`, `req_run_member`, `pcrec_find_run_window_start`,
  the `<p>_reqrun_whole` second part, R-30's led compare and the `pres-window` lever are all gone.
- K is the whole run's position-0 offset (`head_max` int64_t, may be <= 0). The twin admission
  runs at max(K,0), with the mass taken over the reply's extent.
- `<PREFIX>_REQ_RUN` names the whole run. Its `@` comes from a first-match table: the
  pre-check's reply, else the window-site find's member, else no `@`.
- abi 99 -> 100 (renumbered over main's [FEAT-FAMILIES] 99 at the merge). MF_SITE_ABI 27,
  MF_CLASS_V 9.
- Checks:
  - strict and the memfn families are green.
  - test-codegen is green except one check. The merge's [facts-tie] failure is fixed. After the
    last src fix, reqcube and facts were re-run green; the full codegen re-run is gate 605.
  - The G2 presence family is green: 934,050 checks, oracle over 53,592 records, all 11 plants
    RED.
  - The census sample is green (see Movers).
- One real defect was found by the census and fixed (Movers, item 6).

## EMIT-3 first

Commit b8c27d40c is its own commit, made before any seam change. It adds 200 window-family IN-RUN
sites under `run-tie-left`, from their own stream.

- They reach the in-run stop's set-candidate and meet-narrowed branches.
- Plants S3040 (the stop overrides a set candidate) and S3041 (the order reads R's own sets) are
  both RED.
- The lever census has floors.

## Seam event (Parts A and B)

Commits e1c6846e2 and a2e25576c (code), a5d208993 (abi and test readers), 2c3b2097e (cover-row
fix), bda562f50 (the landmark mass reads `req_run`).

Kit side (memfn/include/memfn.h, memfn/src/{compose,finder,kit.h,ofsskip,precheck,presence,
runcmp,window}.c):

1. The run span in set form:
   - nalt 1, start 0, len n, verify NO, core STATED all, wfloor SUBJECT, nterm 0, placed LAST;
   - recognizer `nalt == 1 && nterm == 0`;
   - `omin` < 0 admitted on it only;
   - refusals in `pres_run_check`.
2. The derived run part: FUNC, `fn_ref` only (nalt 0, nterm 0, need 0). `window.c`
   `derive_run_part` builds one RUN term at `ver_lo`, with candidate = run position 0 and floor
   `max(0, lo + omin)` (`precheck.c` `run_floor`).
3. `kit_run_decide` with the mode table `fd_run_modes`:
   - the deciding row P3 gives WINDOW (<= 8 positions around the scan);
   - every other row gives WHOLE;
   - a verify-NO prefilter member gives EXACT_AROUND.
   The ROUTE is the input (K7 U3).
4. `mf_class.run` (`mf_run_reply`) is the one reply spelling (K7 U1). `mf_pres_picks.run_scan`/
   `run_window` are retired, and `MF_PRES_WINDOW` is kit-internal.
5. `head_max` is int64_t. The twin runs at max(K,0) over the reply's extent.

pcrec side (src/gen/emit_dfa.c, src/facts/{facts,kset,req}.c, src/core/{findings,internal,
limits}, cli/main.c):

- `req_pres_spans` states the set form.
- `req_site_define` lays out the derived part and keeps the define's `cls.run` on the Job's
  pre-check record (`MemfnPre.run`).
- K is `whole_maxoff`.
- The run pin and `ofs_test_of` read the whole run.
- The REQ_RUN `@` table is `req_run_at`, asked quietly in the prologue because the stamps
  precede the bodies:
  - row 1: the reply's scan;
  - row 2: the cover find's own window offset (`mf_wreply.stop`) mapped into the whole run, or the
    run-pinned prefilter's member;
  - row 3: none.
- REQ_BYTE stays pcrec's own pick (`pcrec_fact_req_run_stated(cx)->idx`).
- The landmark mass (`req_landmark_hit_ppm`) reads the reply's extent.

## abi package

pcrec abi 98 -> 99 (commit a5d208993), renumbered 99 -> 100 at the merge fc8538569, because main
took 99 for [FEAT-FAMILIES]. Every file holding the number, found by grep:

- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI 100`.
- `tests/codegen/run_codegen_tests.sh`: `ABI_EXPECT=100`, plus the "99->100" transition text
  copied from the changelog.
- `docs/spec/match_api.md`: the guard block (`!= 100`, `(abi 100)`, `PCREC_RX_ABI_H 100`), the
  rx_info table's `100`, and §6¶17 "It is `100`".
- `docs/dev/history/abi_changelog.md`: a new top entry (the populations). The 99 and 98 entries
  are moved to past tense.
- `tests/mech/sabotages/S693_abi_not_bumped.sh`: BEFORE 100, AFTER 99, with a re-aim note.
- `tests/codegen/run_recursion_identity.sh`: (B) FILEPIN self-pinned to bda562f50, the lane's last
  src commit. The manager re-pins it to the landing merge. ABASEPIN is unchanged: no call-free
  region moves.
- `tests/resource/run_resource_tests.sh`: the 767073 pin was measured and is unchanged
  (`a{5,25000}` moves only its abi digits).
- Not a reader: `docs/dev/optloop/gapreport/fixture/fakepcrec.py` (a fake fixture's own text).

MF_SITE_ABI 27 / MF_CLASS_V 9, readers found by `git grep -n "MF_SITE_ABI 27\|MF_CLASS_V 9"`:

- kit: memfn.h (12 hits), compose.c (9), finder.c, kit.h, precheck.c (2), window.c (5);
- G2: g2_pres_gen.c, run_g2_pres.sh, memfn/tests/CLAUDE.md, NOTES.md;
- pcrec: emit_dfa.c;
- fixtures: tests/memfn/arm_fixtures.c, mass_check.c;
- sabotage: S1106.

The historical `MF_SITE_ABI n` texts are unchanged (plan_frame rev2 F25's class). The kit journal
entry and the ledger lines belong to the kit manager; this lane did not write them.

Spec hunks (D80), sheet §4.4:

- `tuning.md`: §2.28¶5/¶7, §2.29¶3/¶4, §2.30¶4, §2.41¶1/¶7a/¶8a/¶8b.
- `match_api.md`: §6.3.1¶5a, §6.3.4's handoff row, §6.3.7¶5/¶6/¶7 (the @ table), the new ¶7a,
  and ¶11.
- `facts_listing.md`: §4.1¶2, §4.1.2¶1/¶7/¶8/¶8b.
- `findings.md`: §4 (the scan-member and window rows, ¶2).
- `registry.md`: `fd-pres-pick`.
- The least-candidate narrowing of §3.3 (sheet §4.4) is in `match_api.md` §6.3.7¶11 and
  `tuning.md` §2.41¶1/¶8a/¶8b. The pre-check returns the least CANDIDATE: no occurrence's
  position 0 lies in `[startpos, c)`, and c holds the verified stretch. It is the least occurrence
  where that stretch is the whole run.

DEVIATION from sheet §4.3/§4.4: the listing rows `req_run`/`req_run_maxoff` do NOT retire. Their
readers keep them:

- REQ_BYTE's pick reads `req_run`'s own index;
- reqcube's C4 lever rows and S3042's reach compare the stamp against it;
- the facts goldens list it.

What changed instead: `facts_listing.md` §4.1.2¶8 now states that `req_run` lists the whole run
with pcrec's own `@idx`, and that `req_run_maxoff` equals `req_landmark_maxoff`. Retiring the rows
is a listing change with its own golden re-pin, left for the stage that retires REQ_BYTE's own
reader (OWED).

## PLAN items (c)-(e) and K7 U1/U3

- (c) FAM-2 (G2 presence family): scan and extent are read off `mf_class.run`, and mf_ask's reply
  must equal mf_defined's. Finding: no K38-2a reader read the reply's `ver_len`. The site extent
  was derived by G2 itself, and the part extent came from `mf_wdecide` on the part's own whole
  statement. So the C2 decision plant (S3064, reply `ver_len` + 1) could not reach at K38-2a; it
  now reaches and is RED by EXTENT.
- (d) ORC-3: the records are in the run frame, with the site's reply and signed omin.
  - The partial-extent-hit floor is 539; measured 599 partial-extent hits over 73 sites.
  - The oracle code (`tests/memfn/occurrence_oracle.py`) is unchanged.
  - The oracle is green over 53,592 records.
- (e) EMIT-3: done first (above).
- K7 U1: `mf_run_reply` is `mf_class.run`'s type, one spelling.
- K7 U3: the route (`need`) is `kit_run_decide`'s input, and the mode is chosen by the declared
  table `fd_run_modes`.
- G2 extension (§3.5 witnesses, expectations generated from the stated rules): W-L1, W-L1b, W-K1,
  W-K2, W-K3, W-K4a and W-K4b are all GREEN and all reach.
  - 171 negative-omin sites.
  - 118 ASSIGN sites with omin < 0, 72 of them with K <= 0.
- Floors changed. Each new value is the measured count with no margin, per the kit manager's
  ruling. Cause: one derived run part per site, since the second whole-run part is gone.

  | floor | old | new | population before -> after |
  |---|---|---|---|
  | NEARMISS | 28540 | 28450 | 31712 -> 28450 |
  | COVER | 11450 | 13992 | 12729 -> 13992 |
  | EXTENT | 5630 | 6944 | 6254 -> 6944 |

  Every other floor keeps its K38-2a literal.
- S3062: the plant reads the re-entry fact itself (the use's `lo` differs from the define's
  `start` hook, the activation's origin), not `!h->result_decl`. That was a proxy, true of every
  ON_MISS entry too. Still RED on W-K2.

## Movers (5.1 populations)

Census: `docs/dev/lanes/k382_evidence/census.py` (README beside it).

- Shape: lane r30b's census shape, because emit_sweep has no abi normalization.
- It predicts the movers from BASE alone (its facts listing and its artifact) and classifies each
  moved line by region. It is two-sided: a predicted mover that did not move, or any unexplained
  line, is RED.
- Floors: P1, P2a, P2b and P3 each >= 1 over c-default+c-vm.
- Arms: c-default, c-utf8, c-vm, c-vm-utf8, c-comments, c-simd, ir, facts, composition, every
  emit_sweep `--extra` identity arm (start: 42 arms; witness via SIMD-witness builds).
- BASE = main d81ebd294 (binary `scratch/memfn/k382/base2/build/pcrec`, from `git archive`).

FINAL sample, run on the frozen 19:40 tip (after the cover-row fix and the landmark mass's
fact). Log: `scratch/memfn/k382/census/s3.log`/`s3.tsv`. Result: 300 patterns, 0 unexplained,
GREEN, with 275 `--extra` arms also at 0 unexplained.

| arm | movers (predicted) | P1 | P2a | P2b | P2s | Aa_K | P3 | P4 (P4f) | other |
|---|---|---|---|---|---|---|---|---|---|
| c-default | 59 (50) | 8 | 13 | 37 | 9 | 8 | 15 | 5 (2) | |
| c-utf8 | 61 (50) | 12 | 17 | 33 | 11 | 12 | 17 | | |
| c-vm | 51 (50) | | 49 | 1 | 1 | | 49 | | |
| c-vm-utf8 | 52 (50) | | 49 | 1 | 2 | | 49 | | |
| c-comments | 62 (53) | 8 | 13 | 37 | 9 | 8 | 15 | 5 (2) | P5 16, P5k 9 |
| c-simd | 59 (50) | 8 | 13 | 37 | 9 | 8 | 15 | 5 (2) | P3v 1 |
| ir | 0 | | | | | | | | |
| facts | 63 | 31 | 63 (P2) | | | | 4 | 25 | used 2 |
| composition | 1 of 444 files | 1 | 1 | | | 1 | 1 | | |

Key to the columns:

- Every P2s member is the dominated kind (P2sd): no run-part find is rendered, and no window-site
  find is on a run member.
- Aa_K: the landmark admission or NEXT pick moved WITH K, so it is inside population 1.
- Admission or pick moves with K UNCHANGED (Aa_noK) occur on 2 artifacts:
  - which: `[a-z]abcdefghijklmnopqrstuvwx[0-9]` and one other, on the `-fno-req-handoff` and
    `start -fno-req-handoff` arms only;
  - cause: they are population 4's predicted `dominated` -> `emitted` flips (P4f). The whole run
    pin (`run_pin` 10 -> `1:0+23`) leaves run positions past the walk unverified, so REQ_WHY flips;
  - with the handoff denied, K cannot move, so the census files them as no-K admission moves;
  - none is the landmark mass alone.
- The landmark mass reader (`req_landmark_hit_ppm`):
  - Fate: §4.1's `ver_lo`/`ver_len` reader, required by §3.2 `[r1 F6]`. pcrec's mass and the kit
    twin's read the reply's extent in the same commit.
  - It reads the `req_run` fact as before, which is now uncut. The build-time switch to
    `req_whole_run` was reverted (2c3b2097e..bda562f50), so the lookbehind `used` flip is gone.
  - Over the sample, no admission or pick moves with K unchanged other than the P4f pair above.
    That is the "1m" population of the sheet's addendum: measured 0 on the sample, with the full
    count at gates 601-603.
- facts `used` 2: those same two P4f artifacts. Once emitted, the pre-check asks `req_set` and
  `req_landmark_maxoff` (population 4's consequence).

Earlier samples were run before the fixes: 300 patterns against BASE 37a6b36ed, then against
d81ebd294. They found the cover-row defect (item 6 below) and the `used` flip.

Also confirmed:

1. The four sheet populations predicted for runs > 8 (P1, P2a, P2b, P3) are populated.
2. P4: the run pin over the whole run, with the dominated->emitted flips counted inside it.
3. P5: `-fcomments` text.
4. Witnesses confirmed by hand on the tip:
   - `(?:ab|cd)xabcdefghijkq`: K 7 -> 2.
   - `xabcdefghijkq`: `65666768696a6b71@7` -> `786162636465666768696a6b71@12`.
   - `hello world --engine=vm`: `rx_reqrun_whole` -> `rx_reqrun`, and `RX_MEMFN_LIBC` loses
     `memcmp`.
   - `/abcd[xy]/user` (no-window-search): run pin 6:6+2 -> 6:6+5.
5. Unpredicted, ACCEPTED as declared populations (kit manager), and written into the sheet's §5.1
   addendum `[k382]`:
   - P2s, `@` dropped on short runs. Rule: no scan position (no `<p>_reqrun` block, no run-pinned
     prefilter, a cover find outside the run). Examples: `(a)(b)`, `0x[0-9a-fA-F]+`, `\Aab\Z`,
     `[0-9]+ABCDEFGH`, and `abcdefg(?=x)` (the cover find reads `x`). Outside C4's population.
   - P5k: the [K82] comment becomes "whole run" on uncut runs too.
   - P3v: one `-fmemfn-simd` artifact (`(x?)(?i:abcdefghijkl)\1`) gains `vrun@w16`.
   - The facts `used` flip of `req_whole_run` on lookbehind patterns (seen at the second sample):
     REMOVED. The landmark mass reads the `req_run` fact again (bda562f50).
6. DEFECT FOUND AND FIXED (2c3b2097e). The census's 22 unexplained artifacts were real: the cover
   row of the `@` table read `mf_wreply.run_member` (R's member) as a window offset. A cover window
   longer than the run therefore lost its `@` (`(a.){10}xyz` --no-captures, `\p{Emoji_Modifier}`
   utf8). It now maps the find's own offset (`stop`): both keep `@2` as at BASE, `abcd.efgh` keeps
   `@1`, and reqcube is 106/0.
   NOTE for the kit manager's ruling 1, which widened P2s to accept these 22 as "dominated, so
   no `@`". I kept the sheet's §4.1 table instead. Row 2 gives a dominated `cover` artifact an `@`
   wherever its window find reads a run member, and BASE stamped exactly that. These 22 are
   therefore NOT movers now. The census's P2s rule follows the table: no run-part find, and no
   window-site find on a run member. If the ruling is that every dominated artifact drops its
   `@`, that is a one-line change to `req_run_at` plus a spec edit to table row 2. Raised for the
   critic round.

Negative controls, all RED:

- `--control no-p3`: 158 unexplained;
- `--control no-norm`: 1566;
- a BASE-equal tip: 294 predicted movers did not move.

## Sabotage fates

Anchor check: `python3 -I scripts/m6read_check_sab_anchors.py` reports 1237 rows, all anchors
resolve (0 stale). REACH_ONLY verdicts could not be taken on the box: the lock was held by queue
jobs. The probes were evaluated by hand on the tip, and the formal verdicts are gates 606-609.

- Re-anchored (same intent):
  - S1095: the T_MASS_SET plant on kit_run_decide's one kit_run_member call; also moves
    window.c's verify-NO member.
  - S1097, S458: `<` -> `<=` against `scan_mass`.
  - S1106: the omin<0 refusal is member-span only now.
  - S1420: rank_n planted before the derived part.
  - S286, S288: the P2 block reads `rs`.
  - S3005: the twin loop over the reply extent.
  - S448: `ofs_test_of` over the whole run.
  - S452: coverage over the reply extent.
  - S453: whole/whole_mask.
  - S459: `order != 1`.
  - S463: the `whole_len` context line.
  - S811: the `k > 0 ? k : 0` anchor.
- Re-aimed:
  - S1103: the member half; its run half is S278's plant.
  - S1107: the head/rest halves through `pres_layout_check`; the run half cannot disagree (a
    statement rule), and S1095 is the per-reader tie plant.
  - S1700: onto the kit's ASSIGNed value, `precheck.c` `run_line`; detector handoff_vm.rxt.
  - S280: the per-placement byte test in kset.c's clipped loop; probe on the 11-position run.
  - S460: the gate block against the derived part.
- DEVIATION from the sheet: S278 is KEPT and re-aimed (kit manager's ruling). The sheet retired it
  because the old plant (`pk.run_window`) no longer compiles. Retiring it would leave K66's
  whole-run answer with no plant. The new plant adds a `{ "P0", KIT_RUN_WINDOW }` row to
  `fd_run_modes[]`, so P0 verifies an 8-window. Reach: REACH-K66-WHOLE-RUN-EMITTED. Condition: it
  must be DETECTED at the gates; if not, retire it and name the replacing control.
- Retired (git rm):
  - S1543, S1544: R-30's window beside the whole part. Control: the one-run-part statement rule.
  - S449: K66's second part. Controls: S3011, reqcube's K66 cells.
  - S1545, S1547: R-30's led compare.
  - S1546: suspected and confirmed; its reach was MISSING.
  - S1548: the `pres-window` lever; its successor is S3009. Its ALLOW entry and comment in
    `tests/compound/run_lever_fence.sh` were removed at the merge.
- New rows:
  - S3042: the REQ_RUN `@` fed pcrec's index. Planted on a scratch copy, it is DETECTED by
    reqcube's C4 lever rows (3 FAIL).
  - S3060-S3064 (G2 plants plus mech rows):
    - S3060: the run floor is lo.
    - S3061: lo - N wraps.
    - S3062: the re-entry floors at lo.
    - S3063: K read unsigned.
    - S3064: the reply claims one more position.
    Each is RED by its own detector, and VALIDATE_ONLY passes.
- Sheet rows not on the stale list: S329 and S285 still anchor, so their re-aims are checked by
  REACH_ONLY at the gates.
- Not edited: `S1543` in run_g2_win.sh (G2's own plant id), and `S449` in gen_reqcube.py/
  reqcube.rxt/reqcube_check.py (the design-provisional id, now S450).

## Checks

| check | result |
|---|---|
| `nice make -j4`, `make strict` | clean, after the merge |
| `make test-codegen` (PROCS=2, after the merge) | 1 FAIL, [facts-tie], fixed in 209729226; `run_facts_checks.sh` rc=0 |
| reqcube_check.py, after the cover-row fix | 106/0 |
| `run_prechecks.sh` (before the merge) | 395/0 |
| full test-codegen on the final tip | gate 605 (OWED) |
| `make test-memfn-finder test-memfn-rows test-memfn-link test-memfn-targets` (after the merge) | green: finder 1108, purity 1157 plus its plants RED, mass 43, targets 42/0, no make Error lines |
| G2 presence family (G2_JOBS=2) | 934,050 passed, 0 failed; oracle 53,592 records green; lever 24/24 per target; 11 plants RED |
| `tests/compound/run_lever_fence.sh` | PASS |
| anchors | 0 stale |
| resource pin | unchanged |

BASE-vs-tip samples: `foo.*barbaz`, `a.{1,50}zz`, `ab+cdefgh`, `abc` and `(?i)hello` are SAME;
the population witnesses are listed under Movers.

## Gate jobs

The jobs are in `/var/tmp/pcrec-pcrec/scratch/memfn/k382/jobs/` (common.sh, ident.sh, mech.sh,
basis.py). They were prepared but NOT queued. All ten `--dry-run` rc=0. BASE is d81ebd294 with the
base2 binary; the jobs check abi 99 on BASE and 100 on the tip.

- 600: strict.
- 601-603: census shards over the whole corpus. Shard 1 also runs emit_sweep's dumps stream with
  two declared rows (`PCREC_MAX_REQ_RUN_EMIT` gone, `PCREC_MAX_REQ_RUN_SCAN` changed), declared on
  EVERY arm that carries dumps, found from the arm list (today `base` and `start`).
- 604: reach, re-pointed. GONE/MAP were derived from the BASE reach log: they are empty, and the
  31 REACH keys are equal on both sides. Absent or extra keys stay RED.
- 605: the memfn quick families plus test-codegen. This replaces a box make test (no box job for
  make test).
- 606: plants: 28 G2 window plants, 11 presence plants, and S3042 through
  `run_sabotage_matrix.sh` (with its REACH_ONLY probe).
- 607-609: mech, 393 rows. The set is the previous rows, plus rows_for over the diff, plus the
  edited rows, plus NEW_ROWS S3042 and S3060-S3064, minus the 7 retired rows. It runs overnight;
  main queues it.

Cloud lines. Per `scripts/entry cloudrun`, `cloudrun` pushes its own cloud ref, and the branch
now carries main's cloud-test.yml after the merge:

```
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind test --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind axes --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind ubsan --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind asan --ref lane/memfn-k382
```

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| EMIT-3 first | yes, b8c27d40c |
| set-form run, derived part, mf_class.run, signed omin/K, twin at max(K,0) over the reply, pres-window retired | yes, e1c6846e2 and a2e25576c |
| pcrec readers §4.1-§4.3, REQ_RUN @ table, K = whole_maxoff, run pin whole | yes, plus the cover-row fix 2c3b2097e |
| abi event, readers by grep, recorded | yes, 99 -> 100 after the merge; files listed |
| MF_SITE_ABI move, readers recorded | yes, 27 / MF_CLASS_V 9; files listed |
| spec hunks §4.4 | yes, with one deviation: the listing rows kept (stated above) |
| movers only in §5.1 populations, two-sided | census green on the sample; the unpredicted populations are ruled and in the sheet's addendum; full count at gates |
| fates S1700, S448, S1548, S280, S1546, S1107 (REACH_ONLY) | fates done; REACH_ONLY probes checked by hand; formal at gates |
| G2 presence family: neg omin, signed K, FAM-2, ORC-3, W-* | yes, green |
| gate jobs 600-609 + cloud lines, dry-run | yes |
| report, lanecheck | this file |

OWED:
- The full census and all formal sabotage verdicts (REACH_ONLY, mech) are gates 601-609.
- Full test-codegen on the final tip is gate 605.
- Retiring the `req_run`/`req_run_maxoff` listing rows is deferred (its reader is REQ_BYTE's
  pick).
- The kit journal and ledger lines belong to the kit manager.
- (B) FILEPIN (self-pinned to bda562f50) must be re-pinned to the landing merge.
- The 20:00-01:00 hold applied: nothing heavy ran after 19:58.

## STATE AT HANDOFF

- Branch lane/memfn-k382 is committed and clean.
- Gate jobs 600-609 are prepared and dry-run, not queued (`scratch/memfn/k382/jobs/`).
- The cloud lines are above.
- The critic round follows.
- Re-pin FILEPIN at landing.
