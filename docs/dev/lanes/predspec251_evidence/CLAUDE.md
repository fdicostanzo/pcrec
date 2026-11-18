# docs/dev/lanes/predspec251_evidence/ — rev 25.1 of predicates_draft.md (review r43's fixes), its evidence

Lane predspec251 (2026-11-18), DESIGN EVIDENCE: every answer-level witness of critic review r43 (groups A, B, C, D,
SIMULATE-4, SIMULATE-7) re-run, and group J's evidence repairs. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec251_model.py` — the engine. LOADS lane predspec25's engine (`../predspec25_evidence/predspec25_model.py`,
  never edited) in memory up to its first print (which loads predspec244's: the one-rule path enumerator, the mode
  helpers; then the libpcre2 helpers, the rx-module expander, the instantiator). PARTS: A numbers (over `|`, through a
  hole, name = number across `&`); B an `&` operand inside a hole, and a hole inside a filter operand (three
  readings); C pass-start-read at two depths and inside an `occurrences` argument (84 / 134 of 364); D the product's
  order (the discriminating witness, and why rev 25's could not discriminate), legality facts, the removal unit, the
  joined copies' compile check; I a backreference under `(?J)` and across a splice, PART H's hit list under the
  canonical-numeral judge; J the parse rule's checks. Controls: libpcre2-8 through `../rxmodel_evidence/pcre2h.py`
  (run, never read) on hand-written regex; the one-rule engine; Python `re` as an intent oracle.
- `predspec251_model.out` — the forward run (committed). `predspec251_sabotage.out` — the run with every sabotage.

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec251 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec251_evidence/predspec251_model.py > fwd.out)

Seconds. `PREDSPEC251_SABOTAGE=s1|s2|s3|s4|1` (one, a comma list, or all): s1 the product first hole FASTEST; s2 copies
differing in a group name joined by branch reset; s3 the parse rule without the record's clause "the sequence mark
is explicit"; s4 predspec25's operator-order sabotage on PART J's parser.

Verdicts (2026-11-18): forward 25 of 25 OK. Sabotage: s1 24 of 25 (D1 FAILED); s2 24 of 25 (D5); s3 24 of 25 (J9
`(item SEQ ",")* SEQ item`); s4 22 of 25 (J9 `x+ | y`, `x + y`, `x * y`); all four 20 of 25 (s4's order replaces
the parser s3 sabotages, so s3 shows only alone). Every sabotage caught.

## The tokenizer and parser predicates (review r43 lesson 1), beside the draft sentence that states each

| predicate (predspec25's expander, used here) | draft sentence (rev 25.1) |
|---|---|
| operators read longest first (`++ +? *+ *? ?+ ??` before `+ * ?`) | R.1.14 "THE MANAGER'S READINGS ... read LONGEST FIRST" |
| after `+`/`*`, a token that can begin an operand (a string, `(`, `[`, a name) makes it binary | R.1.14 the parse rule (MINE in the record) |
| a sequence mark cannot begin an operand (`starts_operand` excludes `SEQ`) | R.1.14, rev 25.1: the record's clause restored as a constraint on the spellings review |
| postfix operators stack, each on the operand so far (`x+?` is one token; `x+ *` two operators) | R.1.14, rev 25.1: THE DRAFT'S READING (stacking) |
| a statement ends at the end of the text given (one expression per call) | §5.1, rev 25.1: THE DRAFT'S READING (a statement ends before `NAME :=`) |
| `&`'s right operand is a condition `@c` only | engine LIMIT (the surface used), not a rule: decides nothing |
| a dotted name (`rx.digit`) is one token | engine shortcut for §5.4's `.` (a field); decides nothing here |

LIMITS: B2's readings (ii)/(iii) are run, reading (i) is a compile error by construction; C2's pool is alphabet `37x`
length <= 5; D3 legality is libpcre2's compile verdict (the draft's reading, rev 25.1, is the LANGUAGE's legality).
