# r74 growth2: inline verification (coordinator, 2026-11-21 ~13:40)
Inline per skill §6.2 (every CONFIRMED finding is a quote claim or a one-call repro). Calls run with
CRIT_SCRATCH=PCREC_TMPDIR=.coord/verify, SUBJECT review tree d5257c005.

## VERDICT-1  HOLDS
cells.tsv:78-79 `empty ... 1000000 budget 1 stability refuse:pattern too large none (K156) - K156:compiled` (inl alike).
judge(spine/empty@1000000, refused "pattern too large: NFA exceeds") -> (True, ''): any size cap's text passes.
Fix direction checked: growth_driver one 0 442368 RAISE=0 on empty x 1,000,000 -> rc=-1 "pattern too large: 5014582
bytes of emitted code (limit 500000)"; inl -> rc=-1 "... 11014582 bytes of emitted code". The shipped emit cap refuses both.
## VERDICT-2  HOLDS (quote): run_growth.py:84-87 second key `plus-edge-matcher-cost`; docs/testing.md:5589 names it.
## VERDICT-3  HOLDS
run_growth.py:228 expect = edge text + ",refuse:" + PLUS_REPLICATION_TEXT for every `+`@250 cell. judge(matrix/group.plus.sole.lit@250
[limit PCREC_MAX_NFA_STATES], refused "...nested bounded repeats would replicate...") -> (True,''). Real: judge_cell.py subject
matrix/group.plus.sole.bref@250 -> refused "pattern too large: nested bounded repeats would replicate a body 262144 times" -> PASS.
## VERDICT-4  HOLDS (a, c); (b) by reading
(c) judge(depth/grp@251, refused "internal error: parentheses are too deeply nested in walk") -> (True,''); ladder_ok(depth/grp@251,
refused "internal error: out of memory in the walk") -> True. (a) ladder_ok(spine/lit_ship@131069, refused "pattern too large (NFA exceeds
131072 states)") -> False. Latent: no src/ internal-error text contains the substrings today (critic's grep; not re-run).
## VERDICT-5  HOLDS (quote): run_growth.py job(): `if cap < 2 * len(cell.pattern): continue`, no count, no output.
## VERDICT-6  doc, not verified (text-only).
## FIXES-1  HOLDS (quote): run_growth.py:463 `plog = os.path.join(os.path.dirname(walls_path()), "growth-lib-progress.log")`, untagged.
## FIXES-2  HOLDS (quote): run_compile_stack.sh:276-284 (exit 0 + non-empty cout -> "did NOT die"); growth_driver.c:201 prints
`rc=-9 hw=0 ... could not start the thread` and main() returns 0.
## FIXES-3  doc, by the critic's grep (PLUS_250 appears only in matrix_axes.tsv's header).
## HOUSE-1  HOLDS (grep): `sample` hits in run_growth.py only (def :269, argparse :532, use :555); none in run_growth.sh, Makefile,
run_compile_stack.sh, docs/testing.md.
## HOUSE-6  HOLDS: cnt (?:ab){2,5} raise 1: n=9362 rc=0, n=9363 rc=-1 "NFA exceeds 131072 states". Cells at 16384/100000, no limit twin.
## HOUSE-8  PARTLY: alt_cap_emit WITHOUT a main() (the stability twin's mode): 800 rc=0, 801 rc=0, 802 refused (emitted code);
WITH a main() (the limit cell's mode): 800 refused. So each half sits at the exact edge of ITS OWN mode (the main() is the gap, as
for alt_lit); the critic's "800 already refused" is the with-main reading. The doc sentence "one unit past it" is still wrong.
cat_grp_emit 1008 no-main rc=0 (same shape).
## HOUSE-2/3/4/5/7  not verified (maintenance/doc/timing; HOUSE-4's 30.5 MB emit costs 1.4 GB RSS: not re-run on the shared box).
VERIFY COMPLETE
