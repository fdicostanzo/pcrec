# verify — memfn-mcfix (review tree /home/pcrec/projects/pcrec/worktrees/crit-memfn-mcfix, slot dir = docs/design/memfn/span_cards/slot)

## FIDELITY-1
HOLDS. link.py:203-234 timed_shape_check: `if callee in defined: bad`, `elif r: ext.add`; link.py:590 `timed_shape_check(a.name, o, sym)` discards ext. Re-ran critic's drive.py over p0-p7.o (python3 -I drive.py SLOT p*.o, rc 0): p0 PASS, p1 REFUSE, p2 (section(".text.site")) PASS ['.text.site'], p3 (noinline,cold) PASS ['.text.unlikely'], p4 (indirect) PASS [], p5 (extern) PASS ['mf_ext'], p6 REFUSE, p7 REFUSE. Guard gap, no wrong timing today.

## FIDELITY-2
PARTLY. Mechanics HOLD: d197_rule.py:139 `"any" if which == "shipped"`, arm table row `memchr-variant-not-the-arms` (d197_rule.py:50-51) refuses only when want != "any"; re-ran swap.py (both records memchr=avx2 + GLIBC_TUNABLES, all forms cheaper): {'generic':'WIN','x86-64':'WIN','x86-64-v3':'WIN'}, no refusal, EVEX never timed (rule() :132-136 confirm path also takes any shipped variant; no code_commit read in the file: grep). RULE-8(b) same root. Consequence overstated: main's condition says "variant recorded", and it is (arm line prints memchr=avx2, GLIBC_TUNABLES in record), so the literal condition is met; a wrong-binding shipped arm is visible to a reader but not refused. Gap, not a contradiction.

## FIDELITY-3
HOLDS (CONFIRMED by plant, upgraded from SUSPECTED). est._synth(window=mfcard) in my dir, then plant3.py swapped the events+ns_e6 columns of kit.find_hit.mfind-swar.periodic.one.2.0 and ...mfind-w16... for all 7 launch pairs in cells.JMH.tsv (every (job,arm,length,launch) key stays unique). `est.py rows` base rc=0, plant rc=0, 0 REFUSED; diff: the two rows exchange values (swar 2068898 -> 2163387, w16 2163387 -> 2068898). Nothing pins cells.*.tsv (read_cells est.py:552-565 checks id/base/uniqueness only). Tamper/relabel-only vector; comment at est.py:559-560 over-claims.

## RULE-1
HOLDS. d197_rule.tsv verdict row 1 `INCONCLUSIVE shipped-arm-no-verdict` precedes `NOT-WIN second-run`. Re-ran diffdrill.py: "shipped refused --second" and "shipped variant unknown --second" -> INCONCLUSIVE,INCONCLUSIVE,INCONCLUSIVE. Contradicts main's condition "a second INCONCLUSIVE is NOT-WIN" literally (arguable: a refused run is no measurement). Contradiction of main's condition, not of D197.

## RULE-2
HOLDS. d197_rule.py:132-136 checks only outcome != REFUSED and variant; diffdrill "confirm: SAME record as confirm" -> LOSS at x86-64-v3; the drill's own [R3] case (d197_rule.py:211-213) passes the identical one_loss record as confirmation. Undeclared enforcement gap vs main's "must reproduce in one confirming re-run" (not a contradiction of a written row).

## RULE-3
HOLDS. grep d197 in docs/design/memfn/span_cards/slot: only d197_rule.py, .tsv, sabotage.sh; none in record.py/est.py/run.py; d197_rule.py:21 loads the live table. Undeclared gap (the header says "declared before any number exists" but nothing enforces it).

## RULE-4
PARTLY. row_x (d197_rule.py:68-73) refuses absent/drift/no-x; est.py:735-743 unpriced() also returns "text" for r.get("null")/gate False: divergence real. Line 94 `a=gc, b=gc` real (cosmetic). But the rule's own statistic is its x/aa floor, a null est row still has per-launch x, so pricing it is arguably intended; doc gap (define "unpriced" in the TSV), not a contradiction.

## RULE-5
HOLDS. diffdrill "confirm: cell missing" and "shipped confirm refused (absent)": reader -> CONFIRM again (critic's text-only reading LOSS is itself ambiguous). Undeclared/doc gap; contradicts no ruling.

## RULE-6
HOLDS. diffdrill "confirm not reproduced, no --second, avx2 ties" -> INCONCLUSIVE x3; with --second -> NOT-WIN x3. CONFIRM trigger text (verdict table) omits --second. Doc gap only.

## RULE-7
HOLDS. d197_rule.py:104 format string literally contains "ratio %s" (prints "ratio -" when a row is missing); :257 `all("ratio" in x[4] ...)` can never fail. Main's "scan ratio printed per level" has no failing witness: check-quality gap, not a contradiction.

## CHECKS-A1
HOLDS (by reading; not re-planted). window.c:2511 `wf_wsearch[FF_MFIND + 1]` and :2518 `_Static_assert(sizeof/sizeof == FF_MFIND + 1)`: both keyed to FF_MFIND, tautological; wsearch_of (:2524) answers NONE by bounds test for a later member. kit.h:668 enum ends FF_MFIND, no sentinel.

## CHECKS-A2
HOLDS. tests/memfn/rows_check.py:807-808 `good = len(why) > len("instrument:")`: any non-empty unit passes; unit is read nowhere else (grep).

## CHECKS-A3
HOLDS. memfn/tests/run_g2_mfind.py:417 `scale = max(0.0, (a.sites - 40) / 40.0)`: sites=40 -> 0 floors; defaults 80/160 unchanged (min(scale,1)). Non-default only.

VERIFY COMPLETE
