# suitetri report: full suite 20261027 (frozen 7d3be7ec7), recursion-identity red and mech anomalies

Logs read: `build/full_suite/20261027_7d3be7ec7/{summary.txt,red_stages.txt,trailer.log,recidentity.log,mech.log}` (main tree), the 10-23 run's `recidentity.log`/`mech.log` under `build/full_suite/20261023_5596c3207/`, plan row [RECID-A], docs/dev/lanes/recpin_report.md, docs/dev/full_suite_ledger.md, the runner header and verdict block of tests/mech/run_sabotage_matrix.sh. No make test/mech/axes was run; one throwaway build of ac4917d and tip in this worktree's `build/` (removed) tried single-pattern probes and was abandoned (ac4917d's CLI has no `-fcomments`/`--pattern`; the gate's own invocation shape is needed to compare regions).

## Summary

- Recursion identity: the red is ONLY the known (A) failure. (A) differing counts are 167 / 381 / 167 / 111 (default / vm / noprefilter / nocaptures), identical to 7234c2e86's, so SCANEDGE-SET (abi 87), INLINE-C stage 0 (abi 88), 1a and 1b (abi 89) added no (A) mover. (B), the positive controls and the linkage arm all pass. One new datum: the bref-rename bucket reads 328 on every axis (366 on 10-23, band 381..441), cause not pinned to a pattern list (see below).
- Mech: the matrix verdict is `unexpected 0` and rc=0 (the stage is green). The 31 anomalies are all one new kind: the plant does not compile (CHK-1 classifier, substr1fix 7047b69e4, 2026-10-24, landed AFTER the 10-23 freeze). None is a harness/timing artifact and none comes from the callout rows (S1646-S1676 produced no anomaly). They are 31 rows whose DETECTED claim was never a compile-clean measurement; the run exits 0 on anomalies by design, so they sit green.
- Unreached 15 / undetected 20: both are the same size as before in the expected sets; membership changes are small and all explained (below).
- Out of scope but on the same summary line: `san=RED(rc=2)`. Not triaged here.

## Recursion identity

Stage rc=2 (`make: *** [Makefile:1202: test-recursion-identity-locked] Error 1`). Log verdict: `checks passed: 10, checks failed: 8`. The 8 FAIL lines are exactly 2 per axis (default, vm, noprefilter, nocaptures), the same two checks each time:

1. `(A) N call-free patterns emit a DIFFERENT PROGRAM REGION than ac4917d for a reason no ruling has recorded`.
2. `(A) the bref-rename bucket admitted 328 patterns against ... census of 411 ... outside the +/-30 band`.

Counts, this run against 7234c2e86 (plan row [RECID-A] status 2026-10-26) and against 5596c3207 (10-23 full run log):

| axis | 10-23 (5596c3207) | 7234c2e86 (plan) | this run (7d3be7ec7) |
|---|---|---|---|
| default | 78 | 167 | 167 |
| vm | 127 | 381 | 381 |
| noprefilter | 78 | 167 | 167 |
| nocaptures | 54 | 111 | 111 |

Corpus: 4798 patterns (4348 call-free) on 10-23; 4950 (4467 call-free) now. Every other (A) tally the log prints is consistent with the known canonicalizer buckets (all `*-stamped-but-deny-is-a-noop=0`, `unstamped-but-*-moves=0`, `call-bearing-in-population=0`).

Everything else passes: the positive control (pre-module reference refuses all 483 call-bearing patterns) on all four axes; (B) whole-file vs 719a17ccb `differing=0, stamp-moved=0, refusal-mismatch=0` on all four axes (same=4101 on vm, 4100 on the others); linkage (4100 identical with and without `-fno-splice-calls`); the four named elision patterns; MEMFN R4h and R-12 liveness; ART-SIZE movers. So no other pin or part of the stage failed.

Attribution of growth: none to the landings you list. The count did not move between 7234c2e86 and 7d3be7ec7 on any axis, and the new landings (scan edge sets, the callout kind, abi digits, the kind row refactor) change either the abi stamp, which (A)'s program-region compare excludes, or callout-bearing artifacts, which are not call-free. Caveat, stated plainly: equal counts prove no pattern was ADDED to the differing set, not that no member's region text changed; the log prints only the first 10 names per axis and no list, so a same-count swap is not excluded. The 78 -> 167 growth (and 54 -> 111, 127 -> 381) happened earlier, between 10-23 and 7234c2e86, i.e. the I1/I2 iterators, subst, abi 84-86 and the corpus growth the plan row already names; the printed names are the K128 empty-iteration-guard shapes recpin diagnosed (`((?:a|b|))+a\1`, `((?:()|a)+?)b`, `((?=a))+?\B\g{-1}` etc.).

