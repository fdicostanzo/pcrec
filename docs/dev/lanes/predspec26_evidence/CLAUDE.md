# docs/dev/lanes/predspec26_evidence/ — rev 26 of predicates_draft.md (the 2026-11-18 rulings), its evidence

Lane predspec26 (2026-11-18), DESIGN EVIDENCE: every 2026-11-18 ruling of COND-FAMILY that decides an answer, run;
every table the owner was SHOWN in those entries, reproduced; every MANAGER'S READING a run can test, tested. Rules
nothing. Historical after merge; never edited after.

## Files

- `predspec26_model.py` — STANDALONE (loads no earlier engine). Controls: libpcre2-8 10.46 through
  `../rxmodel_evidence/pcre2h.py` (run, never read: D181) on hand-written regex, a condition a string callout, FIND-ALL
  PCRE2's global loop (R.1.2); Python `re` where the owner was shown a Python run. PARTS: N number-names and 0; H
  hit-carry and the nullable argument; P product order, removal, name-hole, the count-hole kind; AL array-lift; HF
  hole-in-filter; REF the reference rule (free-name); EX the export rule's visibility table; CS condition-in-sequence
  and quantified-condition; LA lookahead-labels; CX complement-place, lone-complement-match, `anything`; VH the value
  hole fleshed out (a callout model, controlled against `\k<y>`); RS the two held-back questions re-stated.
- `predspec26_model.out` — the forward run (committed): CHECKS 106 of 106 OK.
- `predspec26_sabotage.out` — all thirteen sabotages at once: 78 of 106. `predspec26_sabotage_each.out` — each alone.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec26 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec26_evidence/predspec26_model.py > fwd.out)

Seconds. `PREDSPEC26_SABOTAGE=1` (all) or `s1,..`: s1 hit-carry off; s2 product first fastest; s3 removal of the
piece; s4 a filter judged before its holes are filled; s5 dynamic scoping of references; s6 `_` ignored; s7 numbers on
composed patterns; s8 array arithmetic pairwise; s9 a value reinterpreted as regex; s10 a lone complement matching;
s11 a quantified condition read as regex; s12 lookahead labels invisible; s13 a sequenced condition tested once.
Each alone fails at least one check (the `_each` file); every sabotage caught.

## The classifier predicates (RULE-AS-CODE), beside the draft sentence that states each

There is NO tokenizer or parser here: programs are written as Python structures, so no parse reading is exercised.
The compile-time classifiers are the rulings' words as code: a classifier line is a CONSISTENCY check, never an
independent control.

| predicate | draft sentence (rev 26) |
|---|---|
| `number_allowed`: 0 always; else one written literal (or an `&` chain with exactly one pattern operand) and a group whose name is not shared | §R.1 place table, column NUMBER; R.1.13 "number-names" |
| `hole_ok`: count = values that are counts; name = exactly one name; pattern = any (an alternation in the group); class/option/backreference = OPEN | §R.1 HOLE POSITIONS table |
| `copies`: the product, first hole slowest; `remove`: the whole copy | §R.1 HOLE POSITIONS, count row |
| `lift`: every combination, first operand slowest | R.1.14 "array-lift" |
| `outward` + `judge_filter`: holes filled first, then the operand judged by the conservative edge classifier (an edge `\b \B \G \K`, an edge lookbehind / lookahead) | R.1.4 operand-context; place table, KIND column |
| `resolve_backref`: a reference reads the namespace of the rx it is written in; a name it does not define is an error | place table, REFERENCE column |
| `exported` / `visible_inside`: public unless `_`; outside: own literals' public labels + public part labels by path; `[_ = A]` closes all | place table, VISIBLE column |
| `can_match` / `can_filter`: a complement filters only; an outward-looking literal matches only; an `&` chain matches with one match-capable operand | place table, KIND column |
| `quant_ok`: a postfix quantifier on a condition is an error | R.1.14 "quantified-condition" |

LIMITS: the outward classifier reads only the operand's first and last atom (enough for its witnesses); the value-hole
model is exact for one value at a time (a lazy capture plus an equality callout), its width readings are the two
candidates named in the draft, not a ruling.
