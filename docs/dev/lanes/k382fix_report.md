# k382fix — the ruled findings of review 2026-11-11 r1 k382 applied to K38-2

Lane k382fix (opus), branch lane/memfn-k382 in worktrees/k382. BASE is main d81ebd294 (abi 99). The
abi stays 100.

## Summary

All of F1-F19 are applied as RULED. The F2 trace found the dominance ask reachable without a
cycle, so the lane did not stop.

- **Dominance (F2).** It now reads the kit's run reply. The run-pinned long runs are `dominated`
  again, as at BASE, and P4f is 0 on the sample.
- **Run floor (F1).** There is one run floor, `kit_run_floor`, read by both the pre-check row and
  the generic row. G2 gained a generic pass (`on_miss_leaves` 0) with a PRESENCE rule.
- **Listing rows (F5).** The `req_run` and `req_run_maxoff` rows are retired, together with
  `ReqRun.idx`/`len`, `pcrec_req_window` and `pcrec_req_run_masked`.
- **REQ_BYTE (F10).** It is rendered from the `req_byte` fact.
- **Run modes (F12).** P0, P3 and P9 are listed explicitly; an unlisted row is refused.
- **Run-span member (F13).** `member` on the run span is 0.
- **Controls.** New G2 controls cover F14 (two refusals) and F16 (W-K1b).
- **Rows.** There are six new sabotage rows (S3043-S3048) and six re-aimed or re-anchored rows.
- **Spec.** The spec hunks for F2, F5 and F6 are in place (D80).
- **Census.** The sample of 300 is GREEN with 0 unexplained.
- **Checks.** Every check named in the brief is green.
- **Gate jobs.** 600-609 are re-pointed and pass `--dry-run`. They are NOT queued.

## Findings F1-F19 (one line each: done or why not)

- F1 done:
  - `kit_run_floor` (presence.c) is read by precheck.c and generic.c, so there is no second copy.
  - G2 has a generic pass (354 sites) with a PRESENCE rule and floors.
  - Plant S3043 (the generic loop starts at `lo`) goes RED by its detector.
- F2 done: `ofs_test_verifies_run` asks `req_pres_ask` with the proof stated before its run
  verdict, and tests the reply's scan and `[ver_lo, ver_lo+ver_len)`. The trace is below.
- F3 done: `req_run_in_cover` resolves among the placements that contain the find; `abcd[0-9]abcd`
  stamps `61626364@1`, as BASE does.
- F4 done:
  - `req_note_run` and the kit's `run_comment` name the whole run.
  - Where the stretch is partial, they add the positions compared.
  - A whole stretch keeps BASE's text.
- F5 done: the rows are retired (details in "F5 retirement"), and the spec, test readers, mech rows
  and census are updated.