The one thing not explained by the plan row: the bref-rename bucket. 10-23: 366 (recpin: 401 at the pre-corefix base); now 328 on all four axes. A bucket drop cannot come from new corpus patterns; the bucket only admits a pattern if the rewritten reference equals the tip region byte for byte (run_recursion_identity.sh around `rbrefrename`), so 38 backreference patterns that the rename rewrite used to explain now differ for a second reason and fall out (into the differing set or an earlier bucket). I did not identify them: that needs the gate's KEEP=1 membership, a 23-minute box-lock run. The check has been failing since before corefix, so this does not change the verdict; it is evidence the never-moving pin keeps accumulating causes, which is the [RECID-A] argument. Hypothesis (unverified): the same K128 empty-iteration guard text, or the emitbidi respelling of kit run-compare constants, breaks the rewrite for brefs inside nullable loops.

## Mech anomalies

Trailer: `== mech run COMPLETE: 1041 rows (unexpected: 0, undetected: 20, unreached: 15, anomalies: 31, oracle-skipped: 0) at 7d3be7ec7`. Previous: 942 rows, unexpected 6, undetected 20, unreached 18, anomalies 2. The runner counts `ANOMALY|APPLY-FAILED|BUILD-FAILED|FATAL` (verdict block) and exits 1 only on `unexpected > 0` (`[ "${unexpected:-0}" -gt 0 ] && exit 1`, end of run_sabotage_matrix.sh; nocompile_selftest.sh line 8 records "the matrix exits 0 on an anomaly").

What the 31 are: all 31 carry `ANOMALY (the plant does not compile: ... -- a compile failure is not a catch; make the plant warning-clean)`. That verdict is produced by CHK-1 (commit 7047b69e4, 2026-10-24, after the 10-23 freeze): a failing arm whose log has a `file:L:C: error:` line is scored ANOMALY ahead of DETECTED (`score_arm`, `NOCOMPILE_ERE`). The previous run's two anomalies were different (stale plant text, S465 and S1392) and are gone (fixed by fsfix). So none of the 31 is a harness artifact; it is a new instrument finding that the 31 old DETECTED scores may have been compile failures. By the error text each row logs, three kinds:

| kind | n | rows | what the log shows |
|---|---|---|---|
| A. plant trips -Werror in the artifact or driver | 14 | S1152, S1159, S1174 (`'window' may be used uninitialized`), S135, S231, S272, S666 (unused parameter), S1418, S739 (unused variable), S676, S678 (`rx_class_bitmap1` defined but not used), S677, S719 (suggest parentheses), S707 (unsigned `< 0` always false) | the plant leaves a warning that the harness's `-Wall -Wextra -Werror` GENCFLAGS turns into an error |
| B. plant breaks the code outright | 11 | S106, S271 (implicit declaration of `rx_span_match` / `rx_span_match_caseless`: the plants name the pre-seam-rename `_bref_match` family), S36 (`'w' undeclared`), S403 (`rx_class_bitmap0` undeclared), S448 (`rx_ofs_k0`), S51 (`pa_rv0_mk`), S53, S56, S57 (`stv` undeclared), S41 (`stray '\'`), S1084 (`expected expression before '{'`, kit proof_sites.c) | the plant no longer compiles against the code it was written for (stale after later emitter/seam changes) or never did |
| C. compile failure IS the row's intended catch | 6 | S07 (errno without errno.h; its own header counts a compile check as a catcher), S1112 (SAB_DESC: "and the artifact does not compile"; reach:ok now, partlayout 7fail), S184 (a generated `_Static_assert` catches it by design, header lines 15-24), S526 (the detector is a compile of static asserts), S989 and S1242 (the layering rule is detected by compiling ksrc.c/ks_measures.c on a parts-only include path: `pcrec.h: No such file`) | the classifier cannot tell a designed compile-time catch from a plant that merely broke the build |

