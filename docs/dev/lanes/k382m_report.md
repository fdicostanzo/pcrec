# k382m — K38-2 brought up to date with main, abi re-bumped 100 -> 101

Lane k382m (opus), branch lane/memfn-k382 in worktrees/k382. The new BASE is main e889ba64c
([PFFIX] abi 100, the D27 `\p` corpus, the cloud mech/recid kinds). K38-2 lands SECOND, so it
takes abi 101.

## Summary

- **Merge.** Main e889ba64c merged in 5880ecb2c. Five files conflicted, and each was resolved on
  its merits. `make strict` is clean.
- **abi.** The abi is 101. Every reader of the number was found by grep. The recursion-identity
  FILEPIN self-pins to the merge (2a0116b75).
- **Census.** The census against the new BASE is GREEN on the 300-pattern sample, with 0
  unexplained.
  - The first sample was red on one pattern. The cause was a bug in the census, not in K38-2.
  - Main's new corpus shifted the sample onto a pattern the old sample never drew, and that
    pattern exposed the bug. The census is fixed.
- **Cloud reds.** All but one cloud red was REAL. The odd one out was the rung, which came from
  the stale base. Run 43165322653 ran on the branch's own shard table.
  - The real reds are K38-2 readers that the sheet's §4.3 declares moved, but the branch never
    moved them. K38-2's lanes ran no `make test`.
  - All are fixed except test-findings §7/§8. That one waits on a ruling about the findings reader
    c2b (see Cloud reds).
- **Gate jobs.** Jobs 600-609 are re-pointed to BASE e889ba64c and pass every `--dry-run`. They
  are NOT queued.

OWED: test-findings §7/§8 (the c2b reader's fate, a ruling asked of main 2026-11-12; nothing else
is owed)

## Merge and conflicts

`git merge main` ran alone in its own command. It conflicted in five files:

- `docs/dev/history/abi_changelog.md`: K38-2's entry reads "is `101` ... 100 -> 101", and it
  notes the re-bump over [PFFIX]. Pffix's entry becomes "was `100`".
- `docs/dev/history/claude_md/docs__dev__lanes.md`: both sides' index entries are kept. K38-2's
  entry notes the re-bump.
- `tests/codegen/run_codegen_tests.sh`: the `[DD-14.FB]` transition string is main's (it ends
  `99->100: [PFFIX]`) plus K38-2's text as `100->101`. `ABI_EXPECT=101`.
- `tests/codegen/run_recursion_identity.sh`: the FILEPIN self-pin, re-pinned to the merge
  5880ecb2c in the next commit (a commit cannot name itself). ABASEPIN stays main's e41ac3534,
  because K38-2 moves no call-free program region; the branch kept its base's ABASEPIN through
  K38-2.
- `tests/mech/sabotages/S693_abi_not_bumped.sh`: re-aimed with BEFORE 101 and AFTER 100.

Everything else merged clean. That includes `src/gen/emit_dfa.c` and `docs/spec/match_api.md`,
which both sides touched. After the merge, `make` and `make strict` are clean.

## abi 101 re-bump (readers by grep)

The grep was `(abi|ABI)[^0-9]{0,40}\b100\b|\b100\b[^0-9]{0,25}(abi|ABI)`, plus `abi 100`,
`99 -> 100` and `ABI_H 100`, over the tree. It excluded only the history, reviews, journal and
lane reports. Main's own bump commit f1304934d was used as a cross-check of the reader set.

Readers moved:

- `src/gen/emit_dfa.c` `PCREC_ARTIFACT_ABI 101`.
- `docs/spec/match_api.md`:
  - the guard `!= 101`;
  - the `#error` text "(abi 101)";
  - `#define PCREC_RX_ABI_H 101`;
  - the rx_info table row (`101`);
  - §6¶17 "It is `101`".
- `tests/codegen/run_codegen_tests.sh` `ABI_EXPECT` and its message.
- S693 BEFORE/AFTER.
- `abi_changelog.md`.
- The recid FILEPIN.
- The census defaults (`--abi 100:101`, `--base-rev e889ba64c`) and its README.

The remaining hits are historical or explanatory ("since abi 100", pffix's notes), so they stay.
`match_api.md` §6.3.6's `"empty"` row ("abi 100") dates pffix's change and also stays.

The abi number keeps its width (3 digits), so no size pin moves with the digits.

## Census against the new BASE

BASE is a niced `git archive e889ba64c` build at `$PCREC_TMPDIR/scratch/memfn/k382m/base/`
(abi 100). NEW is the tip (abi 101). The command was
`census.py --abi 100:101 --base-rev e889ba64c --sample 300 --jobs 4`. Logs are
`scratch/memfn/k382m/census{1,2,3,4}.{log,txt}`.

- **census1: RED, 2 unexplained.** Both were `^(a)(b)(c)(d)(e)(f)(g)(h)(i)(j|k)(?-10)$` on the
  identity arm `start:utf8+-fno-req-run-fold`, at c-default and c-vm. The verdict was "a MUST move
  is not the declared one (P2)".
  - **Not K38-2's.** The pattern is old (it is in d81ebd294's corpus). It surfaced now only
    because main's d27 corpus changed the corpus the sample's even spread is drawn from.
  - **The cause was a census bug.** Every x-arm predicted from BASE's DEFAULT facts listing (only
    `-i` had its own listing).
    - Under `-fno-req-run-fold`, BASE's run is the unfolded `616263646566676869`.
    - The default listing gives the folded `6162636465666768696a/ff..fe`.
    - The utf8 cut window `6263646566676869` is the same in both, so the MUST fired against the
      wrong whole run. The tip's stamp is in fact the arm's whole run.
