# r1onax report

## STATE AT HANDOFF
Floors re-pinned in tests/axes/memfn_arm.py (committed on lane/r1on); local axes cell green (90 passed, 0 failed). Rulings file: none present. cloudrun r1on-axes2 launched as the last act.

## CAUSE
Premise held: the failed log of run 43625961160 showed only the four precheck-assign-byte floor lines (byte 130 < 131, utf8 185 < 189, default and simd). Reach diff over the corpus (default vs `--harness=restore=alt`, deny `--memfn=no-precheck-assign-byte`): byte 123 -> 120, utf8 178 -> 174; nothing joined. Leavers: byte `((a)|b){2,4}c`, `ab|a\Gb`, `a{1,2}(?:(?=\w)|(?<=\w))A`; utf8 those three plus `-{1,2}(?:(?!a)|)a`. All four are named census movers (s2r1b_report.md classes 1, 2, 4). A stated run through an equal-width alternation replaced the one-byte assign pre-check. No answer change.

## PINS
byte c-default 131 -> 130, utf8 c-default 189 -> 185, both layers (default, simd); comment names rule (1) ON, abi 107.

## VALIDATION
`MEMFN_REACH_ONLY=1 AXES=--memfn=no-precheck-assign-byte tests/axes/run_axes.sh` under boxlock: differ=130/185 at floors 130/185, both layers; memfn arm OK, 90/0.

## OWED
Cloud axes r1on-axes2 (verdict via monread/queuewatch).