(Check the count: 14 + 11 + 6 = 31. S272's header predicts a COMPILE ERROR as its catch, but the error now logged is an unused parameter, not the predicted `bad AST node`, so it is filed under A; it also shows its plant behaviour has drifted.)

Disposition class per the brief: none of the 31 is (i) expected from the new callout rows or landings (no S1646-S1676 row is among them; the new mech rows scored DETECTED), none is (ii) a timing artifact. Kinds A and B (25 rows) are (iii) real check weakness: the row's catch is unproven until the plant compiles clean. Kind C (6 rows) is also (iii), but in the classifier: it has no declaration for a designed compile-time catch, so it files false anomalies.

Unreached 15 and undetected 20, membership against 10-23:
- Unreached: 18 -> 15. Gone: S1112, S1114, S1120 (the three stale partlayout caller-count witnesses; re-aimed, reach now `ok`). S1112 then re-enters as an anomaly (kind C). The 15 remaining are the previous run's declared-EXPECTED set, unchanged (e.g. S904, S917, S919 print `UNREACHED (EXPECTED ...)`).
- Undetected: 20 -> 20, but not identical. Gone: S283-run-rows-offset-skip-bit-dropped (now `DETECTED`, prechecks 11fail/384pass, reach ok; the previous run's open question D is closed in the safe direction). Added: S1352-ctx-init-reads-fresh-vars (`UNDETECTED (EXPECTED)`, subst 0fail/8919pass; retired on purpose by 1222b31be, 2026-10-24: RX_ITER_INIT writes vars/nvars, equivalent mutant). S903 (previous question D) is now a declared `UNDETECTED (EXPECTED)` (compound:0fail).
- The previous run's other reds are gone: S1112/S1114/S1120 stale witnesses, S465 and S1392 plant text, S284 stale expectation (now `DETECTED`, scanedge 3fail).

## Dispositions

| item | disposition |
|---|---|
| Recursion identity (A), 167/381/167/111 | plan note on [RECID-A]: counts unchanged from 7234c2e86, the four landings added no mover. Fix lane stays the row's own (re-base or retire the pin; manager's leaning already recorded). No new row. |
| bref-rename bucket 366 -> 328 | plan note on [RECID-A]: the bucket shrank 38 since 10-23, cause unidentified; the re-base lane should list bucket membership (KEEP=1 run) at 10-23 vs tip before re-basing, so no canonicalizer stays tuned to a number nobody explained. |
| recursion (B), controls, linkage | none (green). |
| 14 kind-A plants (-Werror in artifact/driver) | fix lane needed: make each plant warning-clean (the S1354/S1374 treatment of 7047b69e4), re-measure, keep DETECTED only if a non-compile arm fails. No row exists for it. File a plan row (suggest `[MECH-NOCOMPILE]`). |
| 11 kind-B plants (broken against current code) | same fix lane; these are stale plants (S106/S271 name the pre-rename seam), each needs a re-anchor with its intent re-verified, not a mechanical edit. |
| 6 kind-C rows (designed compile-time catch) | fix lane needed, small, in the runner: a declared opt-in (a row field such as the compile failure being the intended catch, with the expected `error:` text) so CHK-1 stops flagging them, or re-aim the rows at a runtime arm. A checking change; the manager decides the spelling. Same plan row. |
| Anomalies exit 0 | plan note on the same row: 31 unmeasured rows leave `make mech` green by design (nocompile_selftest.sh line 8). If the manager wants the gate to enforce the clean-plant rule, an anomaly-count ratchet (declared allowance, shrinking) is the harness-minimal form; not a recommendation to build now. |
| Unreached 15 | none (all declared EXPECTED, unchanged). |
| Undetected 20 | none (all declared EXPECTED; S1352 is an intentional new member, S283 left because it is DETECTED). |
| `san=RED(rc=2)` | out of this brief; separate triage (sanred landed 7aaebf962 before the freeze; a fresh `san.log` read is needed). |

## Ledger-ready verdict line

`2026-10-27 7d3be7ec7: recidentity RED = only the known [RECID-A] (A) (167/381/167/111 differing, identical to 7234c2e86; bref-rename bucket 328 vs census 411, was 366; (B), controls, linkage green); mech GREEN rc=0, unexpected 0, undetected 20, unreached 15 (all declared), anomalies 31 = CHK-1 "plant does not compile" (14 -Werror, 11 stale/broken plants, 6 designed compile catches), a new instrument finding, not a regression; san=RED not triaged here.`

## STATE AT HANDOFF

STATE: complete. Read-only triage; no code or test change, no run owed. Rulings file docs/dev/lanes/suitetri_rulings.md read before the report: "(none yet)", nothing applied. Open facts I could not close without a heavy run: the identity of the 38 patterns that left the bref-rename bucket, and whether any of the 31 anomaly rows still has a real non-compile catch. Branch lane/suitetri, report committed.
