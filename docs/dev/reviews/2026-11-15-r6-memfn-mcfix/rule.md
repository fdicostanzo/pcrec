# rule — memfn-mcfix

## Findings

### RULE-1 CONFIRMED — a SECOND run whose shipped arm has no verdict reads INCONCLUSIVE (offers a third run), not NOT-WIN
severity measurement; effort 1 row; blast: the verdict ledger at every level. d197_rule.tsv `#section verdict` row 1
`INCONCLUSIVE shipped-arm-no-verdict` precedes `NOT-WIN second-run`. Repro: rule/diffdrill.py cases "shipped refused
--second" and "shipped variant unknown --second" -> INCONCLUSIVE x3 levels, trigger "ONE re-run allowed". Main's
condition: "a second INCONCLUSIVE is NOT-WIN". Fix: a `NOT-WIN second-run` row (or `second-run-and-shipped-no-verdict`)
above row 1, plus a drill case.
### RULE-2 CONFIRMED — `--confirm` accepts ANY records, including the first run's own: a 1-2 cell loss "reproduces" with no re-run
severity measurement (the control shares its source with what it controls, learnings §3); effort small; blast: every
LOSS resting on 1-2 of 36 comparisons. d197_rule.py:132-136 checks only outcome != REFUSED and the variant; never that
the confirming record is window `mfconfirm` (record.py:44), a run id other than the first run's, its JMHC rows = the
CONFIRM verdict's `d197_confirm_cells`. Repro: diffdrill "confirm: SAME record as confirm" -> x86-64-v3 LOSS; the
drill's own case "[R3] that one-cell loss REPRODUCES" (d197_rule.py:211-213) passes the IDENTICAL `one_loss` record as
the confirmation. Likewise `--second` is a bare flag, never checked against a run id. Fix: refuse unless window/run
id/cell set match; drill case with the same record must REFUSE.
### RULE-3 CONFIRMED (code) — the rule TSV/reader are not PINNED in the run record: "declared before any number exists" is unenforced
severity measurement/design; effort small (record.py pins tables' sha-256 already for plan/floor/cards/policy); blast:
the verdict. No reader of d197_rule.tsv/.py's sha in record.py/est.py/run.py (grep `d197`: only sabotage.sh). The
scorer loads the LIVE table at verdict time (d197_rule.py:21), so a table edited after the numbers decides silently.
Fix: pin sha-256 of both in the mfcard window record at `window`; `rule` refuses a mismatch.
### RULE-4 CONFIRMED — TEXT/SCRIPT divergence on "unpriced": the reader prices rows est.py itself calls unpriced (NULL / gate false)
severity measurement (minor); effort 1 line; d197_rule.py:68-73 `row_x` refuses only absent/drift/no-x, while est.py's
own `unpriced()` (est.py ~ after drift) also counts `null` delta rows ("text": per-hit cost below its paired A/A or
signs mixed). A find_hit row est would not price still decides a cell. Also `either-row-unpriced` is evaluated on
`a=gc, b=gc` (d197_rule.py:94): both "rows" are the same object, so the predicate's two-row wording is cosmetic. Either
define "unpriced" in the TSV header (absent | drift | no W) or reuse est's `unpriced`.
### RULE-5 CONFIRMED — a missing or refused confirming record re-issues CONFIRM without bound; the TSV is silent
severity doc/design; effort 1 row + 1 drill case. The text says a confirmed cell "count[s] only if they lose again ...
one that does not reproduce scores tie" — a confirmation that is ABSENT (refused record, mis-bound AVX2, cell missing)
is neither. Reader: conf None -> loss unconfirmed -> CONFIRM again (diffdrill "confirm: cell missing", "shipped confirm
refused"); my text-only reading gave LOSS. Neither forbidden, but undeclared and loops. Declare it (e.g. CONFIRM once
more, then NOT-WIN), drill it.
### RULE-6 CONFIRMED — CONFIRM's trigger omits that `--second` must ride along; dropped, an unreproduced loss on the re-run reads INCONCLUSIVE (a third run)
severity doc; effort words. verdict row CONFIRM trigger "then this rule again with --confirm". diffdrill "confirm not
reproduced, no --second" -> INCONCLUSIVE vs "--second" -> NOT-WIN. Say "with --confirm (and --second if this was the
re-run)" or derive second-ness from the record (ties to RULE-2).
### RULE-7 CONFIRMED — the drill's end-to-end "scan printed per level" check cannot fail
severity maintenance (check); effort 1 line. d197_rule.py:257 checks `"ratio" in x[4]`, but the scan string always
contains "ratio" (d197_rule.py:104 prints `ratio -` when either find_byte row is missing). Main's condition "the scan
ratio is printed per level" has no failing witness. Check for a number, not the word.
### RULE-8 doc — wording: "loss CELLS" vs comparisons; axes cells incomplete/unchecked
severity doc; effort words. (a) header + `three-or-more-loss-cells` say CELLS; the reader counts (cell, libc row)
COMPARISONS (x1 + x2, d197_rule.py:119), which is what main's condition says ("1-2 of 36 comparisons"): one cell lost
on both rows = 2 -> CONFIRM, 2 cells x 2 rows = 4 -> LOSS at once (diffdrill). Rename the predicate. (b) `axes`: the
x86-64-v3 form is `mfind@w32+w16` but the row names no tail axis (w16 tail vs libc's own tail/page-cross handling);
every row asserts "32-byte EVEX shipped" while the shipped arm accepts ANY bound variant (want "any",
d197_rule.py:139) — on a box binding another variant the declared axes are false and nothing refuses. Either require
memchr=evex for shipped on this box or print axes from the recorded variant.
### RULE-9 design (family + general form) — third ad-hoc table/section reader in slot/
severity maintenance; effort small. `#section` parsers: record.py:81, est.py:578, d197_rule.py:25; verdict rules:
j1_rule.py (constants in code, m 0.5 k 5), d197_rule.py (TSV + WHEN), record.py's CAUSE table, est's outcome table.
General form: one `rules.py` (load sections, `WHEN` registry, `first(table, x)` returning (row, why), a pin of the
table's sha into the record, and an unused-predicate/unreached-row check over the drill) that j1's rule moves onto as
a TSV. Unlocks: pre-registration enforced for every slot verdict (RULE-3 once), drill reach counts per row (which
rows no case reaches). Trigger: the next declared verdict table (stage-2 re-measure after a WIN, or J1's re-run).

## PROBED-AND-HELD
- 30 constructed outcomes (rule/diffdrill.py) through d197_rule.py's own arm/levels vs my TSV-only reader (rule/mine.py):
  28 SAME, 2 DIFF (RULE-5, a text gap). Held: per-level verdicts (mixed swar LOSS / w32 WIN independent); 1 and 2 losses
  -> CONFIRM, 3+ comparisons -> LOSS at once; losses+wins mixed -> CONFIRM; non-reproduced -> tie -> WIN path; AVX2
  variant mismatch -> INCONCLUSIVE / NOT-WIN on --second; AVX2 refused + shipped losses -> LOSS; all unpriced ->
  INCONCLUSIVE / NOT-WIN; --second 18 losses -> LOSS (allowed: a real loss, not a second INCONCLUSIVE); gain == floor
  -> tie, gain == -floor -> tie, -floor-1 -> LOSS; one non-positive launch trimmed -> WIN; exactly 9/18 wins -> not WIN,
  10/18 -> WIN (denominator 18 incl. unresolved).
- Statistic: est.compute's x = (cell - base.<form>)/E per launch (E = cells' events, base = own miss-only base, same job
  and launch), / control slope u_l, / unit W, ppm; aa = med_l |x_l(twin) - x_l(arm)| (paired); gain_l = x(L)-x(F);
  floor = aa(L)+aa(F): as the TSV says. med = lower median (odd L=7: exact). trim drops the farthest (ties: last index).
- Scan cost: no predicate reads find_byte; printed only. No global verdict path (levels() loops `levels` rows).
- Keys: d197 key() = plan.py's find_hit key format; scan key = plan's kit.find_byte.<form>; CONFIRM cells move every
  form + twin to JMHC with its own bases (plan.py:450-457), window mfconfirm = J2 + JMHC.