- **The fix (`census.py`).** BASE's facts listing is now read under the arm's own flags, engine
  and encoding. A listing BASE refuses, where BASE still compiles the arm's artifact, is a
  problem on the arm, never a silent fall-back. census2 and census3 found the two cases this
  needs:
  - `-fprefilter` is VM-only.
  - `--emit-facts=byte,utf8` refuses what a one-encoding arm compiles (`(*UCP)x\B` under the VM;
    the utf8 `\p` classes; one pattern that is too large in both encodings).
- **Did main's new content move anything?** No artifact moves BECAUSE of main's content. Both
  sides carry pffix's empty engine and the d27 corpus. No sample pattern is unexplained, and the
  population counts are K38-2's alone.
- **census4: GREEN, 0 unexplained.** Selected arms:

  | arm | movers | must | P1 | P2a | P2b | P3 | P4 |
  |---|---|---|---|---|---|---|---|
  | c-default | 38 | 32 | 4 | 9 | 23 | 11 | 5 |
  | c-vm | 32 | 32 | — | 31 | 1 | 31 | — |
  | ir | 0 | — | — | — | — | — | — |

  The facts arm had 274 movers, all of them Fret.
- **Negative control.** `--control no-norm` on two witnesses is RED (18 unexplained), so the
  normalization is load-bearing.

## Cloud reds

Run 43165322653 (`cloud/kit/test/lane-memfn-k382-e5d0977`) used the BRANCH's own shard table.
Its red shards were 6, 9, 11, 13, 15 and 17, and shard 1 was green. The red sections are taken
from the job logs (the make `***` lines). Each was then re-run on the merged tree, in
`scratch/memfn/k382m/reds.log` and then `reds2.log`.

| shard | section | cause | stale base or K38-2 | now |
|---|---|---|---|---|
| 11 | test-resource | the `a{5,25000}` rung read 767075 against the branch's pin 767073 | STALE BASE: pffix2 re-pinned it on main; the merged tree reads 767075 = pin, and K38-2 does not move it | green |
| 6 | test-memfn-manifest | `site_manifest.tsv` rows PRE and VERIFY named `req_run_tests` and `req_part_window` | K38-2: deleted with the cut; the run is stated uncut by `req_pres_spans`; both rows re-aimed, VERIFY's note says so | green (C17 14/0) |
| 6 | test-cpset-structure | `^foo$` EMITTED_BYTES 26497 -> 26495 | K38-2: RX_REQ_RUN `"666f6f@0"` -> `"666f6f"` (§6.3.7¶7 row 3), read by diff against BASE; re-recorded with its note | green |
| 9 | test-registry | `--list-limits` 82 rows against a manifest count of 83 | K38-2: `PCREC_MAX_REQ_RUN_EMIT` retired (the names list had moved, the count had not); the count is now 82 | green |
| 13 | test-encoding-checks | DD12a(i) new strict diverger `fra(n|m)k|frost` (`RX_REQ_RUN "N@K"`) | K38-2: byte "emitted" `6672@0` against utf8 "dominated" `6672`; the `@` follows REQ_WHY, which (iii) already lets differ and holds to its stamp; REQRUN_STAMP_RE's `@K` made optional (hex and mask still compared) | green (DD12a(i) PASS, 248 pairs) |
| 15 | test-cand-oracle | pres-picks: no `scan`/`window`/`rwin`/`rwhole` record, K35 | K38-2: those four records RETIRED (sheet §4.3); PICKS and the 10 witness lines retired | green |
| 17 | test-findings §5 | KNOWN_READERS `pcrec_req_window` not reached | K38-2 F5 deleted it; dropped from the set | green |
| 17 | test-findings §7/§8 | fire-c2b moves nothing; w-c2a/w-c2b pins | K38-2: c2b reads "REQ_RUN before '@', the 8-byte window", which no longer exists (findings.md §4: window row "none") | OWED: ruling asked of main (below) |

The c2b question went to main as plain text with a leaning. The options are:

- **(A), my leaning.** Re-aim c2b at the `@` that the @ table's row 2 produced (a cover or
  run-pinned window search). c2a becomes the row-1 `@` (a `_reqrun` pre-check). Re-pin w-c2a and
  w-c2b, and re-derive the fire reach rows.
