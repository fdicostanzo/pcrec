# l3cen: census for lookaround unit L3 (BACK, lookbehind)

## Summary
Census run FIRST under D191 addendum 1, at main f8789cd2e (L1 landed), build in this worktree. The model predicts
57 movers: 55 corpus-only, 2 bench. Verdict: PROCEED (not a STOP). All 16 expectation rows (§14.2's L3 rows, the
READYL3-1/-6 rows and 5 non-movers) agree with the model; no §14.4 L3 prediction is contradicted.
Nothing built; no src/ change.

## The instrument
`docs/dev/lanes/l3cen_evidence/census_l3.py`: reuses census_l1.py's scanner, exact-set positions and item model
(census_e1/e2). Rule built from §14.4 L3 / D-4 / D-6 / D-11 text only: the root's left guard `lg` = the lookbehind
item's terms passing the root's left edge (offsets -1..-t contiguous, each 1..128 members); candidate = `lg ++ head`
at -t (head = maximal exact in-domain consumed stretch from the root start), first 32 positions kept; `t <= lb_bytes`
holds by construction under `byte`. The candidate is SPELLED and compiled by the base compiler (`--emit-facts=byte`);
its listed `req_whole_run` is the predicted run, compared with today's by information (8 - ceil(log2 |S|) summed),
the first row of `rn_choice_rows`. Today's route stamps (RX_REQ_WHY/HANDOFF, RX_DFA_SCAN, RX_DFA_PREFILTER,
RX_VM_PREFILTER) are read from the pattern's emitted C. `lg`'s `++ rg` clause is L2's and is not modelled.
Outputs: `summary.txt` (full), `movers.txt` (all movers with run, K, stamps).
Reproduce: `python3 -I census_l3.py <build/pcrec> <tree> docs/dev/lanes/sae1_evidence/bench_patterns.txt <outdir>`.

## Population
7613 rows (7224 corpus, 389 bench), 5932 distinct texts; 416 contain `(?<=`. Abstained 73 (all corpus: (?x)/(?i) 13,
conditional 11, recursion 4, subroutine call 40, verb 2, other 3). Read 343. Of those: alternation root 9 (BACK
combine not modelled; listed as ALTROOT, counted not predicted); never (L1 dead rows, no BACK candidate) 27; no left
leftover 205; BACK candidate 102 (compiler refuses 4; candidate not better than today's 40; information tie 1).

## Movers
57 = corpus 55 + bench 2 (a text in both counts once; none overlapped).
- new run (today none): 52 (corpus 51, bench 1).
- narrower required run (today a run, candidate strictly more information): 5 (corpus 4, bench 1).
- landmark K moves to -t: all 57.
- dead: 0 (BACK adds a candidate; never bits are L1's). Empty-extent movers: 0 in the population (the READYL3-6 rows
  stay witnesses only).
- cover route (today RX_DFA_SCAN "cover"): 7 corpus, all `(?<=one char)x` forms, why "dominated". §14.5: L3 does not
  change the cover route, so these gain a stated run/K in facts but no route change.
- prefilter: today's DFA prefilter on movers: memchr 37, offset-set 3, handoff 4, first-memchr-bounded 2, run-pinned 1,
  memchr-bounded 1, none 9 (cover/VM-only). Stamp movers expected at the gate: 9 movers are `emitted` today (handoff 0 for 7, none for 2: handoff would become the signed K where a handoff row applies); 48 are `dominated` (the pre-check becomes emitted).
- By today's WHY: dominated 48, emitted 9.

## Bench movers
- bench:258 `(?<=item )done`: narrower run `done` -> `item done` (K -5); today emitted, handoff 0, offset-set prefilter.
- bench:333 `(?<=\xc3\xa9)x`: new run `c3a978` (K -2), today none; dominated, memchr. (Spelled as bytes; the pattern
  is a UTF-8 literal, so under utf8 the census's byte reading holds only for the byte-encoding compile.)
Bench lookbehind texts read: 5 (1 has no leftover, `(?<=a|\xc3\xa9)x` is below the run floor: not a mover).
Bench abstentions: 0.

## Verdict under D191
GO (not STOP): the model predicts movers in corpus (55) and bench (2); the unit proceeds to its readiness fixes
(READYL3-1/-4/-6) and remodels. The owner's expectation of "some stuff" moving holds, but the bench share is small
(2 of 389 patterns; bench has few lookbehinds). No prediction of §14.4 L3 is contradicted. Notes for the two-sided
compare after the feature: (a) the 9 ALTROOT texts (e.g. `(?<=a)b|(?<=bc)d`, `(?<=ab)z|\bw`) are outside the model;
(b) `(?<=qz)x?a:` is an information tie (rarity decides); (c) `(?<=a)\Kb` and `(?<=\Ga)b` are predicted movers by
the model reading \K/\G as zero-width, which the build gate should confirm.

## STATE AT HANDOFF
Instrument and evidence committed on lane/l3cen. Rulings file absent (no entries to apply). No owed runs.
