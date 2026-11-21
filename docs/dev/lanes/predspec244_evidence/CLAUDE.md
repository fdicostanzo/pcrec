# docs/dev/lanes/predspec244_evidence/ — rev 24.4 of predicates_draft.md, its evidence engine

Lane predspec244 (2026-11-17), DESIGN EVIDENCE: every answer revision 24.4 of `docs/design/predicates_draft.md`
adds or changes (§R) is a line of `predspec244_model.out`. Rules nothing. Historical after merge; never edited after.

## Files

- `predspec244_model.py` — the engine. A NEW, small path enumerator (it patches none of the earlier engines): a regex
  subset parsed in the file (literals, classes, `\d \D \w \s`, groups, atomic groups, lookarounds, `\b`, anchors,
  greedy and lazy quantifiers), paths in PCRE's preference order, conditions as callout nodes `(?C"name")` reading the
  labels under one of three rules: `244` (the one rule: entering any branching resets the names inside it), `243`
  (rev 24.3's: a loop resets on entry and at every pass start) and `carry` (PCRE's capture). FIND-ALL is PCRE2's
  global loop; an empty iteration past the minimum is the last pass. Controls run on libpcre2-8 through
  `../rxmodel_evidence/pcre2h.py` (the library run, never read): plain PCRE2 for the capture, the MARKER MODEL for the
  one rule (an empty capture before every branching that contains the name; the label is the copy set last unless a
  marker was entered at or after it).
  PARTS: A rev 24.3's printed label lines under 244 and 243 (82); B 244 vs 243 over 16 programs and the carry counts
  rev 24.3 printed; C where the two rules part (a condition before its group in a pass); L the separated list (rulings
  R1, R2); N two groups of one name, with libpcre2 under `(?J)`; M the marker model and the order check; H the hit list
  on libpcre2 (the model, the failed first try) and in the engine; F the filter sentence's refusals (a classifier, THE
  DRAFT'S READING); S shared-label's candidates; J join order and zero-place; D the review drills; CHECKS.
- `predspec244_model.out` — the forward run (committed).

## Run (one engine process at a time; no make; nothing under /tmp)

    (cd $PCREC_TMPDIR/scratch/predspec244 && timeout 1800 python3 -I -B \
        <worktree>/docs/dev/lanes/predspec244_evidence/predspec244_model.py > fwd.out)

Well under a minute. `PREDSPEC244_SABOTAGE=1`: rule 244 resets only on entering a LOOP (not an alternation or an
optional). `PREDSPEC244_RULES=243`: the default rule of PARTS H, F, J becomes rev 24.3's (PART A runs both rule sets
on every line in every run).

Verdicts (2026-11-17): forward checks 129 of 129 OK; PART A 0 of 82 lines differ under either rule; sabotage 68 of
129 OK (S1-S5, REP, NEST, the empty pass, PART B, the marker-model comparisons and the duplicate-name lines FAILED):
caught; the 243 switch 129 of 129, output identical but for its header line.

LIMITS: the marker model compares positions (exact when every label group consumes a character; no row has an empty
label group); PART F's classifier is a small reading for the operands listed, not a compiler check; the engine has no
backreference or DEFINE node; PART B's pools are the earlier engines' (strings over an alphabet up to length 5,
lists of up to three items).