- **(B).** Retire c2b: the reader, fire-c2b, w-c2b, the axes arm and the cloud axes row.

The sheet's §4.3 reads "the c2a/c2b rows re-aimed at rows 2 and 3 and counted", which leans
toward (A). Under K38-2 the measured values are:

- w-c2a: default `6769746875625f7061745f@10`, under its bundle `@7`.
- w-c2b: default `666f6f62617262617a71757578@8`, under its bundle `@0`.

## Checks

| check | result |
|---|---|
| `make strict` (merged tree) | clean |
| `make test-codegen` (after the self-pin) | rc 0, 920 PASS (`scratch/memfn/k382m/codegen.log`) |
| memfn finder/rows/link/targets (`make -k`) | rc 0; every family `checks failed: 0` (`memfn.log`) |
| G2 presence family, every pass incl. generic (G2_JOBS=4) | 1,123,853 passed / 0 failed; oracle green over 53,790 records (`g2pres.log`) |
| G2 presence `--plants` (16) | 16/16 RED by their own detectors (`g2plants.log`) |
| anchors (`scripts/m6read_check_sab_anchors.py`) | 1243 rows, all resolve |
| `CLAUDEMD_ROOT=worktrees/k382 scripts/check_claudemd_size.sh --all` | 365 within limits |
| census sample 300 | GREEN, 0 unexplained (census4) |
| re-run of the cloud-red sections (encoding-checks, cand-oracle, memfn-manifest, cpset-structure, registry) | rc 0 (`reds2.log`); test-resource green in `reds.log` |
| `tests/registry/limits_check.sh` standalone | 0 failed |
| test-findings | §5 green; §7/§8 OWED (c2b) |

Not run here: test-recursion-identity. The FILEPIN self-pin is to the merge, and nothing under
`src/` moved after it. The check is a gate job (cloud kind `recidentity`).

## Gate jobs

`$PCREC_TMPDIR/scratch/memfn/k382/jobs/` is re-pointed. The original is at
`scratch/memfn/k382m/common.sh.orig`.

- **`common.sh`.**
  - `BASE=e889ba64c` and `ABI_OLD=100; ABI_NEW=101`.
  - `REF` is k382m's niced archive build at `scratch/memfn/k382m/base/build/pcrec`.
  - `REFTR` and `WREF` carry `$BASE` in their paths, so the jobs rebuild the -DMF_TRACE and
    witness BASE from e889ba64c instead of reusing d81ebd294's.
- **Comment updates.** `ident.sh` names BASE through common.sh. `mech.sh` derives its rows from
  `git diff $BASE HEAD`. `604-kit-k382-reach` notes that its empty GONE/MAP was derived against
  d81ebd294 and still declares nothing.
- **Dry runs.** Every `--dry-run` passes: 600-609 rc 0. The ident shards read
  `--abi 100:101 --base-rev e889ba64c`, and dumps on 2 arms (base, start). mech is 136/135/135 of
  406 rows. NOT queued.

## Charter-vs-committed checklist

| charter item | committed |
|---|---|
| 1. merge main alone, resolve on merits, abi 101 by grep, re-pin stamps/expectations, strict, commit | 5880ecb2c (merge), 2a0116b75 (FILEPIN self-pin); strict clean |
| 2. census vs new BASE, `--abi 100:101`, 300 GREEN 0 unexplained; explain main-content movers | census4 GREEN; the one red was a census bug surfaced by the sample shift; fixed in 801078b0a, bb2e3120c, 12aee66c2 |
| 3. cloud reds checked locally; stale base or K38-2; fix real ones | table above; real ones fixed in 801078b0a and bb2e3120c, except findings §7/§8 (OWED, ruling) |
| 4. jobs 600-609 re-pointed, every --dry-run passes, not queued | done (scratch, not committed) |
| CHECKS list | all run, all green, except test-findings §7/§8 |
| report with the deliver file's sections and an `OWED:` line; lanecheck DONE | this file |

## STATE AT HANDOFF

- **Branch.** lane/memfn-k382 is committed and clean, with no rulings file. Every item is done
  except test-findings §7/§8, which waits on main's ruling on the reader c2b.
- **Under (A)** (my leaning):
  - In `gen_adversarial.py`, `choices()` reads c2a as the `@` when the artifact has a `_reqrun(`
    block (row 1), and c2b as the `@` otherwise (row 2).
  - Re-derive fire-c2b's rows in reach.tsv.
  - Re-pin w-c2a and w-c2b in witness.tsv to the values in "Cloud reds".
- **Under (B):** retire c2b at every reader listed in "Cloud reds".
- **Either way,** test-findings is the check to run. It is one harness section of a few minutes.
- **The box.** Nothing queued, no run in flight.

STATE: stopped (waiting on the c2b ruling; everything else delivered)

OWED: test-findings §7/§8 only, which waits on main's ruling on c2b (see "Cloud reds").
