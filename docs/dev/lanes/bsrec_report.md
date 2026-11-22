# bsrec report

## Summary
Records only, in three files: decisions.md (D201 addendum 3, plus the r67 -> r68 fix), memfn/docs/requests.md (one AMENDED line under R-47), plan.md (five child rows under [REQ-PAST-LAST]). plan_lint: 388 rows, 0 violations. No builds.

## R-23 amendments
D201 addendum 3 (manager, 2026-11-21) restates R-47's GO line ("No go for the scalar layer: it stays H64") and D201's Consequences line ("Off by default rides on -fmemfn-simd (OFF) as today") as amended under option A: the selector wrapper is live in the default build; scalar machine-code changes are checked for no loss (census, then a short timing in a cleared window), losers keep today's text. R-47 gets one appended line "AMENDED (D201 add. 3, 2026-11-21): ...". Original lines untouched.
Also (ruling R-1): addendum 2's population line now says "review r68 memfn-bspan" (was r67).

## R-24 records
In addendum 3, each marked by who: KIT MANAGER (scan scope = the WALK only; the wrap's deny live at both layers); KIT bspan ruling R-4 (smallest form serving 710's table; main asked for it); OBSERVATION (Frank's recollection, not a ruling), with the quoted words.
CITATION GAP: the verbatim words "We talked about that being the way we'd organize simd stuff anyway back when you used ifdef macro code" are NOT in the kit's record at the commits checked (grep of lane/memfn-k1108 7b0ac8bae, lane/bspan3, lane/bspan4, main: journal, responses, r68/r69 reviews, block_span.md). The kit records only the substance, in block_span.md rev 3 (lane/bspan3 0187ffda9, the F-23 paragraph, "Frank recalled (this round, through the manager)..."). Addendum 3 cites that and says the words are the manager's relay. Main should say where the verbatim words live if a better cite exists.

## R-30 plan rows
Children of [REQ-PAST-LAST] (no block-span row exists): [BSPAN-LEVERS] trigger: a bound is questioned by a C6 or Zen 1 run; [BSPAN-G1-TIMING] trigger: a bin reaches 8 real movers; [BSPAN-GCC-RERUN] trigger: the house gcc changes; [BSPAN-ZEN1-C6] trigger: CANDIDATE until a run on each bench box, Zen 1 via main (r69 R-31); [BSPAN-VANY-RIDE] trigger: vany's next touch. All from the kit's note/review, none invented.

## STATE AT HANDOFF
Rulings file: last entry applied R-1. Nothing owed. No new decision asked of main. Committed on lane/bsrec.
OWED: none