- F6 done:
  - tuning §2.27¶4 (REQ_BYTE is pcrec's pick), §2.28¶1 and ¶5 (positions vs bytes), §2.29¶4 (head
    and window owner);
  - findings §4 (the kit's window; "the pinned stretch");
  - registry `fd-pres-pick`;
  - match_api §6.3.7¶6's example (`.tar` is `@0`, the cover find).
- F7 done: `pcrec_req_run_masked` and its comment are deleted.
- F8 done: `run_tested` is deleted. The struct comment names the readers that re-ask:
  `req_run_at`, `req_landmark_hit_ppm`, `req_parts_in_whole` and `ofs_test_verifies_run`.
- F9 done:
  - The `pres-window` shard word is gone from cloud_axes_shards.tsv, and `cloud_axes_check`
    passes.
  - The wf_ties bases and memfn/src/CLAUDE.md are restated.
  - The dead-word check is filed as PLAN (f) in the sheet's §5 K38-2 row.
- F10 done: the REQ_BYTE stamp is `pcrec_fact_stamp(cx, PF_REQ_BYTE)` and its comment is restated.
  Goal 2's measurable form is amended to the code: three callers, all pcrec's own picks, none on
  the pre-check.
- F11 done: the texts in window.c, memfn/src/CLAUDE.md and decider_census.tsv rows 55-56 are fixed.
  The NOTED step toward §6 Q6 (1) is recorded in the goal-2 amendment and the addendum.
- F12 done:
  - `fd_run_modes[]` lists P0 WHOLE, P3 WINDOW and P9 WHOLE, and refuses an unlisted row.
  - Plant S3045 goes RED.
  - PLAN: "the stretch as a row column" is folded into PLAN (a).
- F13 done: `member` on the run span is 0. Plant S3044 goes RED, and the finder fixtures now read
  m0.
- F14 done: the generator has controls (ii) and (iii), each of which must be refused BY ITS OWN
  RULE (353 sites each, with floors). Plants S3046 and S3047 go RED.
- F15 done:
  - New row S3048 (K66 mask dropped to 0xFF) goes RED by hand on reqcube_check (k66 witness and
    `(?i)select`).
  - `k66_precheck_whole_run.rxt` stays 16/16 under the plant, so it is recorded as NOT a detector.
- F16 done, first choice:
  - Witness W-K1b is W-K1 with the scan at offset 0 < N - origin.
  - S3061 now reds on the ANSWER: in layout U on the generic pass, and in layout L on the precheck
    pass. In layout U on the precheck pass, the wrapped floor reads 2 bytes below the subject and
    the whole-run verify rejects them, so the answer holds there.
  - The row and the plant expectation require both answer lines.
- F17 done: the re-pin procedure, steps (a)-(c), sits in the run_g2_pres.sh header beside the
  floors.
- F18 done: the sheet's §5 column says S1545, S1546 and S1547 were retired with their code, with no
  successor.
- F19 done:
  - DOC: the 2s sentence now covers landmark-walk, rev-end and one-attempt (addendum).
    `req_set_leads_own` is named a trace shadow in §4.1.
  - NOTED items unchanged.

## F2 dominance trace

- **Asking with a NULL proof cycles:** `ofs_test_verifies_run` -> `req_pres_ask` ->
  `req_pres_site` -> `req_pres_proof_quiet` -> `dfa_cand_scan` -> `cand_row_scan` ->
  `ofs_test_verifies_run`.
- **Asking with an EXPLICIT proof** (`req_pres_proof_of(cs)`, stated before the run verdict, `run`
  0) builds the site from that proof and does not re-enter `dfa_cand_scan`, so there is no call
  cycle.
- **Under `run` 0 with a run stated,** the kit's P2 (G1 dominance) declines. The run's link is
  then decided by its route alone, and the reply is exactly the stretch an emitted pre-check would
  verify. That is the reply the dominance must cover, so the ask is REACHABLE and the lane did not
  stop.
- **Results:**
  - `Connection refused by remote host`, `error: segmentation fault at`,
    `[a-z]abcdefghijklmnopqrstuvwx[0-9]`, `hello world` and `(?i)hello world foo bar` are all
    `dominated`, as at BASE.
  - P4f is 0 on the census sample.
  - A pinned stretch that does not cover the reply keeps its pre-check (tuning §2.30¶1).

## F5 retirement

- **Removed:**
  - facts.def rows REQ_RUN and REQ_RUN_MAXOFF, and their clear/derive/render arms;
  - `pcrec_fact_req_run(_stated)`, `pcrec_fact_req_run_maxoff` and `pcrec_fact_stamp_req_byte`;
  - `ReqRun.len`/`idx`, `pcrec_req_window` and `pcrec_req_run_masked`.
- **Renamed:** the readers use `pcrec_fact_req_whole_run(_stated)` and `whole_len`.
- **Dependencies moved:** REQ_BYTE <- req_set + req_whole_run; REQ_LANDMARK_MAXOFF <-
  req_set_maxoff + req_whole_run + req_byte; RUN_PIN <- kset_walk + req_whole_run.
- **`pcrec_req_pick`** computes the index in place.
- **Spec:**
  - facts_listing §4.1¶2 (the `used` move), §4.1.2¶1/¶8/¶8b, §4.1.3¶4a;
  - tuning §2.27¶5, §2.28¶8, §2.39¶4;
  - findings §4¶2.
- **Tests:**
  - run_facts_checks.sh: the `req_run` rows are dropped; 14/14 pass.
  - reqcube_check.py: the C4 lever compares against the default build's `@`; 106/106 pass.
  - run_prechecks.sh: comments only.
- **Mech rows:**
  - S3042 is re-aimed: the plant makes `req_run_at` answer pcrec's pick, and the reach compares
    against the default build's stamp. Its REACH_ONLY probe is reached.
  - S299 is re-aimed to the `req_pieces` row's deny bit. It went RED by hand on [facts-why]
    (13/14), and still moves no emitted byte.
  - S1908's reach now reads `req_byte`; its REACH_ONLY probe is reached.
  - S453 is re-anchored on the in-place pick. The anchor check shows 1243 rows, all resolving.
  - Comments are updated in axes_dump.c, req.c and src/opt/NOTES.md.

## Movers re-count (5.1 addendum)

The census is `census.py --sample 300 --jobs 2` against BASE (`k382/base2`), at the tip after the run-note period fix. Log: `scratch/memfn/k382fix/census2.{log,txt}`. The verdict is
**GREEN, 0 unexplained**, and all 275 `--extra` arms are at 0.

| arm | movers | P1 | P2a | P2b | P2sd | Aa_K | P3 | P4 (P4f) | other |
|---|---|---|---|---|---|---|---|---|---|
| c-default | 58 | 5 | 10 | 38 | 10 | 5 | 12 | 5 (0) | |
| c-utf8 | 59 | 11 | 16 | 32 | 11 | 11 | 16 | | |
| c-vm | 51 | | 48 | | 3 | | 48 | | |
| c-vm-utf8 | 51 | | 48 | | 3 | | 48 | | |
| c-comments | 62 | 5 | 10 | 38 | 10 | 5 | 12 | 5 (0) | P5 15, P5k 9 |
| c-simd | 58 | 5 | 10 | 38 | 10 | 5 | 12 | 5 (0) | P3v 1 |
| ir | 0 | | | | | | | | |
| facts | 281 | 29 | 60 (P2) | | | | 4 | 24 | Fret 281, used 92 |

- **P4f went from 2 (k382) to 0.** The flips are reverted by F2. Aa_noK is 0.
- **Fret is new.** Both listing rows are gone on every listing.
- **`used` 92:** the `req_whole_run` no -> yes moves, where BASE's `req_run` was `yes`. They are
  declared, and supersede the k382 addendum's "used does not move".
- **P5 needed no widening.**
  - The first sample (census1) was RED with 143 comment-only movers. The cause was my F4 code
    dropping the run note's closing period on a whole stretch, which is a defect, not a population.
    It was fixed in commit "the whole-extent run note keeps its closing period".
  - That RED is also the census's negative control: a comment-only edit outside the declared
    populations came out UNEXPLAINED, so P5 (allowed only beside a P1-P4/P5k move) is not vacuous.
  - The new partial-stretch text rides only on P3 movers.
- **Sheet:** the populations are recorded in the sheet's §5.1 addendum `[k382fix]`.
- **Census tool:** `Fret` was added to the populations and documented in its docstring.

## New controls and sabotage rows

Each plant below was shown RED by hand by its own detector (logs `scratch/memfn/k382fix/plants*.log`):

| id | finding | plants | detector |
|---|---|---|---|
| S3043 | F1 | the generic loop starts at `lo` | G2 generic pass, PRESENCE and W-L1 |
| S3044 | F13 | `if (!member) k.member = 0;` deleted | G2 generator link check ("`member` is not 0 on the run span"); also the finder fixtures |
| S3045 | F12 | P3 renamed out of `fd_run_modes[]` | G2: mf_ask refused |
| S3046 | F14 (ii) | `pres_layout_check`'s run-part refusal deleted | G2 control (ii) |
| S3047 | F14 (iii) | `wf_parts_check`'s second-part refusal deleted | G2 control (iii) |
| S3048 | F15 | K66 run mask stated as 0xFF | reqcube_check (k66 witness, `(?i)select`) |
| S3061 | F16 (re-aimed) | the floor wraps | W-K1b's answer (generic U, precheck L) |
| S3060/S3062 | re-aimed | (kit_run_floor) | W-L1b / W-K2 |
| S299 | F5 (re-aimed) | `req_pieces` deny bit | [facts-why] |

Controls:

- G2 generic pass: floors GENERIC, PRES_CHECKS and PRES_BELOW.
- F14 controls: floors CTL_NOPART and CTL_TWO.
- W-K1b: the witness line requires `K1b=1/1`.
- New reach token: `REACH-G2P-GENERIC-FLOOR` (n=291).

Every new mech row is in mech.sh's NEW_ROWS. The S3043-S3047 plants are in run_g2_pres.sh's
PLANTS list, which job 606 runs.

## Checks

All runs used parallelism 2 under `nice` (`-n 10` after the manager's note).

| check | result |
|---|---|
| make strict | clean |
| make test-codegen (PROCS=2) | rc 0, 21/21 scripts in the last group, no `*** [test-` error |
| test-memfn-finder | 3414/0 (after the F13 fixture update) |
| test-memfn-rows | 97/0 |
| test-memfn-link | 11/0 |
| test-memfn-targets | 42/0 |
| G2 presence family, every pass incl. generic (G2_JOBS=2) | 1,123,853 passed / 0 failed; oracle green over 53,790 records; witnesses incl. K1b 1/1 |
| G2 presence `--plants` (16 plants) | 16/16 RED by their own detectors, rc 0 (`scratch/memfn/k382fix/plantsall.log`) |
| `--reach` | 8 tokens, all > 0 |
| anchors (m6read_check_sab_anchors.py) | 1243 rows, all resolve |
| census sample 300, -j2 | GREEN, 0 unexplained |
| facts checks / reqcube_check | 14/0 and 106/0 |
| cloud_axes_check / decider_census | PASS / 97/0 |
| check_claudemd_size --all | 364 within limits |

## Gate jobs

The jobs live in `/var/tmp/pcrec-pcrec/scratch/memfn/k382/jobs/` (the originals are copied to
`scratch/memfn/k382fix/jobs.orig`). They read HEAD at run time, so they cover the fixed tip. Every
`--dry-run` passes (rc 0, 600-609). None is queued.

- **600:** runs `make test-claudemd-size` after strict; its trailer reports `claudemd=N`.
- **601-603:** the census shards are unchanged. They run the updated census.py (Fret).
- **604, 605:** unchanged.
- **606:**
  - PRES_PLANTS now includes S3043-S3047, 16 plants in all.
  - NEW_ROWS is S3042 S3048 S1908, with a REACH_ONLY pass by hand: 3/3 reached.
  - It adds the presence `--reach` step with all 8 tokens, the GENERIC-FLOOR token being new.
- **607-609:**
  - NEW_ROWS adds S3043-S3048.
  - The re-aimed rows (S299, S1908, S3042, S3061, S453) come in through the row-file diff.
  - In all, 406 rows over the three shards.

Cloud lines, unchanged from k382:

```
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind test --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind axes --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind ubsan --ref lane/memfn-k382
/home/pcrec/projects/pcrec/scripts/cloudrun --owner kit --kind asan --ref lane/memfn-k382
```

FILEPIN: (B) `run_recursion_identity.sh` is still self-pinned to bda562f50, k382's last src commit.
The fixes move bytes (F2, F3, F4), so the manager must re-pin it to the landing merge, as the k382
report already notes. `test-recursion-identity` is not in test-codegen and was not run.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| F2 trace first, STOP rule | yes; reachable, trace above |
| F1, F5, F13, F12 in order, then the rest | yes, every one of F1-F19 |
| movers re-counted vs BASE, §5.1 addendum in the same change | yes, census GREEN; addendum `[k382fix]` |
| every new or changed check has a plant shown RED | yes (table above; S3048 and S299 by hand builds) |
| new rows in NEW_ROWS, new reach probe in 606 | yes |
| abi stays 100, FILEPIN note kept | yes |
| check_claudemd_size after C changes | yes |
| checks as listed | yes (table) |
| gate jobs re-pointed, 600 + claudemd-size, dry-run, not queued, cloud lines kept | yes |

## STATE AT HANDOFF

- Branch lane/memfn-k382 is committed (WIP commits as listed in `git log d81ebd294..HEAD`).
- Gate jobs 600-609 are dry-run and NOT queued.
- FILEPIN must be re-pinned at landing.

OWED: none
