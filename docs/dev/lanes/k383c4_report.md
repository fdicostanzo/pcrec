# k383c4 report

## Summary
Cloud `test-memfn-arch` (C4) was red on S3098..S3104. Prose is reworded arch-free (headers, SAB_DESC, SAB_DOC_FIGURE, and S3103's SAB_ID); 9 counted allowlist rows cover only the text that must name a level or target. `make test-memfn-arch` is green (17 passed, 0 failed); `m6read_check_sab_anchors.py` passes (1255 rows, all anchors resolve); `make strict` passes.

## Per-row changes
- S3098-S3102: header/SAB_DESC/SAB_DOC_FIGURE worded "narrowest/wider vector level". Rows: class 6 x1 each for the SAB_AFTER plant edit naming the kit identifier LV_X86_W16/LV_X86_W32 (S3102: LV_X86_W32 in the threshold expression).
- S3103: prose arch-free; SAB_ID reworded to `S3103-kit-admits-wider-level-on-baseline-target` (no other reader; the file name is unchanged). Rows: class 1 x2 (SAB_BEFORE2/AFTER2 anchors, verbatim targets.def text), class 6 x1 (SAB_AFTER names LV_X86_W32 and the target name).
- S3104: prose arch-free. Rows: class 1 x1, class 6 x2 (SAB_BEFORE/AFTER carry the target triple list the detector passes on the command line, verbatim from run_g2_pres.sh).
- Non-comment, non-SAB_DESC/SAB_DOC_FIGURE lines diff identical to HEAD except the S3103 SAB_ID. No plant or detector changed.

## Checks
make test-memfn-arch green; anchors check passes; make strict passes. Other new files on the branch (memfn/, docs/design/memfn/, tests/ci, tests/knowledge, run_sabotage_matrix.sh): C4 scans them and reports no new hit, so none is at risk today.

## Charter-vs-committed checklist
- Arch-free prose: done. Allowlist rows only for must-name text, each justified: done. No plant/detector change: done.

OWED: none

## STATE AT HANDOFF
Committed; nothing owed. No rulings file.
