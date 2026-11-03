# s677fix report (2026-11-03)

WRONG: S677's plant joined strided per-position tests with `||`; the kit emits them inside `while ((more) && TEST)`, so the artifact had a bare `a || b` beside `&&` and the harness's `-Werror=parentheses` failed the build: scored ANOMALY (suitetri_report.md class A).

NEW PLANT: same mutant (OR for AND), plus a second pair (SAB_FILE2 = same file) that parenthesises TEST in the while emission: `" && (%s)) {\n"`. Only the S677 row file changed; no memfn/src edit.

EVIDENCE: committed first (runner archives HEAD), VALIDATE_ONLY ok, then a real single-row run (~1 min, log $PCREC_TMPDIR/scratch/memfn/s677fix/run.log): reach ok 1/1, corpus 0fail/3653pass, memfnarms 32fail/342pass, DETECTED; trailer `1 rows (unexpected 0, undetected 0, unreached 0, anomalies 0)` at b5d99d1ff. SAB_DOC_FIGURE replaced by this measurement.

OWED: nothing for S677. (Other class A rows remain: S1152 S1159 S1174 S135 S231 S272 S666 S1418 S739 S676 S678 S719 S707.)
