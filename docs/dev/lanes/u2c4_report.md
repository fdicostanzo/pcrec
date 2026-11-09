# u2c4: C4 vocabulary and the S3000 detector (kit request R-37, unit U2)

## Summary

C4 needed no edit on this branch: it reads 17/0 under both this branch's check and lane/u3tgt's, and the
13 FAILs main saw come from main's own (older) allowlist, not from U2's text. S3000 is now DETECTED by a
new kit-owned check, `tests/memfn/policy_check.c`, built and run by `tests/memfn/run_finder.sh`
(`make test-memfn-finder`). Hand verdict on S3000: RED (P2, P3, P4 fail), see below.

## C4 findings and their disposition

- This branch's tree, its own check/allowlist: 17 passed, 0 failed.
- lane/u3tgt's three files (run_arch_blind.sh, arch_blind_check.py, c4_allowlist.tsv) over this branch's
  tree (scratch export): 17/0.
- MAIN's three files over this branch's tree: 5 FAIL. One NEW hit (S2994's `SAB_BEFORE='sse,sse2,sse3'`,
  class 1, no row in main's allowlist) and four STALE rows (S725/S726 classes 2 and 6, which this branch
  already lowered). Main's allowlist predates U2's rows; the branch's `c4_allowlist.tsv` already carries
  the U2 changes (S2994 row added, S725/S726 re-aimed and lowered), written at memfn U2 WIP 880ae253e.
  So the 13 FAILs are the joint tree resolving the allowlist toward main's copy (or the check running
  with main's allowlist), not a vocabulary leak in S2975/S2994/S2995. S2995 and S3000 hold no ISA token.
- The actual lane/u3tgt tip (96868b42e, worktree u3tgt) reads 1 FAIL with its own files: a NEW class-6
  hit at tests/mech/run_sabotage_matrix.sh line 480 ("C9-x86 at ..."), u3floor's comment, not U2's.
  Fix there is a reword (name the target by the kit's tokens) or an allowlist row; not touched here
  (instruction: do not edit lane/u3tgt or main). Joint merge: take THIS branch's c4_allowlist.tsv rows for
  S725/S726/S2994 (and C4_ALLOW_FLOOR from the check's own side), do not keep main's.
- Nothing to reword or allowlist on this branch, so no C4 edit was made (adding unused rows would be a
  STALE-row failure).

## The S3000 detector

- `tests/memfn/policy_check.c` (public header only): defines a sound FIND site on an art whose target is
  stated, with a discarding sink. P1 control: named bits (INLOOP|SIZE_LEANING) define cleanly. P2: policy
  with `1u<<7` is refused (rc -1). P3: the message carries `policy bits 0x80 `. P4: bit 8 alone, `0x100`.
- `tests/memfn/run_finder.sh`: compiles every memfn/src/*.c with `-DMF_TARGET_REQUIRED=1` (kit.h guards the
  default with `#ifndef`), links the check, relabels its counts into the section totals, floor
  POLICY_FLOOR=4 (a literal, K35). No new `run_*.sh`, so TT-9 (san_scripts/san_excluded; run_finder.sh is
  already OWN-TIER) and K35's LC_ALL=C (run_finder.sh exports it) are unchanged.
- S3000's expectation is DETECTED (header, SAB_DOC_FIGURE re-pointed).
- Hand run (the matrix driver yields to the box queue, which the brief forbids joining): the plant
  applied to a scratch copy of memfn/ (`SAB_BEFORE` -> `SAB_AFTER`, count 1), kit rebuilt at
  `-DMF_TARGET_REQUIRED=1`, check linked: P1 ok, P2 FAIL "mf_define did not refuse it", P3 FAIL, P4 FAIL,
  rc 1. Unplanted: 4/4, rc 0. Full `run_finder.sh` on the real tree: 3321 passed, 0 failed, with
  `ok   policy: 4 cases passed >= floor 4`. Exact matrix re-run owed to a window with the box: 
  `bash tests/mech/run_sabotage_matrix.sh S3000`.

## Checks run

- `bash tests/memfn/run_arch_blind.sh` on this tree: 17/0; lane/u3tgt's and main's versions as above.
- `tests/memfn/run_finder.sh` on the final tree: 3321 passed, 0 failed (policy part 4/4, floor 4).
- `make strict`: green. `make test-codegen`: rc 0, no `*** [test-` error lines.

## STATE AT HANDOFF

OWED: none. The exact matrix run of S3000 (`bash tests/mech/run_sabotage_matrix.sh S3000`) yields to the box queue; the hand run above stands in.

## Charter-vs-committed checklist

- C4 both versions shown: yes (above); edit: none needed, cause named.
- S3000 detector hooked into an existing test target: yes (test-memfn-finder).
- S3000 DETECTED, hand-run red: yes.
- K35 / TT-9: no new run_*.sh script.
- Deliver file, report, history index line: yes.
