# docs/dev/lanes/predspec25_evidence/ — rev 25 of predicates_draft.md, its evidence engine

Lane predspec25 (2026-11-17), DESIGN EVIDENCE: every answer revision 25 of `docs/design/predicates_draft.md` adds or
changes is a line of `predspec25_model.out`. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec25_model.py` — the engine. LOADS lane predspec244's engine (`../predspec244_evidence/predspec244_model.py`,
  never edited) in memory: its text up to its first print (the parser, the path enumerator with the one label rule
  "244", rev 24.3's "243" and PCRE's "carry", the mode helpers). On top: an EXPANDER for the rx-module surface
  (placeholder marks `SEQ`, the nine postfix quantifier operators, `&` with a condition `@c`, `|`, `[n = E]`), written
  from the ruled sentences (postfix tightest, then the sequence operator, then `&`, then `|`; operators read longest
  first); an INSTANTIATOR for holes in value positions (one copy of the literal per combination, the cartesian
  product, illegal combinations removed, legality = libpcre2 compiles it); a NUMBERING step for the label-number
  trial. Controls: libpcre2-8 through `../rxmodel_evidence/pcre2h.py` (run, never read) on HAND-WRITTEN regex; Python
  `re` as an intent oracle; THE STATIC-ORDER MODEL (labels of loop-free patterns from plain captures and pattern
  order, exact where a lookahead sets a label at a later text position).
  PARTS: PS pass-start-read (the sorted list shown to the owner); AS array-slot; LF label-flow; NUM label numbers
  (the trial); RX the rx module (splice, precedence, holes, positions, counts, repeat, the nine operators, binding,
  tokens, a quantified condition, arithmetic beside patterns); E the error-or-warning rulings' shown rows; W the
  looped-warning vs `label.unset` reading; CHECKS.
- `predspec25_model.out` — the forward run (committed).

## Run (one process; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec25 && timeout 900 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec25_evidence/predspec25_model.py > fwd.out)

A few seconds. `PREDSPEC25_SABOTAGE=1`: the sequence operator looser than `|` and a postfix binding the whole chain;
two count arguments read as the union; a count hole read as an inner alternation; a condition in a loop body under
rev 24.3's per-pass reset.

Verdicts (2026-11-17): forward CHECKS 42 of 42 OK; sabotage 29 of 42 OK (PS shown lines and oracles, RX2, RX4, RX5,
RX8 FAILED): caught. The sabotage does not reach PART LF, NUM, E or W (their rules are not among the sabotaged ones).

LIMITS: the static-order model is for loop-free patterns only; the expander covers the surface used here, not a
grammar; legality of a combination is libpcre2's compile verdict; PART W's "can be unset" is over a small pool.
