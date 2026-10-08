# b2tri2 — B2 test-findings red

Failed check: `FAIL: §5 S3 src/core/internal.h: PfAdmitSel carries a table pointer`
(tests/findings/structural_check.py, S3; the only red of 88 in test-findings).

Class: (b), a reader that B2's new code legitimately moved. PfAdmitSel is B2's
new struct and has no table pointer. S3's regex `typedef struct\s*\w*\s*\{(.*?)\}\s*(\w+Sel)\s*;`
with re.S is lazy but unbounded: from an earlier `typedef struct {` whose name does
not end in `Sel` it matched across `}` boundaries (13 KB) up to `} PfAdmitSel;` and
found a `unsigned *care` in unrelated prototypes. Not trace-ifdef related.

Fix: body is now `[^{}]*` (cannot cross a brace). Population unchanged: 5 *Sel structs
(FitSel, PflwSel, StWhySel, CandSel, PfAdmitSel). Plant (`unsigned *tbl` in a
PlantSel) still FAILs S3; reverted.

Solo re-run: `make test-findings` rc=0; `make strict` clean. No other section reads this
script. Commit 70b848d7 on lane/decfbB2.
